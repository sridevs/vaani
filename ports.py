from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Message:
    role: str
    content: str


class SpeechRecognizer(Protocol):
    def transcribe(self, audio: Sequence[float], language: str | None = None) -> str: ...


class VoiceActivityDetector(Protocol):
    def record_turn(self) -> Sequence[float] | None: ...


class ConversationModel(Protocol):
    def reply(self, messages: list[Message]) -> str: ...


class SpeechSynthesizer(Protocol):
    def speak(self, text: str) -> None: ...

