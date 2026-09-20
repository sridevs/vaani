# Vaani

Vaani is a small local voice assistant that connects:

```text
microphone → faster-whisper → Ollama → Piper → speakers
```

The conversation stays on your Mac when Ollama, Whisper, Silero VAD, and Piper are all configured with local models. No ChatGPT, LiveKit Cloud, or paid API is required.

## Requirements

- macOS with Python 3.11 or newer
- [Ollama](https://ollama.com) with a local model already downloaded
- A Piper executable and a Piper `.onnx` voice model
- A microphone and speakers (headphones are recommended)

## Prerequisites and installation

Install each dependency before running Vaani. These commands target macOS (Apple Silicon or Intel).

**1. Python 3.11+** (skip if already installed):

```bash
brew install python@3.11
```

**2. Ollama** — the local LLM server, plus at least one chat model:

```bash
brew install ollama
ollama serve &                 # start the Ollama server (or open the Ollama app)
ollama pull llama3.2            # or any other model you plan to use, e.g. dolphin3, gemma4
ollama list                     # confirm the model is available
```

**3. Piper** — the local text-to-speech engine, installed as a Python package (provides the `piper` CLI):

```bash
source .venv/bin/activate       # after creating the venv in the Setup section below
python -m pip install piper-tts
```

**4. A Piper voice model** — download a `.onnx` voice (and its matching `.onnx.json` config) from the [Piper voices repository](https://huggingface.co/rhasspy/piper-voices/tree/main). Example, English voice:

```bash
mkdir -p ~/piper-voices
curl -L -o ~/piper-voices/en_US-lessac-medium.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
curl -L -o ~/piper-voices/en_US-lessac-medium.onnx.json \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

**5. Microphone and speaker access** — no install needed, just grant permission (see "Permissions and troubleshooting" below).

`faster-whisper` and Silero VAD do not need separate installation; they are pulled in by `requirements.txt` and download their model weights automatically on first run.

## Setup

Create a virtual environment and install the Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start Ollama and verify your model name:

```bash
ollama serve
ollama list
```

The first run downloads the faster-whisper and Silero VAD model files. After that, they run locally. Keep the Piper voice model somewhere on your Mac and note its full path.

## Run

Replace the model names and paths with the ones on your Mac:

```bash
source .venv/bin/activate
python -m vaani \
  --ollama-model llama3.2 \
  --whisper-model small \
  --voice /path/to/en_US-lessac-medium.onnx
```

For Tamil recognition, use `--language ta`. Whisper can recognize Tamil, but Piper voice availability depends on the voice model you install. If the Piper voice does not support Tamil, use an English voice for the first test and swap the TTS component later.

Useful environment variables are also supported: `VAANI_OLLAMA_MODEL`, `VAANI_OLLAMA_HOST`, `VAANI_WHISPER_MODEL`, `VAANI_LANGUAGE`, and `VAANI_PIPER`.

## Permissions and troubleshooting

On macOS, allow the terminal or Python application to use the microphone in System Settings → Privacy & Security → Microphone. If the wrong input or output device is selected, choose it in macOS Sound settings before starting Vaani.

- **Ollama connection error:** start `ollama serve` and verify `ollama list` shows the selected model.
- **No transcription:** check the microphone permission and run in a quiet room.
- **Piper not found:** pass `--piper /full/path/to/piper`.
- **No sound:** confirm the Piper voice model path and your macOS output device.
- **Slow replies:** try a smaller Whisper model or a smaller Ollama model.

## Design and tests

The code follows ports-and-adapters design. `ports.py` defines small strategy interfaces for detection, recognition, conversation, and synthesis. The `adapters/` package contains one module per concrete integration (Silero VAD, faster-whisper, Ollama, Piper). The `components` package owns the conversation flow (`VoiceConversation`) and can be tested without a microphone, model download, or network connection. Tests mirror this layout under `tests/adapters/` and `tests/application/`, with external calls (audio I/O, subprocesses, HTTP) mocked out.

Install the test dependency and run the suite with [pytest](https://docs.pytest.org/):

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

All tests under `tests/` run together as a single suite. To run just one group, use the auto-applied `adapters` or `application` markers:

```bash
python -m pytest -v -m adapters      # only adapters/ tests
python -m pytest -v -m components   # only components/ tests
```

This first version uses turn-based replies. Silero VAD detects when you stop speaking; full barge-in cancellation while Vaani is speaking is the next improvement.
