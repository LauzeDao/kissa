"""Erzeugt die KDE Global Themes org.kissa.matcha und org.kissa.hojicha.

usage: python tools/gen_lookandfeel.py system_files/usr/share/plasma/look-and-feel

Ein Global Theme bündelt Farbschema, Mauszeiger, Fensterrahmen, Panel-Layout und den
Ladebildschirm nach dem Login (KSplash). Angewendet wird es mit:
  plasma-apply-lookandfeel -a org.kissa.matcha [--resetLayout]
"""
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

VARIANTS = {
    "matcha": dict(name="kissa Matcha", scheme="KissaMatcha", bg="#FAF4ED", fg="#575279",
                   accent="#7A9A4F", hoji=ROOT / "assets/hoji-matcha.png",
                   desc="Heller Paperlook mit Matcha-Akzent"),
    "hojicha": dict(name="kissa Hojicha", scheme="KissaHojicha", bg="#2A211C", fg="#EDE3D3",
                    accent="#F0B6C1", hoji=ROOT / "assets/hoji-hojicha.png",
                    desc="Dunkles Hojicha-Braun mit Sakura-Akzent"),
}

# Panel-Layout: Seitenleiste links (Dock) + "Notch" oben mittig.
# Unsichere Eigenschaften stehen in try/catch, damit ein Fehler nicht das ganze Layout abbricht.
LAYOUT_JS = r"""// kissa – Panel-Layout: Seitenleiste links + Notch oben
var desktops = desktopsForActivity(currentActivity());
for (var i = 0; i < desktops.length; i++) {
    desktops[i].wallpaperPlugin = "org.kde.image";
}

function set(panel, key, value) {
    try { panel[key] = value; } catch (e) { print("kissa: " + key + " nicht gesetzt: " + e); }
}

// ---------- Seitenleiste (Dock) links ----------
var dock = new Panel;
dock.location = "left";
dock.height = 60;                 // Dicke der Leiste
set(dock, "floating", true);
set(dock, "lengthMode", "fit");   // so lang wie der Inhalt
dock.alignment = "center";
dock.hiding = "none";

var launcher = dock.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "/usr/share/kissa/hoji-launcher.png");

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "preferred://browser",
    "applications:org.kde.konsole.desktop",
    "applications:org.kde.discover.desktop",
    "applications:systemsettings.desktop"
].join(","));

// ---------- Notch oben mittig ----------
var notch = new Panel;
notch.location = "top";
notch.height = 34;
set(notch, "floating", true);
set(notch, "lengthMode", "fit");
notch.alignment = "center";
notch.hiding = "none";

notch.addWidget("org.kde.plasma.systemtray");
var clock = notch.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateFormat", "shortDate");
"""

DEFAULTS = """[kdeglobals][General]
ColorScheme={scheme}

[kdeglobals][KDE]
widgetStyle=Breeze

[kdeglobals][Icons]
Theme=kissa-{variant}

[kdeglobals][Sounds]
Theme=kissa

[plasmarc][Theme]
name=default

[kcminputrc][Mouse]
cursorTheme=kissa-cursors
cursorSize=32

[kwinrc][org.kde.kdecoration2]
library=org.kde.breeze
theme=Breeze

[kwinrc][WindowSwitcher]
LayoutName=org.kde.breeze.desktop

[ksplashrc][KSplash]
Engine=KSplashQML
Theme=org.kissa.{variant}

[Wallpaper]
Image=Kissa-fruehling
"""

SPLASH_QML = """import QtQuick

// kissa – Ladebildschirm nach dem Login: Hoji wippt, darunter der Schriftzug.
Rectangle {{
    id: root
    color: "{bg}"
    property int stage

    Image {{
        id: hoji
        source: "images/hoji.png"
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -30
        height: 240
        fillMode: Image.PreserveAspectFit
        smooth: true
        transform: Translate {{ id: bob; y: 0 }}
    }}

    SequentialAnimation {{
        running: true
        loops: Animation.Infinite
        NumberAnimation {{ target: bob; property: "y"; to: -10; duration: 650; easing.type: Easing.InOutQuad }}
        NumberAnimation {{ target: bob; property: "y"; to: 0; duration: 650; easing.type: Easing.InOutQuad }}
    }}

    Text {{
        text: "おかえり · kissa"
        color: "{fg}"
        opacity: 0.85
        font.pixelSize: 22
        font.letterSpacing: 3
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: hoji.bottom
        anchors.topMargin: 28
    }}

    Row {{
        spacing: 10
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: hoji.bottom
        anchors.topMargin: 72
        Repeater {{
            model: 5
            Rectangle {{
                width: 10; height: 10; radius: 5
                color: "{accent}"
                opacity: index < root.stage ? 1.0 : 0.25
                Behavior on opacity {{ NumberAnimation {{ duration: 200 }} }}
            }}
        }}
    }}
}}
"""


def hoji_png(src, height):
    img = Image.open(src).convert("RGBA")
    img = img.crop(img.getbbox())
    return img.resize((round(img.width * height / img.height), height), Image.LANCZOS)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for variant, v in VARIANTS.items():
        pkg = out / f"org.kissa.{variant}"
        (pkg / "contents/layouts").mkdir(parents=True, exist_ok=True)
        (pkg / "contents/splash/images").mkdir(parents=True, exist_ok=True)
        meta = {
            "KPackageStructure": "Plasma/LookAndFeel",
            "KPlugin": {
                "Authors": [{"Name": "kissa"}],
                "Category": "",
                "Description": v["desc"],
                "Id": f"org.kissa.{variant}",
                "License": "GPL-2.0-or-later",
                "Name": v["name"],
                "Version": "1.0",
            },
            "X-Plasma-APIVersion": "2",
        }
        (pkg / "metadata.json").write_text(json.dumps(meta, indent=4, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        (pkg / "contents/defaults").write_text(DEFAULTS.format(scheme=v["scheme"], variant=variant), encoding="utf-8", newline="\n")
        (pkg / "contents/layouts/org.kde.plasma.desktop-layout.js").write_text(LAYOUT_JS, encoding="utf-8", newline="\n")
        (pkg / "contents/splash/Splash.qml").write_text(SPLASH_QML.format(**v), encoding="utf-8", newline="\n")
        hoji_png(v["hoji"], 480).save(pkg / "contents/splash/images/hoji.png")
        # Vorschaubild für die Systemeinstellungen
        prev = Image.new("RGBA", (480, 270), v["bg"])
        h = hoji_png(v["hoji"], 200)
        prev.alpha_composite(h, ((480 - h.width) // 2, 35))
        (pkg / "contents/previews").mkdir(exist_ok=True)
        prev.save(pkg / "contents/previews/preview.png")
        print("wrote", pkg.name)

    # Startmenü-Symbol: Hojis Kopf, quadratisch
    head = Image.open(ROOT / "assets/hoji-matcha.png").convert("RGBA")
    head = head.crop(head.getbbox())
    w = head.width
    head = head.crop((0, 0, round(w * 0.81), round(w * 0.76)))  # nur der Kopf mit Ohren
    side = max(head.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(head, ((side - head.width) // 2, (side - head.height) // 2))
    icon_dir = ROOT / "system_files/usr/share/kissa"
    sq.resize((256, 256), Image.LANCZOS).save(icon_dir / "hoji-launcher.png")
    print("wrote hoji-launcher.png")
