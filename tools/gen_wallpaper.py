"""kissa wallpapers v2 – chibi style with outlines, small centered scene, spotlight glow.

matcha  = light: Hoji with a matcha bowl, matcha tea-house sign
hojicha = dark:  Hoji with a pastel-pink paper lantern, pink sign
usage: python gen_wallpaper.py <out_dir>
"""
import random
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
W, H = 1920, 1080
CX, GROUND = 960, 735          # scene centre x, ground line y

LINE = "#3B2420"               # outline colour (both themes)
RUST, RUST_DARK, CREAM, LEG, EYE, BLUSH = "#D06A35", "#A64B26", "#FBF0E2", "#4A2A22", "#2B1B16", "#F4A9B4"

THEMES = {
    "matcha": dict(
        bg0="#FFFAF3", bg1="#FAF4ED", bg2="#E6DAD0", glow="#FFFFFF", glow_op=.0,
        cloud="#D3E0B3", cloud_line="#A9C07E", accent="#7A9A4F", accent_in="#FBF7F0",
        petal="#E8B4BC", ink="#9893A5", item="bowl", stars=False, noise=.06,
    ),
    "hojicha": dict(
        bg0="#4A3830", bg1="#2A211C", bg2="#0F0B09", glow="#F0B6C1", glow_op=.22,
        cloud="#5A4239", cloud_line="#F0B6C1", accent="#F0B6C1", accent_in="#2A211C",
        petal="#F0B6C1", ink="#A8988A", item="lantern", stars=True, noise=.09,
    ),
}


def ol(w=5):
    return f'stroke="{LINE}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def cloud(x, y, s, flip, t):
    """Japanese swirl cloud: bumpy body, spiral curls, a long wisp."""
    body = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>' for cx, cy, r in
                   [(0, 0, 26), (32, -14, 32), (70, -8, 28), (98, 4, 20), (-24, 8, 18)])
    curls = (
        f'<path d="M-24 8 m-9 0 a9 9 0 1 1 9 9 a5 5 0 1 1 -3 -7" />'
        f'<path d="M32 -14 m-14 2 a14 14 0 1 1 14 14 a8 8 0 1 1 -5 -11" />'
        f'<path d="M70 -8 m-10 0 a10 10 0 1 1 10 10" />'
        f'<path d="M-30 24 C-90 30 -140 14 -190 22 a10 10 0 1 1 6 -14" />'
    )
    fx = -1 if flip else 1
    return (f'<g transform="translate({x} {y}) scale({s * fx} {s})">'
            f'<g fill="{t["cloud"]}">{body}<rect x="-24" y="4" width="122" height="22" rx="11"/></g>'
            f'<g fill="none" stroke="{t["cloud_line"]}" stroke-width="3.5" stroke-linecap="round" opacity=".9">{curls}</g></g>')


def hoji(t):
    """Chibi red panda standing upright. Origin = between the feet on the ground."""
    ear = (f'<path d="M-150 -22 C-176 -112 -156 -176 -122 -178 C-92 -178 -64 -140 -44 -96 Z" fill="{CREAM}" {ol(6)}/>'
           f'<path d="M-136 -44 C-148 -108 -136 -150 -118 -150 C-100 -148 -84 -124 -72 -98 Z" fill="{LEG}"/>')
    head = f"""
    {ear}<g transform="scale(-1,1)">{ear}</g>
    <path d="M-165 10 C-170 -90 -90 -128 0 -128 C90 -128 170 -90 165 10 C162 85 95 128 0 128 C-95 128 -162 85 -165 10 Z" fill="{RUST}" {ol(6)}/>
    <path d="M-150 34 C-140 96 -76 116 0 116 C76 116 140 96 150 34 C132 16 108 22 92 40 C74 60 46 58 30 38 C16 22 -16 22 -30 38 C-46 58 -74 60 -92 40 C-108 22 -132 16 -150 34 Z" fill="{CREAM}"/>
    <ellipse cx="0" cy="66" rx="56" ry="44" fill="{CREAM}"/>
    <ellipse cx="-60" cy="-46" rx="24" ry="14" fill="{CREAM}"/>
    <ellipse cx="60" cy="-46" rx="24" ry="14" fill="{CREAM}"/>
    {''.join(f'<ellipse cx="{x}" cy="6" rx="19" ry="24" fill="{EYE}"/><circle cx="{x+7}" cy="-4" r="7.5" fill="#fff"/><circle cx="{x-7}" cy="15" r="3.5" fill="#fff"/>' for x in (-58, 58))}
    <ellipse cx="-108" cy="60" rx="24" ry="12" fill="{BLUSH}" opacity=".8"/>
    <ellipse cx="108" cy="60" rx="24" ry="12" fill="{BLUSH}" opacity=".8"/>
    <path d="M-14 48 Q0 42 14 48 Q12 60 0 64 Q-12 60 -14 48 Z" fill="{EYE}"/>
    <path d="M-18 76 Q-9 87 0 76 Q9 87 18 76" fill="none" stroke="{EYE}" stroke-width="4.5" stroke-linecap="round"/>
    """
    tail = (f'<path d="M48 -60 C150 -40 196 -130 150 -232" fill="none" stroke="{LINE}" stroke-width="72" stroke-linecap="round"/>'
            f'<path d="M48 -60 C150 -40 196 -130 150 -232" fill="none" stroke="{RUST}" stroke-width="61" stroke-linecap="round"/>'
            f'<path d="M48 -60 C150 -40 196 -130 150 -232" fill="none" stroke="{RUST_DARK}" stroke-width="61" stroke-dasharray="24 30" stroke-dashoffset="-34"/>')
    body = (f'<ellipse cx="-30" cy="-16" rx="27" ry="20" fill="{LEG}" {ol()}/>'
            f'<ellipse cx="30" cy="-16" rx="27" ry="20" fill="{LEG}" {ol()}/>'
            f'<path d="M-62 -30 C-74 -100 -52 -150 0 -150 C52 -150 74 -100 62 -30 C40 -20 -40 -20 -62 -30 Z" fill="{RUST}" {ol()}/>'
            f'<path d="M-36 -32 C-44 -80 -30 -118 0 -118 C30 -118 44 -80 36 -32 C20 -26 -20 -26 -36 -32 Z" fill="{LEG}"/>')
    if t["item"] == "bowl":
        item = (f'<path d="M-46 -112 L46 -112 Q42 -64 0 -60 Q-42 -64 -46 -112 Z" fill="{CREAM}" {ol()}/>'
                f'<path d="M-34 -84 Q0 -77 34 -84" fill="none" stroke="#CDB898" stroke-width="4" stroke-linecap="round"/>'
                f'<ellipse cx="0" cy="-112" rx="46" ry="9" fill="#9DBB6B" {ol(4)}/>'
                f'<ellipse cx="-50" cy="-90" rx="17" ry="20" fill="{LEG}" {ol()}/>'
                f'<ellipse cx="50" cy="-90" rx="17" ry="20" fill="{LEG}" {ol()}/>')
        glow_item = ""
    else:
        lx, ly = 118, -110
        item = (f'<ellipse cx="-38" cy="-84" rx="17" ry="19" fill="{LEG}" {ol()}/>'
                f'<path d="M44 -112 L{lx} -168" fill="none" stroke="{LINE}" stroke-width="7" stroke-linecap="round"/>'
                f'<path d="M{lx} -168 L{lx} -150" fill="none" stroke="{LINE}" stroke-width="4"/>'
                f'<rect x="{lx-16}" y="-152" width="32" height="10" rx="3" fill="{LINE}"/>'
                f'<ellipse cx="{lx}" cy="{ly}" rx="34" ry="40" fill="#F7CCD4" {ol()}/>'
                + "".join(f'<path d="M{lx-31+abs(d)*0.25} {ly+d} Q{lx} {ly+d+6} {lx+31-abs(d)*0.25} {ly+d}" fill="none" stroke="#E79AAA" stroke-width="2.5"/>' for d in (-24, -8, 8, 24))
                + f'<text x="{lx}" y="{ly+10}" text-anchor="middle" font-family="Yu Mincho, Noto Serif CJK JP, serif" font-size="30" font-weight="700" fill="#C2566E">茶</text>'
                f'<rect x="{lx-14}" y="{ly+38}" width="28" height="9" rx="3" fill="{LINE}"/>'
                f'<ellipse cx="46" cy="-112" rx="17" ry="19" fill="{LEG}" {ol()}/>')
        glow_item = f'<circle cx="{lx}" cy="{ly}" r="150" fill="url(#lantern)"/>'
    return f"""{glow_item}{tail}{body}<g transform="translate(0 -262) scale(.82)">{head}</g>{item}"""


def sign(t):
    """Round tea-house sign on a post, like a little bus stop."""
    return f"""
  <rect x="-9" y="-300" width="18" height="300" rx="6" fill="#8C7A6B" {ol()}/>
  <path d="M-34 0 L-26 -26 L26 -26 L34 0 Z" fill="#6E5D4F" {ol()}/>
  <circle cx="0" cy="-332" r="62" fill="{t['accent']}" {ol(6)}/>
  <circle cx="0" cy="-332" r="50" fill="none" stroke="{t['accent_in']}" stroke-width="5"/>
  <path d="M-30 -344 L30 -344 Q28 -306 0 -302 Q-28 -306 -30 -344 Z" fill="{t['accent_in']}"/>
  <path d="M28 -336 q16 2 12 14 q-4 9 -16 6" fill="none" stroke="{t['accent_in']}" stroke-width="6" stroke-linecap="round"/>
  <path d="M-10 -356 c-8 -10 6 -16 -2 -26 M8 -356 c-8 -10 6 -16 -2 -26" fill="none" stroke="{t['accent_in']}" stroke-width="5" stroke-linecap="round"/>
"""


def teapot(t):
    return f"""
  <path d="M-48 -26 C-60 -40 -66 -58 -76 -64" fill="none" stroke="{LINE}" stroke-width="14" stroke-linecap="round"/>
  <path d="M-48 -26 C-60 -40 -66 -58 -76 -64" fill="none" stroke="#8FA672" stroke-width="7" stroke-linecap="round"/>
  <path d="M38 -50 q30 4 22 30 q-4 10 -18 10" fill="none" stroke="{LINE}" stroke-width="7" stroke-linecap="round"/>
  <path d="M-44 -8 C-50 -60 -28 -78 0 -78 C28 -78 50 -60 44 -8 C30 0 -30 0 -44 -8 Z" fill="#8FA672" {ol()}/>
  <path d="M-36 -38 Q0 -30 36 -38" fill="none" stroke="#6F8656" stroke-width="4"/>
  <path d="M-18 -78 Q0 -94 18 -78 Z" fill="#6F8656" {ol(4)}/>
  <circle cx="0" cy="-92" r="6" fill="#6F8656" {ol(3)}/>
  <path d="M-80 -78 c-14 -20 10 -30 -4 -50 M-62 -84 c-12 -18 10 -28 -2 -46" fill="none" stroke="{t['cloud_line']}" stroke-width="4" stroke-linecap="round" opacity=".8"/>
"""


def petal(x, y, r, s, color, op):
    return (f'<path transform="translate({x:.0f} {y:.0f}) rotate({r:.0f}) scale({s:.2f})" opacity="{op:.2f}" fill="{color}" '
            'd="M0 0 C6 -12 22 -10 22 2 C22 10 12 15 6 12 L4 8 L1 12 C-2 10 -2 4 0 0 Z"/>')


def build(t):
    rnd = random.Random(11)
    stars = ""
    if t["stars"]:
        stars = "".join(
            f'<circle cx="{rnd.uniform(40, W-40):.0f}" cy="{rnd.uniform(30, 620):.0f}" r="{rnd.uniform(.8, 2.2):.1f}" fill="#EDE3D3" opacity="{rnd.uniform(.15, .55):.2f}"/>'
            for _ in range(70))
    petals = "".join(petal(CX + rnd.uniform(-420, 420), rnd.uniform(330, 700), rnd.uniform(0, 360),
                           rnd.uniform(.6, 1.1), t["petal"], rnd.uniform(.5, .9)) for _ in range(11))
    clouds = (cloud(CX - 150, 400, 1.15, False, t) + cloud(CX + 250, 470, .9, True, t)
              + cloud(CX - 330, 560, .7, False, t))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <radialGradient id="bg" cx="{CX}" cy="560" r="1150" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{t['bg0']}"/><stop offset=".38" stop-color="{t['bg1']}"/><stop offset="1" stop-color="{t['bg2']}"/>
  </radialGradient>
  <radialGradient id="glow" cx="{CX}" cy="560" r="420" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{t['glow']}" stop-opacity="{t['glow_op']}"/><stop offset="1" stop-color="{t['glow']}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="lantern"><stop offset="0" stop-color="#FFD6DE" stop-opacity=".55"/><stop offset="1" stop-color="#FFD6DE" stop-opacity="0"/></radialGradient>
  <filter id="paper" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" seed="4"/>
    <feColorMatrix values="0 0 0 0 .35  0 0 0 0 .25  0 0 0 0 .15  0 0 0 {t['noise']} 0"/>
  </filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{stars}
<rect width="{W}" height="{H}" fill="url(#glow)"/>
{clouds}
{petals}
<ellipse cx="{CX}" cy="{GROUND+4}" rx="330" ry="18" fill="{LINE}" opacity=".18"/>
<g transform="translate({CX-250} {GROUND})">{sign(t)}</g>
<g transform="translate({CX-120} {GROUND})">{teapot(t)}</g>
<g transform="translate({CX+30} {GROUND})">{hoji(t)}</g>
<text x="{CX}" y="{GROUND+70}" text-anchor="middle" font-family="Zen Maru Gothic, Nunito, Segoe UI, sans-serif" font-size="22" font-weight="700" letter-spacing="6" fill="{t['ink']}" opacity=".8">喫茶 kissa</text>
<rect width="{W}" height="{H}" filter="url(#paper)"/>
</svg>
"""


OUT.mkdir(parents=True, exist_ok=True)
for name, t in THEMES.items():
    (OUT / f"kissa wallpaper {name}.svg").write_text(build(t), encoding="utf-8")
    print("wrote", name)

# standalone Hoji (transparent) – source for the terminal pixel art
for name, t in THEMES.items():
    (OUT / f"hoji {name}.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="750" height="870" viewBox="-150 -420 375 435">{hoji(t)}</svg>',
        encoding="utf-8")
