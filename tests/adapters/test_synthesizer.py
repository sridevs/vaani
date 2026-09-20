from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from adapters.synthesizer import PiperSynthesizer


@patch("adapters.synthesizer.sd")
@patch("adapters.synthesizer.subprocess.Popen")
def test_speak_sends_text_and_plays_returned_samples(mock_popen, mock_sd):
    process = MagicMock()
    process.stdin = MagicMock()
    process.stdout.read.return_value = np.array([1, 2, 3], dtype=np.int16).tobytes()
    process.returncode = 0
    mock_popen.return_value = process

    synthesizer = PiperSynthesizer("piper", "voice.onnx")
    synthesizer.speak("hello")

    process.stdin.write.assert_called_once_with(b"hello")
    process.stdin.close.assert_called_once()
    played_samples = mock_sd.play.call_args[0][0]
    np.testing.assert_array_equal(played_samples, np.array([1, 2, 3], dtype=np.int16))
    mock_sd.wait.assert_called_once()


@patch("adapters.synthesizer.sd")
@patch("adapters.synthesizer.subprocess.Popen")
def test_speak_raises_when_piper_fails(mock_popen, mock_sd):
    process = MagicMock()
    process.stdin = MagicMock()
    process.stdout.read.return_value = b""
    process.returncode = 1
    mock_popen.return_value = process

    synthesizer = PiperSynthesizer("piper", "voice.onnx")
    with pytest.raises(RuntimeError):
        synthesizer.speak("hello")
    mock_sd.play.assert_not_called()
