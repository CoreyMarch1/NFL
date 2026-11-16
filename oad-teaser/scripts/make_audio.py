#!/usr/bin/env python3
"""Synthesizes the full teaser soundtrack to out/audio/soundtrack.wav.

Everything is generated from oscillators and noise: two pulse voices (lead and
sixteenth-note arpeggio), a triangle bass, a noise drum channel, plus the
frame-accurate sound effects. No samples. 48 kHz stereo, 15.000 s.

Usage: python3 scripts/make_audio.py
Timings below are in video frames (30 fps) so they line up with src/config.ts.
"""
import os
import re
import subprocess
import wave

import numpy as np

SR = 48000
FPS = 30
DURATION_FRAMES = 450
N = SR * DURATION_FRAMES // FPS
BPM = 120
BEAT = 60.0 / BPM  # 0.5 s = 15 frames
S16 = BEAT / 4

TARGET_LUFS = -14.0
MAX_TRUE_PEAK_DB = -1.5

# ------------------------------ SFX timings (frames) ------------------------
SFX = {
    "coin": 3,
    "power_on": 12,
    "bar_ticks": (66, 96),
    "menu_blips": (105, 120),
    "confirm": 135,
    "card_tones": (165, 180, 195),
    "button": 255,
    "counter": (288, 318),
    "level_clear": 318,
    "flash_hits": (330, 350, 370),
    "coin_single": 393,
    "jingle": 405,  # resolves by frame 440
}
MUSIC_IN = 60  # 0:02
GROOVE_IN = 150  # 0:05
FILL_IN = 330  # 0:11
STOP_AT = 390  # 0:13

rng = np.random.default_rng(1992)


def f2s(frame):
    return int(round(frame * SR / FPS))


def note(name):
    """'A4' -> Hz"""
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    m = re.match(r"([A-G])(#|b)?(-?\d)", name)
    semis = names[m.group(1)] + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0)
    midi = semis + 12 * (int(m.group(3)) + 1)
    return 440.0 * 2 ** ((midi - 69) / 12)


def env(n, attack=0.002, decay=None, release=0.01, sustain=1.0):
    """Simple attack / exponential decay / release envelope over n samples."""
    t = np.arange(n) / SR
    e = np.ones(n) * sustain
    if decay:
        e = sustain + (1 - sustain) * np.exp(-t / decay)
    a = max(1, int(attack * SR))
    e[:a] *= np.linspace(0, 1, a)
    r = max(1, min(n, int(release * SR)))
    e[-r:] *= np.linspace(1, 0, r)
    return e


def phase(freq, n):
    f = np.full(n, freq) if np.isscalar(freq) else freq
    return np.cumsum(f) / SR


def pulse(freq, n, duty=0.5):
    """Band-limited-ish pulse wave (4x oversampled, then averaged down)."""
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.asarray(freq, float)
    ph = np.cumsum(np.repeat(f, 4)) / (SR * 4)
    w = np.where((ph % 1.0) < duty, 1.0, -1.0)
    return w.reshape(n, 4).mean(axis=1) - (2 * duty - 1)


def triangle(freq, n):
    ph = phase(freq, n) % 1.0
    return 4 * np.abs(ph - 0.5) - 1


def sine(freq, n):
    return np.sin(2 * np.pi * phase(freq, n))


def noise(n, color=1.0):
    """White noise; color < 1 applies a one-pole low-pass (0..1 = cutoff)."""
    x = rng.uniform(-1, 1, n)
    if color >= 1.0:
        return x
    y = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += color * (x[i] - acc)
        y[i] = acc
    return y


class Bus:
    def __init__(self):
        self.l = np.zeros(N)
        self.r = np.zeros(N)

    def add(self, start, mono, gain=1.0, pan=0.0):
        """pan -1..1, equal power."""
        if start >= N:
            return
        start = max(0, start)
        mono = mono[: N - start]
        a = (pan + 1) * np.pi / 4
        self.l[start : start + len(mono)] += mono * gain * np.cos(a) * 1.4142
        self.r[start : start + len(mono)] += mono * gain * np.sin(a) * 1.4142


music = Bus()
sfx = Bus()
hum = Bus()

# ------------------------------- cabinet hum --------------------------------
t = np.arange(N) / SR
h = 0.6 * np.sin(2 * np.pi * 60 * t) + 0.25 * np.sin(2 * np.pi * 120 * t + 0.4) + 0.12 * np.sin(2 * np.pi * 180 * t + 1.1)
h += 0.02 * rng.uniform(-1, 1, N)
hum_level = np.ones(N) * 0.35
hum_level[: f2s(MUSIC_IN)] = 1.0  # hum alone before the music
hum_level[f2s(STOP_AT) :] = 0.8  # and in the gap after the hard stop
hum_level[: f2s(2)] *= np.linspace(0, 1, f2s(2))
# CRT power-on bumps the hum
hum_level[f2s(12) : f2s(20)] *= 1.5
k = int(0.03 * SR)
hum_level = np.convolve(hum_level, np.ones(k) / k, mode="same")
hum.add(0, h * hum_level, 0.18)

# --------------------------------- music ------------------------------------
# One chord per half bar (1 s). Bars are 2 s long and start at 1, 3, 5 ... s,
# so the cuts at 5, 11 and 13 s all land on downbeats.
CHORDS = {
    "Am": ["A", "C", "E"],
    "F": ["F", "A", "C"],
    "C": ["C", "E", "G"],
    "G": ["G", "B", "D"],
    "Dm": ["D", "F", "A"],
    "E": ["E", "G#", "B"],
}
BASS_OCT = {"Am": "A1", "F": "F1", "C": "C2", "G": "G1", "Dm": "D2", "E": "E1"}
# (start second, chord)
PROG = [(2, "Am"), (3, "F"), (4, "G"), (5, "Am"), (6, "F"), (7, "C"), (8, "G"), (9, "Am"), (10, "F"), (11, "Dm"), (12, "E")]


def chord_tones(ch, base_oct, count):
    """Ascending chord tones starting in base_oct."""
    out = []
    names = CHORDS[ch]
    octv = base_oct
    last = 0
    i = 0
    while len(out) < count:
        f = note(f"{names[i % 3]}{octv}")
        if f <= last:
            octv += 1
            f = note(f"{names[i % 3]}{octv}")
        out.append(f)
        last = f
        i += 1
    return out


def energy(sec):
    """0 sparse, 1..3 groove levels rising every bar-pair boundary, 4 fill."""
    if sec < 5:
        return 0
    if sec < 7:
        return 1
    if sec < 9:
        return 2
    if sec < 11:
        return 3
    return 4


for sec, ch in PROG:
    e = energy(sec)
    start = sec * SR
    # --- arpeggio (pulse 2), sixteenth notes
    tones = chord_tones(ch, 3 if e < 2 else 4, 6)
    if e == 0:
        pattern = [0, 2, 1, 2, 0, 2, 1, 2]  # sparse, narrow
        vol, duty = 0.16, 0.5
    elif e == 4:
        pattern = None  # rising run handled below
        vol, duty = 0.24, 0.25
    else:
        pattern = [0, 1, 2, 3, 2, 1, 2, 3] if e == 1 else [0, 2, 3, 5, 4, 3, 2, 4]
        vol, duty = 0.17 + 0.025 * e, 0.25 if e >= 2 else 0.5
    for i in range(8):
        n = int(S16 * SR)
        if pattern is None:
            # rising arpeggio through the fill: climbs chord tones every sixteenth
            step = (sec - 11) * 8 + i
            run = chord_tones(ch, 3, 16)
            f = run[min(15, step % 8 + (step // 8) * 4 + 2)]
        else:
            f = tones[pattern[i]]
        x = pulse(f, n, duty) * env(n, 0.002, 0.07, 0.01, 0.35)
        music.add(start + i * n, x, vol, pan=0.35)
    # --- bass (triangle)
    root = note(BASS_OCT[ch])
    if e == 0:
        n = int(BEAT * 2 * SR)
        music.add(start, triangle(root, n) * env(n, 0.005, 0.5, 0.05, 0.6), 0.5)
    else:
        for i in range(4):  # eighth notes: root, root, octave, root
            n = int(BEAT / 2 * SR)
            f = root * (2 if i == 2 else 1)
            music.add(start + i * n, triangle(f, n) * env(n, 0.003, 0.12, 0.02, 0.55), 0.55)
    # --- drums (noise channel) from the groove onward
    if e >= 1:
        for i in range(8):
            pos = start + i * int(S16 * SR)
            beat_pos = i % 4
            if i in (0, 4) and e < 4:  # kick on the beat: low noise thump + pitch drop
                n = int(0.11 * SR)
                sweep = np.linspace(150, 45, n)
                kick = sine(sweep, n) * env(n, 0.001, 0.035, 0.01, 0.0) + 0.5 * noise(n, 0.08) * env(n, 0.001, 0.02, 0.01, 0.0)
                music.add(pos, kick, 0.8)
            if i == 4 and e < 4:  # snare on the backbeat
                n = int(0.13 * SR)
                music.add(pos, noise(n, 0.75) * env(n, 0.001, 0.04, 0.01, 0.0), 0.42)
            hat_on = (beat_pos in (0, 2)) if e == 1 else True
            if hat_on and e < 4:
                n = int(0.035 * SR)
                x = noise(n)
                x = np.diff(x, prepend=0)  # crude high-pass
                music.add(pos, x * env(n, 0.001, 0.008, 0.005, 0.0), 0.16 + 0.02 * e, pan=-0.3 if i % 2 else 0.3)
    if e == 4:
        # drum fill: sixteenth snares, then thirty-seconds for the last beat
        hits = [i * S16 for i in range(8)]
        if sec == 12:
            hits = [i * S16 for i in range(4)] + [0.5 + i * S16 / 2 for i in range(8)]
        for j, off in enumerate(hits):
            n = int(0.07 * SR)
            lvl = 0.3 + 0.35 * (((sec - 11) + off) / 2)
            tone = 0.55 + 0.4 * (((sec - 11) + off) / 2)
            x = noise(n, min(1.0, tone)) * env(n, 0.001, 0.025, 0.01, 0.0)
            music.add(start + int(off * SR), x, lvl, pan=0.4 * np.sin(j))
        if sec == 11:
            n = int(0.11 * SR)
            music.add(start, sine(np.linspace(150, 45, n), n) * env(n, 0.001, 0.035, 0.01, 0.0), 0.8)

# --- lead melody (pulse 1), eighth notes, enters with the groove. Original line.
LEAD = {
    5: ["A4", "C5", "E5", "D5", "C5", None, "A4", None],
    6: ["A4", "C5", "F5", "E5", "C5", None, "D5", None],
    7: ["G5", "E5", "C5", "E5", "G5", None, "A5", None],
    8: ["B4", "D5", "G5", "D5", "B5", None, "A5", "G5"],
    9: ["A5", "E5", "A5", "C6", "B5", "A5", "E5", "A5"],
    10: ["C6", "A5", "F5", "A5", "C6", "D6", "E6", None],
    11: ["D6", None, "A5", None, "F6", None, "D6", None],
    12: ["E6", None, "G#5", "B5", "E6", "G#6", "B6", None],
}
for sec, notes in LEAD.items():
    for i, nm in enumerate(notes):
        if nm is None:
            continue
        n = int(S16 * SR)  # 8 slots per second = sixteenth-length slots
        hold = 1
        while i + hold < len(notes) and notes[i + hold] is None:
            hold += 1
        n *= hold
        vib = 1 + 0.004 * np.sin(2 * np.pi * 6 * np.arange(n) / SR)
        x = pulse(note(nm) * vib, n, 0.25 if sec < 9 else 0.125) * env(n, 0.004, 0.15, 0.02, 0.6)
        music.add(sec * SR + i * int(S16 * SR), x, 0.2 + 0.02 * energy(sec), pan=-0.25)

# --- hard stop on the downbeat at 0:13: one tight stab, then silence
n = int(0.09 * SR)
stab = sum(pulse(note(x), n, 0.25) for x in ("A3", "E4", "A4")) / 3 * env(n, 0.001, 0.03, 0.02, 0.2)
music.add(f2s(STOP_AT), stab, 0.5)
music.add(f2s(STOP_AT), sine(np.linspace(160, 45, n), n) * env(n, 0.001, 0.03, 0.01, 0.0), 0.9)
cut = f2s(STOP_AT) + n
music.l[cut:] = 0
music.r[cut:] = 0


# ---------------------------------- SFX -------------------------------------
def ping(freq, dur=0.22, bright=1.0):
    """Metallic ping: inharmonic partials with fast decays (a coin, not a beep)."""
    n = int(dur * SR)
    x = np.zeros(n)
    for ratio, amp, dec in ((1.0, 1.0, 0.07), (2.76, 0.5 * bright, 0.045), (5.40, 0.3 * bright, 0.03), (8.93, 0.15 * bright, 0.02)):
        x += amp * sine(freq * ratio, n) * np.exp(-np.arange(n) / SR / dec)
    return x * env(n, 0.0005, None, 0.02)


def blip(freq, dur=0.06, duty=0.5, bend=1.0):
    n = int(dur * SR)
    f = np.linspace(freq, freq * bend, n)
    return pulse(f, n, duty) * env(n, 0.001, dur / 2, 0.008, 0.2)


def tone(nm, dur, duty=0.5, decay=0.12):
    n = int(dur * SR)
    return pulse(note(nm), n, duty) * env(n, 0.002, decay, 0.02, 0.35)


# frame 3: coin drop, two quick high metallic pings
sfx.add(f2s(SFX["coin"]), ping(2350, 0.18), 0.55)
sfx.add(f2s(SFX["coin"]) + int(0.085 * SR), ping(3130, 0.32), 0.6)

# frame 12: CRT power-on, low thunk plus a rising whine
n = int(0.22 * SR)
thunk = sine(np.linspace(95, 38, n), n) * env(n, 0.001, 0.06, 0.03, 0.0) + 0.4 * noise(n, 0.05) * env(n, 0.001, 0.03, 0.02, 0.0)
sfx.add(f2s(SFX["power_on"]), thunk, 1.0)
n = int(0.75 * SR)
whine_f = 900 * (15600 / 900) ** (np.linspace(0, 1, n) ** 0.6)
whine = sine(whine_f, n) * np.linspace(0.0, 1.0, n) ** 0.5 * env(n, 0.02, None, 0.3)
sfx.add(f2s(SFX["power_on"]), whine, 0.10)
n = int(0.5 * SR)
sfx.add(f2s(SFX["power_on"]) + int(0.06 * SR), noise(n, 0.3) * env(n, 0.05, 0.12, 0.1, 0.0), 0.12)

# frames 66..96: soft ascending ticks as the six stat bars fill (one run per bar)
a, b = SFX["bar_ticks"]
steps = 16
for i in range(steps):
    fr = a + (b - a) * i / steps
    sfx.add(f2s(fr), blip(700 * 2 ** (i / 12), 0.03, 0.5), 0.2, pan=-0.3 + 0.6 * i / steps)

# frames 105, 120: menu blip on each cursor move
for fr in SFX["menu_blips"]:
    sfx.add(f2s(fr), blip(880, 0.05, 0.25, 0.85), 0.5)

# frame 135: select confirm, two-note rising chirp
sfx.add(f2s(SFX["confirm"]), tone("E5", 0.07, 0.25, 0.05), 0.5)
sfx.add(f2s(SFX["confirm"]) + int(0.07 * SR), tone("B5", 0.16, 0.25, 0.08), 0.5)

# frames 165, 180, 195: three rising confirm tones, one per card
for fr, nm in zip(SFX["card_tones"], ("C5", "E5", "G5")):
    x = tone(nm, 0.2, 0.25, 0.09)
    x[: int(0.012 * SR)] += 0.5 * noise(int(0.012 * SR)) * np.linspace(1, 0, int(0.012 * SR))
    sfx.add(f2s(fr), x, 0.5)

# frame 255: button press click
n = int(0.03 * SR)
click = noise(n, 0.6) * env(n, 0.0005, 0.006, 0.005, 0.0) + sine(np.linspace(420, 180, n), n) * env(n, 0.0005, 0.012, 0.005, 0.0)
sfx.add(f2s(SFX["button"]), click, 0.9)

# frames 288..318: fast score-counter ticking, pitch rising (ticks slow as it eases out)
a, b = SFX["counter"]
count = 26
for i in range(count):
    u = i / (count - 1)
    fr = a + (b - a) * (1 - (1 - u) ** 1.6)  # dense first, sparser at the end
    sfx.add(f2s(fr), blip(900 * 2 ** (u * 1.4), 0.022, 0.5), 0.26, pan=0.2 * np.sin(i))

# frame 318: "level clear" three-note sting
for i, nm in enumerate(("D6", "F#6", "A6")):
    sfx.add(f2s(SFX["level_clear"]) + int(i * 0.075 * SR), tone(nm, 0.11 if i < 2 else 0.3, 0.25, 0.1), 0.42)

# frames 330, 350, 370: short noise hits on each flash cut
for j, fr in enumerate(SFX["flash_hits"]):
    n = int(0.16 * SR)
    hit = noise(n, 0.5) * env(n, 0.0005, 0.035, 0.03, 0.0) + sine(np.linspace(130, 50, n), n) * env(n, 0.001, 0.04, 0.02, 0.0)
    sfx.add(f2s(fr), hit, 0.8, pan=(-0.3, 0.3, 0.0)[j])

# frame 393: single coin drop
sfx.add(f2s(SFX["coin_single"]), ping(2740, 0.4), 0.6)

# frame 405: five-note "ready" jingle in A major, resolving by frame 440
jingle = [("A4", 0), ("C#5", 4), ("E5", 8), ("C#5", 12), ("A5", 16)]  # offsets in frames
for nm, off in jingle:
    last = nm == "A5"
    dur = 0.55 if last else 0.14  # final note ends at frame 405 + 16 + 16.5 = 437.5
    f0 = note(nm)
    n = int(dur * SR)
    x = pulse(f0, n, 0.25) * env(n, 0.003, 0.25 if last else 0.1, 0.08, 0.45)
    x += 0.5 * pulse(f0 * 2, n, 0.5) * env(n, 0.003, 0.08, 0.05, 0.2)
    sfx.add(f2s(SFX["jingle"] + off), x, 0.42)
    sfx.add(f2s(SFX["jingle"] + off), triangle(f0 / 2, n) * env(n, 0.003, 0.2, 0.05, 0.5), 0.3)

# ---------------------------------- mix -------------------------------------
# Effects sit above the music: the music ducks under the effects envelope.
sfx_env = np.abs(sfx.l) + np.abs(sfx.r)
k = int(0.04 * SR)
sfx_env = np.convolve(sfx_env, np.ones(k) / k, mode="same")
duck = 1.0 - 0.45 * np.clip(sfx_env * 4, 0, 1)
MUSIC_GAIN, SFX_GAIN = 0.62, 1.0
mix = np.stack(
    [
        music.l * duck * MUSIC_GAIN + sfx.l * SFX_GAIN + hum.l,
        music.r * duck * MUSIC_GAIN + sfx.r * SFX_GAIN + hum.r,
    ],
    axis=1,
)
# no click at the loop point
fade = int(0.01 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "out", "audio", "soundtrack.wav")
os.makedirs(os.path.dirname(OUT), exist_ok=True)


def write(x):
    pcm = np.clip(x, -1, 1)
    pcm = (pcm * 32767).astype("<i2")
    with wave.open(OUT, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def measure():
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", OUT, "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    tail = r.stderr[r.stderr.rfind("Summary:") :]
    lufs = float(re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1))
    peak = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail).group(1))
    return lufs, peak


def limit(x, ceiling_db):
    """Soft-knee limiter: transparent below 70% of the ceiling, tanh above."""
    c = 10 ** (ceiling_db / 20)
    knee = 0.7 * c
    a = np.abs(x)
    over = a > knee
    y = x.copy()
    y[over] = np.sign(x[over]) * (knee + (c - knee) * np.tanh((a[over] - knee) / (c - knee)))
    return y


# Normalize to the loudness target, keeping true peak under the ceiling.
gain = 0.5 / np.max(np.abs(mix))
for _ in range(6):
    write(limit(mix * gain, MAX_TRUE_PEAK_DB - 0.4))
    lufs, peak = measure()
    if abs(lufs - TARGET_LUFS) < 0.1:
        break
    gain *= 10 ** ((TARGET_LUFS - lufs) / 20)
print(f"wrote {OUT}: {N / SR:.3f} s, integrated {lufs:.1f} LUFS, true peak {peak:.1f} dBFS")
