import pytest

from ilpc_ableton.automation import ShowRunner, curve_value
from ilpc_ableton.live import AbletonError, AbletonTimeout, AbletonClient, apply_song
from ilpc_ableton.spec import load_spec, parse_spec


def test_ping_and_status(client, live):
    assert client.ping()
    st = client.status()
    assert st["tracks"] == ["Drums", "Bass"] and st["tempo"] == 120.0


def test_timeout_when_live_absent():
    c = AbletonClient("127.0.0.1", 9, recv_port=0, timeout=0.2, bind_host="127.0.0.1")
    try:
        assert c.ping() is False
        with pytest.raises(AbletonTimeout):
            c.query("/live/song/get/tempo")
    finally:
        c.close()


def test_apply_example(client, live, example_path):
    song = load_spec(example_path)
    res = apply_song(client, song, log=lambda _m: None)
    names = [t["name"] for t in live.tracks]
    assert names == ["Drums", "Bass", "Keys", "Pad", "Arp", "Lead"]  # existing reused, rest created
    assert res.created_tracks == ["Keys", "Pad", "Arp", "Lead"]
    assert live.tempo == 98.0 and live.signature == [4, 4]
    assert [s["name"] for s in live.scenes] == ["Walk-in", "Groove", "Breakdown", "Countdown"]
    pad_t, groove_s = names.index("Pad"), res.scene_index["Groove"]
    clip = live.clips[(pad_t, groove_s)]
    expected = song.scene("Groove").clips["Pad"]
    assert clip["length"] == expected.length
    assert len(clip["notes"]) == len(expected.notes)
    assert clip["notes"][0] == (expected.notes[0].pitch, expected.notes[0].start, expected.notes[0].duration,
                                expected.notes[0].velocity, False)
    assert res.notes_written == sum(len(c["notes"]) for c in live.clips.values())
    assert live.tracks[names.index("Keys")]["panning"] == pytest.approx(-0.15)
    # big clips are split into several packets
    assert len(live.sent("/live/clip/add/notes")) > res.clips_written


def test_apply_is_idempotent(client, live, example_path):
    song = load_spec(example_path)
    apply_song(client, song, log=lambda _m: None)
    first = {k: list(v["notes"]) for k, v in live.clips.items()}
    apply_song(client, song, log=lambda _m: None)
    assert len(live.tracks) == 6 and len(live.scenes) == 4
    assert {k: v["notes"] for k, v in live.clips.items()} == first


def test_keep_existing(client, live):
    song = parse_spec({"tracks": [{"name": "Bass"}], "scenes": [{"name": "A", "bars": 1, "clips": {"Bass": {"notes": [["C2", 0, 1]]}}}]})
    apply_song(client, song, first_scene=0, log=lambda _m: None)
    live.clips[(1, 0)]["notes"] = ["sentinel"]
    apply_song(client, song, first_scene=0, replace=False, log=lambda _m: None)
    assert live.clips[(1, 0)]["notes"] == ["sentinel"]


def test_errors_surface(client, live):
    client.send("/live/clip/set/name", 0, 5, "x")  # no such clip -> /live/error
    with pytest.raises(AbletonError):
        client.barrier()


def test_curves():
    assert curve_value(0, 1, 0.5, "linear") == 0.5
    assert curve_value(0, 1, 0.5, "exp") == 0.25
    assert curve_value(0, 1, 0.5, "s") == pytest.approx(0.5)
    assert curve_value(1, 0, 2.0, "log") == 0
    with pytest.raises(ValueError):
        curve_value(0, 1, 0.5, "zigzag")


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, dt):
        self.t += dt


def test_show_runner(client, live):
    clock = FakeClock()
    live.scenes = [{"name": "Intro"}, {"name": "Main"}]
    cues = [
        {"bar": 1, "fire_scene": "Intro"},
        {"bar": 1, "ramp": {"target": "volume", "track": "Bass", "from": 0.0, "to": 0.8, "bars": 2, "curve": "linear"}},
        {"bar": 2, "ramp": {"target": "device", "track": "Drums", "device": "Drift", "param": "Filter Freq", "to": 1.0, "beats": 2}},
        {"bar": 3, "fire_scene": "Main"},
        {"bar": 3, "set": {"target": "send", "track": "Drums", "send": 0, "value": 0.4}},
        {"bar": 4, "tempo": 60},
        {"bar": 5, "stop": True},
    ]
    live.playing = True
    runner = ShowRunner(client, cues, tempo=120, beats_per_bar=4, rate_hz=50,
                        clock=clock, sleep=clock.sleep, log=lambda _m: None)
    runner.run()
    assert live.scenes[0]["fired"] == 1 and live.scenes[1]["fired"] == 1
    vols = [a[1] for a in live.sent("/live/track/set/volume") if a[0] == 1]
    assert vols[0] == 0.0 and vols[-1] == pytest.approx(0.8) and vols == sorted(vols)
    assert live.tracks[0]["devices"][0]["values"][1] == pytest.approx(1.0)
    assert live.tracks[0]["sends"][0] == pytest.approx(0.4)
    assert live.tempo == 60 and live.playing is False
    # bars 1-4 at 120 BPM = 6 s; bar 4->5 at 60 BPM = 4 s  => ~10 s
    assert 9.9 <= clock.t <= 10.1


def test_show_ramp_reads_current_value(client, live):
    clock = FakeClock()
    live.tracks[1]["volume"] = 0.5
    ShowRunner(client, [{"beat": 0, "ramp": {"target": "volume", "track": "Bass", "to": 0.0, "beats": 1}}],
               tempo=120, clock=clock, sleep=clock.sleep, log=lambda _m: None).run()
    vols = [a[1] for a in live.sent("/live/track/set/volume")]
    assert vols[0] == 0.5 and vols[-1] == 0.0
