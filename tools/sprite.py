"""Hoji als handgezeichnetes Pixel-Art-Sprite -> Truecolor-Halbblock-ANSI fürs Terminal.

usage: python sprite.py <out_dir> [preview.html]
Schreibt hoji-matcha.ansi / hoji-hojicha.ansi (1x, 24x10 Zellen) und *-2x.ansi (48x20 Zellen).
Jede Textzelle zeigt zwei Pixel übereinander ('▀' Vordergrund oben, Hintergrund unten).
"""
import sys
from pathlib import Path

SPRITE = [
    "..KKK..........KKK......",
    ".KCCCK........KCCCK.....",
    ".KCLLKKKKKKKKKKLLCK.....",
    "KCLRRRRRRRRRRRRRRLCK....",
    "KRRCCCRRRRRRRRCCCRRK.KK.",
    "KRRRRRRRRRRRRRRRRRRKKRRK",
    "KRRRWERRRRRRRRWERRRKRRRK",
    "KRRREERRRRRRRREERRRKDDDK",
    "KCPPCRRCCCCCCRRCPPCKRRRK",
    "KCCCCCCCCEECCCCCCCCKDDDK",
    "KCCCCCCCCCCCCCCCCCCKRRRK",
    ".KCCCCCCECCECCCCCCKDDDDK",
    "..KKCCCCCEECCCCCKKRRRRRK",
    "....KKKKKKKKKKKKKDDDDDK.",
    "...KRLGGGGGGGGLRKRRRRK..",
    "...KRLMMMMMMMMLRKDDDK...",
    "...KRRKMMMMMMKRRKRRK....",
    "...KRRLKKKKKKLRRKKK.....",
    "...KLLLK....KLLLK.......",
    "....KKK......KKK........",
]

BASE = {"K": "#3B2420", "R": "#D06A35", "D": "#A64B26", "C": "#FBF0E2", "L": "#4A2A22",
        "E": "#2B1B16", "W": "#FFFFFF", "P": "#F4A9B4", "M": "#F3E6D3"}
THEMES = {"matcha": {**BASE, "G": "#9DBB6B"},     # Matcha-Schale
          "hojicha": {**BASE, "G": "#F0B6C1"}}    # Sakura-Latte, passend zum rosa Akzent


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def render(sprite, colors, scale=1):
    grid = ["".join(ch * scale for ch in row) for row in sprite for _ in range(scale)]
    if len(grid) % 2:
        grid.append("." * len(grid[0]))
    ansi, html = [], []
    for y in range(0, len(grid), 2):
        a, h = "", ""
        for top_c, bot_c in zip(grid[y], grid[y + 1]):
            top = rgb(colors[top_c]) if top_c != "." else None
            bot = rgb(colors[bot_c]) if bot_c != "." else None
            if not top and not bot:
                a += "\x1b[0m "; h += " "
            elif not bot:
                a += "\x1b[0m\x1b[38;2;%d;%d;%dm▀" % top; h += f'<span style="color:rgb{top}">▀</span>'
            elif not top:
                a += "\x1b[0m\x1b[38;2;%d;%d;%dm▄" % bot; h += f'<span style="color:rgb{bot}">▄</span>'
            else:
                a += "\x1b[38;2;%d;%d;%dm\x1b[48;2;%d;%d;%dm▀" % (top + bot)
                h += f'<span style="color:rgb{top};background:rgb{bot}">▀</span>'
        ansi.append(a + "\x1b[0m")
        html.append(h)
    return "\n".join(ansi) + "\n", "\n".join(html)


if __name__ == "__main__":
    assert all(len(r) == len(SPRITE[0]) for r in SPRITE), [len(r) for r in SPRITE]
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    previews = []
    for name, colors in THEMES.items():
        for scale, suffix in ((1, ""), (2, "-2x")):
            a, h = render(SPRITE, colors, scale)
            (out / f"hoji-{name}{suffix}.ansi").write_text(a, encoding="utf-8", newline="\n")
            for bg in ("#FFFAF3", "#221A16"):
                previews.append(f'<pre style="display:inline-block;vertical-align:top;margin:8px;padding:12px;'
                                f'background:{bg};font:16px/1 Consolas,monospace">{h}</pre>')
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text('<body style="margin:0;background:#888">' + "".join(previews), encoding="utf-8")
    print("ok")
