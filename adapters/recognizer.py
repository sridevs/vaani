from __future__ import annotations

import numpy as np
from faster_whisper import WhisperModel

from ports import SpeechRecognizer


class FasterWhisperRecognizer(SpeechRecognizer):
    """Transcribes audio into text using a local faster-whisper model."""

    def __init__(self, model_name: str) -> None:
        self._model = WhisperModel(model_name, device="auto", compute_type="int8")

    def transcribe(self, audio: np.ndarray, language: str | None = None) -> str:
        segments, _ = self._model.transcribe(audio, language=language, vad_filter=True, beam_size=1)
        return " ".join(segment.text.strip() for segment in segments).strip()
