"""In-process fake of the AbletonOSC remote script, for testing without Live."""
from __future__ import annotations

import socket
import threading
from typing import Any

from ilpc_ableton.osc import decode_message, encode_message


class FakeLive:
    def __init__(self, tracks: list[str] | None = None, scenes: int = 1):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self.tempo = 120.0
        self.signature = [4, 4]
        self.playing = False
        self.song_time = 0.0
        self.tracks: list[dict[str, Any]] = [self._new_track(n) for n in (tracks or [])]
        self.scenes: list[dict[str, Any]] = [{"name": ""} for _ in range(scenes)]
        self.clips: dict[tuple[int, int], dict[str, Any]] = {}
        self.log: list[tuple[str, list[Any]]] = []
        self._running = True
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    @staticmethod
    def _new_track(name: str, kind: str = "midi") -> dict[str, Any]:
        return {"name": name, "kind": kind, "volume": 0.85, "panning": 0.0, "color": 0, "sends": [0.0],
                "devices": [{"name": "Drift", "params": ["Device On", "Filter Freq", "Resonance"],
                             "values": [1.0, 0.5, 0.2]}]}

    def close(self) -> None:
        self._running = False
        self.sock.close()

    def _serve(self) -> None:
        while self._running:
            try:
                data, addr = self.sock.recvfrom(65535)
            except OSError:
                return
            address, args = decode_message(data)
            self.log.append((address, args))
            try:
                reply = self.handle(address, args)
            except Exception as e:  # mimic AbletonOSC: report errors on /live/error
                reply = ("/live/error", [f"{type(e).__name__}: {e}"])
            if reply is not None:
                self.sock.sendto(encode_message(reply[0], reply[1]), addr)

    def sent(self, address: str) -> list[list[Any]]:
        return [a for addr, a in self.log if addr == address]

    def handle(self, a: str, args: list[Any]):
        T, S = self.tracks, self.scenes
        if a == "/live/test":
            return a, ["ok"]
        if a == "/live/song/get/tempo":
            return a, [float(self.tempo)]
        if a == "/live/song/set/tempo":
            self.tempo = float(args[0]); return None
        if a == "/live/song/set/signature_numerator":
            self.signature[0] = args[0]; return None
        if a == "/live/song/set/signature_denominator":
            self.signature[1] = args[0]; return None
        if a == "/live/song/get/is_playing":
            return a, [int(self.playing)]
        if a == "/live/song/get/current_song_time":
            return a, [float(self.song_time)]
        if a == "/live/song/start_playing":
            self.playing = True; return None
        if a == "/live/song/stop_playing":
            self.playing = False; return None
        if a == "/live/song/get/num_tracks":
            return a, [len(T)]
        if a == "/live/song/get/track_names":
            return a, [t["name"] for t in T]
        if a == "/live/song/get/num_scenes":
            return a, [len(S)]
        if a == "/live/song/create_midi_track":
            T.append(self._new_track(f"{len(T) + 1}-MIDI")); return None
        if a == "/live/song/create_audio_track":
            T.append(self._new_track(f"{len(T) + 1}-Audio", "audio")); return None
        if a == "/live/song/create_scene":
            S.append({"name": ""}); return None
        if a.startswith("/live/scene/"):
            i = args[0]
            if a == "/live/scene/get/name":
                return a, [i, S[i]["name"]]
            if a == "/live/scene/fire":
                S[i]["fired"] = S[i].get("fired", 0) + 1; return None
            if a.startswith("/live/scene/set/"):
                S[i][a.rsplit("/", 1)[1]] = args[1]; return None
        if a.startswith("/live/track/"):
            t = T[args[0]]
            prop = a.rsplit("/", 1)[1]
            if a == "/live/track/get/devices/name":
                return a, [args[0]] + [d["name"] for d in t["devices"]]
            if a == "/live/track/get/send":
                return a, [args[0], args[1], t["sends"][args[1]]]
            if a == "/live/track/set/send":
                t["sends"][args[1]] = args[2]; return None
            if "/get/" in a:
                return a, [args[0], t[prop]]
            if "/set/" in a:
                t[prop] = args[1]; return None
        if a.startswith("/live/device/"):
            dev = T[args[0]]["devices"][args[1]]
            if a == "/live/device/get/parameters/name":
                return a, [args[0], args[1]] + dev["params"]
            if a == "/live/device/get/parameter/value":
                return a, [args[0], args[1], args[2], dev["values"][args[2]]]
            if a == "/live/device/set/parameter/value":
                dev["values"][args[2]] = args[3]; return None
        if a.startswith("/live/clip_slot/"):
            key = (args[0], args[1])
            if key[0] >= len(T) or key[1] >= len(S):
                raise IndexError(f"slot {key} out of range")
            if a == "/live/clip_slot/get/has_clip":
                return a, [args[0], args[1], int(key in self.clips)]
            if a == "/live/clip_slot/create_clip":
                if key in self.clips:
                    raise RuntimeError("Clip slot already has a clip")
                self.clips[key] = {"length": args[2], "notes": [], "name": ""}; return None
            if a == "/live/clip_slot/delete_clip":
                del self.clips[key]; return None
        if a.startswith("/live/clip/"):
            clip = self.clips[(args[0], args[1])]
            if a == "/live/clip/add/notes":
                rest = args[2:]
                if len(rest) % 5:
                    raise ValueError("notes must be 5-tuples")
                clip["notes"] += [tuple(rest[i:i + 5]) for i in range(0, len(rest), 5)]
                return None
            if "/set/" in a:
                clip[a.rsplit("/", 1)[1]] = args[2]; return None
        raise NotImplementedError(a)
