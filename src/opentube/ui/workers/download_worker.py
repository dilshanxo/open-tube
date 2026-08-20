from PySide6.QtCore import QThread, Signal

from opentube.app.services.download_service import DownloadService
from opentube.domain.models import DownloadProgress, DownloadRequest


class DownloadWorker(QThread):
    progress_updated = Signal(DownloadProgress)
    error_occurred = Signal(str)

    def __init__(self, request: DownloadRequest, service: DownloadService) -> None:
        super().__init__()
        self._request = request
        self._service = service

    def run(self) -> None:
        try:
            # We pass our signal's emit method as the callback!
            self._service.start_download(self._request, self.progress_updated.emit)
        except Exception as e:  # noqa: BLE001
            self.error_occurred.emit(str(e))

    def cancel(self) -> None:
        self._service.cancel_download()
