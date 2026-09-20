from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import asdict

from ports import ConversationModel, Message


class OllamaModel(ConversationModel):
    """Generates replies by calling a local Ollama chat model over HTTP."""

    def __init__(self, model: str, host: str) -> None:
        self._model = model
        self._host = host.rstrip("/")

    def reply(self, messages: list[Message]) -> str:
        payload = {"model": self._model, "messages": [asdict(message) for message in messages], "stream": False}
        return self._post("/api/chat", payload)["message"]["content"].strip()

    def _post(self, path: str, payload: dict) -> dict:
        request = urllib.request.Request(f"{self._host}{path}", data=json.dumps(payload).encode(),
                                         headers={"Content-Type": "components/json"})
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return json.load(response)
        except urllib.error.URLError as error:
            raise RuntimeError(f"Could not reach Ollama at {self._host}: {error}") from error
