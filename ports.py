from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class Message:
    role: str
    content: str


class SpeechRecognizer(Protocol):
    def transcribe(self, audio: np.ndarray, language: str | None = None) -> str: ...


class VoiceActivityDetector(Protocol):
    def record_turn(self) -> np.ndarray | None: ...


class ConversationModel(Protocol):
    def reply(self, messages: list[Message]) -> str: ...


class SpeechSynthesizer(Protocol):
    def speak(self, text: str) -> None: ...
