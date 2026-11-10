import struct

import pytest

from ilpc_ableton.midi import interpolate_cc, song_to_midi, write_midi
from ilpc_ableton.osc import decode_message, decode_packet, encode_message
from ilpc_ableton.spec import load_spec


def test_osc_roundtrip():
    args = [1, -2, 0.5, "Pad ✓", True, False, None, b"\x01\x02\x03"]
    addr, out = decode_message(encode_message("/live/x", args))
    assert addr == "/live/x"
    assert out == args
    assert len(encode_message("/a", [1])) % 4 == 0


def test_osc_rejects_bad_input():
    with pytest.raises(ValueError):
        encode_message("no-slash")
    with pytest.raises(ValueError):
        encode_message("/a", [2**40])
    with pytest.raises(TypeError):
        encode_message("/a", [object()])


def test_osc_bundle_decode():
    m1, m2 = encode_message("/a", [1]), encode_message("/b", ["x"])
    bundle = b"#bundle\x00" + b"\x00" * 8 + struct.pack(">i", len(m1)) + m1 + struct.pack(">i", len(m2)) + m2
    assert decode_packet(bundle) == [("/a", [1]), ("/b", ["x"])]


def test_matches_python_osc_reference():
    pythonosc = pytest.importorskip("pythonosc.osc_message_builder")
    b = pythonosc.OscMessageBuilder("/live/clip/add/notes")
    args = [0, 0, 60, 0.0, 1.5, 100, False]
    for a in args:
        b.add_arg(a)
    assert b.build().dgram == encode_message("/live/clip/add/notes", args)


def test_cc_interpolation():
    pts = interpolate_cc([(0, 0), (4, 127)], step=1)
    assert pts[0] == (0, 0) and pts[-1] == (4, 127)
    assert [v for _, v in pts] == sorted(v for _, v in pts)


def test_midi_structure(example_path, tmp_path):
    song = load_spec(example_path)
    data = song_to_midi(song)
    assert data[:4] == b"MThd"
    fmt, ntracks, ppq = struct.unpack(">HHH", data[8:14])
    assert (fmt, ntracks, ppq) == (1, 1 + len(song.tracks), 480)
    files = write_midi(song, tmp_path, split=True)
    assert files[0].name == "ilpc-2026-walk-in.mid"
    assert len(files) == 1 + sum(len(s.clips) for s in song.scenes)


def test_midi_reads_back_with_mido(example_path, tmp_path):
    mido = pytest.importorskip("mido")
    song = load_spec(example_path)
    path = write_midi(song, tmp_path)[0]
    mf = mido.MidiFile(path)
    total_beats = sum(song.scene(n).bars for n in song.arrangement) * song.beats_per_bar
    assert abs(mf.length - total_beats * 60 / song.tempo) < 0.01
    by_name = {t.name: t for t in mf.tracks}
    expected_notes = sum(len(song.scene(n).clips.get("Drums").notes) if "Drums" in song.scene(n).clips else 0
                         for n in song.arrangement)
    assert sum(1 for m in by_name["Drums"] if m.type == "note_on" and m.velocity > 0) == expected_notes
    assert all(m.channel == 9 for m in by_name["Drums"] if m.type == "note_on")
    assert any(m.type == "control_change" and m.control == 74 for m in by_name["Pad"])
