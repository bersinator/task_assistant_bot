"""Voice MCP server: transcribes Telegram voice messages with a local Whisper (faster-whisper)."""

import logging
import os
import sys
import threading
import time
from pathlib import Path

import anyio
import av
import numpy as np
from mcp.server import MCPServer

MODEL = os.environ.get("WHISPER_MODEL", "large-v3-turbo")
# Optional folder with already downloaded models; without it faster-whisper downloads the model to the Hugging Face cache.
MODELS_DIR = os.environ.get("WHISPER_MODELS_DIR")
# Language code such as "en" or "ru"; empty - detect automatically.
LANGUAGE = os.environ.get("WHISPER_LANGUAGE") or None
BEAM_SIZE = int(os.environ.get("WHISPER_BEAM_SIZE", "5"))
KEEP_DAYS = 7
MAX_BYTES = 20 * 1024 * 1024  # Telegram doesn't give bots anything larger

INSTRUCTIONS = """\
Transcribes voice and audio messages from Telegram. The path comes from the Telegram plugin's download_attachment.
"""

log = logging.getLogger("mcp_voice")
mcp = MCPServer("voice", instructions=INSTRUCTIONS)

_model = None
_model_lock = threading.Lock()


def inbox_dir() -> Path:
    """The Telegram plugin's inbox folder: same logic as the plugin."""
    state = os.environ.get("TELEGRAM_STATE_DIR")
    if not state:
        config = os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude"
        state = Path(config) / "channels" / "telegram"
    return Path(state) / "inbox"


def load_model():
    """Load the model once and keep it in memory."""
    global _model
    with _model_lock:
        if _model is None:
            from faster_whisper import WhisperModel

            started = time.monotonic()
            options = dict(device="cpu", compute_type="int8")
            if MODELS_DIR and Path(MODELS_DIR).is_dir():
                options["download_root"] = MODELS_DIR
            try:
                _model = WhisperModel(MODEL, local_files_only=True, **options)
            except Exception:
                log.info("Model %s not found locally, downloading", MODEL)
                _model = WhisperModel(MODEL, **options)
            log.info("Model %s loaded in %.1f s", MODEL, time.monotonic() - started)
        return _model


def _check_path(path: str) -> Path:
    inbox = inbox_dir().resolve()
    file = Path(path).expanduser().resolve()
    if not file.is_relative_to(inbox):
        raise ValueError(f"Only files from the Telegram inbox folder are transcribed: {inbox}")
    if not file.is_file():
        raise ValueError(f"No such file: {file}")
    if file.stat().st_size > MAX_BYTES:
        raise ValueError("File is larger than 20 MB.")
    return file


def _clean_inbox() -> None:
    """Delete files older than KEEP_DAYS days from the inbox: the plugin doesn't clean it up."""
    border = time.time() - KEEP_DAYS * 24 * 3600
    for file in inbox_dir().glob("*"):
        try:
            if file.is_file() and file.stat().st_mtime < border:
                file.unlink()
        except OSError:
            pass


def _load_audio(file: Path) -> np.ndarray:
    """Mono 16 kHz float32. Decoded here: the faster-whisper decoder (PyAV) breaks on newer av versions."""
    resampler = av.AudioResampler(format="flt", layout="mono", rate=16000)
    chunks = []
    with av.open(str(file)) as container:
        for frame in container.decode(audio=0):
            chunks += [f.to_ndarray()[0] for f in resampler.resample(frame)]
        chunks += [f.to_ndarray()[0] for f in resampler.resample(None)]
    return np.concatenate(chunks) if chunks else np.zeros(0, np.float32)


def _transcribe(file: Path) -> str:
    audio = _load_audio(file)
    segments, info = load_model().transcribe(audio, language=LANGUAGE, beam_size=BEAM_SIZE, vad_filter=True)
    text = " ".join(s.text.strip() for s in segments).strip()
    log.info("%s: %.1f s of audio", file.name, info.duration)
    return text


@mcp.tool()
async def transcribe_audio(path: str) -> str:
    """Transcribe a Telegram voice or audio message and return the text.

    path - the path returned by download_attachment (the Telegram plugin's inbox folder).
    """
    file = _check_path(path)
    text = await anyio.to_thread.run_sync(_transcribe, file)
    _clean_inbox()
    return text or "(no speech recognized: silence or noise)"


def main() -> None:
    sys.stderr.reconfigure(encoding="utf-8")  # MCP server log; otherwise non-ASCII text breaks on Windows code pages
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    # The model takes a few seconds to load - start now so the first voice message doesn't wait.
    threading.Thread(target=load_model, daemon=True).start()
    mcp.run()
