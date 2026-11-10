"""Music theory helpers: note names, scales and chord symbols -> MIDI pitches."""
from __future__ import annotations

import re

NOTE_OFFSETS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
ACCIDENTALS = {"": 0, "#": 1, "b": -1, "##": 2, "bb": -2}

SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "pentatonic": [0, 2, 4, 7, 9],
    "minor_pentatonic": [0, 3, 5, 7, 10],
}

# Chord qualities -> intervals from the root (semitones). Longest suffix wins.
CHORD_QUALITIES = {
    "": [0, 4, 7],
    "maj": [0, 4, 7],
    "m": [0, 3, 7],
    "min": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "+": [0, 4, 8],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "sus": [0, 5, 7],
    "5": [0, 7],
    "6": [0, 4, 7, 9],
    "m6": [0, 3, 7, 9],
    "7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "M7": [0, 4, 7, 11],
    "m7": [0, 3, 7, 10],
    "min7": [0, 3, 7, 10],
    "mmaj7": [0, 3, 7, 11],
    "m7b5": [0, 3, 6, 10],
    "dim7": [0, 3, 6, 9],
    "7sus4": [0, 5, 7, 10],
    "add9": [0, 4, 7, 14],
    "madd9": [0, 3, 7, 14],
    "9": [0, 4, 7, 10, 14],
    "maj9": [0, 4, 7, 11, 14],
    "m9": [0, 3, 7, 10, 14],
    "11": [0, 4, 7, 10, 14, 17],
    "m11": [0, 3, 7, 10, 14, 17],
    "13": [0, 4, 7, 10, 14, 21],
}

_NOTE_RE = re.compile(r"^([A-Ga-g])(##|bb|#|b)?(-?\d+)$")
_CHORD_RE = re.compile(r"^([A-G])(##|bb|#|b)?(.*?)(?:/([A-G])(##|bb|#|b)?)?$")


def pitch_class(letter: str, accidental: str | None = "") -> int:
    return (NOTE_OFFSETS[letter.upper()] + ACCIDENTALS[accidental or ""]) % 12


def note_to_midi(note: str | int) -> int:
    """'C4' -> 60 (Ableton/Yamaha convention puts middle C at C3; we use the
    scientific convention C4 = 60 and document it). Integers pass through."""
    if isinstance(note, int):
        midi = note
    else:
        m = _NOTE_RE.match(note.strip())
        if not m:
            raise ValueError(f"Invalid note name: {note!r} (expected e.g. 'C4', 'F#3', 'Bb2')")
        letter, acc, octave = m.groups()
        midi = (int(octave) + 1) * 12 + NOTE_OFFSETS[letter.upper()] + ACCIDENTALS[acc or ""]
    if not 0 <= midi <= 127:
        raise ValueError(f"Note out of MIDI range 0-127: {note!r} -> {midi}")
    return midi


def parse_key(key: str) -> tuple[int, list[int]]:
    """'D major' / 'F# minor' / 'A dorian' -> (root pitch class, scale intervals)."""
    parts = key.strip().split()
    if not parts:
        raise ValueError("Empty key")
    m = re.match(r"^([A-Ga-g])(##|bb|#|b)?$", parts[0])
    if not m:
        raise ValueError(f"Invalid key root: {parts[0]!r}")
    mode = (parts[1] if len(parts) > 1 else "major").lower()
    if mode not in SCALES:
        raise ValueError(f"Unknown scale {mode!r}; choose from {sorted(SCALES)}")
    return pitch_class(m.group(1), m.group(2)), SCALES[mode]


def parse_chord(symbol: str) -> tuple[int, list[int], int | None]:
    """Chord symbol -> (root pitch class, intervals, bass pitch class or None)."""
    m = _CHORD_RE.match(symbol.strip())
    if not m:
        raise ValueError(f"Invalid chord symbol: {symbol!r}")
    letter, acc, quality, bass_letter, bass_acc = m.groups()
    if quality not in CHORD_QUALITIES:
        raise ValueError(f"Unknown chord quality {quality!r} in {symbol!r}")
    bass = pitch_class(bass_letter, bass_acc) if bass_letter else None
    return pitch_class(letter, acc), CHORD_QUALITIES[quality], bass


def chord_pitches(symbol: str, octave: int = 4, voice_lead_from: list[int] | None = None) -> list[int]:
    """Chord symbol -> sorted MIDI pitches with the root in `octave`.

    If `voice_lead_from` is given, each chord tone is moved by octaves to sit as
    close as possible to the previous voicing's centre (smooth pad movement).
    """
    root, intervals, _ = parse_chord(symbol)
    base = (octave + 1) * 12 + root
    pitches = [base + i for i in intervals]
    if voice_lead_from:
        centre = sum(voice_lead_from) / len(voice_lead_from)
        moved = []
        for p in pitches:
            while p - centre > 6:
                p -= 12
            while centre - p > 6:
                p += 12
            moved.append(p)
        pitches = sorted(set(moved))
    for p in pitches:
        if not 0 <= p <= 127:
            raise ValueError(f"Chord {symbol!r} at octave {octave} leaves MIDI range")
    return sorted(pitches)


def chord_bass(symbol: str, octave: int = 2) -> int:
    root, _, bass = parse_chord(symbol)
    return (octave + 1) * 12 + (bass if bass is not None else root)


def scale_pitches(key: str, low: int, high: int) -> list[int]:
    root, intervals = parse_key(key)
    allowed = {(root + i) % 12 for i in intervals}
    return [p for p in range(low, high + 1) if p % 12 in allowed]
