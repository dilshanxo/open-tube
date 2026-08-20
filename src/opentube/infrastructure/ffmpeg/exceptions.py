class FFmpegError(Exception):
    """Base exception for FFmpeg failures."""

class FFmpegNotFoundError(FFmpegError):
    """Raised when the FFmpeg executable cannot be found."""

class FFmpegProcessingError(FFmpegError):
    """Raised when the subprocess returns a non-zero exit code."""
