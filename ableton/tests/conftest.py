import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fake_live import FakeLive  # noqa: E402
from ilpc_ableton.live import AbletonClient  # noqa: E402

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "ilpc2026-walkin.yaml"


@pytest.fixture
def live():
    fake = FakeLive(tracks=["Drums", "Bass"], scenes=1)
    yield fake
    fake.close()


@pytest.fixture
def client(live):
    c = AbletonClient("127.0.0.1", live.port, recv_port=0, timeout=2.0, bind_host="127.0.0.1")
    yield c
    c.close()


@pytest.fixture
def example_path():
    return EXAMPLE
