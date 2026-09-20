from unittest.mock import MagicMock, patch

from adapters.recognizer import FasterWhisperRecognizer


@patch("adapters.recognizer.WhisperModel")
def test_joins_stripped_segment_texts(mock_whisper_model_cls):
    segments = [MagicMock(text=" hello "), MagicMock(text="world ")]
    mock_whisper_model_cls.return_value.transcribe.return_value = (segments, None)

    recognizer = FasterWhisperRecognizer("small")
    result = recognizer.transcribe([0.1, 0.2], language="en")

    assert result == "hello world"
    mock_whisper_model_cls.return_value.transcribe.assert_called_once_with(
        [0.1, 0.2], language="en", vad_filter=True, beam_size=1)


@patch("adapters.recognizer.WhisperModel")
def test_returns_empty_string_when_no_segments(mock_whisper_model_cls):
    mock_whisper_model_cls.return_value.transcribe.return_value = ([], None)

    recognizer = FasterWhisperRecognizer("small")
    result = recognizer.transcribe([0.1])

    assert result == ""
