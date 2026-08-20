from enum import Enum, auto


class DownloadState(Enum):
    IDLE = auto()
    FETCHING_METADATA = auto()
    READY = auto()
    DOWNLOADING = auto()
    POST_PROCESSING = auto()
    COMPLETED = auto()
    CANCELLING = auto()
    CANCELLED = auto()
    ERROR = auto()
