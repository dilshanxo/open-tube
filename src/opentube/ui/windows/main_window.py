from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from opentube.app.services.download_service import DownloadService
from opentube.app.services.format_service import FormatSelectionService
from opentube.domain.enums import DownloadState, MediaType
from opentube.domain.models import (
    AppSettings,
    AudioFormatOption,
    DownloadProgress,
    DownloadRequest,
    MediaMetadata,
    PresentationOption,
    VideoFormatOption,
)
from opentube.ui.workers.download_worker import DownloadWorker
from opentube.ui.workers.extractor_worker import ExtractorWorker


def format_size(size_bytes: int | None) -> str:
    if not size_bytes:
        return "--"
    size_mb = size_bytes / (1024 * 1024)
    return f"{size_mb:.1f} MB"


class FormatRowWidget(QFrame):
    clicked = Signal(int)

    def __init__(self, index: int, title: str, subtitle: str, right_text: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.index = index
        self.setObjectName("FormatRow")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        self.radio = QRadioButton()
        self.radio.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.radio.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.radio)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("FormatTitle")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("FormatSubtitle")
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.right_label = QLabel(right_text)
        self.right_label.setObjectName("FormatRightText")
        layout.addWidget(self.right_label)

    def set_selected(self, selected: bool) -> None:
        self.radio.setChecked(selected)
        if selected:
            self.setProperty("selected", True)
        else:
            self.setProperty("selected", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event: Any) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OpenTube")
        self.setMinimumSize(1100, 750)
        
        self._settings = AppSettings(download_directory=str(Path.home() / "Downloads"))
        self._download_service = DownloadService()
        self._current_metadata: MediaMetadata | None = None
        
        self._video_options: list[VideoFormatOption] = []
        self._audio_options: list[AudioFormatOption] = []
        self._current_media_type = MediaType.VIDEO_MP4
        self._selected_format_idx: int = -1
        
        self._extractor_worker: ExtractorWorker | None = None
        self._download_worker: DownloadWorker | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- LEFT SIDEBAR ---
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 24, 12, 24)
        sidebar_layout.setSpacing(8)
        
        logo_layout = QHBoxLayout()
        logo_icon = QLabel("▶") # Placeholder for actual icon
        logo_icon.setObjectName("LogoIcon")
        logo_text = QLabel("OpenTube")
        logo_text.setObjectName("LogoText")
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        
        sidebar_layout.addLayout(logo_layout)
        sidebar_layout.addSpacing(32)
        
        self.btn_downloader = QPushButton("Downloader")
        self.btn_downloader.setObjectName("SidebarButtonActive")
        
        self.btn_history = QPushButton("History")
        self.btn_history.setObjectName("SidebarButton")
        
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setObjectName("SidebarButton")
        
        self.btn_about = QPushButton("About")
        self.btn_about.setObjectName("SidebarButton")
        
        sidebar_layout.addWidget(self.btn_downloader)
        sidebar_layout.addWidget(self.btn_history)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addWidget(self.btn_about)
        sidebar_layout.addStretch()
        
        main_layout.addWidget(sidebar)
        
        # --- RIGHT WORKSPACE ---
        workspace = QWidget()
        workspace.setObjectName("Workspace")
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(40, 40, 40, 40)
        workspace_layout.setSpacing(24)
        
        # 1. URL Area
        url_layout = QHBoxLayout()
        url_layout.setSpacing(12)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube link here...")
        self.url_input.setFixedHeight(44)
        
        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.setFixedHeight(44)
        self.fetch_btn.setFixedWidth(120)
        self.fetch_btn.setObjectName("FetchButton")
        self.fetch_btn.clicked.connect(self._on_fetch_clicked)
        
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.fetch_btn)
        workspace_layout.addLayout(url_layout)
        
        # 2. Metadata Card (Hidden initially)
        self.meta_card = QFrame()
        self.meta_card.setObjectName("MetaCard")
        meta_layout = QHBoxLayout(self.meta_card)
        meta_layout.setContentsMargins(20, 20, 20, 20)
        meta_layout.setSpacing(24)
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(160, 90)
        self.thumbnail_label.setObjectName("ThumbnailPlaceholder")
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        meta_details_layout = QVBoxLayout()
        meta_details_layout.setSpacing(4)
        
        self.title_label = QLabel("Title")
        self.title_label.setObjectName("MetaTitle")
        self.title_label.setWordWrap(True)
        
        self.uploader_label = QLabel("Channel Name")
        self.uploader_label.setObjectName("MetaUploader")
        
        self.duration_label = QLabel("Duration")
        self.duration_label.setObjectName("MetaDuration")
        
        meta_details_layout.addWidget(self.title_label)
        meta_details_layout.addWidget(self.uploader_label)
        meta_details_layout.addWidget(self.duration_label)
        meta_details_layout.addStretch()
        
        meta_layout.addWidget(self.thumbnail_label)
        
        meta_details_widget = QWidget()
        meta_details_widget.setLayout(meta_details_layout)
        meta_layout.addWidget(meta_details_widget, 1)
        
        self.meta_card.setVisible(False)
        workspace_layout.addWidget(self.meta_card)
        
        # 3. Middle Config Area (Options and Formats)
        self.config_widget = QWidget()
        config_layout = QHBoxLayout(self.config_widget)
        config_layout.setContentsMargins(0, 0, 0, 0)
        config_layout.setSpacing(24)
        
        # 3a. Download Options (Left Col)
        options_panel = QWidget()
        options_layout = QVBoxLayout(options_panel)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(16)
        
        options_title = QLabel("Download Options")
        options_title.setObjectName("SectionTitle")
        options_layout.addWidget(options_title)
        
        # Segmented Control for Type
        type_label = QLabel("Type")
        type_label.setObjectName("FieldLabel")
        options_layout.addWidget(type_label)
        
        segment_widget = QWidget()
        segment_layout = QHBoxLayout(segment_widget)
        segment_layout.setContentsMargins(0, 0, 0, 0)
        segment_layout.setSpacing(0)
        
        self.btn_mp4 = QPushButton("Video (MP4)")
        self.btn_mp4.setCheckable(True)
        self.btn_mp4.setChecked(True)
        self.btn_mp4.setObjectName("SegmentLeft")
        self.btn_mp4.setFixedHeight(40)
        
        self.btn_mp3 = QPushButton("Audio (MP3)")
        self.btn_mp3.setCheckable(True)
        self.btn_mp3.setObjectName("SegmentRight")
        self.btn_mp3.setFixedHeight(40)
        
        self.btn_mp4.clicked.connect(lambda: self._set_media_type(MediaType.VIDEO_MP4))
        self.btn_mp3.clicked.connect(lambda: self._set_media_type(MediaType.AUDIO_MP3))
        
        segment_layout.addWidget(self.btn_mp4)
        segment_layout.addWidget(self.btn_mp3)
        options_layout.addWidget(segment_widget)
        
        options_layout.addSpacing(16)
        
        # Save To
        save_label = QLabel("Save To")
        save_label.setObjectName("FieldLabel")
        options_layout.addWidget(save_label)
        
        save_layout = QHBoxLayout()
        save_layout.setSpacing(8)
        self.path_input = QLineEdit(self._settings.download_directory)
        self.path_input.setReadOnly(True)
        self.path_input.setFixedHeight(40)
        
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.setFixedHeight(40)
        self.btn_browse.setObjectName("SecondaryButton")
        
        save_layout.addWidget(self.path_input)
        save_layout.addWidget(self.btn_browse)
        options_layout.addLayout(save_layout)
        
        options_layout.addStretch()
        
        # 3b. Formats List (Right Col)
        formats_panel = QWidget()
        formats_layout = QVBoxLayout(formats_panel)
        formats_layout.setContentsMargins(0, 0, 0, 0)
        formats_layout.setSpacing(16)
        
        self.formats_title = QLabel("Available Video Qualities")
        self.formats_title.setObjectName("SectionTitle")
        formats_layout.addWidget(self.formats_title)
        
        self.formats_scroll = QScrollArea()
        self.formats_scroll.setWidgetResizable(True)
        self.formats_scroll.setObjectName("FormatsScroll")
        
        self.formats_content = QWidget()
        self.formats_content.setObjectName("FormatsContent")
        self.formats_list_layout = QVBoxLayout(self.formats_content)
        self.formats_list_layout.setContentsMargins(0, 0, 0, 0)
        self.formats_list_layout.setSpacing(8)
        self.formats_list_layout.addStretch()
        
        self.formats_scroll.setWidget(self.formats_content)
        formats_layout.addWidget(self.formats_scroll)
        
        config_layout.addWidget(options_panel, 4)
        config_layout.addWidget(formats_panel, 6)
        
        self.config_widget.setVisible(False)
        workspace_layout.addWidget(self.config_widget, 1)
        
        # 4. Bottom Action Area
        self.action_card = QFrame()
        self.action_card.setObjectName("ActionCard")
        action_layout = QVBoxLayout(self.action_card)
        action_layout.setContentsMargins(24, 20, 24, 20)
        action_layout.setSpacing(16)
        
        top_action_layout = QHBoxLayout()
        self.status_icon = QLabel() # Empty or spinner or check
        self.status_icon.setFixedSize(24, 24)
        self.status_icon.setObjectName("StatusIcon")
        
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("StatusLabel")
        
        top_action_layout.addWidget(self.status_icon)
        top_action_layout.addWidget(self.status_label)
        top_action_layout.addStretch()
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedSize(100, 44)
        self.btn_cancel.setObjectName("SecondaryButton")
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self._on_cancel_clicked)
        
        self.btn_open_folder = QPushButton("Open Folder")
        self.btn_open_folder.setFixedSize(120, 44)
        self.btn_open_folder.setObjectName("SecondaryButton")
        self.btn_open_folder.setVisible(False)
        
        self.btn_download = QPushButton("Download MP4")
        self.btn_download.setFixedSize(160, 44)
        self.btn_download.setObjectName("PrimaryButton")
        self.btn_download.clicked.connect(self._on_download_clicked)
        
        top_action_layout.addWidget(self.btn_cancel)
        top_action_layout.addWidget(self.btn_open_folder)
        top_action_layout.addWidget(self.btn_download)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        
        action_layout.addLayout(top_action_layout)
        action_layout.addWidget(self.progress_bar)
        
        self.action_card.setVisible(False)
        workspace_layout.addWidget(self.action_card)
        
        main_layout.addWidget(workspace)

    def _on_fetch_clicked(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            return
            
        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Fetching...")
        
        self._extractor_worker = ExtractorWorker(url)
        self._extractor_worker.metadata_fetched.connect(self._on_metadata_fetched)
        self._extractor_worker.error_occurred.connect(self._on_error)
        self._extractor_worker.start()

    def _on_metadata_fetched(self, metadata: MediaMetadata) -> None:
        self._current_metadata = metadata
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch")
        
        self.title_label.setText(metadata.title)
        self.uploader_label.setText(metadata.uploader or "Unknown")
        
        dur_str = f"{metadata.duration // 60}:{metadata.duration % 60:02d}" if metadata.duration else "Unknown"
        self.duration_label.setText(dur_str)
        
        self._video_options = FormatSelectionService.get_video_options(metadata)
        self._audio_options = FormatSelectionService.get_audio_options(metadata)
        
        self.meta_card.setVisible(True)
        self.config_widget.setVisible(True)
        self.action_card.setVisible(True)
        
        self._set_media_type(self._current_media_type)
        self.status_label.setText("Ready to download")

    def _set_media_type(self, mtype: MediaType) -> None:
        self._current_media_type = mtype
        self._selected_format_idx = -1
        
        if mtype == MediaType.VIDEO_MP4:
            self.btn_mp4.setChecked(True)
            self.btn_mp3.setChecked(False)
            self.formats_title.setText("Available Video Qualities")
            self.btn_download.setText("Download MP4")
            self._render_video_list()
        else:
            self.btn_mp4.setChecked(False)
            self.btn_mp3.setChecked(True)
            self.formats_title.setText("Available Audio Qualities")
            self.btn_download.setText("Download MP3")
            self._render_audio_list()
            
        self._update_download_button_state()

    def _clear_formats_layout(self) -> None:
        while self.formats_list_layout.count() > 1:
            item = self.formats_list_layout.takeAt(0)
            if item is not None:
                w = item.widget()
                if w is not None:
                    w.deleteLater()

    def _render_video_list(self) -> None:
        self._clear_formats_layout()
        
        for i, opt in enumerate(self._video_options):
            vc = opt.video_codec or "unknown"
            ac = opt.audio_codec or "unknown"
            subtitle = f"MP4 • {opt.fps} FPS" if opt.fps else "MP4"
            subtitle += f" • {vc} + {ac}"
            right_text = format_size(opt.filesize_approx)
            
            row = FormatRowWidget(i, opt.resolution, subtitle, right_text)
            row.clicked.connect(self._on_format_row_clicked)
            self.formats_list_layout.insertWidget(i, row)
            
        if self._video_options:
            self._on_format_row_clicked(0)

    def _render_audio_list(self) -> None:
        self._clear_formats_layout()
        
        for i, opt in enumerate(self._audio_options):
            title = f"{opt.bitrate_kbps} kbps"
            subtitle = "High quality MP3" if opt.bitrate_kbps >= 256 else "Standard quality MP3"
            right_text = format_size(opt.filesize_approx)
            
            row = FormatRowWidget(i, title, subtitle, right_text)
            row.clicked.connect(self._on_format_row_clicked)
            self.formats_list_layout.insertWidget(i, row)
            
        if self._audio_options:
            self._on_format_row_clicked(0)

    def _on_format_row_clicked(self, index: int) -> None:
        self._selected_format_idx = index
        
        # Update UI selection state
        for i in range(self.formats_list_layout.count() - 1):
            item = self.formats_list_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if isinstance(widget, FormatRowWidget):
                    widget.set_selected(widget.index == index)
                
        self._update_download_button_state()

    def _update_download_button_state(self) -> None:
        self.btn_download.setEnabled(self._selected_format_idx >= 0)

    def _get_selected_option(self) -> PresentationOption | None:
        if self._selected_format_idx < 0:
            return None
            
        if self._current_media_type == MediaType.VIDEO_MP4:
            if self._selected_format_idx < len(self._video_options):
                return self._video_options[self._selected_format_idx]
        else:
            if self._selected_format_idx < len(self._audio_options):
                return self._audio_options[self._selected_format_idx]
        return None

    def _on_download_clicked(self) -> None:
        if not self._current_metadata:
            return
            
        selected_opt = self._get_selected_option()
        if not selected_opt:
            return
            
        request = DownloadRequest(
            metadata=self._current_metadata,
            media_type=self._current_media_type,
            selected_option=selected_opt,
            output_path=self._settings.download_directory
        )
        
        self.btn_download.setVisible(False)
        self.btn_open_folder.setVisible(False)
        self.btn_cancel.setVisible(True)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setStyleSheet("color: #FFFFFF;")
        
        # Disable interaction
        self.btn_mp4.setEnabled(False)
        self.btn_mp3.setEnabled(False)
        self.url_input.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        
        for i in range(self.formats_list_layout.count() - 1):
            item = self.formats_list_layout.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setEnabled(False)
        
        self._download_worker = DownloadWorker(request, self._download_service)
        self._download_worker.progress_updated.connect(self._on_progress_updated)
        self._download_worker.error_occurred.connect(self._on_download_error)
        self._download_worker.start()

    def _on_progress_updated(self, progress: DownloadProgress) -> None:
        if progress.state == DownloadState.DOWNLOADING:
            self.progress_bar.setValue(int(progress.percentage))
            self.status_label.setText(f"Downloading... {progress.percentage:.1f}%")
        elif progress.state == DownloadState.POST_PROCESSING:
            self.status_label.setText("Processing with FFmpeg...")
            self.progress_bar.setValue(0)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
        elif progress.state == DownloadState.COMPLETED:
            self._reset_download_ui()
            self.status_label.setText("Download Complete")
            self.status_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
            self.btn_open_folder.setVisible(True)
        elif progress.state == DownloadState.CANCELLED:
            self._reset_download_ui()
            self.status_label.setText("Download Cancelled.")

    def _on_cancel_clicked(self) -> None:
        if self._download_worker and self._download_worker.isRunning():
            self._download_worker.cancel()
            self.status_label.setText("Cancelling...")
            self.btn_cancel.setEnabled(False)

    def _on_error(self, message: str) -> None:
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch")
        QMessageBox.critical(self, "Error", message)
        
    def _on_download_error(self, message: str) -> None:
        self._reset_download_ui()
        self.status_label.setText("Download Failed.")
        QMessageBox.critical(self, "Download Error", message)

    def _reset_download_ui(self) -> None:
        self.btn_download.setVisible(True)
        self.btn_cancel.setVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(100)
        
        self.btn_mp4.setEnabled(True)
        self.btn_mp3.setEnabled(True)
        self.url_input.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        
        for i in range(self.formats_list_layout.count() - 1):
            item = self.formats_list_layout.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setEnabled(True)
