"""ILPC Ableton toolkit: drive Ableton Live from code for automated music production.

Layers:
- osc:        dependency-free OSC 1.0 encode/decode (UDP)
- live:       AbletonClient for the AbletonOSC remote script (ports 11000/11001)
- theory:     note names, scales, chord symbols
- spec:       declarative song spec (YAML/JSON) -> clips, notes, automation
- midi:       Standard MIDI File export (tempo, notes, CC automation)
- automation: beat-synced parameter ramps and show cue lists
"""

__version__ = "0.1.0"
