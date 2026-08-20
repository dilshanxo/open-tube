---
name: ffmpeg
description: FFmpeg integration, subprocess handling, merging, audio extraction
---
# FFmpeg Skill

## Principles
- **Subprocess Handling**: Use safe `subprocess.run` with argument arrays. No `shell=True` unless strictly necessary.
- **Lifecycle**: Ensure FFmpeg processes are cleanly terminated on cancellation or shutdown.
- **Packaging**: Handle cases where FFmpeg is missing gracefully.
