"""Declarative song spec -> concrete tracks, scenes, clips, notes and CC automation.

A spec is a YAML/JSON document (see examples/). Everything is validated up
front so a bad spec fails before a single message reaches Ableton.
"""
from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import theory

GM_DRUMS = {
    "kick": 36, "rim": 37, "snare": 38, "clap": 39, "snare2": 40,
    "low_tom": 41, "hat": 42, "closed_hat": 42, "mid_tom": 45, "pedal_hat": 44,
    "open_hat": 46, "high_tom": 50, "crash": 49, "ride": 51, "tambourine": 54,
    "cowbell": 56, "conga_hi": 62, "conga_lo": 64, "shaker": 70, "cabasa": 69,
    "talking_drum": 66, "agogo": 67,  # agogo/timbale slots map to GM 67/66
}
STEP_VELOCITY = {"x": 112, "X": 127, "o": 84, "g": 48}  # g = ghost note
REST, TIE = ".", "-"


class SpecError(ValueError):
    pass


@dataclass
class Note:
    pitch: int
    start: float
    duration: float
    velocity: int = 100
    mute: bool = False


@dataclass
class Clip:
    name: str
    length: float  # beats
    notes: list[Note] = field(default_factory=list)
    cc: dict[int, list[tuple[float, int]]] = field(default_factory=dict)
    color: int | None = None
    loop: bool = True


@dataclass
class Track:
    name: str
    kind: str = "midi"  # midi | audio
    color: int | None = None
    volume: float | None = None  # 0..1 (Live: 0.85 ~= 0 dB)
    pan: float | None = None  # -1..1
    channel: int = 0  # MIDI export channel (0-15); drums default to 9
    instrument: str | None = None  # human hint, e.g. "Drift > Warm Pad"


@dataclass
class Scene:
    name: str
    bars: int
    clips: dict[str, Clip] = field(default_factory=dict)
    tempo: float | None = None
    color: int | None = None


@dataclass
class Song:
    title: str
    tempo: float
    numerator: int
    denominator: int
    key: str | None
    tracks: list[Track]
    scenes: list[Scene]
    arrangement: list[str]
    show: list[dict[str, Any]]

    @property
    def beats_per_bar(self) -> float:
        return self.numerator * 4 / self.denominator

    def track(self, name: str) -> Track:
        for t in self.tracks:
            if t.name == name:
                return t
        raise SpecError(f"Unknown track {name!r}")

    def scene(self, name: str) -> Scene:
        for s in self.scenes:
            if s.name == name:
                return s
        raise SpecError(f"Unknown scene {name!r}")


# --------------------------------------------------------------------------- helpers

def parse_color(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.startswith("#") and len(value) == 7:
        return int(value[1:], 16)
    raise SpecError(f"Color must be '#RRGGBB' or int, got {value!r}")


def _step_events(pattern: str, beats_per_bar: float, bars: int, pattern_bars: int = 1):
    """Yield (start_beat, duration_beats, velocity) for a step pattern over `bars` bars."""
    pattern = pattern.replace(" ", "").replace("|", "")
    if not pattern:
        raise SpecError("Empty step pattern")
    bad = set(pattern) - set(STEP_VELOCITY) - {REST, TIE}
    if bad:
        raise SpecError(f"Invalid step characters {sorted(bad)} in {pattern!r} (use x X o g . -)")
    step = beats_per_bar * pattern_bars / len(pattern)
    events: list[list[float]] = []
    reps = -(-bars // pattern_bars)  # ceil
    total = bars * beats_per_bar
    for r in range(reps):
        offset = r * pattern_bars * beats_per_bar
        for i, ch in enumerate(pattern):
            start = offset + i * step
            if start >= total - 1e-9:
                break
            if ch in STEP_VELOCITY:
                events.append([start, step, STEP_VELOCITY[ch]])
            elif ch == TIE and events and abs(events[-1][0] + events[-1][1] - start) < 1e-9:
                events[-1][1] += step
    return [(round(s, 6), round(d, 6), int(v)) for s, d, v in events]


def _progression(chords: str | list[str], beats_per_bar: float, total_beats: float, bars_per_chord: float):
    """'Dmaj7 Bm7:2 G' -> [(symbol, start, duration)] looped to fill total_beats.

    ':N' after a chord overrides its length in bars (fractions allowed, e.g. ':0.5').
    """
    tokens = chords.split() if isinstance(chords, str) else list(chords)
    if not tokens:
        raise SpecError("Empty chord progression")
    parsed = []
    for tok in tokens:
        sym, _, bars = str(tok).partition(":")
        theory.parse_chord(sym)  # validate early
        length = (float(bars) if bars else bars_per_chord) * beats_per_bar
        if length <= 0:
            raise SpecError(f"Chord length must be positive: {tok!r}")
        parsed.append((sym, length))
    out, t, i = [], 0.0, 0
    while t < total_beats - 1e-9:
        sym, length = parsed[i % len(parsed)]
        out.append((sym, t, min(length, total_beats - t)))
        t += length
        i += 1
    return out


def _humanize(notes: list[Note], amount: int, rng: random.Random) -> None:
    if amount <= 0:
        return
    for n in notes:
        n.velocity = max(1, min(127, n.velocity + rng.randint(-amount, amount)))


# --------------------------------------------------------------------------- clip builders

def build_clip(cfg: dict[str, Any], *, name: str, bars: int, beats_per_bar: float,
               key: str | None, is_drum: bool, seed: int) -> Clip:
    length = bars * beats_per_bar
    clip = Clip(name=cfg.get("name", name), length=length, color=parse_color(cfg.get("color")))
    rng = random.Random(seed)
    velocity = int(cfg.get("velocity", 96))
    kinds = [k for k in ("chords", "drums", "melody", "notes", "arp_scale") if k in cfg]
    if len(kinds) > 1:
        raise SpecError(f"Clip {name!r}: pick one of chords/drums/melody/notes, got {kinds}")

    if "chords" in cfg:
        style = cfg.get("style", "pad")
        octave = int(cfg.get("octave", 4 if style != "bass" else 2))
        prog = _progression(cfg["chords"], beats_per_bar, length, float(cfg.get("bars_per_chord", 1)))
        prev: list[int] | None = None
        for sym, start, dur in prog:
            if style == "bass":
                root = theory.chord_bass(sym, octave)
                rhythm = cfg.get("rhythm", "x---")
                for s, d, v in _step_events(rhythm, beats_per_bar, max(1, math.ceil(dur / beats_per_bar - 1e-9))):
                    if s >= dur - 1e-9:
                        break
                    clip.notes.append(Note(root, start + s, min(d, dur - s), round(v * velocity / 112)))
                continue
            pitches = theory.chord_pitches(sym, octave, prev if cfg.get("voice_lead", True) else None)
            prev = pitches
            if style == "pad":
                for p in pitches:
                    clip.notes.append(Note(p, start, dur, velocity))
            elif style == "stabs":
                rhythm = cfg.get("rhythm", "x.x.x.x.")
                chord_bars = max(1, math.ceil(dur / beats_per_bar - 1e-9))
                for s, d, v in _step_events(rhythm, beats_per_bar, chord_bars):
                    if s >= dur - 1e-9:
                        break
                    for p in pitches:
                        clip.notes.append(Note(p, start + s, min(d, dur - s), round(v * velocity / 112)))
            elif style == "arp":
                rate = float(cfg.get("rate", 0.5))
                span = int(cfg.get("octaves", 2))
                seq = [p + 12 * o for o in range(span) for p in pitches]
                if cfg.get("direction", "up") == "updown" and len(seq) > 2:
                    seq = seq + seq[-2:0:-1]
                elif cfg.get("direction") == "down":
                    seq = seq[::-1]
                t, i = 0.0, 0
                while t < dur - 1e-9:
                    p = seq[i % len(seq)]
                    if p > 127:
                        raise SpecError(f"Arp in clip {name!r} exceeds MIDI range")
                    clip.notes.append(Note(p, start + t, min(rate * float(cfg.get("gate", 0.9)), dur - t), velocity))
                    t += rate
                    i += 1
            else:
                raise SpecError(f"Clip {name!r}: unknown chord style {style!r} (pad|stabs|arp|bass)")

    elif "drums" in cfg:
        voices = cfg["drums"]
        if not isinstance(voices, dict) or not voices:
            raise SpecError(f"Clip {name!r}: drums must map voice -> step pattern")
        pattern_bars = int(cfg.get("pattern_bars", 1))
        for voice, pattern in voices.items():
            pitch = GM_DRUMS.get(voice) if not isinstance(voice, int) else voice
            if pitch is None:
                try:
                    pitch = theory.note_to_midi(voice)
                except ValueError:
                    raise SpecError(f"Unknown drum voice {voice!r}; use {sorted(GM_DRUMS)} or a note/int") from None
            for s, d, v in _step_events(pattern, beats_per_bar, bars, pattern_bars):
                clip.notes.append(Note(pitch, s, min(d, 0.25), round(v * velocity / 112)))

    elif "melody" in cfg:
        t = 0.0
        tokens = cfg["melody"].split() if isinstance(cfg["melody"], str) else cfg["melody"]
        repeat = bool(cfg.get("repeat", False))
        while True:
            for tok in tokens:
                pitch_s, _, dur_s = str(tok).partition(":")
                dur = float(dur_s) if dur_s else 1.0
                if t >= length - 1e-9:
                    break
                if pitch_s.lower() not in ("r", "rest"):
                    clip.notes.append(Note(theory.note_to_midi(pitch_s), t, min(dur, length - t), velocity))
                t += dur
            if not repeat or t >= length - 1e-9 or t == 0:
                break

    elif "notes" in cfg:
        for raw in cfg["notes"]:
            if isinstance(raw, dict):
                pitch, start, dur, vel = raw["pitch"], raw["start"], raw.get("duration", 1), raw.get("velocity", velocity)
            else:
                pitch, start, dur, *rest = raw
                vel = rest[0] if rest else velocity
            clip.notes.append(Note(theory.note_to_midi(pitch), float(start), float(dur), int(vel)))

    _humanize(clip.notes, int(cfg.get("humanize", 0)), rng)

    for number, points in (cfg.get("cc") or {}).items():
        number = int(number)
        if not 0 <= number <= 127:
            raise SpecError(f"CC number out of range: {number}")
        pts = sorted((float(b), int(v)) for b, v in points)
        for b, v in pts:
            if not 0 <= v <= 127 or not 0 <= b <= length:
                raise SpecError(f"CC{number} point ({b}, {v}) out of range in clip {name!r}")
        clip.cc[number] = pts

    for n in clip.notes:
        if not 0 <= n.pitch <= 127 or not 1 <= n.velocity <= 127 or n.duration <= 0 or n.start < 0:
            raise SpecError(f"Invalid note {n} in clip {name!r}")
        if n.start >= length:
            raise SpecError(f"Note starts after clip end in {name!r}: {n}")
    clip.notes.sort(key=lambda n: (n.start, n.pitch))
    return clip


# --------------------------------------------------------------------------- loading

def load_spec(source: str | Path | dict[str, Any]) -> Song:
    if isinstance(source, dict):
        data = source
    else:
        path = Path(source)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            data = json.loads(text)
        else:
            import yaml  # PyYAML; only needed for YAML specs
            data = yaml.safe_load(text)
    return parse_spec(data)


def parse_spec(data: dict[str, Any]) -> Song:
    if not isinstance(data, dict):
        raise SpecError("Spec root must be a mapping")
    tempo = float(data.get("tempo", 120))
    if not 20 <= tempo <= 999:
        raise SpecError(f"Tempo out of Live's range 20-999: {tempo}")
    sig = data.get("time_signature", [4, 4])
    numerator, denominator = int(sig[0]), int(sig[1])
    if denominator not in (1, 2, 4, 8, 16) or not 1 <= numerator <= 99:
        raise SpecError(f"Invalid time signature {sig}")
    key = data.get("key")
    if key:
        theory.parse_key(key)
    seed = int(data.get("seed", 2026))
    beats_per_bar = numerator * 4 / denominator

    tracks: list[Track] = []
    for i, t in enumerate(data.get("tracks") or []):
        if "name" not in t:
            raise SpecError(f"Track #{i} has no name")
        kind = t.get("type", "midi")
        if kind not in ("midi", "audio"):
            raise SpecError(f"Track {t['name']!r}: type must be midi or audio")
        drum = bool(t.get("drums", False))
        # Melodic tracks skip channel 10 (index 9), which GM reserves for drums.
        channel = int(t.get("channel", 9 if drum else min(i if i < 9 else i + 1, 15)))
        if not 0 <= channel <= 15:
            raise SpecError(f"Track {t['name']!r}: channel must be 0..15")
        vol, pan = t.get("volume"), t.get("pan")
        if vol is not None and not 0 <= float(vol) <= 1:
            raise SpecError(f"Track {t['name']!r}: volume must be 0..1")
        if pan is not None and not -1 <= float(pan) <= 1:
            raise SpecError(f"Track {t['name']!r}: pan must be -1..1")
        tracks.append(Track(t["name"], kind, parse_color(t.get("color")),
                            None if vol is None else float(vol), None if pan is None else float(pan),
                            channel, t.get("instrument")))
    names = [t.name for t in tracks]
    if len(set(names)) != len(names):
        raise SpecError("Track names must be unique")
    drum_tracks = {t["name"] for t in data.get("tracks") or [] if t.get("drums")}

    scenes: list[Scene] = []
    for si, s in enumerate(data.get("scenes") or []):
        if "name" not in s:
            raise SpecError(f"Scene #{si} has no name")
        bars = int(s.get("bars", 8))
        if bars <= 0:
            raise SpecError(f"Scene {s['name']!r}: bars must be > 0")
        scene = Scene(s["name"], bars, tempo=s.get("tempo"), color=parse_color(s.get("color")))
        for track_name, cfg in (s.get("clips") or {}).items():
            if track_name not in names:
                raise SpecError(f"Scene {s['name']!r} references unknown track {track_name!r}")
            if tracks[names.index(track_name)].kind != "midi":
                raise SpecError(f"Scene {s['name']!r}: cannot generate notes on audio track {track_name!r}")
            scene.clips[track_name] = build_clip(
                cfg or {}, name=f"{s['name']} - {track_name}", bars=bars, beats_per_bar=beats_per_bar,
                key=key, is_drum=track_name in drum_tracks, seed=seed + si * 101 + names.index(track_name))
        scenes.append(scene)
    scene_names = [s.name for s in scenes]
    if len(set(scene_names)) != len(scene_names):
        raise SpecError("Scene names must be unique")

    arrangement = list(data.get("arrangement") or scene_names)
    for name in arrangement:
        if name not in scene_names:
            raise SpecError(f"Arrangement references unknown scene {name!r}")

    show = list(data.get("show") or [])
    for cue in show:
        if not any(k in cue for k in ("fire_scene", "ramp", "stop", "tempo", "set")):
            raise SpecError(f"Show cue does nothing: {cue}")
        if "fire_scene" in cue and cue["fire_scene"] not in scene_names:
            raise SpecError(f"Show cue fires unknown scene {cue['fire_scene']!r}")
        ramp = cue.get("ramp")
        if ramp and ramp.get("track") is not None and ramp["track"] not in names:
            raise SpecError(f"Show ramp targets unknown track {ramp['track']!r}")

    return Song(data.get("title", "Untitled"), tempo, numerator, denominator, key,
                tracks, scenes, arrangement, show)
