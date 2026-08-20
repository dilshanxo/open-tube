from PySide6.QtCore import QThread, Signal

from opentube.domain.models import MediaMetadata
from opentube.infrastructure.ytdlp import ExtractorError, YtDlpExtractor


class ExtractorWorker(QThread):
    metadata_fetched = Signal(MediaMetadata)
    error_occurred = Signal(str)

    def __init__(self, url: str) -> None:
        super().__init__()
        self._url = url
        self._extractor = YtDlpExtractor()

    def run(self) -> None:
        try:
            metadata = self._extractor.extract_metadata(self._url)
            self.metadata_fetched.emit(metadata)
        except ExtractorError as e:
            self.error_occurred.emit(str(e))
        except Exception as e:  # noqa: BLE001
            self.error_occurred.emit(f"An unexpected error occurred: {e}")
