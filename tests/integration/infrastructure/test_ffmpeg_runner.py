import subprocess
from unittest.mock import MagicMock, patch

import pytest

from opentube.infrastructure.ffmpeg import FFmpegNotFoundError, FFmpegProcessingError, FFmpegRunner


def test_ffmpeg_not_found() -> None:
    with patch("shutil.which", return_value=None), patch("pathlib.Path.is_file", return_value=False), pytest.raises(FFmpegNotFoundError):
        FFmpegRunner()

@patch("subprocess.run")
def test_merge_video_audio(mock_run: MagicMock) -> None:
    with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
        with patch("pathlib.Path.is_file", return_value=False):
            runner = FFmpegRunner()
            runner.merge_video_audio("video.mp4", "audio.m4a", "output.mp4")

            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "/usr/bin/ffmpeg" in args
        assert "-y" in args
        assert "-c" in args
        assert "copy" in args
        assert "output.mp4" in args

@patch("subprocess.run")
def test_extract_mp3(mock_run: MagicMock) -> None:
    with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
        runner = FFmpegRunner()
        runner.extract_mp3("input.webm", "output.mp3", "192")
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "192k" in args
        assert "libmp3lame" in args

@patch("subprocess.run")
def test_ffmpeg_processing_error(mock_run: MagicMock) -> None:
    mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg", stderr="Invalid codec")
    with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
        runner = FFmpegRunner()
        with pytest.raises(FFmpegProcessingError) as exc:
            runner.merge_video_audio("video.mp4", "audio.m4a", "output.mp4")
        
        assert "Invalid codec" in str(exc.value)
