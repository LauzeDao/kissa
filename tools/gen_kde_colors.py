"""Erzeugt die KDE-Plasma-Farbschemata KissaMatcha.colors und KissaHojicha.colors.

usage: python tools/gen_kde_colors.py system_files/usr/share/color-schemes
"""
import sys
from pathlib import Path

THEMES = {
    "KissaMatcha": dict(
        name="kissa Matcha",
        window="#FAF4ED", view="#FFFAF3", alt="#F2E9E1", button="#F2E9E1", header="#F2E9E1",
        fg="#575279", inactive="#9893A5", accent="#7A9A4F", on_accent="#FFFAF3", hover="#9DBB6B",
        link="#286983", visited="#907AA9", negative="#B4637A", neutral="#EA9D34", positive="#5C7A3A",
        # Complementary = dunkle Flächen (z. B. Sperrbildschirm-Overlays) -> Hojicha
        comp_bg="#2A211C", comp_fg="#EDE3D3", comp_alt="#342A23",
    ),
    "KissaHojicha": dict(
        name="kissa Hojicha",
        window="#2A211C", view="#221A16", alt="#342A23", button="#342A23", header="#342A23",
        fg="#EDE3D3", inactive="#A8988A", accent="#F0B6C1", on_accent="#2A211C", hover="#F7CCD4",
        link="#8FB0CF", visited="#D7B4C9", negative="#E07A6A", neutral="#E3B860", positive="#A3C27A",
        comp_bg="#221A16", comp_fg="#EDE3D3", comp_alt="#2A211C",
    ),
}


def rgb(h):
    return ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))


def group(bg, alt, fg, t, sel=False):
    fg_n = t["on_accent"] if sel else fg
    fg_i = t["on_accent"] if sel else t["inactive"]
    return {
        "BackgroundAlternate": rgb(alt), "BackgroundNormal": rgb(bg),
        "DecorationFocus": rgb(t["accent"]), "DecorationHover": rgb(t["hover"]),
        "ForegroundActive": rgb(t["accent"] if not sel else t["on_accent"]),
        "ForegroundInactive": rgb(fg_i), "ForegroundLink": rgb(t["link"]),
        "ForegroundNegative": rgb(t["negative"]), "ForegroundNeutral": rgb(t["neutral"]),
        "ForegroundNormal": rgb(fg_n), "ForegroundPositive": rgb(t["positive"]),
        "ForegroundVisited": rgb(t["visited"]),
    }


def build(key, t):
    sections = {
        "ColorEffects:Disabled": {"Color": "56,56,56", "ColorAmount": "0", "ColorEffect": "0",
                                  "ContrastAmount": "0.65", "ContrastEffect": "1",
                                  "IntensityAmount": "0.1", "IntensityEffect": "2"},
        "ColorEffects:Inactive": {"ChangeSelectionColor": "true", "Color": "112,111,110",
                                  "ColorAmount": "0.025", "ColorEffect": "2", "ContrastAmount": "0.1",
                                  "ContrastEffect": "2", "Enable": "false",
                                  "IntensityAmount": "0", "IntensityEffect": "0"},
        "Colors:Button": group(t["button"], t["alt"], t["fg"], t),
        "Colors:Complementary": group(t["comp_bg"], t["comp_alt"], t["comp_fg"],
                                      {**t, "inactive": "#A8988A"}),
        "Colors:Header": group(t["header"], t["alt"], t["fg"], t),
        "Colors:Header][Inactive": group(t["window"], t["alt"], t["fg"], t),
        "Colors:Selection": group(t["accent"], t["hover"], t["on_accent"], t, sel=True),
        "Colors:Tooltip": group(t["view"], t["alt"], t["fg"], t),
        "Colors:View": group(t["view"], t["alt"], t["fg"], t),
        "Colors:Window": group(t["window"], t["alt"], t["fg"], t),
        "General": {"ColorScheme": key, "Name": t["name"], "shadeSortColumn": "true"},
        "KDE": {"contrast": "4"},
        "WM": {"activeBackground": rgb(t["header"]), "activeBlend": rgb(t["fg"]),
               "activeForeground": rgb(t["fg"]), "inactiveBackground": rgb(t["window"]),
               "inactiveBlend": rgb(t["inactive"]), "inactiveForeground": rgb(t["inactive"])},
    }
    return "\n".join(f"[{name}]\n" + "".join(f"{k}={v}\n" for k, v in kv.items())
                     for name, kv in sections.items())


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for key, t in THEMES.items():
        (out / f"{key}.colors").write_text(build(key, t), encoding="utf-8", newline="\n")
        print("wrote", key)
