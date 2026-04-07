"""Procedurally-generated audio for Iron Slug.

All sounds are synthesised at runtime with NumPy — no audio files needed.
"""
import numpy as np
import pygame

_SR = 44100
_sounds: dict = {}
_music_ch: "pygame.mixer.Channel | None" = None


# ── helpers ───────────────────────────────────────────────────────────────────

def _to_sound(arr: np.ndarray) -> pygame.mixer.Sound:
    s      = np.clip(arr, -1.0, 1.0)
    stereo = np.column_stack([s, s])
    return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))


def _tone(freq: float, dur: float, vol: float = 0.25,
          kind: str = 'square') -> np.ndarray:
    n = int(_SR * dur)
    if n <= 0 or freq <= 0:
        return np.zeros(max(n, 1))
    t = np.linspace(0, dur, n, endpoint=False)
    if kind == 'square':
        w = np.sign(np.sin(2 * np.pi * freq * t)) * vol
    elif kind == 'saw':
        w = (2 * (t * freq % 1.0) - 1.0) * vol
    else:                                          # sine
        w = np.sin(2 * np.pi * freq * t) * vol
    fade = min(int(0.005 * _SR), n // 4)
    w[:fade]  *= np.linspace(0, 1, fade)
    w[-fade:] *= np.linspace(1, 0, fade)
    return w


# ── background music ──────────────────────────────────────────────────────────

def _build_music() -> pygame.mixer.Sound:
    BPM = 178
    q   = 60.0 / BPM          # quarter note (s)
    e   = q / 2               # eighth
    s   = q / 4               # sixteenth
    R   = 0.0                  # rest

    # Frequencies — E-minor pentatonic + passing tones
    E3, G3, A3, B3     = 164.81, 196.00, 220.00, 246.94
    D4, E4, G4, A4, B4 = 293.66, 329.63, 392.00, 440.00, 493.88
    D5, E5, G5         = 587.33, 659.25, 783.99

    # Lead melody — 4 bars × 4/4
    melody = [
        # bar 1 – ascending run
        (E4,s),(G4,s),(A4,s),(B4,s),  (D5,e),(E5,e),  (D5,s),(B4,s),(A4,e),  (G4,q),
        # bar 2 – call & response
        (R,e),(A4,e),                  (B4,s),(D5,s),(E5,e),  (D5,e),(B4,e),  (A4,q),
        # bar 3 – high run
        (B4,s),(D5,s),(E5,s),(G5,s),  (E5,e),(D5,e),  (B4,s),(A4,s),(G4,e),  (E4,q),
        # bar 4 – resolve
        (D4,e),(E4,e),                 (G4,s),(A4,s),(B4,e),  (D5,e),(B4,e),  (E5,q),
    ]

    # Bass line — same 4 bars
    bass = [
        (E3,q),(R,e),(E3,e),(G3,e),(E3,e),(B3,q),
        (A3,q),(R,e),(A3,e),(A3,e),(B3,e),(A3,q),
        (E3,q),(R,e),(E3,e),(G3,e),(B3,e),(E4,q),
        (D4,e),(R,e),(E3,q),(B3,e),(D4,e),(E3,q),
    ]

    lead   = np.concatenate([_tone(f, d, 0.16, 'square') for f, d in melody])
    btrack = np.concatenate([_tone(f, d, 0.20, 'square') for f, d in bass])

    L      = max(len(lead), len(btrack))
    lead   = np.pad(lead,   (0, L - len(lead)))
    btrack = np.pad(btrack, (0, L - len(btrack)))

    # Percussion
    rng  = np.random.default_rng(42)
    perc = np.zeros(L)
    bN   = max(1, int(q * _SR))    # samples per beat

    for i in range(L // bN + 1):
        p = i * bN
        if p >= L:
            break

        # kick on beats 1 & 3 — frequency-swept sine (chirp)
        if i % 4 in (0, 2):
            k   = min(int(0.07 * _SR), L - p)
            tt  = np.linspace(0, 0.07, k, False)
            f0, dk = 160.0, 25.0
            phi = 2 * np.pi * f0 * (1 - np.exp(-dk * tt)) / dk
            perc[p:p+k] += np.sin(phi) * np.exp(-tt * 18) * 0.30

        # snare on beats 2 & 4
        if i % 4 in (1, 3):
            k  = min(int(0.06 * _SR), L - p)
            tt = np.linspace(0, 1, k, False)
            perc[p:p+k] += rng.uniform(-1, 1, k) * np.exp(-tt * 10) * 0.15

        # hi-hat on every off-beat eighth
        hp = p + bN // 2
        if hp < L:
            k  = min(int(0.012 * _SR), L - hp)
            tt = np.linspace(0, 1, k, False)
            perc[hp:hp+k] += rng.uniform(-1, 1, k) * np.exp(-tt * 15) * 0.07

    return _to_sound(lead + btrack + perc)


# ── SFX ───────────────────────────────────────────────────────────────────────

def _build_dash() -> pygame.mixer.Sound:
    """Short air-whoosh for the dash."""
    n   = int(0.12 * _SR)
    t   = np.linspace(0, 0.12, n, False)
    rng = np.random.default_rng(9)

    # Filtered noise sweep: bright at start, fades quickly
    noise  = rng.uniform(-1, 1, n) * np.exp(-t * 22) * 0.55
    tone   = np.sin(2 * np.pi * (600 + 400 * (1 - t / 0.12)) * t) * np.exp(-t * 20) * 0.30
    wave   = (noise + tone) * 0.80

    fade = min(int(0.002 * _SR), n)
    wave[:fade] *= np.linspace(0, 1, fade)
    return _to_sound(wave)


def _build_slash() -> pygame.mixer.Sound:
    """Sharp metallic swoosh — knife slash."""
    n   = int(0.15 * _SR)
    t   = np.linspace(0, 0.15, n, False)
    rng = np.random.default_rng(7)

    # High-frequency noise filtered by a fast descending tone (metal ring)
    noise  = rng.uniform(-1, 1, n) * np.exp(-t * 30) * 0.45
    ring   = np.sin(2 * np.pi * 3500 * t) * np.exp(-t * 25) * 0.35
    swoosh = np.sin(2 * np.pi * (800 - 600 * t / 0.15) * t) * np.exp(-t * 18) * 0.25

    wave = noise + ring + swoosh
    fade = min(int(0.002 * _SR), n)
    wave[:fade] *= np.linspace(0, 1, fade)
    return _to_sound(wave)


def _build_shoot(weapon: str) -> pygame.mixer.Sound:
    seed = {'pistol': 1, 'ak47': 2, 'flamethrower': 3}.get(weapon, 0)
    rng  = np.random.default_rng(seed)

    if weapon == 'flamethrower':
        dur, body_decay, freq = 0.10, 6.0, 180.0
        n    = int(_SR * dur)
        t    = np.linspace(0, dur, n, False)
        body = rng.uniform(-1, 1, n) * np.exp(-t * body_decay) * 0.50
        low  = np.sin(2 * np.pi * freq * t) * np.exp(-t * body_decay * 1.5) * 0.35
        wave = (body + low) * 0.75

    elif weapon == 'ak47':
        dur, body_decay, click_freq = 0.13, 28.0, 1800.0
        n     = int(_SR * dur)
        t     = np.linspace(0, dur, n, False)
        body  = rng.uniform(-1, 1, n) * np.exp(-t * body_decay) * 0.60
        click = np.sin(2 * np.pi * click_freq * t) * np.exp(-t * 55) * 0.40
        wave  = (body + click) * 0.85

    else:  # pistol
        dur, body_decay, click_freq = 0.11, 35.0, 2800.0
        n     = int(_SR * dur)
        t     = np.linspace(0, dur, n, False)
        body  = rng.uniform(-1, 1, n) * np.exp(-t * body_decay) * 0.55
        click = np.sin(2 * np.pi * click_freq * t) * np.exp(-t * 80) * 0.45
        wave  = (body + click) * 0.85

    # brief attack to prevent click at sample start
    fade = min(int(0.001 * _SR), len(wave))
    wave[:fade] *= np.linspace(0, 1, fade)
    return _to_sound(wave)


# ── public API ────────────────────────────────────────────────────────────────

def init() -> None:
    """Generate all sounds. Must be called after pygame.init()."""
    pygame.mixer.set_num_channels(16)
    _sounds['music']        = _build_music()
    _sounds['pistol']       = _build_shoot('pistol')
    _sounds['ak47']         = _build_shoot('ak47')
    _sounds['flamethrower'] = _build_shoot('flamethrower')
    _sounds['slash']        = _build_slash()
    _sounds['dash']         = _build_dash()
    _sounds['music'].set_volume(0.35)


def play_music() -> None:
    """Start background music loop on a dedicated channel."""
    global _music_ch
    _music_ch = pygame.mixer.Channel(0)
    _music_ch.play(_sounds['music'], loops=-1)


def play_shoot(weapon: str) -> None:
    """Play the firing sound for the given weapon."""
    _sounds.get(weapon, _sounds['pistol']).play()


def play_slash() -> None:
    """Play the knife slash sound."""
    _sounds['slash'].play()


def play_dash() -> None:
    """Play the dash whoosh sound."""
    _sounds['dash'].play()
