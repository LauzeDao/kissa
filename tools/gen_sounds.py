"""Erzeugt das kissa-Soundtheme: leise, weiche Kalimba-/Holz-Töne mit einem Hauch Papier.

usage: python tools/gen_sounds.py system_files/usr/share/sounds/kissa

Freedesktop-Soundtheme (index.theme + stereo/<ereignis>.wav). Fehlende Ereignisse
fallen über "Inherits" auf ocean/freedesktop zurück. Aktiv über kdeglobals [Sounds] Theme=kissa.
Tonleiter: japanische Yo-Pentatonik (D E G A B) – klingt nie schief.
"""
import math
import random
import struct
import sys
import wave
from pathlib import Path

OUT = Path(sys.argv[1])
RATE = 44100
NOTE = {n: 440 * 2 ** ((i - 9) / 12 + o)
        for o, base in ((-1, 3), (0, 4), (1, 5))
        for n, i in (("D", 2), ("E", 4), ("G", 7), ("A", 9), ("B", 11))
        for n in [f"{n}{base}"]}


def pluck(freq, dur=0.9, amp=0.5, decay=6.0, bright=0.25):
    """Kalimba-artiger Ton: Grundton + leiser hoher Oberton, weicher Anschlag."""
    n = int(dur * RATE)
    out = []
    for i in range(n):
        t = i / RATE
        env = min(1.0, t / 0.004) * math.exp(-decay * t)
        tine = math.sin(2 * math.pi * freq * t) + 0.18 * math.sin(2 * math.pi * 2 * freq * t) * math.exp(-10 * t)
        click = bright * math.sin(2 * math.pi * 5.4 * freq * t) * math.exp(-40 * t)
        out.append(amp * env * (tine + click))
    return out


def paper(dur=0.05, amp=0.08, seed=1, lowpass=0.35):
    """Kurzes Rascheln: gefiltertes Rauschen."""
    rnd = random.Random(seed)
    n, y, out = int(dur * RATE), 0.0, []
    for i in range(n):
        y += lowpass * (rnd.uniform(-1, 1) - y)
        out.append(amp * y * math.sin(math.pi * i / n))
    return out


def mix(*parts):
    """parts: (startzeit_s, samples)"""
    n = max(int(s * RATE) + len(p) for s, p in parts)
    buf = [0.0] * n
    for s, p in parts:
        o = int(s * RATE)
        for i, v in enumerate(p):
            buf[o + i] += v
    return buf


def seq(notes, step=0.11, **kw):
    return mix(*((i * step, pluck(NOTE[n], **kw)) for i, n in enumerate(notes)))


def write(name, samples, gain=0.6):
    peak = max(1e-9, max(abs(v) for v in samples))
    scale = gain / peak * 32767
    fade = int(0.01 * RATE)
    data = bytearray()
    for i, v in enumerate(samples):
        f = min(1.0, (len(samples) - i) / fade)
        data += struct.pack("<h", int(v * scale * f))
    path = OUT / "stereo" / f"{name}.wav"
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(bytes(data))


SOUNDS = {
    # An- und Abmelden: Windspiel (Furin) auf und ab
    "desktop-login": seq(["D4", "E4", "G4", "A4", "B4", "D5"], step=0.13, dur=1.4, decay=3.0),
    "desktop-logout": seq(["D5", "B4", "A4", "G4", "D4"], step=0.14, dur=1.3, decay=3.2),
    # Nachrichten und Hinweise: zwei helle Töne "pon-pon"
    "message-new-instant": seq(["A4", "D5"], step=0.12, dur=0.7),
    "message-new-email": seq(["G4", "B4", "D5"], step=0.1, dur=0.7),
    "message-highlight": seq(["B4", "D5"], step=0.09, dur=0.6),
    "message-attention": seq(["D5", "A4", "D5"], step=0.12, dur=0.6),
    "dialog-information": seq(["E4", "A4"], step=0.11, dur=0.7),
    "dialog-question": seq(["A4", "B4"], step=0.14, dur=0.7),
    "dialog-warning": seq(["A4", "A4"], step=0.16, dur=0.6, decay=7),
    "dialog-error": seq(["E4", "D4"], step=0.15, dur=0.8, decay=5, bright=0.1),
    "bell": pluck(NOTE["A4"], dur=0.5, decay=8),
    # Erledigt / Erfolg / Fehler
    "complete": seq(["G4", "B4", "D5"], step=0.08, dur=0.8),
    "outcome-success": seq(["D4", "G4", "B4"], step=0.08, dur=0.8),
    "outcome-failure": seq(["B3", "G3"], step=0.14, dur=0.8, bright=0.1),
    # Geräte und Strom: kurz hoch bzw. runter
    "device-added": seq(["G4", "D5"], step=0.07, dur=0.5),
    "device-removed": seq(["D5", "G4"], step=0.07, dur=0.5),
    "power-plug": seq(["D4", "A4"], step=0.07, dur=0.5),
    "power-unplug": seq(["A4", "D4"], step=0.07, dur=0.5),
    "battery-low": seq(["E4", "E4"], step=0.18, dur=0.6, decay=7),
    "battery-caution": seq(["E4", "D4", "E4", "D4"], step=0.15, dur=0.6, decay=7),
    "battery-full": seq(["G4", "B4", "D5", "G4"], step=0.1, dur=0.8),
    "alarm-clock-elapsed": seq(["D5", "B4", "D5", "B4", "D5", "B4"], step=0.16, dur=0.6),
    # Lautstärke: ein ganz leises Holz-Tick
    "audio-volume-change": pluck(NOTE["D5"], dur=0.18, decay=24, amp=0.35),
    # Papiergeräusche
    "trash-empty": mix((0, paper(0.09, seed=3)), (0.07, paper(0.07, seed=5)), (0.13, paper(0.12, seed=7, lowpass=0.2))),
    "screen-capture": mix((0, paper(0.03, seed=9, lowpass=0.6)), (0.02, pluck(NOTE["B4"], dur=0.25, decay=18, amp=0.3))),
}
SOUNDS["camera-shutter"] = SOUNDS["screen-capture"]
SOUNDS["service-login"] = SOUNDS["desktop-login"]
SOUNDS["service-logout"] = SOUNDS["desktop-logout"]
SOUNDS["completion-success"] = SOUNDS["outcome-success"]
SOUNDS["completion-fail"] = SOUNDS["outcome-failure"]
SOUNDS["theme-demo"] = SOUNDS["desktop-login"]

(OUT / "stereo").mkdir(parents=True, exist_ok=True)
for name, samples in SOUNDS.items():
    write(name, samples)
(OUT / "index.theme").write_text("""[Sound Theme]
Name=kissa
Comment=Leise Kalimba- und Papiertöne für kissa
Inherits=ocean,freedesktop
Directories=stereo

[stereo]
OutputProfile=stereo
""", encoding="utf-8", newline="\n")
print(f"wrote {len(SOUNDS)} sounds")
