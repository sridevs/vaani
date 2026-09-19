from __future__ import annotations

import json
import queue
import subprocess
import urllib.error
import urllib.request
from collections.abc import Sequence

import numpy as np
import sounddevice as sd
import torch
from faster_whisper import WhisperModel
from silero_vad import VADIterator, load_silero_vad

from ports import ConversationModel, Message, SpeechRecognizer, SpeechSynthesizer, VoiceActivityDetector

SAMPLE_RATE = 16_000
FRAME_SAMPLES = 512


class SileroTurnDetector(VoiceActivityDetector):
    def __init__(self, threshold: float = 0.5, silence_ms: int = 650) -> None:
        self._vad = VADIterator(load_silero_vad(), sampling_rate=SAMPLE_RATE, threshold=threshold,
                                min_silence_duration_ms=silence_ms)

    def record_turn(self) -> Sequence[float] | None:
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


class FasterWhisperRecognizer(SpeechRecognizer):
    def __init__(self, model_name: str) -> None:
        self._model = WhisperModel(model_name, device="auto", compute_type="int8")

    def transcribe(self, audio: Sequence[float], language: str | None = None) -> str:
        segments, _ = self._model.transcribe(audio, language=language, vad_filter=True, beam_size=1)
        return " ".join(segment.text.strip() for segment in segments).strip()


class OllamaModel(ConversationModel):
    def __init__(self, model: str, host: str) -> None:
        self._model = model
        self._host = host.rstrip("/")

    def reply(self, messages: list[Message]) -> str:
        payload = json.dumps({"model": self._model, "messages": [message.__dict__ for message in messages],
                              "stream": False}).encode()
        request = urllib.request.Request(f"{self._host}/api/chat", data=payload,
                                         headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return json.load(response)["message"]["content"].strip()
        except urllib.error.URLError as error:
            raise RuntimeError(f"Could not reach Ollama at {self._host}: {error}") from error


class PiperSynthesizer(SpeechSynthesizer):
    def __init__(self, executable: str, voice_model: str) -> None:
        self._executable = executable
        self._voice_model = voice_model

    def speak(self, text: str) -> None:
        process = subprocess.Popen([self._executable, "--model", self._voice_model, "--output-raw"],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        assert process.stdin is not None and process.stdout is not None
        process.stdin.write(text.encode())
        process.stdin.close()
        samples = np.frombuffer(process.stdout.read(), dtype=np.int16)
        process.wait()
        if process.returncode:
            raise RuntimeError("Piper failed to synthesize audio")
        sd.play(samples, samplerate=22_050)
        sd.wait()
