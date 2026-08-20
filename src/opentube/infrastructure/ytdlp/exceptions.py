class ExtractorError(Exception):
    """Base exception for extraction issues."""

class UnsupportedURLError(ExtractorError):
    """Raised when the URL is not supported by yt-dlp."""

class VideoUnavailableError(ExtractorError):
    """Raised when the video is private, deleted, or otherwise unavailable."""
