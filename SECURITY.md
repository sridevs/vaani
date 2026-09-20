# Security and Privacy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability or privacy exposure.
Use GitHub's private vulnerability reporting feature for this repository. If
that feature is unavailable, contact the repository owner privately through
their GitHub profile.

Include the affected version or commit, reproduction steps, expected impact,
and any suggested mitigation. Please do not access data that is not yours or
disrupt services while investigating.

## Privacy expectations

Vaani is local-first. Contributors must not add telemetry, upload audio,
transcripts, memories, or credentials, or enable a remote provider by default.
Any feature that sends user data off-device must:

- be explicitly enabled by the user;
- identify the destination and data being sent;
- document retention and deletion implications;
- fail visibly rather than silently changing providers;
- avoid logging secrets or sensitive conversation content.

Vaani is experimental software. Users should review configured models, tools,
permissions, and storage before relying on it for sensitive tasks.
