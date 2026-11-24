"""Erzeugt das Mauszeiger-Theme "kissa-cursors" (Xcursor-Format) – ohne externe Tools.

usage: python tools/gen_cursors.py system_files/usr/share/icons/kissa-cursors [vorschau.png]

Zeiger werden mit Pillow in 4-facher Auflösung gezeichnet und herunterskaliert.
Die vielen Alias-Namen (left_ptr, hand2, …) legt build.sh als Symlinks an
(build_files/cursor-aliases.txt), weil Symlinks unter Windows/Git unzuverlässig sind.
"""
import math
import struct
import sys
from pathlib import Path
from PIL import Image, ImageDraw

SIZES = [24, 32, 48, 64]
SS = 4  # Supersampling

INK = (59, 36, 32, 255)        # Konturbraun
CREAM = (255, 250, 243, 255)   # Tofu
PAD = (74, 42, 34, 255)        # Pfotenballen dunkel
BEAN = (244, 169, 180, 255)    # Sakura-Bohnen
RUST = (208, 106, 53, 255)     # Hoji
MATCHA = (122, 154, 79, 255)
FOAM = (157, 187, 107, 255)
UME = (192, 86, 110, 255)
TRACK = (59, 36, 32, 70)


def canvas(size):
    img = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), size * SS


def finish(img, size):
    return img.resize((size, size), Image.LANCZOS)


def P(pts, s):
    return [(x * s, y * s) for x, y in pts]


def outlined_polygon(d, pts, s, fill, w):
    d.polygon(P(pts, s), fill=fill, outline=INK, width=max(1, int(w)))


# ---------- einzelne Zeiger (Koordinaten 0..1 relativ zur Größe) ----------
ARROW = [(0.10, 0.06), (0.10, 0.80), (0.29, 0.63), (0.43, 0.92), (0.56, 0.86), (0.42, 0.58), (0.68, 0.58)]


def arrow(size):
    img, d, s = canvas(size)
    outlined_polygon(d, ARROW, s, CREAM, s * 0.065)
    # kleiner Sakura-Punkt als kawaii-Detail
    d.ellipse(P([(0.17, 0.42), (0.25, 0.50)], s), fill=BEAN)
    return finish(img, size), (round(0.11 * size), round(0.07 * size))


def paw(size, closed=False):
    img, d, s = canvas(size)
    w = s * 0.055
    cy = 0.62 if not closed else 0.66
    # Hauptballen
    d.ellipse(P([(0.26, cy - 0.16), (0.74, cy + 0.22)], s), fill=CREAM, outline=INK, width=int(w))
    d.ellipse(P([(0.36, cy - 0.04), (0.64, cy + 0.14)], s), fill=BEAN)
    # Zehen
    toes = [(0.24, 0.34), (0.40, 0.20), (0.60, 0.20), (0.76, 0.34)] if not closed else \
           [(0.30, 0.42), (0.43, 0.34), (0.57, 0.34), (0.70, 0.42)]
    r = 0.105 if not closed else 0.09
    for tx, ty in toes:
        d.ellipse(P([(tx - r, ty - r), (tx + r, ty + r)], s), fill=CREAM, outline=INK, width=int(w))
        d.ellipse(P([(tx - r * 0.45, ty - r * 0.3), (tx + r * 0.45, ty + r * 0.5)], s), fill=BEAN)
    hot = (round(0.50 * size), round(0.12 * size)) if not closed else (round(0.5 * size), round(0.3 * size))
    return finish(img, size), hot


def ibeam(size):
    img, d, s = canvas(size)
    for col, wid in ((CREAM, 0.17), (INK, 0.08)):
        d.line(P([(0.5, 0.18), (0.5, 0.82)], s), fill=col, width=int(s * wid))
        d.line(P([(0.36, 0.16), (0.64, 0.16)], s), fill=col, width=int(s * wid))
        d.line(P([(0.36, 0.84), (0.64, 0.84)], s), fill=col, width=int(s * wid))
    return finish(img, size), (size // 2, size // 2)


def bowl(d, s, cx, cy, scale):
    """Kleine Matcha-Schale."""
    def q(x, y):
        return (cx + x * scale) * s, (cy + y * scale) * s
    w = int(s * 0.05 * scale * 2)
    pts = [q(-0.30, -0.05), q(0.30, -0.05), q(0.26, 0.12), q(0.12, 0.25), q(-0.12, 0.25), q(-0.26, 0.12)]
    d.polygon(pts, fill=CREAM, outline=INK, width=max(1, w))
    x0, y0 = q(-0.30, -0.12); x1, y1 = q(0.30, 0.02)
    d.ellipse([x0, y0, x1, y1], fill=FOAM, outline=INK, width=max(1, w))


def spinner_frame(size, phase, with_arrow=False):
    img, d, s = canvas(size)
    if with_arrow:
        outlined_polygon(d, [(x * 0.72, y * 0.72) for x, y in ARROW], s, CREAM, s * 0.05)
        cx, cy, R, sc = 0.70, 0.70, 0.22, 0.55
    else:
        cx, cy, R, sc = 0.5, 0.5, 0.38, 1.0
    box = P([(cx - R, cy - R), (cx + R, cy + R)], s)
    lw = int(s * (0.07 if not with_arrow else 0.05))
    d.ellipse(box, outline=TRACK, width=lw)
    start = phase * 360
    d.arc(box, start, start + 100, fill=RUST, width=lw)
    d.arc(box, start + 180, start + 240, fill=MATCHA, width=lw)
    bowl(d, s, cx, cy + 0.02, sc * 0.75)
    hot = (round(0.07 * size), round(0.05 * size)) if with_arrow else (size // 2, size // 2)
    return finish(img, size), hot


def not_allowed(size):
    img, d, s = canvas(size)
    box = P([(0.18, 0.18), (0.82, 0.82)], s)
    d.ellipse(box, outline=CREAM, width=int(s * 0.16))
    d.ellipse(box, outline=UME, width=int(s * 0.09))
    d.line(P([(0.30, 0.70), (0.70, 0.30)], s), fill=UME, width=int(s * 0.09))
    return finish(img, size), (size // 2, size // 2)


def crosshair(size):
    img, d, s = canvas(size)
    for col, wid in ((CREAM, 0.14), (INK, 0.06)):
        d.line(P([(0.5, 0.1), (0.5, 0.4)], s), fill=col, width=int(s * wid))
        d.line(P([(0.5, 0.6), (0.5, 0.9)], s), fill=col, width=int(s * wid))
        d.line(P([(0.1, 0.5), (0.4, 0.5)], s), fill=col, width=int(s * wid))
        d.line(P([(0.6, 0.5), (0.9, 0.5)], s), fill=col, width=int(s * wid))
    d.ellipse(P([(0.46, 0.46), (0.54, 0.54)], s), fill=BEAN)
    return finish(img, size), (size // 2, size // 2)


def double_arrow(size, angle, four=False):
    """Doppelpfeil (Größe ändern) – angle 0 = waagerecht."""
    img, d, s = canvas(size)
    shaft = [(-0.22, -0.06), (0.22, -0.06), (0.22, -0.17), (0.42, 0.0), (0.22, 0.17), (0.22, 0.06),
             (-0.22, 0.06), (-0.22, 0.17), (-0.42, 0.0), (-0.22, -0.17)]
    angles = [angle] + ([angle + 90] if four else [])
    for a in angles:
        r = math.radians(a)
        pts = [(0.5 + x * math.cos(r) - y * math.sin(r), 0.5 + x * math.sin(r) + y * math.cos(r)) for x, y in shaft]
        outlined_polygon(d, pts, s, CREAM, s * 0.05)
    return finish(img, size), (size // 2, size // 2)


# ---------- Xcursor schreiben ----------
def write_xcursor(path, frames_by_size, delay=0):
    """frames_by_size: {size: [(Image, (xhot, yhot)), ...]}"""
    chunks = []
    for size, frames in frames_by_size.items():
        for img, (xh, yh) in frames:
            px = img.load()
            data = bytearray()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b, a = px[x, y]
                    # premultiplied ARGB, little-endian
                    r, g, b = (r * a // 255, g * a // 255, b * a // 255)
                    data += struct.pack("<I", (a << 24) | (r << 16) | (g << 8) | b)
            header = struct.pack("<9I", 36, 0xFFFD0002, size, 1, img.width, img.height, xh, yh, delay)
            chunks.append((size, header + bytes(data)))
    ntoc = len(chunks)
    out = bytearray(struct.pack("<4sIII", b"Xcur", 16, 0x10000, ntoc))
    pos = 16 + ntoc * 12
    toc = bytearray()
    for size, blob in chunks:
        toc += struct.pack("<III", 0xFFFD0002, size, pos)
        pos += len(blob)
    out += toc
    for _, blob in chunks:
        out += blob
    path.write_bytes(bytes(out))


CURSORS = {
    "default": lambda sz: [arrow(sz)],
    "pointer": lambda sz: [paw(sz)],
    "grab": lambda sz: [paw(sz)],
    "grabbing": lambda sz: [paw(sz, closed=True)],
    "text": lambda sz: [ibeam(sz)],
    "not-allowed": lambda sz: [not_allowed(sz)],
    "crosshair": lambda sz: [crosshair(sz)],
    "ew-resize": lambda sz: [double_arrow(sz, 0)],
    "ns-resize": lambda sz: [double_arrow(sz, 90)],
    "nwse-resize": lambda sz: [double_arrow(sz, 45)],
    "nesw-resize": lambda sz: [double_arrow(sz, -45)],
    "move": lambda sz: [double_arrow(sz, 0, four=True)],
    "wait": lambda sz: [spinner_frame(sz, i / 12) for i in range(12)],
    "progress": lambda sz: [spinner_frame(sz, i / 12, with_arrow=True) for i in range(12)],
}

if __name__ == "__main__":
    out = Path(sys.argv[1])
    (out / "cursors").mkdir(parents=True, exist_ok=True)
    (out / "index.theme").write_text(
        "[Icon Theme]\nName=kissa\nComment=Hoji-Mauszeiger für kissa\nInherits=breeze_cursors\n",
        encoding="utf-8", newline="\n")
    sheet = Image.new("RGBA", (len(CURSORS) * 72, 2 * 72), (250, 244, 237, 255))
    for i, (name, fn) in enumerate(CURSORS.items()):
        frames = {sz: fn(sz) for sz in SIZES}
        delay = 70 if len(frames[SIZES[0]]) > 1 else 0
        write_xcursor(out / "cursors" / name, frames, delay)
        img48 = frames[48][0][0]
        sheet.alpha_composite(img48, (i * 72 + 12, 12))
        dark = Image.new("RGBA", (72, 72), (42, 33, 28, 255)); dark.alpha_composite(img48, (12, 12))
        sheet.alpha_composite(dark, (i * 72, 72))
    if len(sys.argv) > 2:
        sheet.save(sys.argv[2])
    print("ok:", ", ".join(CURSORS))
