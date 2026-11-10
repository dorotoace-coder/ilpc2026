import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

pytest.importorskip("mcp")
from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def _run(live, calls):
    async def main():
        env = {**os.environ, "ABLETON_PORT": str(live.port), "ABLETON_REPLY_PORT": "0", "ABLETON_HOST": "127.0.0.1"}
        params = StdioServerParameters(command=sys.executable, args=["-m", "ilpc_ableton.mcp_server"], env=env, cwd=str(ROOT))
        out = []
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                for name, args in calls:
                    res = await s.call_tool(name, args)
                    out.append((getattr(res, "is_error", getattr(res, "isError", None)), res.content[0].text))
        return out
    return asyncio.run(main())


def test_mcp_drives_live(live, example_path):
    results = _run(live, [
        ("ableton_status", {}),
        ("apply_spec", {"spec_yaml": example_path.read_text()}),
        ("transport", {"action": "scene", "value": "Groove"}),
        ("automate", {"target": "volume", "track": "Pad", "to": 0.2, "bars": 0.25, "start": 0.6}),
        ("apply_spec", {"spec_yaml": "tracks: [{name: X}]\nscenes: [{name: S, clips: {Y: {chords: C}}}]"}),
    ])
    status_err, status = results[0]
    assert status_err is False and json.loads(status)["connected"] is True
    assert results[1][0] is False and json.loads(results[1][1])["clips"] == 14  # 2 + 5 + 3 + 4 clips across the four scenes
    assert results[2][0] is False
    assert live.scenes[[s["name"] for s in live.scenes].index("Groove")]["fired"] == 1
    assert results[3][0] is False
    pad = [t["name"] for t in live.tracks].index("Pad")
    assert live.tracks[pad]["volume"] == pytest.approx(0.2)
    assert results[4][0] is True and "unknown track 'Y'" in results[4][1]
