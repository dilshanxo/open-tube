from dataclasses import dataclass, field

from .format import MediaFormat


@dataclass
class MediaMetadata:
    video_id: str
    url: str
    title: str
    uploader: str | None = None
    duration: int | None = None
    thumbnail_url: str | None = None
    upload_date: str | None = None
    view_count: int | None = None
    extractor: str | None = None
    formats: list[MediaFormat] = field(default_factory=list)
