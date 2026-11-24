"""Rendert die Jahreszeiten-SVGs aus gen_wallpaper.py zu Plasma-Wallpaper-Paketen.

usage: python tools/render_wallpapers.py <svg_ordner> system_files/usr/share/wallpapers

Ergebnis je Jahreszeit:  Kissa-<season>/metadata.json
                         Kissa-<season>/contents/images/3840x2160.jpg       (Tag  = matcha)
                         Kissa-<season>/contents/images_dark/3840x2160.jpg  (Nacht = hojicha)
                         Kissa-<season>/contents/screenshot.jpg
Gerendert wird mit einem Chromium-Browser im Headless-Modus (Edge unter Windows,
sonst chromium). Pfad bei Bedarf über die Umgebungsvariable BROWSER setzen.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image

SRC, DST = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
SEASONS = {"fruehling": "Frühling", "sommer": "Sommer", "herbst": "Herbst", "winter": "Winter"}
BROWSER = os.environ.get("BROWSER") or next(
    (b for b in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                 shutil.which("chromium"), shutil.which("chromium-browser"), shutil.which("google-chrome")) if b and Path(b).exists()),
    None)


def render(svg: Path, png: Path):
    with tempfile.TemporaryDirectory() as prof:
        html = Path(prof) / "page.html"
        html.write_text(f'<html><body style="margin:0;overflow:hidden"><img src="{svg.as_uri()}" '
                        'style="width:100vw;height:100vh;display:block"></body></html>', encoding="utf-8")
        subprocess.run([BROWSER, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={prof}/p",
                        "--window-size=1920,1080", "--force-device-scale-factor=2", "--virtual-time-budget=3000",
                        f"--screenshot={png}", html.as_uri()], check=True, capture_output=True)


if not BROWSER:
    sys.exit("Kein Chromium-Browser gefunden (BROWSER setzen)")
for season, label in SEASONS.items():
    pkg = DST / f"Kissa-{season}"
    for theme, sub in (("matcha", "images"), ("hojicha", "images_dark")):
        out = pkg / "contents" / sub / "3840x2160.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            png = Path(tmp) / "shot.png"
            render(SRC / f"kissa {season} {theme}.svg", png)
            img = Image.open(png).convert("RGB")
            assert img.size == (3840, 2160), img.size
            img.save(out, quality=90, optimize=True, progressive=True)
            if theme == "matcha":
                img.resize((400, 225), Image.LANCZOS).save(pkg / "contents" / "screenshot.jpg", quality=85)
        print("wrote", out)
    (pkg / "metadata.json").write_text(json.dumps({"KPlugin": {
        "Authors": [{"Name": "kissa"}], "Id": f"Kissa-{season}", "License": "CC-BY-SA-4.0",
        "Name": f"kissa – Hoji im {label}"}}, ensure_ascii=False, indent=4) + "\n", encoding="utf-8", newline="\n")
