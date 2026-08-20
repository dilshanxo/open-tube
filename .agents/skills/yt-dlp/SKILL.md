---
name: yt-dlp
description: yt-dlp integration, metadata extraction, format selection, progress handling
---
# yt-dlp Skill

## Principles
- **Metadata**: Defensive parsing of untrusted/incomplete external metadata. Use `download=False` for initial fetch.
- **Format Extraction**: Rely on yt-dlp's provided formats, do not guess.
- **Progress**: Use yt-dlp progress hooks. Transform yt-dlp specific dicts into internal domain models before passing to UI.
- **Integration**: Keep yt-dlp code strictly within the Infrastructure layer.
