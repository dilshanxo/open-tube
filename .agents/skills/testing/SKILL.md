---
name: testing
description: Pytest standards, unit/integration testing, mocking for OpenTube
---
# Testing Skill

## Principles
- **pytest**: Use pytest for all tests.
- **Deterministic**: Tests must be deterministic and should not rely on live YouTube network requests by default.
- **Mocks**: Mock external dependencies (yt-dlp, FFmpeg, network) for unit tests.
- **Coverage**: Cover format selection, filename sanitization, error mapping, state transitions.
