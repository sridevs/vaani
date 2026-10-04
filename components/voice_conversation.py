from __future__ import annotations

import numpy as np

from components.speech_text_normalizer import SpeechTextNormalizer
from ports import ConversationModel, Message, SpeechRecognizer, SpeechSynthesizer, VoiceActivityDetector


class VoiceConversation:
    """Drives one turn of listen -> transcribe -> reply -> speak."""

    def __init__(self, detector: VoiceActivityDetector, recognizer: SpeechRecognizer,
                 model: ConversationModel, synthesizer: SpeechSynthesizer,
                 speech_text_normalizer: SpeechTextNormalizer,
                 language: str | None = None) -> None:
        self._detector = detector
        self._recognizer = recognizer
        self._model = model
        self._synthesizer = synthesizer
        self._language = language
        self._speech_text_normalizer = speech_text_normalizer
        self._messages = [Message("system", "You are Vaani, a friendly local voice assistant.")]

    @property
    def messages(self) -> tuple[Message, ...]:
        return tuple(self._messages)

    @property
    def last_message(self) -> Message:
        return self._messages[-1]

    def process_turn(self, audio: np.ndarray | None = None) -> str | None:
        audio = audio if audio is not None else self._detector.record_turn()
        if audio is None or len(audio) == 0:
            return None
        text = self._recognizer.transcribe(audio, self._language)
        if not text:
            return None
        self._messages.append(Message("user", text))
        response = self._model.reply(self._messages)
        normalized_response = self._speech_text_normalizer.normalize(response)
        self._messages.append(Message("assistant", response))
        self._synthesizer.speak(normalized_response)
        return response
