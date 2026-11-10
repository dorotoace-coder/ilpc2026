"""MCP server so Claude (Desktop / Code) can produce music in Ableton Live.

Register with Claude Code:
    claude mcp add ableton -- python -m ilpc_ableton.mcp_server
Works with the MCP Python SDK v1 (FastMCP) and v2 (MCPServer).
"""
from __future__ import annotations

import functools
import os
import threading
from typing import Any, Callable, TypeVar

import yaml

try:  # MCP SDK v2
    from mcp.server.mcpserver import MCPServer as _Server
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:  # MCP SDK v1
    from mcp.server.fastmcp import FastMCP as _Server
    from mcp.server.fastmcp.exceptions import ToolError

from .automation import ShowRunner
from .live import AbletonClient, AbletonError, apply_song
from .midi import write_midi
from .spec import parse_spec

_server = _Server("ableton")
_F = TypeVar("_F", bound=Callable[..., Any])


class _Tools:
    """Registers tools and turns anticipated failures into ToolError, so the
    model sees the real message (bad spec, Live unreachable) instead of a
    generic crash notice."""

    def tool(self, **kwargs: Any) -> Callable[[_F], _F]:
        def decorate(fn: _F) -> _F:
            @functools.wraps(fn)
            def wrapper(*args: Any, **kw: Any) -> Any:
                try:
                    return fn(*args, **kw)
                except (ValueError, TypeError, KeyError, AbletonError, yaml.YAMLError) as e:
                    raise ToolError(str(e)) from e
            _server.tool(**kwargs)(wrapper)
            return fn
        return decorate

    def run(self) -> None:
        _server.run()


mcp = _Tools()
_lock = threading.Lock()
_client: AbletonClient | None = None
_show: threading.Thread | None = None


def client() -> AbletonClient:
    global _client
    if _client is None:
        _client = AbletonClient(os.environ.get("ABLETON_HOST", "127.0.0.1"),
                                int(os.environ.get("ABLETON_PORT", 11000)),
                                int(os.environ.get("ABLETON_REPLY_PORT", 11001)))
    return _client


SPEC_HELP = """Spec is YAML: title, tempo, time_signature [4,4], key, tracks [{name, type midi|audio,
drums bool, color '#RRGGBB', volume 0-1, pan -1..1, instrument}], scenes [{name, bars, clips:
{TrackName: {chords: 'Dmaj7 Bm7:2 G', style pad|stabs|arp|bass, octave, rhythm 'x.x.', rate}
| {drums: {kick: 'x...x...', hat: '.x.x'}} | {melody: 'F#5:1 A5:0.5 r:0.5'} | {notes: [[pitch,start,dur,vel]]},
cc: {74: [[beat, value], ...]}}}], arrangement [scene names], show [cues]."""


@mcp.tool()
def ableton_status() -> dict[str, Any]:
    """Check the connection to Ableton Live and return tempo, transport, track and scene names."""
    with _lock:
        c = client()
        if not c.ping():
            return {"connected": False, "hint": "Enable AbletonOSC in Live: Settings (Live 11: Preferences) > Link, Tempo & MIDI > Control Surface."}
        return {"connected": True, **c.status()}


@mcp.tool(description="Validate a YAML song spec and build it in Live's Session view (tracks matched by name, "
                      "clips written into scenes). " + SPEC_HELP)
def apply_spec(spec_yaml: str, first_scene: int | None = None, replace_existing: bool = True) -> dict[str, Any]:
    song = parse_spec(yaml.safe_load(spec_yaml))
    logs: list[str] = []
    with _lock:
        res = apply_song(client(), song, first_scene=first_scene, replace=replace_existing, log=logs.append)
    return {"clips": res.clips_written, "notes": res.notes_written, "created_tracks": res.created_tracks,
            "scenes": res.scene_index, "log": logs}


@mcp.tool(description="Render a YAML song spec to Standard MIDI Files (drag into Live). " + SPEC_HELP)
def render_midi(spec_yaml: str, out_dir: str = "dist", split_clips: bool = False) -> list[str]:
    song = parse_spec(yaml.safe_load(spec_yaml))
    return [str(p) for p in write_midi(song, out_dir, split=split_clips)]


@mcp.tool()
def transport(action: str, value: str | None = None) -> str:
    """Control Live: action = play | stop | tempo (value=BPM) | scene (value=scene name or index)."""
    with _lock:
        c = client()
        if action == "play":
            c.play()
        elif action == "stop":
            c.stop()
        elif action == "tempo":
            c.set_tempo(float(value))
        elif action == "scene":
            idx = c.fire_scene(int(value) if value and value.isdigit() else value)
            value = f"{value} (#{idx})"
        else:
            raise ValueError("action must be play|stop|tempo|scene")
        c.barrier()
    return f"{action} {value or ''}".strip()


@mcp.tool()
def automate(target: str, track: str, to: float, bars: float = 4, start: float | None = None,
             curve: str = "linear", device: str = "0", param: str = "0", send: int = 0) -> str:
    """Perform a tempo-synced automation ramp now. target = volume | pan | send | device.
    For device: device/param are names or indices. curve = linear | exp | log | s | hold.
    Values are Live's normalized ranges (volume 0-1 where 0.85 = 0 dB, pan -1..1)."""
    cfg: dict[str, Any] = {"target": target, "track": track, "to": to, "bars": bars, "curve": curve, "send": send,
                           "device": int(device) if device.isdigit() else device,
                           "param": int(param) if param.isdigit() else param}
    if start is not None:
        cfg["from"] = start
    with _lock:
        c = client()
        tempo = float(c.query("/live/song/get/tempo")[0])
        ShowRunner(c, [{"beat": 0, "ramp": cfg}], tempo=tempo, log=lambda _m: None).run()
    return f"ramped {target} on {track} to {to} over {bars} bars"


@mcp.tool(description="Start a show cue list in the background (scene launches, ramps, tempo changes, stop). "
                      "cues_yaml is a YAML list like [{bar: 1, fire_scene: Intro}, {bar: 1, ramp: {target: volume, "
                      "track: Pad, from: 0, to: 0.85, bars: 8}}, {bar: 33, stop: true}].")
def run_show(cues_yaml: str, play: bool = True, beats_per_bar: float = 4.0) -> str:
    global _show
    if _show and _show.is_alive():
        return "A show is already running."
    cues = yaml.safe_load(cues_yaml)
    if not isinstance(cues, list) or not cues:
        raise ValueError("cues_yaml must be a non-empty YAML list")

    def _run() -> None:
        with _lock:
            c = client()
            tempo = float(c.query("/live/song/get/tempo")[0])
            if play:
                c.play()
        ShowRunner(c, cues, tempo=tempo, beats_per_bar=beats_per_bar, log=lambda _m: None).run()

    _show = threading.Thread(target=_run, daemon=True)
    _show.start()
    return f"Show started with {len(cues)} cues."


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
