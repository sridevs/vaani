# Oviya

Oviya is a small local voice assistant that connects:

```text
microphone → faster-whisper → Ollama → Piper → speakers
```

The conversation stays on your Mac when Ollama, Whisper, Silero VAD, and Piper are all configured with local models. No ChatGPT, LiveKit Cloud, or paid API is required.

## Requirements

- macOS with Python 3.11 or newer
- Ollama with a local model already downloaded
- A Piper executable and a Piper `.onnx` voice model
- A microphone and speakers (headphones are recommended)

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
python -m oviya \
  --ollama-model llama3.2 \
  --whisper-model small \
  --voice /path/to/en_US-lessac-medium.onnx
```

For Tamil recognition, use `--language ta`. Whisper can recognize Tamil, but Piper voice availability depends on the voice model you install. If the Piper voice does not support Tamil, use an English voice for the first test and swap the TTS component later.

Useful environment variables are also supported: `OVIYA_OLLAMA_MODEL`, `OVIYA_OLLAMA_HOST`, `OVIYA_WHISPER_MODEL`, `OVIYA_LANGUAGE`, and `OVIYA_PIPER`.

## Permissions and troubleshooting

On macOS, allow the terminal or Python application to use the microphone in System Settings → Privacy & Security → Microphone. If the wrong input or output device is selected, choose it in macOS Sound settings before starting Oviya.

- **Ollama connection error:** start `ollama serve` and verify `ollama list` shows the selected model.
- **No transcription:** check the microphone permission and run in a quiet room.
- **Piper not found:** pass `--piper /full/path/to/piper`.
- **No sound:** confirm the Piper voice model path and your macOS output device.
- **Slow replies:** try a smaller Whisper model or a smaller Ollama model.

## Design and tests

The code follows ports-and-adapters design. `ports.py` defines small strategy interfaces for detection, recognition, conversation, and synthesis. `adapters.py` contains the concrete Silero, faster-whisper, Ollama, and Piper integrations. `application.py` owns the conversation flow and can be tested without a microphone, model download, or network connection.

Run the unit tests with:

```bash
python -m unittest discover -s tests -v
```

This first version uses turn-based replies. Silero VAD detects when you stop speaking; full barge-in cancellation while Oviya is speaking is the next improvement.
