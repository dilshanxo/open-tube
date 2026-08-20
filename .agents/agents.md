# OpenTube AI Engineering Constitution

## Project Purpose
OpenTube is a free, open-source desktop media downloader focused on providing a clean, modern, professional desktop experience for downloading publicly accessible media using yt-dlp and FFmpeg.

## Core Principles
1. Never sacrifice architecture for speed.
2. Never block the UI thread.
3. Never place business logic inside UI widgets.
4. Never execute shell commands unsafely.
5. Never hardcode user filesystem paths.
6. Every meaningful feature must have appropriate tests.
7. Every public behavior change must update documentation where appropriate.
8. Never create fake implementations.
9. Never leave unfinished TODO placeholders in production code.
10. Never declare a task complete without verification.
11. Do not introduce unnecessary dependencies.
12. Do not over-engineer the desktop application.
13. Keep external integrations isolated.
14. Keep the UI independent from infrastructure implementation details.
15. Preserve the project's architecture when implementing new features.

## Architecture
- Layered architecture: UI -> Application -> Domain -> Services -> Infrastructure.
- PySide6 for GUI, yt-dlp for extraction, FFmpeg for media processing.
- Workers used for background processing.

## Agent Collaboration
- Architect establishes the design.
- UI Engineer implements presentation.
- Application Engineer implements application and infrastructure logic.
- QA Engineer verifies behavior.
- DevOps Engineer handles packaging and release.
