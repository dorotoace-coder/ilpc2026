import pytest

from ilpc_ableton import theory
from ilpc_ableton.spec import SpecError, load_spec, parse_spec


def test_note_names():
    assert theory.note_to_midi("C4") == 60
    assert theory.note_to_midi("A4") == 69
    assert theory.note_to_midi("F#3") == 54
    assert theory.note_to_midi("Bb2") == 46
    assert theory.note_to_midi("C-1") == 0
    with pytest.raises(ValueError):
        theory.note_to_midi("H2")
    with pytest.raises(ValueError):
        theory.note_to_midi("G#9")  # G9 = 127 is the top; G#9 is out of range
    assert theory.note_to_midi(127) == 127


def test_chords():
    assert theory.chord_pitches("C", 4) == [60, 64, 67]
    assert theory.chord_pitches("Am7", 3) == [57, 60, 64, 67]
    assert theory.chord_pitches("F#m7b5", 4) == [66, 69, 72, 76]
    assert theory.chord_bass("D/F#", 2) == 42
    assert theory.chord_bass("Bbmaj7", 1) == 34
    with pytest.raises(ValueError):
        theory.parse_chord("Cweird")


def test_voice_leading_stays_close():
    a = theory.chord_pitches("Cmaj7", 4)
    b = theory.chord_pitches("Fmaj7", 4, voice_lead_from=a)
    centre_a = sum(a) / len(a)
    assert all(abs(p - centre_a) <= 6 for p in b)


def test_scale():
    assert theory.scale_pitches("C major", 60, 72) == [60, 62, 64, 65, 67, 69, 71, 72]
    with pytest.raises(ValueError):
        theory.parse_key("C lydianish")


def test_example_spec_builds(example_path):
    song = load_spec(example_path)
    assert song.tempo == 98 and song.beats_per_bar == 4
    groove = song.scene("Groove")
    assert groove.bars == 16
    for clip in groove.clips.values():
        assert clip.length == 64
        assert all(0 <= n.start < clip.length and n.duration > 0 for n in clip.notes)
    assert song.track("Drums").channel == 9
    assert {t.channel for t in song.tracks if t.name != "Drums"}.isdisjoint({9})
    assert 74 in song.scene("Walk-in").clips["Pad"].cc


def _song(clips, **extra):
    return parse_spec({"tempo": 100, "tracks": [{"name": "A"}, {"name": "D", "drums": True}],
                       "scenes": [{"name": "S", "bars": 2, "clips": clips}], **extra})


def test_drum_steps_and_ties():
    song = _song({"D": {"drums": {"kick": "x...x...", "snare": "..o-...."}}})
    notes = song.scenes[0].clips["D"].notes
    kicks = [n.start for n in notes if n.pitch == 36]
    assert kicks == [0, 2, 4, 6]  # 8 steps per bar -> half-beat steps, 2 bars
    assert all(n.duration <= 0.25 for n in notes)


def test_bass_ties_extend_notes():
    song = _song({"A": {"chords": "C", "style": "bass", "rhythm": "x---x-..", "velocity": 112}})
    notes = song.scenes[0].clips["A"].notes
    assert [(n.start, n.duration) for n in notes] == [(0, 2), (2, 1), (4, 2), (6, 1)]
    assert {n.pitch for n in notes} == {36}


def test_chord_durations_and_looping():
    song = _song({"A": {"chords": "C:0.5 G:1.5", "style": "pad"}})
    notes = song.scenes[0].clips["A"].notes
    starts = sorted({n.start for n in notes})
    assert starts == [0, 2]
    assert max(n.start + n.duration for n in notes) == 8


def test_arp_and_melody():
    song = _song({"A": {"chords": "C", "style": "arp", "rate": 0.25, "octaves": 1}})
    notes = song.scenes[0].clips["A"].notes
    assert len(notes) == 32 and [n.pitch for n in notes[:4]] == [60, 64, 67, 60]
    song = _song({"A": {"melody": "C4:1 r:1 E4:2", "repeat": True}})
    notes = song.scenes[0].clips["A"].notes
    assert [(n.pitch, n.start) for n in notes] == [(60, 0), (64, 2), (60, 4), (64, 6)]


def test_humanize_is_deterministic():
    cfg = {"D": {"drums": {"hat": "xxxxxxxx"}, "humanize": 20}}
    v1 = [n.velocity for n in _song(cfg).scenes[0].clips["D"].notes]
    v2 = [n.velocity for n in _song(cfg).scenes[0].clips["D"].notes]
    assert v1 == v2 and len(set(v1)) > 1


@pytest.mark.parametrize("bad", [
    {"tempo": 5},
    {"tracks": [{"name": "A"}, {"name": "A"}]},
    {"tracks": [{"name": "A"}], "scenes": [{"name": "S", "clips": {"B": {"chords": "C"}}}]},
    {"tracks": [{"name": "A"}], "scenes": [{"name": "S", "clips": {"A": {"chords": "Cxyz"}}}]},
    {"tracks": [{"name": "A"}], "scenes": [{"name": "S", "clips": {"A": {"drums": {"kick": "x?x"}}}}]},
    {"tracks": [{"name": "A"}], "scenes": [{"name": "S", "clips": {"A": {"chords": "C", "melody": "C4"}}}]},
    {"tracks": [{"name": "A", "volume": 2}]},
    {"tracks": [{"name": "A"}], "scenes": [{"name": "S"}], "arrangement": ["Nope"]},
    {"tracks": [{"name": "A"}], "scenes": [{"name": "S"}], "show": [{"bar": 1, "fire_scene": "Nope"}]},
    {"tracks": [{"name": "A"}], "scenes": [{"name": "S", "clips": {"A": {"chords": "C", "cc": {7: [[0, 200]]}}}}]},
])
def test_invalid_specs_rejected(bad):
    with pytest.raises((SpecError, ValueError)):
        parse_spec(bad)
