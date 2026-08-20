import shutil
import subprocess
from pathlib import Path

from .exceptions import FFmpegError, FFmpegNotFoundError, FFmpegProcessingError


class FFmpegRunner:
    def __init__(self, ffmpeg_path: str | None = None) -> None:
        self._ffmpeg_path = self._resolve_ffmpeg(ffmpeg_path)
        if not self._ffmpeg_path:
            raise FFmpegNotFoundError("FFmpeg executable not found in bundled assets or system PATH.")

    def _resolve_ffmpeg(self, explicit_path: str | None) -> str | None:
        if explicit_path and Path(explicit_path).is_file():
            return explicit_path
            
        # Try bundled first (assuming we might put it in assets/ffmpeg/ffmpeg.exe)
        bundled_path = Path.cwd() / "assets" / "ffmpeg" / "ffmpeg.exe"
        if bundled_path.is_file():
            return str(bundled_path)
            
        # Fallback to system PATH
        sys_path = shutil.which("ffmpeg")
        if sys_path:
            return sys_path
            
        return None

    def merge_video_audio(self, video_path: str, audio_path: str, output_path: str) -> None:
        cmd = [
            str(self._ffmpeg_path),
            "-y",  # Overwrite output files without asking
            "-i", video_path,
            "-i", audio_path,
            "-c", "copy",
            output_path
        ]
        self._run_command(cmd)

    def extract_mp3(self, input_path: str, output_path: str, quality_kbps: str = "320") -> None:
        cmd = [
            str(self._ffmpeg_path),
            "-y",
            "-i", input_path,
            "-q:a", "0",
            "-map", "a",
            "-c:a", "libmp3lame",
            "-b:a", f"{quality_kbps}k",
            output_path
        ]
        self._run_command(cmd)

    def _run_command(self, cmd: list[str]) -> None:
        try:
            # We avoid shell=True strictly.
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
            )
        except subprocess.CalledProcessError as e:
            raise FFmpegProcessingError(f"FFmpeg processing failed with code {e.returncode}: {e.stderr}") from e
        except Exception as e:
            raise FFmpegError(f"Unexpected error running FFmpeg: {e}") from e
