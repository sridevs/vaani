from itertools import cycle
from unittest.mock import MagicMock, patch

import numpy as np

from adapters.silero_turn_detector import SileroTurnDetector


def _make_detector(mock_input_stream, vad_events):
    """Builds a detector whose VAD emits `vad_events` (cycled for every captured frame,
    across any number of `record_turn()` calls)."""
    with patch("adapters.silero_turn_detector.load_silero_vad", return_value=MagicMock()), \
         patch("adapters.silero_turn_detector.VADIterator") as mock_vad_iterator_cls:
        mock_vad_iterator_cls.return_value = MagicMock(side_effect=cycle(vad_events))
        detector = SileroTurnDetector()

    frames = [np.zeros((1, 1), dtype="float32") for _ in vad_events]

    def fake_input_stream(*_args, callback=None, **_kwargs):
        for frame in frames:
            callback(frame, len(frame), None, None)
        return MagicMock(__enter__=MagicMock(), __exit__=MagicMock(return_value=False))

    mock_input_stream.side_effect = fake_input_stream
    return detector


@patch("adapters.silero_turn_detector.sd.InputStream")
def test_captures_audio_between_start_and_end_events(mock_input_stream):
    detector = _make_detector(mock_input_stream, [{"start": 0}, {}, {"end": 1}])
    result = detector.record_turn()
    assert len(result) == 3


@patch("adapters.silero_turn_detector.sd.InputStream")
def test_ignores_frames_before_speech_starts(mock_input_stream):
    detector = _make_detector(mock_input_stream, [{}, {"start": 0}, {"end": 1}])
    result = detector.record_turn()
    assert len(result) == 2


@patch("adapters.silero_turn_detector.sd.InputStream")
def test_returns_audio_when_start_and_end_arrive_on_same_frame(mock_input_stream):
    detector = _make_detector(mock_input_stream, [{"start": 0, "end": 0}])
    result = detector.record_turn()
    assert result is not None
    assert len(result) == 1


@patch("adapters.silero_turn_detector.sd.InputStream")
def test_record_turn_resets_vad_state_every_call(mock_input_stream):
    # Regression test: VADIterator carries recurrent hidden state and a "triggered"
    # flag across calls. Without resetting it, a second turn can silently fail to
    # detect speech because leftover state from the previous turn corrupts it.
    detector = _make_detector(mock_input_stream, [{"start": 0}, {"end": 1}])

    detector.record_turn()
    detector.record_turn()

    assert detector._vad.reset_states.call_count == 2
