# OpenTube

A free, open-source desktop media downloader built with Python, PySide6, yt-dlp, and FFmpeg.

## Features
- Clean, modern, professional desktop UI
- Download publicly accessible media using yt-dlp
- Format selection (MP4 Video, MP3 Audio) with varying qualities
- Asynchronous downloads with progress tracking
- Robust error handling and clean subprocess management

## Requirements
- Python 3.10+
- FFmpeg available in the system PATH (for merging and audio extraction)

## Development Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -e .[dev]
```

## Running Locally
```bash
python -m src.opentube
```

## License
MIT License
