"""Client for Ableton Live via the AbletonOSC remote script.

AbletonOSC listens on UDP 11000 and replies to the sender's IP on UDP 11001.
We bind our socket to 11001 and send from it, so replies always reach us.
Endpoint reference: https://github.com/ideoforms/AbletonOSC
"""
from __future__ import annotations

import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from .osc import OscArg, decode_packet, encode_message
from .spec import Song

NOTE_BATCH = 64  # notes per /live/clip/add/notes message (keeps UDP packets ~2 KB)


class AbletonError(RuntimeError):
    pass


class AbletonTimeout(AbletonError):
    pass


class AbletonClient:
    def __init__(self, host: str = "127.0.0.1", send_port: int = 11000, recv_port: int = 11001,
                 timeout: float = 2.0, bind_host: str = "0.0.0.0"):
        self.addr = (host, send_port)
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((bind_host, recv_port))
        self.errors: list[str] = []
        self._lock = threading.RLock()  # one request/reply exchange at a time

    # -- transport ---------------------------------------------------------
    def send(self, address: str, *args: OscArg) -> None:
        with self._lock:
            self.sock.sendto(encode_message(address, args), self.addr)

    def _drain(self) -> None:
        self.sock.setblocking(False)
        try:
            while True:
                data = self.sock.recv(65535)
                for addr, args in decode_packet(data):
                    if addr == "/live/error":
                        self.errors.append(" ".join(map(str, args)))
        except (BlockingIOError, OSError):
            pass
        finally:
            self.sock.setblocking(True)

    def query(self, address: str, *args: OscArg, timeout: float | None = None) -> list[Any]:
        """Send a get/query and wait for the reply on the same address.

        For indexed queries (track_id, ...) the reply echoes the indices, so we
        only accept replies whose leading args match ours, and strip them.
        """
        with self._lock:
            return self._query(address, args, timeout)

    def _query(self, address: str, args: tuple, timeout: float | None) -> list[Any]:
        self._drain()
        self.send(address, *args)
        deadline = time.monotonic() + (self.timeout if timeout is None else timeout)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AbletonTimeout(
                    f"No reply to {address} {list(args)} from {self.addr[0]}:{self.addr[1]}. "
                    "Is Live running with the AbletonOSC control surface enabled?")
            self.sock.settimeout(remaining)
            try:
                data = self.sock.recv(65535)
            except socket.timeout:
                continue
            for addr, reply in decode_packet(data):
                if addr == "/live/error":
                    raise AbletonError(f"Ableton error after {address}: {' '.join(map(str, reply))}")
                if addr != address:
                    continue
                n = len(args)
                if n and list(reply[:n]) != list(args):
                    continue
                return list(reply[n:])

    def barrier(self) -> None:
        """Round-trip to make sure every previously sent command was processed."""
        self.query("/live/song/get/tempo", timeout=max(self.timeout, 5.0))
        self._drain()
        if self.errors:
            errs, self.errors = self.errors, []
            raise AbletonError("Ableton reported errors: " + " | ".join(errs))

    def close(self) -> None:
        self.sock.close()

    def __enter__(self) -> "AbletonClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- high-level helpers ------------------------------------------------
    def ping(self) -> bool:
        try:
            return self.query("/live/test", timeout=1.0) == ["ok"]
        except AbletonTimeout:
            return False

    def status(self) -> dict[str, Any]:
        return {
            "tempo": self.query("/live/song/get/tempo")[0],
            "is_playing": bool(self.query("/live/song/get/is_playing")[0]),
            "song_time": self.query("/live/song/get/current_song_time")[0],
            "tracks": self.track_names(),
            "scenes": self.scene_names(),
        }

    def track_names(self) -> list[str]:
        num = int(self.query("/live/song/get/num_tracks")[0])
        return [str(n) for n in self.query("/live/song/get/track_names")][:num] if num else []

    def scene_names(self) -> list[str]:
        num = int(self.query("/live/song/get/num_scenes")[0])
        return [str(self.query("/live/scene/get/name", i)[0]) for i in range(num)]

    def track_index(self, name: str) -> int:
        names = self.track_names()
        if name not in names:
            raise AbletonError(f"No track named {name!r} in Live set (have: {names})")
        return names.index(name)

    def scene_index(self, name_or_index: str | int) -> int:
        if isinstance(name_or_index, int):
            return name_or_index
        names = self.scene_names()
        if name_or_index not in names:
            raise AbletonError(f"No scene named {name_or_index!r} (have: {names})")
        return names.index(name_or_index)

    def device_param_index(self, track: int, device: int, param: str | int) -> int:
        if isinstance(param, int):
            return param
        names = [str(n) for n in self.query("/live/device/get/parameters/name", track, device)]
        if param not in names:
            raise AbletonError(f"Device {device} on track {track} has no parameter {param!r} (have: {names})")
        return names.index(param)

    def device_index(self, track: int, device: str | int) -> int:
        if isinstance(device, int):
            return device
        names = [str(n) for n in self.query("/live/track/get/devices/name", track)]
        if device not in names:
            raise AbletonError(f"Track {track} has no device {device!r} (have: {names})")
        return names.index(device)

    def play(self) -> None:
        self.send("/live/song/start_playing")

    def stop(self) -> None:
        self.send("/live/song/stop_playing")

    def fire_scene(self, scene: str | int) -> int:
        idx = self.scene_index(scene)
        self.send("/live/scene/fire", idx)
        return idx

    def set_tempo(self, bpm: float) -> None:
        if not 20 <= bpm <= 999:
            raise ValueError("Tempo must be 20-999 BPM")
        self.send("/live/song/set/tempo", float(bpm))

    def add_notes(self, track: int, slot: int, notes: list) -> None:
        for i in range(0, len(notes), NOTE_BATCH):
            args: list[OscArg] = [track, slot]
            for n in notes[i:i + NOTE_BATCH]:
                args += [int(n.pitch), float(n.start), float(n.duration), int(n.velocity), bool(n.mute)]
            self.send("/live/clip/add/notes", *args)


@dataclass
class ApplyResult:
    track_index: dict[str, int] = field(default_factory=dict)
    scene_index: dict[str, int] = field(default_factory=dict)
    created_tracks: list[str] = field(default_factory=list)
    clips_written: int = 0
    notes_written: int = 0


def apply_song(client: AbletonClient, song: Song, *, first_scene: int | None = None,
               replace: bool = True, log: Callable[[str], None] = print) -> ApplyResult:
    """Build the song in Live's Session view.

    - Tracks are matched by name; missing ones are created (MIDI/audio) at the end.
      Keep a template set with your instruments on named tracks and only the
      clips get rewritten — your sound design is never touched.
    - Scenes are written starting at `first_scene`. By default a scene with the
      same name is reused, else the first unnamed scene, else one is appended.
    """
    result = ApplyResult()
    client.set_tempo(song.tempo)
    client.send("/live/song/set/signature_numerator", song.numerator)
    client.send("/live/song/set/signature_denominator", song.denominator)

    existing = client.track_names()
    for track in song.tracks:
        if track.name in existing:
            idx = existing.index(track.name)
        else:
            client.send("/live/song/create_midi_track" if track.kind == "midi" else "/live/song/create_audio_track", -1)
            client.barrier()
            idx = len(existing)
            existing.append(track.name)
            client.send("/live/track/set/name", idx, track.name)
            result.created_tracks.append(track.name)
            log(f"+ track {track.name!r} ({track.kind}) at {idx}" +
                (f"  -> load: {track.instrument}" if track.instrument else ""))
        result.track_index[track.name] = idx
        if track.color is not None:
            client.send("/live/track/set/color", idx, track.color)
        if track.volume is not None:
            client.send("/live/track/set/volume", idx, float(track.volume))
        if track.pan is not None:
            client.send("/live/track/set/panning", idx, float(track.pan))
    client.barrier()

    scene_names = client.scene_names()
    for i, scene in enumerate(song.scenes):
        if first_scene is not None:
            idx = first_scene + i
        elif scene.name in scene_names:
            idx = scene_names.index(scene.name)
        elif "" in scene_names:
            idx = scene_names.index("")  # reuse empty, unnamed scenes (a new Live set has 8)
        else:
            idx = len(scene_names)
            scene_names.append(scene.name)
        while idx >= int(client.query("/live/song/get/num_scenes")[0]):
            client.send("/live/song/create_scene", -1)
            client.barrier()
        if idx >= len(scene_names):
            scene_names.extend([""] * (idx + 1 - len(scene_names)))
        scene_names[idx] = scene.name
        result.scene_index[scene.name] = idx
        client.send("/live/scene/set/name", idx, scene.name)
        if scene.color is not None:
            client.send("/live/scene/set/color", idx, scene.color)
        if scene.tempo:
            client.send("/live/scene/set/tempo", idx, float(scene.tempo))
            client.send("/live/scene/set/tempo_enabled", idx, 1)

        for track_name, clip in scene.clips.items():
            t = result.track_index[track_name]
            has_clip = bool(client.query("/live/clip_slot/get/has_clip", t, idx)[0])
            if has_clip:
                if not replace:
                    log(f"= keep existing clip {track_name}/{scene.name}")
                    continue
                client.send("/live/clip_slot/delete_clip", t, idx)
            client.send("/live/clip_slot/create_clip", t, idx, float(clip.length))
            client.barrier()
            client.send("/live/clip/set/name", t, idx, clip.name)
            if clip.color is not None:
                client.send("/live/clip/set/color", t, idx, clip.color)
            client.add_notes(t, idx, clip.notes)
            result.clips_written += 1
            result.notes_written += len(clip.notes)
            log(f"~ clip {track_name}/{scene.name}: {len(clip.notes)} notes, {clip.length:g} beats"
                + (f" (CC lanes {sorted(clip.cc)} -> use MIDI export)" if clip.cc else ""))
        client.barrier()
    return result
