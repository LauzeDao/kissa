# 喫茶 kissa

Mein eigenes Linux: Fedora Atomic mit KDE Plasma, gebaut als bootc-Container-Image auf Basis von [Universal Blue Aurora](https://getaurora.dev). Japanischer Paperlook in zwei Teesorten, Maskottchen ist **Hoji**, ein roter Panda.

| Theme | Grundton | Akzent |
|---|---|---|
| **Matcha** (hell) | Washi `#FAF4ED`, Schrift `#575279` (an Rosé Pine Dawn angelehnt) | Matcha `#7A9A4F` |
| **Hojicha** (dunkel) | Hojicha `#2A211C`, Schrift `#EDE3D3` | Sakura `#F0B6C1` |

## Was drin ist

- **Desktop:** KDE-Farbschemata `KissaMatcha` / `KissaHojicha`, Wallpaper-Paket `Kissa` (hell und dunkel)
- **Bootsplash:** Plymouth-Theme `kissa` mit Hoji, Laterne und Ladepunkten, inkl. Passwortabfrage für verschlüsselte Platten
- **Login:** SDDM mit Breeze und Hoji-Hintergrund (statt Plasma Login Manager, der keine eigenen Themes kann)
- **Terminal:** Konsole-Profile und -Farben, Starship-Prompt mit Git- und Kubernetes-Kontext, fastfetch mit Pixel-Hoji
- **CLI:** `kissa` (Menü, Update, Rollback, Theme-Wechsel, K8s-Lab) und `pandasay` / `ocha`
- **Tools:** starship, gum, kind, kubectl, k9s, JetBrainsMono Nerd Font (gepinnt in `build_files/versions.env`, mit Checksummenprüfung)

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
python tools/gen_plymouth.py assets/hoji-hojicha.png system_files/usr/share/plymouth/themes/kissa
```

## Stand

- [x] Design, Wallpaper, CLI, KDE-Farben, Bootsplash, Login
- [x] GitHub-Repo + Actions (Build, cosign-Signatur, Push nach GHCR)
- [ ] Erster erfolgreicher Build
- [ ] Installation auf dem Laptop
- [ ] Renovate für Tool-Versionen
