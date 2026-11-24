# 喫茶 kissa

Mein eigenes Linux: Fedora Atomic mit KDE Plasma, gebaut als bootc-Container-Image auf Basis von [Universal Blue Aurora](https://getaurora.dev). Japanischer Paperlook in zwei Teesorten, Maskottchen ist **Hoji**, ein roter Panda.

| Theme | Grundton | Akzent |
|---|---|---|
| **Matcha** (hell) | Washi `#FAF4ED`, Schrift `#575279` (an Rosé Pine Dawn angelehnt) | Matcha `#7A9A4F` |
| **Hojicha** (dunkel) | Hojicha `#2A211C`, Schrift `#EDE3D3` | Sakura `#F0B6C1` |

## Was drin ist

- **Desktop:** KDE Global Themes `org.kissa.matcha` / `org.kissa.hojicha` mit Seitenleiste links + Notch oben, Farbschemata, Wallpaper-Paket `Kissa` (hell und dunkel), Hoji-Ladebildschirm nach dem Login
- **Mauszeiger:** eigenes Theme `kissa-cursors` – Pfeil, Pfötchen als Klick-Hand, Matcha-Schale beim Warten
- **Transparenz:** Fenster leicht durchscheinend (aktiv 96 %, inaktiv 88 %), Menüs 90 %, Blur – an/aus mit `kissa glas`
- **Bootsplash:** Plymouth-Theme `kissa` mit Hoji, Laterne und Ladepunkten, inkl. Passwortabfrage für verschlüsselte Platten
- **Login:** SDDM mit Breeze und Hoji-Hintergrund (statt Plasma Login Manager, der keine eigenen Themes kann)
- **Terminal:** Konsole-Profile und -Farben, Starship-Prompt mit Git- und Kubernetes-Kontext, fastfetch mit Pixel-Hoji
- **CLI:** `kissa` (Menü, Update, Rollback, Theme-Wechsel, K8s-Lab) und `pandasay` / `ocha`
- **Apps:** VS Code (RPM), Podman mit Docker-Kompatibilität (`docker`, `docker compose`) + Podman Desktop, LibreOffice, Obsidian, Firefox – Flatpaks installiert `kissa-flatpaks.service` beim Start aus `system_files/usr/share/kissa/flatpaks.list`
- **Firefox:** uBlock Origin, DuckDuckGo als Suche, Telemetrie/Pocket/Werbung aus, strenger Tracking-Schutz (`firefox-policies.json`)
- **Tools:** starship, gum, kind, kubectl, k9s, JetBrainsMono Nerd Font (gepinnt in `build_files/versions.env`, mit Checksummenprüfung)

## Sicherheit

| Maßnahme | Umsetzung |
|---|---|
| Signierte Updates | Pipeline signiert mit cosign (Schlüssel als Secret `SIGNING_SECRET`, öffentlicher Teil `cosign.pub`). Das Image enthält eine Regel in `/etc/containers/policy.json`, die nur korrekt signierte Images von `ghcr.io/lauzedao/kissa` annimmt. |
| Firewall | Eigene Zone `kissa`: eingehend nur DHCPv6, mDNS und KDE Connect (1714–1764) |
| Kernel | `sysctl`-Härtung in `/usr/lib/sysctl.d/60-kissa-hardening.conf` |
| Dienste | SSH-Server deaktiviert |
| Lieferkette | Actions per Commit-Hash gepinnt (Dependabot hält sie aktuell), Tool-Downloads mit Checksummenprüfung |
| Passwörter | Bitwarden (EU-Server), Firefox-Passwortspeicher aus |

Einmalig nach dem ersten Image mit Signaturregel auf geprüfte Updates umstellen:

```bash
sudo bootc switch --enforce-container-sigpolicy ghcr.io/lauzedao/kissa:latest
```

## Aufbau

```
Containerfile              Basis-Image + Build-Ablauf
build_files/build.sh       Pakete, Tools, SDDM, Bootsplash, initramfs
build_files/versions.env   gepinnte Tool-Versionen
system_files/              wird 1:1 nach / ins Image kopiert
tools/                     Generatoren für Wallpaper, Pixel-Hoji, KDE-Farben, Bootsplash-Assets
assets/                    gerenderter Hoji, Design-Entwurf
```

## Bauen und testen

```bash
podman build -t localhost/kissa:dev .
```

Wechsel eines bestehenden Fedora-Atomic-/Aurora-Systems auf kissa:

```bash
sudo bootc switch ghcr.io/lauzedao/kissa:latest
systemctl reboot
```

Nach dem ersten Login richtet `kissa setup` Terminal, Prompt und Theme automatisch ein.

## Assets neu erzeugen

```bash
python tools/gen_wallpaper.py <ordner>        # SVGs: Wallpaper + freigestellter Hoji (im Browser zu PNG rendern)
python tools/sprite.py <ordner>               # Pixel-Hoji fürs Terminal (.ansi)
python tools/gen_kde_colors.py system_files/usr/share/color-schemes
python tools/gen_cursors.py system_files/usr/share/icons/kissa-cursors
python tools/gen_lookandfeel.py system_files/usr/share/plasma/look-and-feel
python tools/gen_plymouth.py assets/hoji-hojicha.png system_files/usr/share/plymouth/themes/kissa
```

## Stand

- [x] Design, Wallpaper, CLI, KDE-Farben, Bootsplash, Login
- [x] GitHub-Repo + Actions (Build, cosign-Signatur, Push nach GHCR)
- [ ] Erster erfolgreicher Build
- [ ] Installation auf dem Laptop
- [ ] Renovate für Tool-Versionen
