from dataclasses import dataclass

from ..enums.download_state import DownloadState
from ..enums.media_type import MediaType
from .format import PresentationOption
from .metadata import MediaMetadata


@dataclass
class DownloadRequest:
    metadata: MediaMetadata
    media_type: MediaType
    selected_option: PresentationOption
    output_path: str
    embed_thumbnail: bool = False

@dataclass
class DownloadProgress:
    state: DownloadState
    percentage: float = 0.0
    downloaded_bytes: int = 0
    total_bytes: int | None = None
    speed_bytes: float | None = None
    eta_seconds: int | None = None
