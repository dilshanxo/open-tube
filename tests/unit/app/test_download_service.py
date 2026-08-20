from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from opentube.app.services.download_service import DownloadService
from opentube.domain.enums import DownloadState, MediaType
from opentube.domain.models import (
    AudioFormatOption,
    DownloadProgress,
    DownloadRequest,
    MediaMetadata,
    VideoFormatOption,
)
from opentube.infrastructure.ffmpeg import FFmpegRunner


@pytest.fixture
def dummy_request() -> DownloadRequest:
    meta = MediaMetadata(
        url="http://fake",
        title="Test Video",
        uploader="Test",
        duration=100,
        video_id="dummy_id",
        formats=[]
    )
    opt = VideoFormatOption(
        format_id="137",
        resolution="1080p",
        fps=30,
        video_codec="avc",
        audio_codec="aac",
        filesize_approx=1000
    )
    return DownloadRequest(
        metadata=meta,
        media_type=MediaType.VIDEO_MP4,
        selected_option=opt,
        output_path="/fake/out"
    )

@patch("opentube.app.services.download_service.yt_dlp.YoutubeDL")
@patch("shutil.move")
@patch("pathlib.Path.mkdir")
def test_successful_video_download(mock_mkdir: MagicMock, mock_move: MagicMock, mock_ydl_class: MagicMock, dummy_request: DownloadRequest) -> None:
    mock_runner = MagicMock(spec=FFmpegRunner)
    service = DownloadService(ffmpeg_runner=mock_runner)
    
    mock_ydl_instance = mock_ydl_class.return_value.__enter__.return_value
    mock_ydl_instance.prepare_filename.return_value = "/tmp/OpenTube/Test Video.mp4"
    
    states = []
    def callback(progress: DownloadProgress) -> None:
        states.append(progress.state)
        
    service.start_download(dummy_request, callback)
    
    assert DownloadState.DOWNLOADING in states
    assert DownloadState.COMPLETED in states
    mock_runner.extract_mp3.assert_not_called()
    mock_move.assert_called_once()

@patch("opentube.app.services.download_service.yt_dlp.YoutubeDL")
@patch("shutil.move")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.unlink")
def test_successful_audio_download(mock_unlink: MagicMock, mock_mkdir: MagicMock, mock_move: MagicMock, mock_ydl_class: MagicMock, dummy_request: DownloadRequest) -> None:
    dummy_request.media_type = MediaType.AUDIO_MP3
    dummy_request.selected_option = AudioFormatOption(format_id="bestaudio", bitrate_kbps=320, filesize_approx=100)
    
    mock_runner = MagicMock(spec=FFmpegRunner)
    service = DownloadService(ffmpeg_runner=mock_runner)
    
    mock_ydl_instance = mock_ydl_class.return_value.__enter__.return_value
    mock_ydl_instance.prepare_filename.return_value = "/tmp/OpenTube/Test Video.webm"
    
    states = []
    def callback(progress: DownloadProgress) -> None:
        states.append(progress.state)
        
    service.start_download(dummy_request, callback)
    
    assert DownloadState.POST_PROCESSING in states
    assert DownloadState.COMPLETED in states
    mock_runner.extract_mp3.assert_called_once()
    mock_move.assert_called_once()

@patch("opentube.app.services.download_service.yt_dlp.YoutubeDL")
def test_download_cancellation(mock_ydl_class: MagicMock, dummy_request: DownloadRequest) -> None:
    mock_runner = MagicMock(spec=FFmpegRunner)
    service = DownloadService(ffmpeg_runner=mock_runner)
    
    from opentube.app.exceptions import DownloadCancelledError
    def side_effect(*args: Any, **kwargs: Any) -> Any:
        service.cancel_download()
        raise DownloadCancelledError("simulated failure")
        
    mock_ydl_instance = mock_ydl_class.return_value.__enter__.return_value
    mock_ydl_instance.extract_info.side_effect = side_effect
    
    states = []
    def callback(progress: DownloadProgress) -> None:
        states.append(progress.state)
        
    service.start_download(dummy_request, callback)
        
    assert DownloadState.CANCELLED in states
