#!/usr/bin/env bash
# kissa – Rauchtest für das fertige Image. Läuft in der Pipeline nach dem Build:
#   podman run --rm --network=none -v ./tests:/tests:ro IMAGE bash /tests/image-test.sh
# Prüft, ob alles drin ist, was build.sh und system_files/ liefern sollen.
# Ausgabe: ✓/✗ pro Prüfung, Exit 1, sobald eine Prüfung scheitert.
set -uo pipefail

fails=0
pass() { printf '\033[32m✓\033[0m %s\n' "$1"; }
fail() { printf '\033[31m✗\033[0m %s\n' "$1"; fails=$((fails + 1)); }
check() { # check "Beschreibung" befehl args...
  local desc=$1; shift
  if "$@" >/dev/null 2>&1; then pass "$desc"; else fail "$desc"; fi
}
section() { printf '\n── %s\n' "$1"; }

section "Programme"
for bin in kissa pandasay starship gum kind kubectl k9s tofu helm flux stackit glab code distrobox fastfetch podman docker jq; do
  check "$bin vorhanden" command -v "$bin"
done
# Versionsaufrufe fangen kaputte Downloads ab (falsche Architektur, abgeschnittene Datei)
check "starship startet"   starship --version
check "gum startet"        gum --version
check "kind startet"       kind version
check "kubectl startet"    kubectl version --client
check "k9s startet"        k9s version -s
check "tofu startet"       tofu version
check "helm startet"       helm version
check "flux startet"       flux --version
check "stackit startet"    stackit --version
check "glab startet"       env HOME=/tmp glab --version   # glab legt beim Start ~/.config/glab-cli an; /root zeigt im Image auf /var
check "fastfetch startet"  fastfetch --version
check "podman startet"     podman --version
check "kissa help läuft"   kissa help

section "Terminal"
check "starship.toml (Vorlage) vorhanden" test -f /usr/share/kissa/skel/starship.toml
starship_out=$(STARSHIP_CONFIG=/usr/share/kissa/skel/starship.toml starship print-config 2>&1 >/dev/null)
if grep -qiE 'warn|error' <<<"$starship_out"; then fail "starship.toml lässt sich fehlerfrei laden"; echo "$starship_out" | head -5
else pass "starship.toml lässt sich fehlerfrei laden"; fi
check "fastfetch-Vorlage vorhanden"    test -f /usr/share/kissa/skel/fastfetch/config.jsonc
check "Hoji (Terminal-Pixelbild)"      test -s /usr/share/kissa/hoji-matcha.ansi
check "Tipps für 'kissa tipps'"        test -s /usr/share/kissa/tipps.tsv
check "Nerd Font installiert"          bash -c 'fc-list | grep -qi "JetBrainsMono Nerd"'

section "Desktop"
for v in matcha hojicha; do
  check "Global Theme org.kissa.$v"    test -f "/usr/share/plasma/look-and-feel/org.kissa.$v/metadata.json"
  check "Farbschema Kissa${v^}"        test -f "/usr/share/color-schemes/Kissa${v^}.colors"
  check "Icon-Theme kissa-$v"          test -f "/usr/share/icons/kissa-$v/index.theme"
done
check "Mauszeiger-Theme"               test -f /usr/share/icons/kissa-cursors/index.theme
check "Mauszeiger 'default'"           test -f /usr/share/icons/kissa-cursors/cursors/default
check "Mauszeiger-Alias 'left_ptr'"    test -e /usr/share/icons/kissa-cursors/cursors/left_ptr
check "Hintergrundbild Kissa"          test -f /usr/share/wallpapers/Kissa/metadata.json
for s in fruehling sommer herbst winter; do
  check "Jahreszeiten-Hintergrund $s"  test -f "/usr/share/wallpapers/Kissa-$s/metadata.json"
done
check "Soundtheme kissa"               test -f /usr/share/sounds/kissa/index.theme
check "Tag/Nacht-Timer (Benutzer)"     test -f /usr/lib/systemd/user/kissa-auto.timer
check "Backup-Timer (Benutzer)"        test -f /usr/lib/systemd/user/kissa-backup.timer
check "restic vorhanden"               command -v restic
check "secret-tool vorhanden"          command -v secret-tool
check "Wake-on-LAN-Helfer"             test -x /usr/libexec/kissa-wol
check "Backup-Ausnahmen"               test -s /usr/share/kissa/backup-exclude.txt

section "Boot und Login"
check "Plymouth-Theme kissa aktiv"     bash -c '[[ $(plymouth-set-default-theme) == kissa ]]'
if command -v lsinitrd >/dev/null; then
  check "Bootsplash steckt im initramfs" bash -c 'lsinitrd /usr/lib/modules/*/initramfs.img | grep -q "plymouth/themes/kissa"'
fi
check "SDDM-Hintergrund (theme.conf.user)" grep -q Kissa /usr/share/sddm/themes/breeze/theme.conf.user
check "SDDM aktiviert"                 bash -c '[[ $(systemctl is-enabled sddm.service) == enabled ]]'
check "os-release nennt kissa"         grep -q '^PRETTY_NAME="kissa' /usr/lib/os-release

section "Sicherheit"
check "Signaturregel für ghcr.io/lauzedao/kissa" \
  jq -e '.transports.docker["ghcr.io/lauzedao/kissa"][0].type == "sigstoreSigned"' /etc/containers/policy.json
check "Öffentlicher Schlüssel vorhanden" test -s /etc/pki/containers/kissa.pub
check "Sigstore-Anhänge (registries.d)" test -f /etc/containers/registries.d/kissa.yaml
check "Firewall-Standardzone kissa"    grep -qx 'DefaultZone=kissa' /etc/firewalld/firewalld.conf
check "Firewall-Zone kissa vorhanden"  test -f /etc/firewalld/zones/kissa.xml
check "sysctl-Härtung"                 test -f /usr/lib/sysctl.d/60-kissa-hardening.conf
check "SSH-Server aus"                 bash -c '[[ $(systemctl is-enabled sshd.service 2>/dev/null) != enabled ]]'

section "Apps"
check "kissa-flatpaks.service aktiviert" bash -c '[[ $(systemctl is-enabled kissa-flatpaks.service) == enabled ]]'
check "Flatpak-Liste vorhanden"        test -s /usr/share/kissa/flatpaks.list
check "Firefox-Vorgaben gültiges JSON" jq -e . /usr/share/kissa/firefox-policies.json

echo
if ((fails)); then printf '\033[31m%d Prüfung(en) fehlgeschlagen.\033[0m\n' "$fails"; exit 1; fi
echo "Alle Prüfungen bestanden. 🐾"
