#!/usr/bin/env bash
# One-shot setup of the ILPC Ableton toolkit on macOS.
#   curl -fsSL https://raw.githubusercontent.com/dorotoace-coder/ilpc2026/claude/peaceful-dijkstra-oyo4fq/ableton/install-mac.sh | bash
#
# What it does (safe to re-run):
#   1. installs the AbletonOSC remote script into Live's User Library
#   2. downloads this toolkit to ~/ilpc-ableton (no git needed)
#   3. creates a private Python environment and installs the toolkit
#   4. adds an `ilpc-ableton` shortcut to your shell
#   5. opens Live and waits until you enable the AbletonOSC control surface
#   6. optionally builds the ILPC 2026 walk-in music into the open Live set
set -euo pipefail

BRANCH="${ILPC_BRANCH:-claude/peaceful-dijkstra-oyo4fq}"
REPO="dorotoace-coder/ilpc2026"
DEST="${ILPC_DIR:-$HOME/ilpc-ableton}"
SCRIPTS="${ABLETON_REMOTE_SCRIPTS:-$HOME/Music/Ableton/User Library/Remote Scripts}"
WAIT_SECONDS="${ILPC_WAIT:-300}"
ABLETONOSC_URL="${ABLETONOSC_URL:-https://github.com/ideoforms/AbletonOSC/archive/refs/heads/master.zip}"

bold() { printf '\n\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
die()  { printf '  \033[31m✗ %s\033[0m\n' "$*" >&2; exit 1; }
ask()  { # read from the keyboard even when piped from curl
  local reply=""
  if (exec </dev/tty) 2>/dev/null; then read -r -p "  $1 " reply </dev/tty || true; fi
  printf '%s' "$reply"
}

[ "$(uname -s)" = "Darwin" ] || [ "${ILPC_SKIP_OS_CHECK:-}" = 1 ] || die "This installer is for macOS."
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# --------------------------------------------------------------- Python 3.10+
bold "1/6  Checking Python (3.10 or newer)"
PY=""
for c in python3.14 python3.13 python3.12 python3.11 python3.10 python3 \
         /opt/homebrew/bin/python3 /usr/local/bin/python3 \
         /Library/Frameworks/Python.framework/Versions/Current/bin/python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
    PY="$(command -v "$c")"; break
  fi
done
if [ -z "$PY" ]; then
  warn "No Python 3.10+ found (macOS's built-in python3 is too old)."
  warn "Install it from https://www.python.org/downloads/macos/ then run this command again."
  open "https://www.python.org/downloads/macos/" 2>/dev/null || true
  exit 1
fi
ok "Using $PY ($("$PY" -V 2>&1))"

# --------------------------------------------------------------- AbletonOSC
bold "2/6  Installing AbletonOSC into Live"
mkdir -p "$SCRIPTS"
curl -fsSL "$ABLETONOSC_URL" -o "$TMP/abletonosc.zip"
unzip -q "$TMP/abletonosc.zip" -d "$TMP/osc"
[ -f "$TMP/osc/AbletonOSC-master/manager.py" ] || die "Unexpected AbletonOSC download layout."
if [ -d "$SCRIPTS/AbletonOSC" ]; then
  BACKUP="$SCRIPTS/../AbletonOSC-backup-$(date +%Y%m%d%H%M%S)"
  mv "$SCRIPTS/AbletonOSC" "$BACKUP"
  ok "Previous copy moved to $(cd "$(dirname "$BACKUP")" && pwd)/$(basename "$BACKUP")"
fi
mv "$TMP/osc/AbletonOSC-master" "$SCRIPTS/AbletonOSC"
ok "Installed: $SCRIPTS/AbletonOSC"

# --------------------------------------------------------------- toolkit
bold "3/6  Downloading the ILPC Ableton toolkit"
curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH" -o "$TMP/repo.tgz"
mkdir -p "$TMP/repo" && tar -xzf "$TMP/repo.tgz" -C "$TMP/repo"
SRC="$(find "$TMP/repo" -maxdepth 2 -type d -name ableton | head -n1)"
[ -n "$SRC" ] && [ -f "$SRC/pyproject.toml" ] || die "Toolkit not found in branch $BRANCH."
mkdir -p "$DEST"
# refresh code, keep the user's own specs/output and the existing venv
( cd "$SRC" && tar -cf - . ) | ( cd "$DEST" && tar -xf - )
ok "Toolkit in $DEST"

bold "4/6  Installing (private Python environment)"
[ -x "$DEST/.venv/bin/python" ] || "$PY" -m venv "$DEST/.venv"
LOG="$DEST/install.log"
if ! { "$DEST/.venv/bin/python" -m pip install --upgrade pip &&
       "$DEST/.venv/bin/python" -m pip install -e "$DEST[mcp]"; } >"$LOG" 2>&1; then
  tail -n 20 "$LOG"; die "Install failed — full log: $LOG"
fi
ok "Installed: $DEST/.venv/bin/ilpc-ableton"

RC="$HOME/.zshrc"; [ "${SHELL##*/}" = "bash" ] && RC="$HOME/.bash_profile"
LINE="alias ilpc-ableton='$DEST/.venv/bin/ilpc-ableton'"
if ! grep -qF "$LINE" "$RC" 2>/dev/null; then
  printf '\n# ILPC Ableton toolkit\n%s\n' "$LINE" >> "$RC"
  ok "Added 'ilpc-ableton' shortcut to $RC (works in new Terminal windows)"
fi
CLI="$DEST/.venv/bin/ilpc-ableton"

# --------------------------------------------------------------- connect to Live
bold "5/6  Connecting to Ableton Live"
LIVE_APP="$(ls -d /Applications/Ableton\ Live*.app 2>/dev/null | sort | tail -n1 || true)"
if [ -n "$LIVE_APP" ]; then
  if pgrep -f "Ableton Live" >/dev/null 2>&1; then
    warn "Live is running. It only sees new remote scripts after a restart:"
    warn "quit Live (Cmd+Q), and it will be reopened for you."
    ask "Press Enter once Live has quit..." >/dev/null
  fi
  open "$LIVE_APP" && ok "Opened $(basename "$LIVE_APP")"
else
  warn "Ableton Live not found in /Applications — open it yourself."
fi
cat <<'EOF'

  In Live:  Live menu > Settings  (Live 11: Preferences)
            > Link, Tempo & MIDI  > Control Surface  > choose  AbletonOSC
            (leave Input/Output as None)
  The status bar should read: "AbletonOSC: Listening for OSC on port 11000"

EOF
printf '  Waiting for Live'
deadline=$(( $(date +%s) + WAIT_SECONDS ))
connected=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  if "$CLI" --timeout 1 ping >/dev/null 2>&1; then connected=1; break; fi
  printf '.'; sleep 2
done
echo
if [ "$connected" != 1 ]; then
  warn "Live didn't answer yet. Once AbletonOSC is selected, run:  $CLI ping -v"
  exit 0
fi
ok "Live is connected"

# --------------------------------------------------------------- build the music
bold "6/6  ILPC 2026 walk-in music"
echo "  This writes tracks, scenes and clips into the Live set that is open now."
echo "  Use a NEW EMPTY set (File > New Live Set) so nothing of yours is changed."
REPLY="$(ask "Build it now? [y/N]")"
case "$REPLY" in
  y|Y|yes|YES)
    "$CLI" apply "$DEST/examples/ilpc2026-walkin.yaml"
    echo
    ok "Done. Drag an instrument onto each track (Drums: a Drum Rack kit, Bass: Operator,"
    ok "Keys: Electric, Pad: Drift, Arp + Lead: Wavetable), then save as your ILPC template."
    echo "  Run the pre-service show:  ilpc-ableton show $DEST/examples/ilpc2026-walkin.yaml --play"
    ;;
  *) echo "  Skipped. Later:  ilpc-ableton apply $DEST/examples/ilpc2026-walkin.yaml" ;;
esac

if command -v claude >/dev/null 2>&1; then
  REPLY="$(ask "Let Claude Code control Live (register the MCP server)? [y/N]")"
  case "$REPLY" in
    y|Y|yes|YES) claude mcp add ableton -- "$DEST/.venv/bin/python" -m ilpc_ableton.mcp_server && ok "Claude can now drive Live." ;;
  esac
fi
bold "All set."
