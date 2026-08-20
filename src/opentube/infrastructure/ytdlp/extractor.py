from typing import Any

import yt_dlp
from yt_dlp.utils import DownloadError

from opentube.domain.models import MediaMetadata

from .exceptions import ExtractorError, UnsupportedURLError, VideoUnavailableError
from .parser import parse_duration, parse_formats


class YtDlpExtractor:
    def __init__(self) -> None:
        self._ydl_opts = {
            'extract_flat': 'in_playlist',
            'dump_single_json': True,
            'quiet': True,
            'no_warnings': True,
        }

    def is_supported_url(self, url: str) -> bool:
        extractors = yt_dlp.extractor.gen_extractors()
        for ie in extractors:
            if ie.suitable(url) and ie.IE_NAME != 'generic':
                return True
        return False

    def extract_metadata(self, url: str) -> MediaMetadata:
        if not self.is_supported_url(url):
            raise UnsupportedURLError(f"URL is not supported: {url}")

        try:
            with yt_dlp.YoutubeDL(self._ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise VideoUnavailableError("Could not extract any info.")
                return self._map_to_domain(info)
        except DownloadError as e:
            msg = str(e).lower()
            if "unsupported url" in msg:
                raise UnsupportedURLError(str(e))
            if "video unavailable" in msg or "private video" in msg:
                raise VideoUnavailableError(str(e))
            raise ExtractorError(str(e))
        except Exception as e:
            raise ExtractorError(f"Unexpected extraction error: {e}") from e

    def _map_to_domain(self, info: dict[str, Any]) -> MediaMetadata:
        video_id = info.get("id", "")
        url = info.get("webpage_url") or info.get("url", "")
        title = info.get("title", "Unknown Title")
        
        return MediaMetadata(
            video_id=video_id,
            url=url,
            title=title,
            uploader=info.get("uploader"),
            duration=parse_duration(info.get("duration")),
            thumbnail_url=info.get("thumbnail"),
            upload_date=info.get("upload_date"),
            view_count=info.get("view_count"),
            extractor=info.get("extractor"),
            formats=parse_formats(info.get("formats", []))
        )
