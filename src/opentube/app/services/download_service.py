import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yt_dlp

from opentube.app.exceptions import DownloadCancelledError
from opentube.domain.enums import DownloadState, MediaType
from opentube.domain.models import (
    AudioFormatOption,
    DownloadProgress,
    DownloadRequest,
    VideoFormatOption,
)
from opentube.infrastructure.ffmpeg import FFmpegRunner
from opentube.infrastructure.filesystem import get_temp_dir, sanitize_filename


class DownloadService:
    def __init__(self, ffmpeg_runner: FFmpegRunner | None = None) -> None:
        self._ffmpeg_runner = ffmpeg_runner or FFmpegRunner()
        self._is_cancelled = False

    def cancel_download(self) -> None:
        self._is_cancelled = True

    def start_download(self, request: DownloadRequest, progress_callback: Callable[[DownloadProgress], None]) -> None:
        self._is_cancelled = False
        
        progress = DownloadProgress(state=DownloadState.DOWNLOADING)
        progress_callback(progress)

        safe_title = sanitize_filename(request.metadata.title)
        temp_dir = get_temp_dir()
        
        temp_outtmpl = str(temp_dir / f"{safe_title}.%(ext)s")
        
        # Decide yt-dlp format string based on request
        if isinstance(request.selected_option, AudioFormatOption):
            dl_format = request.selected_option.format_id
        elif isinstance(request.selected_option, VideoFormatOption):
            dl_format = f"{request.selected_option.format_id}+bestaudio/best"
        else:
            # Fallback
            dl_format = "best"

        ydl_opts = {
            'outtmpl': temp_outtmpl,
            'quiet': True,
            'no_warnings': True,
            'format': dl_format,
            'noprogress': True,
        }

        def hook(d: dict[str, Any]) -> None:
            if self._is_cancelled:
                raise DownloadCancelledError("Download was cancelled by user.")

            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                pct = 0.0
                if total > 0:
                    pct = (downloaded / total) * 100

                progress.percentage = pct
                progress.downloaded_bytes = downloaded
                progress.total_bytes = total if total > 0 else None
                progress.speed_bytes = speed
                progress.eta_seconds = eta
                progress_callback(progress)
            elif d['status'] == 'finished':
                progress.percentage = 100.0
                progress_callback(progress)

        ydl_opts['progress_hooks'] = [hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(request.metadata.url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
            if self._is_cancelled:
                raise DownloadCancelledError("Download was cancelled by user.")

            if request.media_type == MediaType.AUDIO_MP3 and isinstance(request.selected_option, AudioFormatOption):
                progress.state = DownloadState.POST_PROCESSING
                progress_callback(progress)
                
                mp3_out = str(temp_dir / f"{safe_title}.mp3")
                kbps = str(request.selected_option.bitrate_kbps)
                    
                self._ffmpeg_runner.extract_mp3(downloaded_file, mp3_out, quality_kbps=kbps)
                
                self._safe_remove(downloaded_file)
                final_source = mp3_out
                final_dest = Path(request.output_path) / f"{safe_title}.mp3"
            else:
                final_source = downloaded_file
                final_dest = Path(request.output_path) / f"{safe_title}.mp4"

            final_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(final_source, str(final_dest))

            progress.state = DownloadState.COMPLETED
            progress_callback(progress)

        except DownloadCancelledError:
            progress.state = DownloadState.CANCELLED
            progress_callback(progress)
            self._cleanup_temp_files(temp_dir, safe_title)
        except Exception:
            progress.state = DownloadState.ERROR
            progress_callback(progress)
            self._cleanup_temp_files(temp_dir, safe_title)
            raise

    def _cleanup_temp_files(self, temp_dir: Path, safe_title: str) -> None:
        try:
            for f in temp_dir.glob(f"{safe_title}*"):
                self._safe_remove(str(f))
        except Exception:  # noqa: BLE001, S110
            pass
            
    def _safe_remove(self, path: str) -> None:
        try:
            Path(path).unlink(missing_ok=True)
        except Exception:  # noqa: BLE001, S110
            pass
