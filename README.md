# Vaani

Vaani is an open-source, local-first personal agent that aims to be an
always-available "Jarvis" for your devices. It should converse naturally,
remember context with permission, and safely take action while keeping users
in control of their data.

Today, Vaani is an early macOS-first voice assistant that connects:

```text
microphone → faster-whisper → Ollama → Piper → speakers
```

The conversation stays on your Mac when Ollama, Whisper, Silero VAD, and Piper are all configured with local models. No ChatGPT, LiveKit Cloud, or paid API is required.

## Product principles

- **Local first:** voice, transcripts, and context stay on the user's device by
  default.
- **Always available, never silently powerful:** listening and acting states
  must be visible, and consequential actions require confirmation.
- **Replaceable components:** speech recognition, language models, speech
  synthesis, memory, and tools remain swappable.
- **Natural interaction:** low latency, interruption, concise spoken responses,
  and multilingual support are first-class goals.
- **One assistant, multiple trusted devices:** desktop and mobile clients share
  an assistant identity without obscuring where data lives or actions run.

## MVP: Reliable Local Agent

The first milestone is a dependable macOS-first agent that can activate
intentionally, hold a natural voice conversation, and run a small set of safe
tools with explicit approval.

The MVP includes speech-safe responses, interruption, wake-word or push-to-talk
activation, visible runtime states, configurable local models, session context,
a typed tool contract, confirmation for consequential actions, startup
diagnostics, privacy documentation, automated tests, and contributor guidance.

Long-term memory, autonomous proactive behavior, mobile and Windows apps,
cross-device synchronization, and broad desktop automation are intentionally
post-MVP.

## Roadmap

| Phase | Outcome |
|---|---|
| Reliable Local Agent | A stable, private, contributor-ready macOS MVP |
| Memory and Personalization | User-controlled preferences and durable context |
| Desktop Experience | Native macOS experience followed by Windows support |
| Mobile Companion | iOS and Android conversations, notifications, and approvals |
| Cross-Device Agent | Secure continuity and explicit execution across trusted devices |

Implementation is tracked in the
[Vaani issues](https://github.com/sridevs/vaani/issues) and
[Vaani Roadmap](https://github.com/users/sridevs/projects/1).

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

**4. A Piper voice model** — download a `.onnx` voice (and its matching `.onnx.json` config) for your preferred language from the [Piper voices repository](https://huggingface.co/rhasspy/piper-voices/tree/main). Keep both files together and use the `.onnx` path with `--voice`:

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

## Privacy and permissions

Vaani's MVP is local-first by default. With the documented local adapters,
audio is captured from the microphone, transcribed by faster-whisper, sent as
messages to the Ollama server configured by `VAANI_OLLAMA_HOST`, converted to
speech by the local Piper process, and played through the selected speakers:

```text
microphone audio → local Whisper model → in-memory conversation → local Ollama
                                                    ↓
                                      local Piper → speakers
```

- **Audio:** microphone samples are held while the current turn is recorded
  and transcribed. Vaani does not write audio recordings or upload them.
- **Transcripts and conversation:** the recognized text and assistant replies
  are kept in the current process so later turns can use context. They are not
  written to transcript files, durable memory, or an external service by the
  MVP.
- **Models:** model files are local after download. faster-whisper and Silero
  may download model weights on first use, and the Piper voice model is
  downloaded separately by the user; review those providers and cache
  locations if the machine has restricted data requirements.
- **Tools:** the MVP does not grant tools or desktop automation permissions.
  Future tools must declare their access, keep provider-specific behavior out
  of the core, and require explicit confirmation for consequential actions.

The default Ollama endpoint is `http://127.0.0.1:11434`; `VAANI_OLLAMA_HOST`
is the configuration that changes it. Pointing that setting at another host is
an explicit opt-in to sending conversation messages off-device. There is no
other off-device conversation or telemetry integration enabled by default.
Vaani does not provide a remote-provider privacy guarantee when this setting
is changed, so review the destination's retention and deletion terms first.

The operating system may require permission for:

- **Microphone:** required to record a turn. Grant access to the terminal or
  Python application in macOS System Settings → Privacy & Security →
  Microphone.
- **Filesystem:** required to read the configured local Whisper and Piper model
  caches and the `--voice` file. Vaani does not request broad filesystem access.
- **Network:** used by the local Ollama HTTP endpoint and, during setup or
  first model use, by the separately managed model downloads. No network
  access is needed to send audio to a hosted speech service.
- **Future tools:** any tool that reads or changes files, runs commands, or
  accesses another service must document that permission and its data flow
  before it is enabled.

By default, process-held audio and conversation context disappear when Vaani
stops. The current MVP has no user-facing durable retention or deletion
control because it does not create those records; model caches remain until
the user removes them using the relevant provider's documented cache path.
For security concerns, follow the private reporting instructions in
[SECURITY.md](SECURITY.md) rather than opening a public issue.

## Run

Replace the model names and paths with the ones on your Mac:

```bash
source .venv/bin/activate
python -m vaani \
  --ollama-model llama3.2 \
  --whisper-model small \
  --voice /path/to/en_US-lessac-medium.onnx
```

Set `--language` to the language code you want Whisper to recognize, or omit it for automatic language detection. Whisper supports multiple languages; Piper voice availability and output language depend on the voice model you install. Choose a Piper voice that supports your target language.

Useful environment variables are also supported: `VAANI_OLLAMA_MODEL`, `VAANI_OLLAMA_HOST`, `VAANI_WHISPER_MODEL`, `VAANI_LANGUAGE`, and `VAANI_PIPER`.

### A sample response

Asked to introduce itself in verse, a local Llama 3.2 model running entirely on
one Mac answered:

```text
In the land of code and circuits bright
Where data flows and information takes flight
There's a world of wonder waiting to be found
In the realm of AI, where knowledge abounds

Vaani's the name, and chat is the game
We'll talk and laugh, and have a good time, it's not lame
I'll answer your questions, and help you out too
In this virtual space, where friendship shines through

So come along, don't be shy
We'll have a conversation, and reach for the sky
With language and logic, we'll navigate the way
And find the answers, come what may
```

No API key, no cloud account, no network round trip. Language models are not
deterministic, so your own first conversation will read differently.

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
python -m pytest -v -m application   # only application/ tests
```

This first version uses turn-based replies. Silero VAD detects when you stop speaking; full barge-in cancellation while Vaani is speaking is the next improvement.

## Contributing

Contributions are welcome. Start with
[CONTRIBUTING.md](CONTRIBUTING.md), then choose a ready issue labeled
[`good first issue`](https://github.com/sridevs/vaani/labels/good%20first%20issue)
or [`help wanted`](https://github.com/sridevs/vaani/labels/help%20wanted).

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
Security concerns should be reported as described in [SECURITY.md](SECURITY.md),
not in a public issue.

### Commit messages

Lead with the issue or story number, followed by a short Conventional
Commit-style type and imperative summary:

```text
[#<issue-number>] <type>: <imperative summary>
```

For example:

```text
[#27] docs: clarify privacy, permissions, and language setup
```

Use types such as `feat`, `fix`, `docs`, `test`, `refactor`, or `chore`.

## License

Vaani is licensed under the [Apache License 2.0](LICENSE).
