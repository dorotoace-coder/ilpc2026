"""Standard MIDI File (format 1) export, stdlib only.

Ableton Live imports multi-track .mid files by drag-and-drop (one track per
MIDI track). Clip CC lanes are written as Control Change events so they can be
mapped to any parameter in Live (or converted to automation via MIDI Map).
"""
from __future__ import annotations

import struct
from pathlib import Path

from .spec import Clip, Song

PPQ = 480


def _vlq(value: int) -> bytes:
    if value < 0:
        raise ValueError("Negative delta time")
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(out))


def _meta(kind: int, data: bytes) -> bytes:
    return bytes([0xFF, kind]) + _vlq(len(data)) + data


def _chunk(events: list[tuple[int, int, bytes]]) -> bytes:
    """events: (abs_tick, order, raw_bytes). Order breaks ties (note-offs before note-ons)."""
    events.sort(key=lambda e: (e[0], e[1]))
    body, last = b"", 0
    for tick, _, raw in events:
        body += _vlq(tick - last) + raw
        last = tick
    body += _vlq(0) + _meta(0x2F, b"")
    return b"MTrk" + struct.pack(">I", len(body)) + body


def _ticks(beats: float) -> int:
    return int(round(beats * PPQ))


def _clip_events(clip: Clip, offset_beats: float, channel: int) -> list[tuple[int, int, bytes]]:
    events = []
    clip_end = offset_beats + clip.length
    for n in clip.notes:
        if n.mute:
            continue
        on = _ticks(offset_beats + n.start)
        off = _ticks(min(offset_beats + n.start + n.duration, clip_end))
        if off <= on:
            off = on + 1
        events.append((on, 2, bytes([0x90 | channel, n.pitch, n.velocity])))
        events.append((off, 0, bytes([0x80 | channel, n.pitch, 0])))
    for number, points in clip.cc.items():
        for beat, value in interpolate_cc(points, step=0.25):
            events.append((_ticks(offset_beats + beat), 1, bytes([0xB0 | channel, number, value])))
    return events


def interpolate_cc(points: list[tuple[float, int]], step: float = 0.25) -> list[tuple[float, int]]:
    """Linear ramp between breakpoints at `step` beat resolution, deduplicating values."""
    if not points:
        return []
    out: list[tuple[float, int]] = []
    for (b0, v0), (b1, v1) in zip(points, points[1:]):
        t = b0
        while t < b1 - 1e-9:
            v = round(v0 + (v1 - v0) * (t - b0) / (b1 - b0))
            if not out or out[-1][1] != v:
                out.append((round(t, 6), v))
            t += step
    last_b, last_v = points[-1]
    if not out or out[-1][1] != last_v:
        out.append((last_b, last_v))
    return out


def song_to_midi(song: Song, scenes: list[str] | None = None) -> bytes:
    """Render the arrangement (scenes back-to-back) into a format-1 SMF."""
    order = scenes or song.arrangement
    bpb = song.beats_per_bar

    conductor: list[tuple[int, int, bytes]] = [
        (0, 0, _meta(0x03, song.title.encode("utf-8"))),
        (0, 0, _meta(0x58, bytes([song.numerator, song.denominator.bit_length() - 1, 24, 8]))),
        (0, 0, _meta(0x51, (round(60_000_000 / song.tempo)).to_bytes(3, "big"))),
    ]
    t = 0.0
    for name in order:
        scene = song.scene(name)
        conductor.append((_ticks(t), 1, _meta(0x06, scene.name.encode("utf-8"))))  # marker
        if scene.tempo:
            conductor.append((_ticks(t), 1, _meta(0x51, round(60_000_000 / float(scene.tempo)).to_bytes(3, "big"))))
        t += scene.bars * bpb

    chunks = [_chunk(conductor)]
    for track in song.tracks:
        if track.kind != "midi":
            continue
        events: list[tuple[int, int, bytes]] = [(0, 0, _meta(0x03, track.name.encode("utf-8")))]
        t = 0.0
        for name in order:
            scene = song.scene(name)
            clip = scene.clips.get(track.name)
            if clip:
                events.extend(_clip_events(clip, t, track.channel))
            t += scene.bars * bpb
        chunks.append(_chunk(events))

    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), PPQ)
    return header + b"".join(chunks)


def write_midi(song: Song, out_dir: str | Path, split: bool = False) -> list[Path]:
    """Write the full arrangement (and optionally one .mid per scene/track clip)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    slug = "".join(c if c.isalnum() else "-" for c in song.title.lower()).strip("-") or "song"
    written = [out / f"{slug}.mid"]
    written[0].write_bytes(song_to_midi(song))
    if split:
        for scene in song.scenes:
            for track_name, clip in scene.clips.items():
                single = Song(song.title, scene.tempo or song.tempo, song.numerator, song.denominator, song.key,
                              [song.track(track_name)], [scene], [scene.name], [])
                path = out / f"{slug}__{_safe(scene.name)}__{_safe(track_name)}.mid"
                path.write_bytes(song_to_midi(single))
                written.append(path)
    return written


def _safe(name: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")
