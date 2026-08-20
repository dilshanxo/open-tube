from dataclasses import dataclass

from ..enums.media_type import MediaType


@dataclass
class AppSettings:
    download_directory: str
    default_media_type: MediaType = MediaType.VIDEO_MP4
    default_video_quality: str = "1080p"
    default_audio_quality: str = "320kbps"
