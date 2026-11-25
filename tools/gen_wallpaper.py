"""kissa wallpapers v2 – chibi style with outlines, small centered scene, spotlight glow.

matcha  = light (Tag):   Hoji with a matcha bowl, matcha tea-house sign
hojicha = dark  (Nacht): Hoji with a pastel-pink paper lantern, pink sign
Jahreszeiten: fruehling (Kirschblüten), sommer (Sonne / Glühwürmchen),
              herbst (Ahornblätter, Vollmond), winter (Schnee, Schal)

usage: python gen_wallpaper.py <out_dir>
  -> "kissa wallpaper <theme>.svg"   (Original)
  -> "kissa <season> <theme>.svg"    (8 Jahreszeiten-Varianten)
  -> "hoji <theme>.svg"              (freigestellter Hoji)
Rendern zu JPG: python tools/render_wallpapers.py <out_dir> system_files/usr/share/wallpapers
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


def scarf(t):
    """Winterschal in der Akzentfarbe, sitzt unter dem Kopf."""
    c = t["accent"]
    return (f'<path d="M-44 -126 C-46 -112 -44 -96 -38 -78 L-16 -82 C-22 -98 -24 -110 -22 -124 Z" fill="{c}" {ol()}/>'
            f'<path d="M-40 -84 l-4 10 M-30 -86 l-2 10 M-20 -86 l0 10" stroke="{LINE}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M-62 -152 C-30 -140 30 -140 62 -152 L60 -128 C30 -116 -30 -116 -60 -128 Z" fill="{c}" {ol()}/>'
            f'<path d="M-40 -142 L-40 -122 M-14 -138 L-14 -118 M14 -138 L14 -118 M40 -142 L40 -122" stroke="{t["accent_in"]}" stroke-width="3" opacity=".6"/>')


def hoji(t, extra=""):
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
    return f"""{glow_item}{tail}{body}{extra}<g transform="translate(0 -262) scale(.82)">{head}</g>{item}"""


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


# ---------- Jahreszeiten ----------
SEASONS = ("fruehling", "sommer", "herbst", "winter")
MAPLE = "M0 -14 L4 -6 L11 -9 L8 -1 L14 2 L6 4 L8 12 L0 7 L-8 12 L-6 4 L-14 2 L-8 -1 L-11 -9 L-4 -6 Z"


def maple(x, y, r, s, color, op):
    return (f'<g transform="translate({x:.0f} {y:.0f}) rotate({r:.0f}) scale({s:.2f})" opacity="{op:.2f}">'
            f'<path d="{MAPLE}" fill="{color}"/><path d="M0 7 L0 18" stroke="{color}" stroke-width="2"/></g>')


def flake(x, y, s, color, op):
    arms = "".join(f'<path d="M0 0 L0 -12 M0 -7 L-4 -10 M0 -7 L4 -10" transform="rotate({a})"/>' for a in range(0, 360, 60))
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({s:.2f})" opacity="{op:.2f}" fill="none" '
            f'stroke="{color}" stroke-width="2.2" stroke-linecap="round">{arms}</g>')


def blossom(x, y, s):
    petals = "".join(f'<ellipse cx="0" cy="-9" rx="6" ry="9" transform="rotate({a})"/>' for a in range(0, 360, 72))
    return (f'<g transform="translate({x} {y}) scale({s})"><g fill="#F7CCD4" stroke="{LINE}" stroke-width="2.5">{petals}</g>'
            f'<circle r="4" fill="#E79AAA"/></g>')


def sakura_branch():
    # Zweig ragt vom linken Bildrand in den Himmel und endet frei in der Luft –
    # deutlich über und links vom Schild (Schildkopf: x 648–772, y ab 341).
    twigs = ('<path d="M-30 140 C150 140 330 180 560 236" />'          # Hauptast, dünner werdend gedacht
             '<path d="M210 160 C240 205 280 232 330 248" />'          # Zweig nach unten
             '<path d="M400 196 C420 166 455 150 500 146" />')         # Zweig nach oben
    wood = (f'<g fill="none" stroke-linecap="round"><g stroke="{LINE}" stroke-width="16">{twigs}</g>'
            f'<g stroke="#7A5A4A" stroke-width="10">{twigs}</g></g>')
    spots = [(120, 142, 1.1), (255, 166, .9), (330, 248, 1.0), (285, 222, .8),
             (430, 200, 1.2), (500, 146, 1.1), (560, 236, 1.0), (365, 186, .8)]
    return wood + "".join(blossom(x, y, sc) for x, y, sc in spots)


def sky(season, night):
    """Hintergrund-Elemente hinter der Szene."""
    if season == "fruehling":
        return sakura_branch()
    if season == "sommer" and not night:
        return (f'<circle cx="{CX+330}" cy="300" r="170" fill="url(#sun)"/>'
                f'<circle cx="{CX+330}" cy="300" r="62" fill="#F6D98C" {ol(5)}/>')
    if season == "herbst" and night:
        return (f'<circle cx="{CX+300}" cy="300" r="240" fill="url(#moonglow)"/>'
                f'<circle cx="{CX+300}" cy="300" r="92" fill="#FBF0E2" {ol(5)}/>'
                f'<circle cx="{CX+270}" cy="280" r="14" fill="#EADCC6"/><circle cx="{CX+330}" cy="330" r="10" fill="#EADCC6"/>')
    if night:
        return f'<path d="M{CX+330} 250 a70 70 0 1 0 60 100 a56 56 0 1 1 -60 -100 Z" fill="#FBF0E2" {ol(5)}/>'
    return ""


def particles(t, season, night, rnd):
    if season == "fruehling":
        return "".join(petal(CX + rnd.uniform(-420, 420), rnd.uniform(330, 700), rnd.uniform(0, 360),
                             rnd.uniform(.6, 1.1), t["petal"], rnd.uniform(.5, .9)) for _ in range(11))
    if season == "sommer":
        if night:   # Glühwürmchen
            pts = [(CX + rnd.uniform(-460, 460), rnd.uniform(380, 720)) for _ in range(16)]
            return "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="26" fill="url(#firefly)"/>'
                           f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3.5" fill="#F4FBC8"/>' for x, y in pts)
        return "".join(f'<path transform="translate({CX + rnd.uniform(-430, 430):.0f} {rnd.uniform(360, 700):.0f}) '
                       f'rotate({rnd.uniform(0, 360):.0f})" d="M0 0 C6 -10 18 -10 22 0 C18 10 6 10 0 0 Z" '
                       f'fill="#9DBB6B" opacity="{rnd.uniform(.6, .9):.2f}"/>' for _ in range(10))
    if season == "herbst":
        cols = ("#D06A35", "#C2566E", "#E09A3E", "#B4452F")
        return "".join(maple(CX + rnd.uniform(-440, 440), rnd.uniform(320, 710), rnd.uniform(0, 360),
                             rnd.uniform(.9, 1.5), rnd.choice(cols), rnd.uniform(.7, .95)) for _ in range(14))
    # winter
    c = "#FFFFFF" if night else "#B7C6D1"
    dots = "".join(f'<circle cx="{rnd.uniform(CX-560, CX+560):.0f}" cy="{rnd.uniform(240, 760):.0f}" '
                   f'r="{rnd.uniform(2, 5):.1f}" fill="{c}" opacity="{rnd.uniform(.5, .9):.2f}"/>' for _ in range(60))
    return dots + "".join(flake(CX + rnd.uniform(-450, 450), rnd.uniform(300, 700), rnd.uniform(.8, 1.4), c, .85)
                          for _ in range(9))


def ground(season):
    if season == "winter":
        return f'<ellipse cx="{CX}" cy="{GROUND+6}" rx="380" ry="24" fill="#FFFFFF" stroke="{LINE}" stroke-opacity=".35" stroke-width="3" opacity=".95"/>'
    if season == "herbst":
        cols = ("#D06A35", "#C2566E", "#E09A3E")
        return "".join(maple(CX + dx, GROUND + 4 + (dx % 7), dx * 3, .9, cols[i % 3], .95)
                       for i, dx in enumerate((-300, -262, -210, -90, 140, 196, 250, 296)))
    return ""


def snowcaps():
    return (f'<g transform="translate({CX-250} {GROUND})"><path d="M-56 -362 C-50 -404 50 -404 56 -362 C40 -372 20 -366 4 -374 '
            f'C-14 -366 -36 -374 -56 -362 Z" fill="#FFFFFF" {ol(4)}/></g>'
            f'<g transform="translate({CX-120} {GROUND})"><path d="M-30 -80 C-24 -100 24 -100 30 -80 C18 -86 6 -82 0 -88 '
            f'C-8 -82 -20 -86 -30 -80 Z" fill="#FFFFFF" {ol(3)}/></g>')


def build(t, season=None):
    """season=None: Original-Motiv (Kirschblütenblätter, ohne Zweig)."""
    rnd = random.Random(11)
    night = t["stars"]
    stars = ""
    if t["stars"]:
        stars = "".join(
            f'<circle cx="{rnd.uniform(40, W-40):.0f}" cy="{rnd.uniform(30, 620):.0f}" r="{rnd.uniform(.8, 2.2):.1f}" fill="#EDE3D3" opacity="{rnd.uniform(.15, .55):.2f}"/>'
            for _ in range(70))
    petals = particles(t, season or "fruehling", night, rnd)
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
  <radialGradient id="sun"><stop offset="0" stop-color="#F6D98C" stop-opacity=".55"/><stop offset="1" stop-color="#F6D98C" stop-opacity="0"/></radialGradient>
  <radialGradient id="moonglow"><stop offset="0" stop-color="#FBF0E2" stop-opacity=".35"/><stop offset="1" stop-color="#FBF0E2" stop-opacity="0"/></radialGradient>
  <radialGradient id="firefly"><stop offset="0" stop-color="#E8F5A3" stop-opacity=".8"/><stop offset="1" stop-color="#E8F5A3" stop-opacity="0"/></radialGradient>
  <radialGradient id="lantern"><stop offset="0" stop-color="#FFD6DE" stop-opacity=".55"/><stop offset="1" stop-color="#FFD6DE" stop-opacity="0"/></radialGradient>
  <filter id="paper" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" seed="4"/>
    <feColorMatrix values="0 0 0 0 .35  0 0 0 0 .25  0 0 0 0 .15  0 0 0 {t['noise']} 0"/>
  </filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{stars}
<rect width="{W}" height="{H}" fill="url(#glow)"/>
{sky(season, night) if season else ""}
{clouds}
{petals if not season or season in ("fruehling", "herbst") or (season == "sommer" and not night) else ""}
<ellipse cx="{CX}" cy="{GROUND+4}" rx="330" ry="18" fill="{LINE}" opacity=".18"/>
{ground(season)}
<g transform="translate({CX-250} {GROUND})">{sign(t)}</g>
<g transform="translate({CX-120} {GROUND})">{teapot(t)}</g>
{snowcaps() if season == "winter" else ""}
<g transform="translate({CX+30} {GROUND})">{hoji(t, scarf(t) if season == "winter" else "")}</g>
{petals if season == "winter" or (season == "sommer" and night) else ""}
<text x="{CX}" y="{GROUND+70}" text-anchor="middle" font-family="Zen Maru Gothic, Nunito, Segoe UI, sans-serif" font-size="22" font-weight="700" letter-spacing="6" fill="{t['ink']}" opacity=".8">喫茶 kissa</text>
<rect width="{W}" height="{H}" filter="url(#paper)"/>
</svg>
"""


OUT.mkdir(parents=True, exist_ok=True)
for name, t in THEMES.items():
    (OUT / f"kissa wallpaper {name}.svg").write_text(build(t), encoding="utf-8")
    for season in SEASONS:
        (OUT / f"kissa {season} {name}.svg").write_text(build(t, season), encoding="utf-8")
    print("wrote", name)

# standalone Hoji (transparent) – source for the terminal pixel art
for name, t in THEMES.items():
    (OUT / f"hoji {name}.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="750" height="870" viewBox="-150 -420 375 435">{hoji(t)}</svg>',
        encoding="utf-8")
