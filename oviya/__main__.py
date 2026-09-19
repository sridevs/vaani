from __future__ import annotations

import argparse
import os

from adapters import FasterWhisperRecognizer, OllamaModel, PiperSynthesizer, SileroTurnDetector
from application import VoiceConversation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Talk to a local Ollama model with Oviya")
    parser.add_argument("--ollama-model", default=os.getenv("OVIYA_OLLAMA_MODEL", "llama3.2"))
    parser.add_argument("--ollama-host", default=os.getenv("OVIYA_OLLAMA_HOST", "http://127.0.0.1:11434"))
    parser.add_argument("--whisper-model", default=os.getenv("OVIYA_WHISPER_MODEL", "small"))
    parser.add_argument("--language", default=os.getenv("OVIYA_LANGUAGE"), help="Optional language code, e.g. en or ta")
    parser.add_argument("--piper", default=os.getenv("OVIYA_PIPER", "piper"))
    parser.add_argument("--voice", required=True, help="Path to a Piper .onnx voice model")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    conversation = VoiceConversation(
        SileroTurnDetector(), FasterWhisperRecognizer(args.whisper_model),
        OllamaModel(args.ollama_model, args.ollama_host),
        PiperSynthesizer(args.piper, args.voice), args.language,
    )
    print("Oviya is ready. Press Ctrl-C to stop.")
    try:
        while True:
            response = conversation.process_turn()
            if response:
                print(f"Oviya: {response}")
    except KeyboardInterrupt:
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
