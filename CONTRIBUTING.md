# Contributing to Vaani

Thank you for helping build a private, local-first personal agent.

## Before you start

1. Read the issue and its acceptance criteria.
2. Comment on the issue before beginning substantial work.
3. Keep the change focused on one user-visible or contributor-visible outcome.
4. Ask maintainers before introducing a hosted service, telemetry, or a new
   runtime dependency.

Issues marked `good first issue` are intended to be independently deliverable.
Issues marked `needs-design` require agreement on an approach before code is
written.

Use the [Vaani Roadmap](https://github.com/users/sridevs/projects/1) to find
work in `Ready`. Epics describe product outcomes; their linked sub-issues are
the independently deliverable stories.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

See the README for Ollama, Piper, model, and microphone setup.

## Architecture

Vaani follows ports-and-adapters design:

- `ports.py` defines integration-neutral protocols.
- `components/` owns application behavior and orchestration.
- `adapters/` integrates external engines and operating-system resources.
- `vaani/` wires concrete implementations into the command-line application.
- `tests/` mirrors application and adapter boundaries.

Keep model-, engine-, and platform-specific behavior in adapters. Keep
conversation policy and agent orchestration in components. Do not make the core
depend on one model provider or operating system.

## Pull requests

- Add or update tests for changed behavior.
- Preserve local-first behavior unless the issue explicitly introduces an
  opt-in integration.
- Surface errors with actionable messages; do not silently fall back to a
  remote service.
- Update user documentation when setup, configuration, or behavior changes.
- Complete the pull request template and link the issue being addressed.

Run the smallest relevant test group before opening a pull request:

```bash
python -m pytest -v -m application
python -m pytest -v -m adapters
```

## Commit authorship

Use an email verified by your GitHub account, or your GitHub noreply address,
so contributions are attributed correctly.
