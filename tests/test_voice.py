import os
import time
from types import SimpleNamespace

import anyio
import numpy as np
import pytest

from mcp_voice import server


class FakeModel:
    def __init__(self):
        self.calls = []

    def transcribe(self, audio, **options):
        self.calls.append((audio, options))
        segments = [SimpleNamespace(text=" Buy wood screws"), SimpleNamespace(text=" by Friday. ")]
        return iter(segments), SimpleNamespace(duration=2.0)


@pytest.fixture
def inbox(tmp_path, monkeypatch):
    monkeypatch.setenv("TELEGRAM_STATE_DIR", str(tmp_path / "telegram"))
    monkeypatch.setattr(server, "_model", FakeModel())
    monkeypatch.setattr(server, "_load_audio", lambda file: np.zeros(16000, np.float32))
    folder = tmp_path / "telegram" / "inbox"
    folder.mkdir(parents=True)
    return folder


def transcribe(path) -> str:
    return anyio.run(server.transcribe_audio, str(path))


def test_transcribe(inbox, monkeypatch):
    monkeypatch.setattr(server, "LANGUAGE", "en")
    voice = inbox / "1761300000000-abc.oga"
    voice.write_bytes(b"ogg")
    assert transcribe(voice) == "Buy wood screws by Friday."
    _, options = server._model.calls[0]
    assert options["language"] == "en" and options["vad_filter"]


def test_silence(inbox, monkeypatch):
    monkeypatch.setattr(server._model, "transcribe", lambda audio, **o: (iter([]), SimpleNamespace(duration=1.0)))
    voice = inbox / "silence.oga"
    voice.write_bytes(b"ogg")
    assert transcribe(voice) == "(no speech recognized: silence or noise)"


def test_only_inbox(inbox, tmp_path):
    outside = tmp_path / "secret.txt"
    outside.write_text("x")
    with pytest.raises(ValueError, match="inbox folder"):
        transcribe(outside)
    with pytest.raises(ValueError, match="inbox folder"):
        transcribe(inbox / ".." / ".." / "secret.txt")
    with pytest.raises(ValueError, match="No such file"):
        transcribe(inbox / "missing.oga")


def test_old_files_removed(inbox):
    old = inbox / "old.jpg"
    old.write_bytes(b"jpg")
    week_ago = time.time() - 8 * 24 * 3600
    os.utime(old, (week_ago, week_ago))
    voice = inbox / "new.oga"
    voice.write_bytes(b"ogg")
    transcribe(voice)
    assert not old.exists()
    assert voice.exists()


def test_inbox_follows_config_dir(monkeypatch, tmp_path):
    monkeypatch.delenv("TELEGRAM_STATE_DIR", raising=False)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
    assert server.inbox_dir() == tmp_path / "channels" / "telegram" / "inbox"
