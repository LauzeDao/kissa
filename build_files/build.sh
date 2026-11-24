#!/usr/bin/env bash
# kissa – Build-Schritte im Container. Wird vom Containerfile aufgerufen.
# Die Dateien aus system_files/ liegen zu diesem Zeitpunkt schon im Image.
set -euxo pipefail

# shellcheck source=versions.env
source /ctx/versions.env
ARCH=x86_64
TMP=$(mktemp -d)

# ---------- Helfer ----------
# Lädt eine Datei und prüft sie gegen die Checksummen-Datei des Releases.
# Die Checksummen-Datei darf nur den Hash enthalten oder Zeilen "HASH  DATEINAME".
fetch_checked() {
  local url=$1 sums_url=$2 out=$3 name want
  name=$(basename "$url")
  curl -fsSL --retry 3 -o "$out" "$url"
  want=$(curl -fsSL --retry 3 "$sums_url" | awk -v f="$name" 'NF==1 {print $1; exit} $2==f || $2=="*"f {print $1; exit}')
  [[ -n $want ]] || { echo "Keine Checksumme für $name gefunden" >&2; exit 1; }
  echo "$want  $out" | sha256sum -c -
}

# Entpackt ein Archiv und installiert die genannte Binärdatei nach /usr/bin.
install_from_tar() {
  local archive=$1 bin=$2 dir
  dir=$(mktemp -d -p "$TMP")
  tar -xzf "$archive" -C "$dir"
  install -m 0755 "$(find "$dir" -type f -name "$bin" | head -n1)" "/usr/bin/$bin"
}

# ---------- Pakete aus den Fedora-Repos ----------
dnf5 install -y \
  fastfetch \
  plymouth-plugin-script \
  sddm sddm-kcm sddm-wayland-plasma

# ---------- Tools als gepinnte Releases ----------
# starship (Prompt)
f=starship-${ARCH}-unknown-linux-gnu.tar.gz
fetch_checked "https://github.com/starship/starship/releases/download/v${STARSHIP_VERSION}/$f" \
              "https://github.com/starship/starship/releases/download/v${STARSHIP_VERSION}/$f.sha256" "$TMP/$f"
install_from_tar "$TMP/$f" starship

# gum (hübsche Menüs für die kissa-CLI)
f=gum_${GUM_VERSION}_Linux_${ARCH}.tar.gz
fetch_checked "https://github.com/charmbracelet/gum/releases/download/v${GUM_VERSION}/$f" \
              "https://github.com/charmbracelet/gum/releases/download/v${GUM_VERSION}/checksums.txt" "$TMP/$f"
install_from_tar "$TMP/$f" gum

# kind (lokale Kubernetes-Cluster)
fetch_checked "https://github.com/kubernetes-sigs/kind/releases/download/v${KIND_VERSION}/kind-linux-amd64" \
              "https://github.com/kubernetes-sigs/kind/releases/download/v${KIND_VERSION}/kind-linux-amd64.sha256sum" "$TMP/kind-linux-amd64"
install -m 0755 "$TMP/kind-linux-amd64" /usr/bin/kind

# kubectl
fetch_checked "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
              "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl.sha256" "$TMP/kubectl"
install -m 0755 "$TMP/kubectl" /usr/bin/kubectl

# k9s (Kubernetes-TUI)
f=k9s_Linux_amd64.tar.gz
fetch_checked "https://github.com/derailed/k9s/releases/download/v${K9S_VERSION}/$f" \
              "https://github.com/derailed/k9s/releases/download/v${K9S_VERSION}/checksums.sha256" "$TMP/$f"
install_from_tar "$TMP/$f" k9s

# JetBrainsMono Nerd Font (für Prompt-Symbole im Terminal)
fetch_checked "https://github.com/ryanoasis/nerd-fonts/releases/download/v${NERDFONTS_VERSION}/JetBrainsMono.tar.xz" \
              "https://github.com/ryanoasis/nerd-fonts/releases/download/v${NERDFONTS_VERSION}/SHA-256.txt" "$TMP/JetBrainsMono.tar.xz"
mkdir -p /usr/share/fonts/jetbrains-mono-nerd
tar -xJf "$TMP/JetBrainsMono.tar.xz" -C /usr/share/fonts/jetbrains-mono-nerd --wildcards '*.ttf'
fc-cache -f /usr/share/fonts/jetbrains-mono-nerd

# ---------- Login-Bildschirm: SDDM statt Plasma Login Manager ----------
# Der Plasma Login Manager (Fedora 44+) ist fest auf Breeze ohne eigene Themes eingestellt.
# SDDM mit Breeze erlaubt ein eigenes Hintergrundbild.
cat > /usr/share/sddm/themes/breeze/theme.conf.user <<'EOF'
[General]
background=/usr/share/wallpapers/Kissa/contents/images_dark/3840x2160.png
type=image
EOF
systemctl disable plasmalogin.service 2>/dev/null || true
systemctl enable --force sddm.service

# ---------- Bootsplash ----------
plymouth-set-default-theme kissa
# Initramfs neu bauen, damit der Bootsplash schon vor dem Root-Dateisystem verfügbar ist.
KVER=$(ls /usr/lib/modules | head -n1)
dracut --no-hostonly --kver "$KVER" --reproducible --zstd -v --add ostree -f "/usr/lib/modules/$KVER/initramfs.img"

# ---------- Sonstiges ----------
chmod 0755 /usr/bin/kissa /usr/bin/pandasay
sed -i 's/^PRETTY_NAME=.*/PRETTY_NAME="kissa (Fedora Atomic · Aurora)"/' /usr/lib/os-release

rm -rf "$TMP"
