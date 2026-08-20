from unittest.mock import MagicMock, patch

import pytest

from opentube.domain.models import MediaMetadata
from opentube.infrastructure.ytdlp import VideoUnavailableError, YtDlpExtractor


@pytest.fixture
def extractor() -> YtDlpExtractor:
    return YtDlpExtractor()

def test_is_supported_url_valid(extractor: YtDlpExtractor) -> None:
    assert extractor.is_supported_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True

def test_is_supported_url_invalid(extractor: YtDlpExtractor) -> None:
    assert extractor.is_supported_url("https://example.com/not-a-video") is False

@patch("opentube.infrastructure.ytdlp.extractor.yt_dlp.YoutubeDL")
def test_extract_metadata_success(mock_ydl_class: MagicMock, extractor: YtDlpExtractor) -> None:
    mock_ydl_instance = mock_ydl_class.return_value.__enter__.return_value
    mock_ydl_instance.extract_info.return_value = {
        "id": "123",
        "webpage_url": "https://test.com/123",
        "title": "Test Video",
        "duration": 120,
        "formats": [
            {
                "format_id": "18",
                "ext": "mp4",
                "height": 360,
                "vcodec": "avc1",
                "acodec": "mp4a"
            }
        ]
    }
    
    # We must patch is_supported_url since the mock URL might not trigger yt-dlp generic correctly
    with patch.object(extractor, 'is_supported_url', return_value=True):
        meta = extractor.extract_metadata("https://test.com/123")
        
        assert isinstance(meta, MediaMetadata)
        assert meta.title == "Test Video"
        assert meta.duration == 120
        assert len(meta.formats) == 1
        assert meta.formats[0].quality == "360p"

@patch("opentube.infrastructure.ytdlp.extractor.yt_dlp.YoutubeDL")
def test_extract_metadata_unavailable(mock_ydl_class: MagicMock, extractor: YtDlpExtractor) -> None:
    from yt_dlp.utils import DownloadError
    mock_ydl_instance = mock_ydl_class.return_value.__enter__.return_value
    mock_ydl_instance.extract_info.side_effect = DownloadError("Video unavailable: This video is private")
    
    with patch.object(extractor, 'is_supported_url', return_value=True), pytest.raises(VideoUnavailableError):
        extractor.extract_metadata("https://test.com/private")
