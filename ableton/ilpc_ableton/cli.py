"""Command line: python -m ilpc_ableton <command> ..."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .spec import SpecError, load_spec


def _client(args):
    from .live import AbletonClient
    return AbletonClient(args.host, args.port, args.reply_port, timeout=args.timeout)


def cmd_validate(args) -> int:
    song = load_spec(args.spec)
    print(f"OK  {song.title!r}  {song.tempo:g} BPM  {song.numerator}/{song.denominator}  key={song.key}")
    for t in song.tracks:
        print(f"  track  {t.name:<12} {t.kind:<5} ch{t.channel + 1:<3} {t.instrument or ''}")
    for s in song.scenes:
        clips = ", ".join(f"{k}({len(c.notes)})" for k, c in s.clips.items())
        print(f"  scene  {s.name:<12} {s.bars:>3} bars  {clips}")
    print(f"  arrangement: {' > '.join(song.arrangement)}   show cues: {len(song.show)}")
    return 0


def cmd_render(args) -> int:
    from .midi import write_midi
    song = load_spec(args.spec)
    for path in write_midi(song, args.out, split=args.split):
        print(f"wrote {path}  ({path.stat().st_size} bytes)")
    return 0


def cmd_ping(args) -> int:
    with _client(args) as c:
        ok = c.ping()
        print("Ableton Live reachable (AbletonOSC OK)" if ok else
              "No reply. Check: Live running, Settings (Live 11: Preferences) > Link, Tempo & MIDI > Control Surface = AbletonOSC, "
              "firewall allows UDP 11000/11001.")
        if ok and args.verbose:
            print(json.dumps(c.status(), indent=2))
        return 0 if ok else 1


def cmd_apply(args) -> int:
    from .live import apply_song
    song = load_spec(args.spec)
    with _client(args) as c:
        if not c.ping():
            print("Ableton not reachable — run `ping` for setup hints.", file=sys.stderr)
            return 1
        res = apply_song(c, song, first_scene=args.first_scene, replace=not args.keep_existing)
        print(f"Done: {res.clips_written} clips, {res.notes_written} notes, "
              f"new tracks: {res.created_tracks or 'none'}, scenes: {res.scene_index}")
    return 0


def cmd_show(args) -> int:
    import yaml
    from .automation import ShowRunner
    song = load_spec(args.spec)
    cues = song.show
    if args.cues:
        cues = yaml.safe_load(Path(args.cues).read_text(encoding="utf-8"))
    if not cues:
        print("No show cues found (add `show:` to the spec or pass --cues).", file=sys.stderr)
        return 1
    with _client(args) as c:
        if not c.ping():
            print("Ableton not reachable.", file=sys.stderr)
            return 1
        c.set_tempo(song.tempo)
        if args.play:
            c.play()
        ShowRunner(c, cues, tempo=song.tempo, beats_per_bar=song.beats_per_bar,
                   rate_hz=args.rate).run(start_beat=(args.from_bar - 1) * song.beats_per_bar)
    return 0


def cmd_transport(args) -> int:
    with _client(args) as c:
        if args.action == "play":
            c.play()
        elif args.action == "stop":
            c.stop()
        elif args.action == "tempo":
            c.set_tempo(float(args.value))
        elif args.action == "scene":
            value = int(args.value) if args.value.isdigit() else args.value
            print(f"fired scene #{c.fire_scene(value)}")
        c.barrier()
    return 0


def cmd_ramp(args) -> int:
    from .automation import ShowRunner
    cfg = {"target": args.target, "track": args.track, "to": args.to, "bars": args.bars, "curve": args.curve}
    if args.start is not None:
        cfg["from"] = args.start
    if args.target == "device":
        cfg.update(device=int(args.device) if args.device.isdigit() else args.device,
                   param=int(args.param) if args.param.isdigit() else args.param)
    if args.target == "send":
        cfg["send"] = args.send
    with _client(args) as c:
        tempo = float(c.query("/live/song/get/tempo")[0])
        ShowRunner(c, [{"beat": 0, "ramp": cfg}], tempo=tempo).run()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ilpc-ableton", description="Automate music production in Ableton Live.")
    p.add_argument("--host", default="127.0.0.1", help="machine running Ableton Live")
    p.add_argument("--port", type=int, default=11000, help="AbletonOSC listen port")
    p.add_argument("--reply-port", type=int, default=11001, help="AbletonOSC reply port")
    p.add_argument("--timeout", type=float, default=2.0)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("validate", help="check a spec and print what it will build")
    s.add_argument("spec"); s.set_defaults(func=cmd_validate)

    s = sub.add_parser("render", help="export the spec to .mid (no Live needed)")
    s.add_argument("spec"); s.add_argument("--out", default="dist")
    s.add_argument("--split", action="store_true", help="also write one .mid per clip")
    s.set_defaults(func=cmd_render)

    s = sub.add_parser("ping", help="check the connection to Live")
    s.add_argument("-v", "--verbose", action="store_true"); s.set_defaults(func=cmd_ping)

    s = sub.add_parser("apply", help="build tracks/scenes/clips in Live's Session view")
    s.add_argument("spec")
    s.add_argument("--first-scene", type=int, default=None, help="scene slot to start writing at")
    s.add_argument("--keep-existing", action="store_true", help="don't overwrite clips already in slots")
    s.set_defaults(func=cmd_apply)

    s = sub.add_parser("show", help="run the spec's show cue list (scene launches + automation)")
    s.add_argument("spec"); s.add_argument("--cues", help="separate YAML cue list")
    s.add_argument("--play", action="store_true", help="start Live's transport first")
    s.add_argument("--from-bar", type=float, default=1.0)
    s.add_argument("--rate", type=float, default=30.0, help="automation updates per second")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("transport", help="play | stop | tempo <bpm> | scene <name|index>")
    s.add_argument("action", choices=["play", "stop", "tempo", "scene"]); s.add_argument("value", nargs="?")
    s.set_defaults(func=cmd_transport)

    s = sub.add_parser("ramp", help="one-off automation ramp")
    s.add_argument("target", choices=["volume", "pan", "send", "device"])
    s.add_argument("track"); s.add_argument("to", type=float)
    s.add_argument("--from", dest="start", type=float); s.add_argument("--bars", type=float, default=4)
    s.add_argument("--curve", default="linear"); s.add_argument("--send", type=int, default=0)
    s.add_argument("--device", default="0"); s.add_argument("--param", default="0")
    s.set_defaults(func=cmd_ramp)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "transport" and args.action in ("tempo", "scene") and args.value is None:
        print(f"transport {args.action} needs a value", file=sys.stderr)
        return 2
    try:
        return args.func(args)
    except SpecError as e:
        print(f"Spec error: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130
    except Exception as e:  # surface Ableton/OSC errors cleanly
        from .live import AbletonError
        if isinstance(e, AbletonError):
            print(f"Ableton error: {e}", file=sys.stderr)
            return 1
        raise


if __name__ == "__main__":
    sys.exit(main())
