"""Erzeugt die Bild-Assets für den Plymouth-Bootsplash (Hoji, Schriftzug, Ladepunkte).

usage: python tools/gen_plymouth.py <hoji-hojicha.png> <zielordner> [schriftdatei]
Die Quelle ist der freigestellte Hoji aus tools/gen_wallpaper.py (im Browser gerendert).
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

src, out = Path(sys.argv[1]), Path(sys.argv[2])
font_path = sys.argv[3] if len(sys.argv) > 3 else "C:/Windows/Fonts/YuGothB.ttc"
out.mkdir(parents=True, exist_ok=True)

# Hoji, 300 px hoch
hoji = Image.open(src).convert("RGBA")
hoji = hoji.crop(hoji.getbbox())
h = 300
hoji = hoji.resize((round(hoji.width * h / hoji.height), h), Image.LANCZOS)
hoji.save(out / "hoji.png")

# Schriftzug "喫茶 kissa" in Reispapier-Beige
font = ImageFont.truetype(font_path, 40)
text = "喫茶  kissa"
l, t, r, b = font.getbbox(text)
mark = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
ImageDraw.Draw(mark).text((4 - l, 4 - t), text, font=font, fill=(237, 227, 211, 230))
mark.save(out / "wordmark.png")

# Ladepunkte: an = Pastellrosa, aus = Kakao
for name, color in (("dot-on", (240, 182, 193, 255)), ("dot-off", (90, 70, 60, 255))):
    d = Image.new("RGBA", (56, 56), (0, 0, 0, 0))
    ImageDraw.Draw(d).ellipse((4, 4, 52, 52), fill=color)
    d.resize((14, 14), Image.LANCZOS).save(out / f"{name}.png")
print("ok")
