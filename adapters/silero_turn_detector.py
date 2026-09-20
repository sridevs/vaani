from __future__ import annotations

import queue

import numpy as np
import sounddevice as sd
import torch
from silero_vad import VADIterator, load_silero_vad

from ports import VoiceActivityDetector

SAMPLE_RATE = 16_000
FRAME_SAMPLES = 512


class SileroTurnDetector(VoiceActivityDetector):
    """Records microphone audio for one conversational turn using Silero VAD."""

    def __init__(self, threshold: float = 0.5, silence_ms: int = 650) -> None:
        self._vad = VADIterator(load_silero_vad(), sampling_rate=SAMPLE_RATE, threshold=threshold,
                                min_silence_duration_ms=silence_ms)

    def record_turn(self) -> np.ndarray | None:
        # The VAD keeps recurrent hidden state and a "triggered" flag across calls;
        # reset them so a previous turn's speech/silence history can't corrupt this one.
        self._vad.reset_states()

        frames: queue.Queue[np.ndarray] = queue.Queue()
        captured: list[np.ndarray] = []
        started = False

        def receive(indata: np.ndarray, _frames: int, _time: object, _status: object) -> None:
            frames.put(indata[:, 0].copy())

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                            blocksize=FRAME_SAMPLES, callback=receive):
            while True:
                frame = frames.get()
                event = self._vad(torch.from_numpy(frame), return_seconds=False)
                started = started or bool(event and "start" in event)
                if started:
                    captured.append(frame)
                if started and event and "end" in event:
                    break
        return np.concatenate(captured) if captured else None
