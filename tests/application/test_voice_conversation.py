import numpy as np

from components.voice_conversation import VoiceConversation
from ports import Message


class FakeDetector:
    def record_turn(self):
        return np.array([0.1], dtype="float32")


class SilentDetector:
    def record_turn(self):
        return None


class FakeRecognizer:
    def transcribe(self, _audio, _language=None):
        return "hello"


class FakeModel:
    def reply(self, messages):
        assert messages[-1] == Message("user", "hello")
        return "Hi there"


class FakeSynthesizer:
    def __init__(self):
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)


def test_turn_is_transcribed_replied_to_and_spoken():
    speaker = FakeSynthesizer()
    conversation = VoiceConversation(FakeDetector(), FakeRecognizer(), FakeModel(), speaker)

    response = conversation.process_turn()

    assert response == "Hi there"
    assert speaker.spoken == ["Hi there"]
    assert conversation.last_message == Message("assistant", "Hi there")


def test_empty_audio_does_not_call_model():
    speaker = FakeSynthesizer()
    conversation = VoiceConversation(FakeDetector(), FakeRecognizer(), FakeModel(), speaker)

    assert conversation.process_turn(np.array([], dtype="float32")) is None
    assert speaker.spoken == []


def test_last_message_reflects_most_recent_entry():
    conversation = VoiceConversation(FakeDetector(), FakeRecognizer(), FakeModel(), FakeSynthesizer())

    assert conversation.last_message == Message("system", "You are Vaani, a friendly local voice assistant.")

    conversation.process_turn()

    assert conversation.last_message == conversation.messages[-1]


def test_multi_sample_ndarray_audio_does_not_raise():
    # Regression test: real VAD output is a multi-element np.ndarray, whose truthiness
    # is ambiguous. process_turn must check emptiness without relying on `if not audio`.
    speaker = FakeSynthesizer()
    conversation = VoiceConversation(FakeDetector(), FakeRecognizer(), FakeModel(), speaker)
    audio = np.array([0.1, 0.2, 0.3], dtype="float32")

    response = conversation.process_turn(audio)

    assert response == "Hi there"
    assert speaker.spoken == ["Hi there"]


def test_empty_ndarray_audio_does_not_call_model():
    speaker = FakeSynthesizer()
    conversation = VoiceConversation(FakeDetector(), FakeRecognizer(), FakeModel(), speaker)

    assert conversation.process_turn(np.array([], dtype="float32")) is None
    assert speaker.spoken == []


def test_detector_returning_none_does_not_call_model():
    # Regression test: when no audio argument is given, process_turn falls back to
    # detector.record_turn(), which returns None on silence. Must not crash on len(None).
    speaker = FakeSynthesizer()
    conversation = VoiceConversation(SilentDetector(), FakeRecognizer(), FakeModel(), speaker)

    assert conversation.process_turn() is None
    assert speaker.spoken == []
