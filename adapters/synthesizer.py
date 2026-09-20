from __future__ import annotations

import subprocess

import numpy as np
import sounddevice as sd

from ports import SpeechSynthesizer


class PiperSynthesizer(SpeechSynthesizer):
    """Synthesizes and plays speech audio using a local Piper executable."""

    def __init__(self, executable: str, voice_model: str) -> None:
        self._executable = executable
        self._voice_model = voice_model

    def speak(self, text: str) -> None:
        process = subprocess.Popen([self._executable, "--model", self._voice_model, "--output-raw"],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        if process.stdin is None or process.stdout is None:
            raise RuntimeError("Piper process did not expose stdin/stdout pipes")
        process.stdin.write(text.encode())
        process.stdin.close()
        samples = np.frombuffer(process.stdout.read(), dtype=np.int16)
        process.wait()
        if process.returncode:
            raise RuntimeError("Piper failed to synthesize audio")
        sd.play(samples, samplerate=22_050)
        sd.wait()
