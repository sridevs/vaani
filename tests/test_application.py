import unittest

from application import VoiceConversation
from ports import Message


class FakeDetector:
    def record_turn(self):
        return [0.1]


class FakeRecognizer:
    def transcribe(self, audio, language=None):
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


class VoiceConversationTests(unittest.TestCase):
    def test_turn_is_transcribed_replied_to_and_spoken(self):
        speaker = FakeSynthesizer()
        conversation = VoiceConversation(FakeDetector(), FakeRecognizer(), FakeModel(), speaker)
        response = conversation.process_turn()
        self.assertEqual(response, "Hi there")
        self.assertEqual(speaker.spoken, ["Hi there"])
        self.assertEqual(conversation.messages[-1], Message("assistant", "Hi there"))

    def test_empty_audio_does_not_call_model(self):
        speaker = FakeSynthesizer()
        conversation = VoiceConversation(FakeDetector(), FakeRecognizer(), FakeModel(), speaker)
        self.assertIsNone(conversation.process_turn([]))
        self.assertEqual(speaker.spoken, [])
