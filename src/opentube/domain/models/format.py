from dataclasses import dataclass


@dataclass(frozen=True)
class MediaFormat:
    format_id: str
    ext: str
    quality: str
    fps: int | None = None
    vcodec: str | None = None
    acodec: str | None = None
    filesize: int | None = None
    is_audio_only: bool = False
    abr: float | None = None
    tbr: float | None = None

@dataclass(frozen=True)
class PresentationOption:
    # Base class for UI presentation options
    pass

@dataclass(frozen=True)
class VideoFormatOption(PresentationOption):
    format_id: str
    resolution: str
    fps: int | None
    video_codec: str | None
    audio_codec: str | None
    filesize_approx: int | None
    
    @property
    def display_name(self) -> str:
        return f"{self.resolution}"

@dataclass(frozen=True)
class AudioFormatOption(PresentationOption):
    format_id: str
    bitrate_kbps: int
    filesize_approx: int | None
    
    @property
    def display_name(self) -> str:
        return f"{self.bitrate_kbps} kbps"
