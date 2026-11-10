# ILPC Ableton: automated music production in Ableton Live

Write a song as a short YAML spec. This toolkit then:

- **Builds it in Live**: creates or reuses tracks and scenes, and writes MIDI clips (chords, bass, drums, arps, melodies) into Session view.
- **Exports MIDI**: writes a multi-track `.mid` file with tempo, scene markers and CC automation. Drag it into Live, or into any other DAW.
- **Runs the show**: a cue list launches scenes, changes tempo and runs volume, pan, send and device ramps on a tempo-synced clock. You can use it for a live service run-sheet, or record it as automation.
- **Lets Claude drive Live**: an MCP server, so you can say *"build a 98 BPM Afro-gospel walk-in in A major and fade the pad in over 8 bars"*.

It talks to Live through **[AbletonOSC](https://github.com/ideoforms/AbletonOSC)**, the open-source remote script (Live 11 or 12). Live listens on UDP **11000** and replies on **11001**.

---

## 1. One-time setup (on the machine running Ableton)

1. Download AbletonOSC: <https://github.com/ideoforms/AbletonOSC/archive/refs/heads/master.zip>. Unzip it and rename the folder to `AbletonOSC`.
2. Copy that folder into Live's Remote Scripts folder:
   - **macOS:** `~/Music/Ableton/User Library/Remote Scripts/`
   - **Windows:** `\Users\<you>\Documents\Ableton\User Library\Remote Scripts\`
3. Restart Live. Go to **Settings → Link, Tempo & MIDI → Control Surface** and pick **AbletonOSC**. Live's status bar should show *"AbletonOSC: Listening for OSC on port 11000"*.
4. Install this toolkit (Python 3.10 or later):

```bash
cd ableton
```

```bash
python -m pip install -e ".[mcp]"
```

5. Check the connection:

```bash
ilpc-ableton ping -v
```

## 2. Daily workflow

```bash
ilpc-ableton validate examples/ilpc2026-walkin.yaml
```

```bash
ilpc-ableton apply examples/ilpc2026-walkin.yaml
```

```bash
ilpc-ableton show examples/ilpc2026-walkin.yaml --play
```

```bash
ilpc-ableton render examples/ilpc2026-walkin.yaml --out dist --split
```

Other commands:

| Command | What it does |
|---|---|
| `ilpc-ableton transport play\|stop` | Starts or stops the transport |
| `ilpc-ableton transport tempo 96` | Sets the tempo |
| `ilpc-ableton transport scene Groove` | Launches a scene by name or index |
| `ilpc-ableton ramp volume Pad 0.0 --bars 8 --curve log` | Runs a one-off fade |
| `ilpc-ableton ramp device Pad 0.9 --device Drift --param "Filter Freq" --bars 4` | Sweeps a device parameter |
| `--host 192.168.1.20` | Controls Live on another machine on your network (open UDP 11000 and 11001) |

**Best practice: use a template set.** Save a Live set that has your instruments already loaded on tracks named `Drums`, `Bass`, `Keys`, `Pad`, `Arp` and `Lead`. `apply` matches tracks **by name** and only rewrites clips, so your sound design is never touched. Any track that is missing gets created empty, and the log names the instrument the spec suggests for it (AbletonOSC cannot load devices).

## 3. Spec format

```yaml
title: My Song
tempo: 98
time_signature: [4, 4]
key: A major
seed: 2026                       # makes humanize repeatable
tracks:
  - {name: Drums, drums: true, color: "#2D0A4E", volume: 0.8}
  - {name: Pad, volume: 0.7, pan: -0.1, instrument: "Drift > Warm Pad"}
scenes:
  - name: Verse
    bars: 8
    clips:
      Pad:   {chords: "Amaj7 F#m7:2 D E", style: pad, octave: 3, cc: {74: [[0, 30], [32, 100]]}}
      Drums: {drums: {kick: "x..x..x.", snare: "....x...", closed_hat: "oxoxoxox"}, humanize: 8}
arrangement: [Verse, Verse]      # order used for the MIDI export
show:                            # cue list for `show`
  - {bar: 1, fire_scene: Verse}
  - {bar: 1, ramp: {target: volume, track: Pad, from: 0, to: 0.7, bars: 8, curve: exp}}
  - {bar: 17, stop: true}
```

**Clip generators.** Each clip uses exactly one of these:

- `chords`: a progression such as `"Dmaj7 Bm7:2 G"`. Each chord lasts one bar; `:N` sets its length in bars.
  - `style: pad` holds voice-led sustained chords.
  - `stabs` plays the chord on a step `rhythm`.
  - `arp` takes `rate` (beats), `octaves`, `direction` (up, down or updown) and `gate`.
  - `bass` plays the root, or the slash-chord bass note, on a step `rhythm`.
- `drums`: one step pattern per voice. Each pattern spans one bar unless you set `pattern_bars`. Voices include `kick snare rim clap closed_hat open_hat shaker tambourine crash ride talking_drum conga_hi conga_lo cowbell agogo`, a MIDI number, or a note name. Drums use the GM map (kick = 36), which matches Live's Drum Rack layout.
- `melody`: `"E5:1.5 C#5:0.5 r:1"`, where each token is note:beats and `r` is a rest. Add `repeat: true` to loop it.
- `notes`: explicit `[pitch, start_beat, duration, velocity]` entries.

**Step patterns:**

| Symbol | Meaning |
|---|---|
| `X` | Velocity 127 |
| `x` | Velocity 112 |
| `o` | Velocity 84 |
| `g` | Ghost note, velocity 48 |
| `.` | Rest |
| `-` | Tie (extends the previous note) |

**Show cues.** Each cue takes a time, `bar` (1-based) or `beat` (0-based), and one or more actions:

- `fire_scene: <name or index>`
- `tempo: <bpm>`
- `set: {target, track, value}`
- `ramp: {target, track, to, from?, bars|beats, curve}`
- `stop: true`

Ramp and set targets are `volume` (0–1, where 0.85 = 0 dB), `pan` (−1 to 1), `send` (add `send: <index>`) and `device` (add `device` and `param`, as names or indices). Curves are `linear`, `exp`, `log`, `s` and `hold`. If you leave out `from`, the ramp starts from the parameter's current value.

**Note naming.** The spec uses the scientific convention, where `C4` = MIDI 60. **Ableton labels MIDI 60 as "C3"**, so a `C4` in the spec appears as C3 in Live's piano roll. Nothing is transposed; only the label differs.

## 4. Recording automation into Live

AbletonOSC can't write envelope breakpoints directly, so automation is *performed* instead. Use one of these two routes:

1. **Arrangement recording:** turn on **Automation Arm**, arm **Arrangement Record**, then run `ilpc-ableton show … --play`. Live captures every ramp as real automation.
2. **MIDI CC lanes:** use the `cc:` lanes in clips, which are written into the `.mid` export. Map a CC to any parameter with MIDI Map (Cmd/Ctrl+M), or let instruments that respond to CC74 (filter) or CC1 (mod) pick it up directly.

## 5. Let Claude produce in Live (MCP)

**Claude Code:**

```bash
claude mcp add ableton -- python -m ilpc_ableton.mcp_server
```

**Claude Desktop** (`claude_desktop_config.json`):

```json
{ "mcpServers": { "ableton": { "command": "python", "args": ["-m", "ilpc_ableton.mcp_server"],
  "env": { "ABLETON_HOST": "127.0.0.1" } } } }
```

The server provides these tools:

| Tool | What it does |
|---|---|
| `ableton_status` | Checks the connection and returns tempo, transport, track and scene names |
| `apply_spec` | Validates a YAML spec and builds it in Live |
| `render_midi` | Exports a spec to `.mid` files |
| `transport` | Play, stop, tempo, or launch a scene |
| `automate` | Runs a tempo-synced ramp now |
| `run_show` | Starts a cue list in the background |

The server works with MCP Python SDK v1 and v2. Errors such as a bad spec or Live not running come back to Claude as readable messages.

## 6. Development

```bash
python -m pip install -e ".[dev,mcp]"
```

```bash
python -m pytest -q
```

The tests run against `tests/fake_live.py`, a UDP fake of AbletonOSC, so CI needs no copy of Live. The OSC encoder is checked byte-for-byte against `python-osc`, and the MIDI export is read back with `mido`.

## Limits (AbletonOSC API, as of the current release)

- It can't load instruments or effects, and it can't place clips in Arrangement view. Use a template set, or drag in the `.mid` export.
- There's no master-track volume endpoint. Fade the individual tracks, or put a Utility on a group or return track and ramp it as a `device`.
- Scene launches follow Live's global launch quantization, which is normally 1 bar.
