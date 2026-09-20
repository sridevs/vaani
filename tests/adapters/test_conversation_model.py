import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from adapters.conversation_model import OllamaModel
from ports import Message


@patch("adapters.conversation_model.urllib.request.urlopen")
def test_reply_posts_messages_and_returns_stripped_content(mock_urlopen):
    response_body = json.dumps({"message": {"content": " Hi there \n"}}).encode()
    mock_response = MagicMock()
    mock_response.read.return_value = response_body
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    model = OllamaModel("llama3.2", "http://127.0.0.1:11434/")
    result = model.reply([Message("user", "hello")])

    assert result == "Hi there"
    request = mock_urlopen.call_args[0][0]
    assert request.full_url == "http://127.0.0.1:11434/api/chat"
    sent_payload = json.loads(request.data.decode())
    assert sent_payload["model"] == "llama3.2"
    assert sent_payload["messages"] == [{"role": "user", "content": "hello"}]
    assert sent_payload["stream"] is False


@patch("adapters.conversation_model.urllib.request.urlopen")
def test_reply_raises_runtime_error_when_host_unreachable(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError("connection refused")

    model = OllamaModel("llama3.2", "http://127.0.0.1:11434")
    with pytest.raises(RuntimeError):
        model.reply([Message("user", "hello")])
