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
  local url=$1 sums_url=$2 out=$3 name sums want
  name=$(basename "$url")
  curl -fsSL --retry 3 -o "$out" "$url"
  # Erst komplett laden, dann suchen: awk bricht nach dem Treffer ab und würde curl
  # in einer Pipe mit "Failed writing body" (Exit 23) scheitern lassen.
  sums=$(curl -fsSL --retry 3 "$sums_url")
  want=$(awk -v f="$name" 'NF==1 {print $1; exit} $2==f || $2=="*"f {print $1; exit}' <<<"$sums")
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
  konsole \
  plymouth-plugin-script \
  sddm sddm-breeze sddm-kcm sddm-wayland-plasma

# ---------- Container: Podman mit Docker-Kompatibilität ----------
# "docker ..." und "docker compose" laufen über Podman (kein Docker Desktop nötig).
# Grafische Oberfläche: Podman Desktop (Flatpak, siehe flatpaks.list).
dnf5 install -y podman-docker podman-compose
touch /etc/containers/nodocker   # unterdrückt den Hinweis "Emulate Docker CLI using podman"

# ---------- VS Code (RPM aus dem Microsoft-Repo, besser als Flatpak für Dev-Container) ----------
rpm --import https://packages.microsoft.com/keys/microsoft.asc
cat > /etc/yum.repos.d/vscode.repo <<'EOF'
[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF
dnf5 install -y code
# Repo danach abschalten: Updates kommen über den täglichen Image-Build
sed -i 's/^enabled=1/enabled=0/' /etc/yum.repos.d/vscode.repo

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

# ---------- Mauszeiger: Alias-Namen als Symlinks ----------
CURSORS=/usr/share/icons/kissa-cursors/cursors
grep -v '^\s*#' /ctx/cursor-aliases.txt | while read -r target aliases; do
  [[ -z $target ]] && continue
  [[ -f $CURSORS/$target ]] || { echo "Zeiger fehlt: $target" >&2; exit 1; }
  for a in $aliases; do ln -sf "$target" "$CURSORS/$a"; done
done

# ---------- Härtung ----------
# 1. Updates nur mit gültiger Signatur: Regel für unser Image in die bestehende
#    policy.json einfügen (Aurora bringt dort schon eigene Regeln mit).
#    Neuere Fedora-Versionen liefern die Standardregeln unter /usr/share/containers/,
#    /etc/containers/policy.json überschreibt sie dann komplett – deshalb als Basis übernehmen.
install -D -m 0644 /ctx/cosign.pub /etc/pki/containers/kissa.pub
policy_src=/etc/containers/policy.json
[[ -f $policy_src ]] || policy_src=/usr/share/containers/policy.json
if [[ -f $policy_src ]]; then
  cp "$policy_src" /tmp/policy-base.json
else
  echo '{"default":[{"type":"insecureAcceptAnything"}],"transports":{"docker-daemon":{"":[{"type":"insecureAcceptAnything"}]}}}' > /tmp/policy-base.json
fi
echo "Basis für policy.json: $policy_src"
jq '.transports.docker["ghcr.io/lauzedao/kissa"] = [{
      "type": "sigstoreSigned",
      "keyPath": "/etc/pki/containers/kissa.pub",
      "signedIdentity": {"type": "matchRepository"}
    }]' /tmp/policy-base.json > /tmp/policy.json
install -D -m 0644 /tmp/policy.json /etc/containers/policy.json
jq -e '.transports.docker["ghcr.io/lauzedao/kissa"]' /etc/containers/policy.json >/dev/null

# 2. Firewall: eigene Zone "kissa" als Standard (eingehend zu, außer mDNS + KDE Connect)
firewall-offline-cmd --set-default-zone=kissa

# 3. SSH-Server aus (privat nicht gebraucht)
systemctl disable sshd.service 2>/dev/null || true

# ---------- Sonstiges ----------
chmod 0755 /usr/bin/kissa /usr/bin/pandasay /usr/libexec/kissa-flatpaks
systemctl enable kissa-flatpaks.service
sed -i 's/^PRETTY_NAME=.*/PRETTY_NAME="kissa (Fedora Atomic · Aurora)"/' /usr/lib/os-release

rm -rf "$TMP"
