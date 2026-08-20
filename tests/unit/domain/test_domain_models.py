from opentube.domain.enums import DownloadState, MediaType
from opentube.domain.models import (
    AppSettings,
    DownloadProgress,
    MediaFormat,
    MediaMetadata,
)


def test_media_format_instantiation() -> None:
    fmt = MediaFormat(
        format_id="137",
        ext="mp4",
        quality="1080p",
        fps=60,
        is_audio_only=False
    )
    assert fmt.format_id == "137"
    assert fmt.quality == "1080p"
    assert fmt.is_audio_only is False

def test_media_metadata_defaults() -> None:
    meta = MediaMetadata(
        video_id="dQw4w9WgXcQ",
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        title="Rick Astley - Never Gonna Give You Up"
    )
    assert meta.video_id == "dQw4w9WgXcQ"
    assert meta.duration is None
    assert meta.formats == []

def test_download_progress_state() -> None:
    progress = DownloadProgress(state=DownloadState.IDLE)
    assert progress.state == DownloadState.IDLE
    assert progress.percentage == 0.0

def test_app_settings_defaults() -> None:
    settings = AppSettings(download_directory="C:/Downloads")
    assert settings.download_directory == "C:/Downloads"
    assert settings.default_media_type == MediaType.VIDEO_MP4
