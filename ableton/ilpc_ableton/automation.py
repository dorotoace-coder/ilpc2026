"""Real-time automation: beat-synced parameter ramps and show cue lists.

AbletonOSC cannot write automation envelopes, so we *perform* them: values are
streamed to Live at `rate_hz` on a tempo-derived clock. Arm Arrangement record
(Live's Automation Arm) and Live captures the moves as real automation.

Cue list format (YAML, under `show:` in a spec or a standalone file):

    - bar: 1
      fire_scene: Walk-in
    - bar: 1
      ramp: {target: volume, track: Pad, from: 0.0, to: 0.85, bars: 8, curve: s}
    - bar: 17
      ramp: {target: device, track: Pad, device: 0, param: Filter Freq, to: 0.9, bars: 4}
    - bar: 33
      set: {target: send, track: Keys, send: 0, value: 0.4}
    - bar: 41
      tempo: 76
    - bar: 49
      stop: true
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Callable

from .live import AbletonClient

CURVES: dict[str, Callable[[float], float]] = {
    "linear": lambda x: x,
    "exp": lambda x: x * x,             # slow start, fast end (fade-ins feel natural)
    "log": lambda x: math.sqrt(x),      # fast start, slow end (fade-outs)
    "s": lambda x: 0.5 - 0.5 * math.cos(math.pi * x),
    "hold": lambda x: 0.0 if x < 1 else 1.0,
}


def curve_value(start: float, end: float, progress: float, curve: str = "linear") -> float:
    if curve not in CURVES:
        raise ValueError(f"Unknown curve {curve!r}; choose from {sorted(CURVES)}")
    p = min(1.0, max(0.0, progress))
    return start + (end - start) * CURVES[curve](p)


@dataclass
class Target:
    """Resolved parameter: how to read and write it over OSC."""
    get_addr: str
    set_addr: str
    index: tuple[int, ...]
    low: float = 0.0
    high: float = 1.0

    def set(self, client: AbletonClient, value: float) -> None:
        client.send(self.set_addr, *self.index, float(min(self.high, max(self.low, value))))

    def get(self, client: AbletonClient) -> float:
        return float(client.query(self.get_addr, *self.index)[0])


def resolve_target(client: AbletonClient, cfg: dict[str, Any]) -> Target:
    kind = cfg.get("target", "volume")
    track = cfg.get("track")
    if track is None:
        raise ValueError(f"Automation target needs a track: {cfg}")
    t = client.track_index(track) if isinstance(track, str) else int(track)
    if kind == "volume":
        return Target("/live/track/get/volume", "/live/track/set/volume", (t,))
    if kind == "pan":
        return Target("/live/track/get/panning", "/live/track/set/panning", (t,), -1.0, 1.0)
    if kind == "send":
        return Target("/live/track/get/send", "/live/track/set/send", (t, int(cfg.get("send", 0))))
    if kind == "device":
        d = client.device_index(t, cfg.get("device", 0))
        p = client.device_param_index(t, d, cfg["param"])
        low = float(cfg.get("min", 0.0))
        high = float(cfg.get("max", 1.0))
        return Target("/live/device/get/parameter/value", "/live/device/set/parameter/value", (t, d, p), low, high)
    raise ValueError(f"Unknown automation target {kind!r} (volume|pan|send|device)")


@dataclass
class _ActiveRamp:
    target: Target
    start_value: float
    end_value: float
    start_beat: float
    beats: float
    curve: str
    last_sent: float | None = None


class ShowRunner:
    """Single-threaded scheduler: fires cues on time and advances all active ramps.

    Time base is beats derived from wall clock and the current tempo, so tempo
    cues bend the clock correctly. `clock`/`sleep` are injectable for tests.
    """

    def __init__(self, client: AbletonClient, cues: list[dict[str, Any]], *, tempo: float,
                 beats_per_bar: float = 4.0, rate_hz: float = 30.0,
                 clock: Callable[[], float] = time.monotonic, sleep: Callable[[float], None] = time.sleep,
                 log: Callable[[str], None] = print):
        self.client = client
        self.tempo = float(tempo)
        self.bpb = beats_per_bar
        self.rate = rate_hz
        self.clock, self.sleep, self.log = clock, sleep, log
        self.cues = sorted((self._cue_beat(c), i, c) for i, c in enumerate(cues))
        self.ramps: list[_ActiveRamp] = []

    def _cue_beat(self, cue: dict[str, Any]) -> float:
        if "beat" in cue:
            return float(cue["beat"])
        return (float(cue.get("bar", 1)) - 1) * self.bpb

    def _length_beats(self, cfg: dict[str, Any]) -> float:
        if "beats" in cfg:
            return float(cfg["beats"])
        return float(cfg.get("bars", 1)) * self.bpb

    def _fire(self, beat: float, cue: dict[str, Any]) -> bool:
        c = self.client
        if "tempo" in cue:
            c.set_tempo(float(cue["tempo"]))
            self.tempo = float(cue["tempo"])
            self.log(f"[{beat:7.2f}] tempo -> {self.tempo:g}")
        if "fire_scene" in cue:
            idx = c.fire_scene(cue["fire_scene"])
            self.log(f"[{beat:7.2f}] fire scene {cue['fire_scene']!r} (#{idx})")
        if "set" in cue:
            target = resolve_target(c, cue["set"])
            target.set(c, float(cue["set"]["value"]))
            self.log(f"[{beat:7.2f}] set {cue['set'].get('target', 'volume')} {cue['set'].get('track')} = {cue['set']['value']}")
        if "ramp" in cue:
            cfg = cue["ramp"]
            target = resolve_target(c, cfg)
            start = float(cfg["from"]) if "from" in cfg else target.get(c)
            r = _ActiveRamp(target, start, float(cfg["to"]), beat, self._length_beats(cfg), cfg.get("curve", "linear"))
            if r.beats <= 0:
                raise ValueError(f"Ramp length must be > 0: {cfg}")
            curve_value(0, 1, 0, r.curve)  # validate curve name now
            r.target.set(c, start)
            r.last_sent = start
            self.ramps.append(r)
            self.log(f"[{beat:7.2f}] ramp {cfg.get('target', 'volume')} {cfg.get('track')} {start:.3f} -> {r.end_value:.3f} over {r.beats:g} beats ({r.curve})")
        if cue.get("stop"):
            c.stop()
            self.log(f"[{beat:7.2f}] stop")
            return True
        return False

    def _advance_ramps(self, beat: float) -> None:
        still = []
        for r in self.ramps:
            progress = (beat - r.start_beat) / r.beats
            value = curve_value(r.start_value, r.end_value, progress, r.curve)
            if r.last_sent is None or abs(value - r.last_sent) > 1e-4 or progress >= 1:
                r.target.set(self.client, value)
                r.last_sent = value
            if progress < 1:
                still.append(r)
        self.ramps = still

    def run(self, start_beat: float = 0.0) -> None:
        """Run until the last cue has fired and every ramp has finished."""
        t_prev = self.clock()
        beat = start_beat
        pending = [c for c in self.cues if c[0] >= start_beat - 1e-9]
        while pending or self.ramps:
            while pending and pending[0][0] <= beat + 1e-9:
                cue_beat, _, cue = pending.pop(0)
                if self._fire(cue_beat, cue):
                    pending.clear()
                    self.ramps.clear()
                    self.client.barrier()
                    return
            self._advance_ramps(beat)
            if not pending and not self.ramps:
                break
            self.sleep(1.0 / self.rate)
            now = self.clock()
            beat += (now - t_prev) * self.tempo / 60.0
            t_prev = now
        self.client.barrier()  # confirm Live processed every command before returning
