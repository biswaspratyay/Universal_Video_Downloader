from pathlib import Path
import subprocess
import sys
from urllib.parse import parse_qs, urlparse

from PySide6.QtCore import QEvent, Qt, QProcess, QTimer
from PySide6.QtGui import QAction, QColor, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QFormLayout
from PySide6.QtWidgets import (
    QBoxLayout,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QMainWindow,
    QScrollArea,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from backend.downloader import DownloadWorker
from backend.history_store import DownloadHistoryStore
from backend.image_loader import ImageLoader
from backend.notifications import play_download_complete_sound
from backend.settings import SettingsManager
from backend.thumbnail_downloader import ThumbnailDownloader
from backend.worker import AnalyzeWorker, DownloadThread, WorkerThread
from ui.dialogs.help_dialog import HelpDialog
from ui.resources import (
    ANALYZE_ICON,
    APP_ICON,
    ASSETS,
    CANCEL_ICON,
    DELETE_ICON,
    DOWNLOAD_ICON,
    FOLDER_ICON,
    PLAY_ICON,
    REFRESH_ICON,
    THUMBNAIL_PLACEHOLDER,
)
from ui.styles import load_styles
from ui.bottom_panel import build_bottom_panel
from ui.center_panel import (
    build_center_panel,
    save_download_settings,
    update_format_controls,
)
from ui.left_panel import build_left_panel
from ui.right_panel import build_right_panel
from functools import partial


def extract_url_from_mime_data(mime_data) -> str:
    urls = mime_data.urls()
    if urls:
        return urls[0].toString().strip()

    text = mime_data.text().strip()
    if text:
        return text

    return ""


class MainWindow(QMainWindow):

    def _apply_theme_palette(self, theme):
        palette = self.palette()
        text_color = "#F3F4F6" if theme == "dark" else "#0F172A"
        accent_color = "#3B82F6" if theme == "dark" else "#2563EB"

        palette.setColor(QPalette.ColorRole.WindowText, QColor(text_color))
        palette.setColor(QPalette.ColorRole.Text, QColor(text_color))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(text_color))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(text_color))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(accent_color))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

        app = QApplication.instance()
        if isinstance(app, QApplication):
            try:
                app.setPalette(palette)
            except Exception:
                pass

        self.setPalette(palette)

        for widget in self.findChildren(QWidget):
            if widget is not self:
                widget.setPalette(palette)

    def change_theme(self, theme):
        reply = QMessageBox.question(
            self,
            "Apply Theme?",
            "This will restart the app to apply the selected theme. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.current_theme = theme
        self.settings.set("theme", theme)
        self.settings.save()

        self.setStyleSheet(
            load_styles(self.current_theme)
        )
        self._apply_theme_palette(theme)
        self.statusBar().showMessage(f"Theme changed to {theme.title()}")

        QTimer.singleShot(150, lambda: self._restart_app())

    def _restart_app(self):
        current_executable = sys.executable
        if not current_executable:
            return

        project_root = Path(__file__).resolve().parent.parent
        entry_script = project_root / "main.py"

        if not entry_script.exists():
            return

        args = [str(entry_script)] + sys.argv[1:]
        working_directory = str(project_root)

        try:
            QProcess.startDetached(current_executable, args, working_directory)
        except Exception:
            try:
                subprocess.Popen([current_executable, str(entry_script)] + sys.argv[1:], cwd=working_directory)
            except Exception:
                pass

        QApplication.quit()

    def _get_download_folder(self) -> Path:
        folder = Path(self.folder_input.text()).expanduser()
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def open_download_folder(self):
        import os

        folder = self._get_download_folder()
        os.startfile(folder)

    def apply_download_settings(self):
        folder_value = self.settings.get("download_folder", "downloads")
        video_value = self.settings.get("video_format", "MP4")
        audio_value = self.settings.get("audio_format", "Original")

        if hasattr(self, "folder_input") and self.folder_input is not None:
            self.folder_input.setText(folder_value)

        if hasattr(self, "format_combo") and self.format_combo is not None:
            if self.format_combo.findText(video_value) >= 0:
                self.format_combo.setCurrentText(video_value)

        if hasattr(self, "audio_combo") and self.audio_combo is not None:
            if self.audio_combo.findText(audio_value) >= 0:
                self.audio_combo.setCurrentText(audio_value)

    def show_download_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Download Defaults")
        dialog.setModal(True)

        form_layout = QFormLayout(dialog)

        folder_edit = QLineEdit(self.settings.get("download_folder", "downloads"))
        folder_edit.setPlaceholderText("downloads")

        folder_row = QHBoxLayout()
        folder_row.addWidget(folder_edit)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(
            lambda: self._choose_default_download_folder(folder_edit)
        )
        folder_row.addWidget(browse_button)

        form_layout.addRow("Default download folder", folder_row)

        video_combo = QComboBox()
        video_combo.addItems(["MP4", "MKV", "WEBM", "MOV", "AVI"])
        video_combo.setCurrentText(self.settings.get("video_format", "MP4"))
        form_layout.addRow("Default video format", video_combo)

        audio_combo = QComboBox()
        audio_combo.addItems(["Original", "MP3", "AAC", "FLAC", "WAV", "OPUS", "OGG"])
        audio_combo.setCurrentText(self.settings.get("audio_format", "Original"))
        form_layout.addRow("Default audio format", audio_combo)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        form_layout.addRow(button_box)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.settings.set("download_folder", folder_edit.text().strip() or "downloads")
        self.settings.set("video_format", video_combo.currentText())
        self.settings.set("audio_format", audio_combo.currentText())
        self.settings.save()

        self.apply_download_settings()
        self.statusBar().showMessage("Download defaults saved")

    def _choose_default_download_folder(self, folder_edit):
        selected_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Default Download Folder",
            folder_edit.text() or self.settings.get("download_folder", "downloads"),
        )
        if selected_folder:
            folder_edit.setText(selected_folder)

    def open_latest_download(self):
        import os

        folder = self._get_download_folder()
        supported_extensions = {
            ".mp4",
            ".mkv",
            ".webm",
            ".avi",
            ".mov",
            ".m4v",
            ".mp3",
            ".m4a",
            ".wav",
            ".flv",
        }

        candidates = [
            path
            for path in folder.iterdir()
            if path.is_file() and path.suffix.lower() in supported_extensions
        ]

        if not candidates:
            self.open_download_folder()
            return

        latest_file = max(candidates, key=lambda path: path.stat().st_mtime)
        os.startfile(latest_file)

    def show_download_complete_dialog(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Download Complete")
        dialog.setText("✓ Download Complete")
        dialog.setIcon(QMessageBox.Icon.Information)

        open_folder_button = dialog.addButton("Open Folder", QMessageBox.ButtonRole.ActionRole)
        play_button = dialog.addButton("Play", QMessageBox.ButtonRole.ActionRole)
        dialog.addButton(QMessageBox.StandardButton.Close)

        dialog.exec()

        clicked_button = dialog.clickedButton()

        if clicked_button == open_folder_button:
            self.open_download_folder()
        elif clicked_button == play_button:
            self.open_latest_download()

    def show_about(self):

        QMessageBox.about(
            self,
            "About Universal Video Downloader",
            """
    <h2>Universal Video Downloader</h2>

    <p><b>Version:</b> 1.0</p>

    <p>
    -> Author: <a href="https://github.com/biswaspratyay">Pratyay Biswas</a>
    </p>

    <p>
    -> Fast • Reliable • Open Source
    </p>

    <p>
    -> Built with Python, PySide6 and yt-dlp. 
    </p>

    <p>
    -> Supports YouTube and hundreds of other websites.
    </p>

    <p>
    -> Feedback and suggestions are always welcome.
    </p>

    """,
        )

    def show_instruction(self):

        dialog = HelpDialog(self)

        dialog.exec()

    def browse_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Download Folder",
            self.folder_input.text(),
        )

        if folder:
            self.folder_input.setText(folder)

    def refresh_screen(self):

        ####################################################
        # URL
        ####################################################

        self.url_input.clear()
        self.platform_frame.setVisible(False)

        ####################################################
        # Thumbnail
        ####################################################

        pixmap = QPixmap(str(THUMBNAIL_PLACEHOLDER))

        self._set_thumbnail_pixmap(pixmap)
        self.download_thumbnail_button.setEnabled(False)

        ####################################################
        # Video Info
        ####################################################

        self.video_info = None
        self._thumbnail_source = None
        self.download_playlist = False
        self.download_source_url = ""
        self.selected_playlist_items = None
        self.playlist_summary_group.setVisible(False)
        self.video_information_group.setVisible(True)

        self.title_label.setText("-")
        self.channel_label.setText("-")
        self.duration_label.setText("-")
        self.upload_label.setText("-")
        self.views_label.setText("-")
        self.live_label.setText("-")

        ####################################################
        # Quality
        ####################################################

        self.quality_combo.clear()
        self.quality_combo.addItem("Analyze a Video First")

        self.format_combo.clear()
        self.format_combo.addItem("Analyze a Video First")
        self.format_combo.setEnabled(False)

        ####################################################
        # Selected Format
        ####################################################

        self.resolution_label.setText("-")
        self.fps_label.setText("-")
        self.type_label.setText("-")
        self.filesize_label.setText("-")

        ####################################################
        # Right Panel
        ####################################################

        self.codec_value.setText("-")
        self.container_value.setText("-")
        self.audio_value.setText("-")
        self.bitrate_value.setText("-")
        self.filesize2_value.setText("-")

        ####################################################
        # Progress
        ####################################################

        self.progress.setValue(0)
        self.progress.setFormat("%p%")

        self.downloaded_label.setText("-- / --")
        self.speed_label.setText("--")
        self.eta_label.setText("--")
        self.status_label.setText("Ready")

        self.analyze_button.setEnabled(True)
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        self.statusBar().showMessage(
            "Ready"
        ) 

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(str(APP_ICON)))
        self.video_info = None
        self.download_playlist = False
        self.download_source_url = ""
        self.selected_playlist_items = None

        self.setWindowTitle("Universal Video Downloader")
        self.resize(1200, 820)

        self.settings = SettingsManager()
        self.current_theme = self.settings.get("theme", "dark")
        self._last_clipboard_url = ""

        self.setStyleSheet(
            load_styles(self.current_theme) + "\nQWidget { font-family: 'Segoe UI'; }"
        )
        self._apply_theme_palette(self.current_theme)

        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.setInterval(1000)
        self.clipboard_timer.timeout.connect(self._check_clipboard_for_url)
        self.clipboard_timer.start()

        self.apply_download_settings()

        self.worker_thread = None
        self.worker = None
        self.current_video = None
        self.history_store = DownloadHistoryStore()

        self.create_menu()
        self.create_statusbar()
        self.build_ui()
        self._update_resume_button_state()
    

    # --------------------------------------------------------
    # Menu
    # --------------------------------------------------------

    def _handle_url_drag_enter(self, event):
        if event.mimeData() and (
            event.mimeData().hasUrls() or event.mimeData().hasText()
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def _handle_url_drop(self, event):
        url = extract_url_from_mime_data(event.mimeData())
        if url:
            self.url_input.setText(url)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _check_clipboard_for_url(self):
        if not hasattr(self, "url_input"):
            return

        clipboard = QApplication.clipboard()
        if clipboard is None:
            return

        text = clipboard.text().strip()
        if not text:
            return

        if self._looks_like_supported_url(text) and text != self._last_clipboard_url:
            self._last_clipboard_url = text
            self._prompt_clipboard_url(text)

    def _looks_like_supported_url(self, text: str) -> bool:
        lowered = text.lower()
        if not lowered.startswith(("http://", "https://")):
            return False

        supported_hosts = (
            "youtube.com",
            "www.youtube.com",
            "youtu.be",
            "m.youtube.com",
            "youtube-nocookie.com",
        )
        return any(host in lowered for host in supported_hosts)

    @staticmethod
    def _is_youtube_playlist_url(url: str) -> bool:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        is_youtube = host in {
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "music.youtube.com",
        }
        # YouTube exposes playlists both through /playlist?list=... and
        # through video URLs such as /watch?v=...&list=....
        return is_youtube and bool(parse_qs(parsed.query).get("list"))

    @staticmethod
    def _detect_platform(url: str) -> str | None:
        parsed = urlparse(url.strip())
        host = parsed.netloc.lower().split(":")[0]
        if not host:
            return None

        if host.startswith("www."):
            host = host[4:]

        platforms = {
            "youtube.com": "YouTube",
            "youtu.be": "YouTube",
            "youtube-nocookie.com": "YouTube",
            "instagram.com": "Instagram",
            "tiktok.com": "TikTok",
            "facebook.com": "Facebook",
            "x.com": "X",
            "twitter.com": "X",
        }

        for domain, platform in platforms.items():
            if host == domain or host.endswith(f".{domain}"):
                return platform

        return None

    def _update_platform_detection(self, url: str):
        if not hasattr(self, "platform_frame"):
            return

        platform = self._detect_platform(url)
        self.platform_frame.setVisible(platform is not None)
        if platform is not None:
            self.platform_value.setText(platform)
        self.playlist_detected_value.setVisible(
            bool(getattr(self.video_info, "is_playlist", False))
        )

    def _prompt_clipboard_url(self, url: str):
        reply = QMessageBox.question(
            self,
            "Clipboard URL Detected",
            "📋 YouTube link detected. Analyze?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.url_input.setText(url)
            self.analyze_video()

    def create_menu(self):

        menu = self.menuBar()

        ####################################################
        # FILE
        ####################################################

        file_menu = menu.addMenu("&File")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.refresh_screen)

        open_folder_action = QAction("Open Downloads Folder", self)
        open_folder_action.triggered.connect(
            self.open_download_folder
        )

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addSeparator()
        file_menu.addAction(open_folder_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        ####################################################
        # SETTINGS
        ####################################################

        settings_menu = menu.addMenu("&Settings")

        themes_menu = settings_menu.addMenu("Themes")

        themes = {
            "Dark": "dark",
            "Light": "light",
        }

        for text, theme in themes.items():

            action = QAction(text, self)
            action.setStatusTip("Selecting this theme will restart the app to apply it.")
            action.setToolTip("Selecting this theme will restart the app to apply it.")

            action.triggered.connect(
                partial(self.change_theme, theme)
            )

            themes_menu.addAction(action)

        settings_menu.addSeparator()

        defaults_action = QAction("Download Defaults...", self)
        defaults_action.triggered.connect(self.show_download_settings_dialog)
        settings_menu.addAction(defaults_action)

        ####################################################
        # HELP
        ####################################################

        help_menu = menu.addMenu("&Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(
            self.show_about
        )

        instruction_action = QAction("Instructions", self)
        instruction_action.triggered.connect(
            self.show_instruction
        )

        help_menu.addAction(instruction_action)
        help_menu.addAction(about_action)

    # --------------------------------------------------------
    # Status Bar
    # --------------------------------------------------------

    def create_statusbar(self):
        self.status = QStatusBar()
        self.status.showMessage("Ready")
        self.setStatusBar(self.status)

    # --------------------------------------------------------
    # Main UI
    # --------------------------------------------------------

    def build_ui(self):
        self.thumbnail_label = QLabel()

        self.thumbnail_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.thumbnail_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)

        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

       #######################################################
        # HEADER
        #######################################################

        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")

        header_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight, header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(10)
        self.header_layout = header_layout

        #######################################################
        # LOGO
        #######################################################
        logo = QLabel()

        from PySide6.QtGui import (
            QPixmap,
            QPainter,
            QPainterPath,
        )

        original = QPixmap(str(ASSETS / "icons" / "logo.png")).scaled(
            64,
            64,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        rounded = QPixmap(original.size())
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(
            0,
            0,
            original.width(),
            original.height(),
            16,     # Corner radius
            16
        )

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, original)
        painter.end()

        logo.setPixmap(rounded)

        header_layout.addWidget(logo)

        #######################################################
        # TITLE
        #######################################################

        title_layout = QVBoxLayout()
        title_layout.setSpacing(6)

        title_row = QHBoxLayout()

        self.title_label = QLabel("Universal Video Downloader")

        self.title_label.setStyleSheet("""
        QLabel{
            font-size:24px;
            font-weight:700;
            color:palette(window-text);
            background:transparent;
            border:none;
        }
        """)

        title_row.addWidget(self.title_label)

        title_row.addSpacing(12)

        self.version_badge = QLabel("v1.1")

        self.version_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.version_badge.setFixedSize(62, 30)

        self.version_badge.setStyleSheet("""
        QLabel{
            background:#2563EB;
            color:white;
            border-radius:10px;
            font-weight:700;
            font-size:12px;
        }
        """)

        title_row.addWidget(self.version_badge)
        title_row.addStretch()

        title_layout.addLayout(title_row)

        tagline = QLabel("Fast • Reliable • Open Source")

        tagline.setStyleSheet("""
        QLabel{
            background:transparent;
            border:none;
            color:palette(window-text);
            font-size:14px;
        }
        """)

        title_layout.addWidget(tagline)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        #######################################################
        # PERSONAL NOTE
        #######################################################

        note_frame = QFrame()
        note_frame.setObjectName("HeaderNoteFrame")
        note_frame.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Preferred,
        )
        self.note_frame = note_frame
        note_frame.setStyleSheet("""
            QFrame#HeaderNoteFrame {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 16px;
            }
        """)

        note_layout = QHBoxLayout(note_frame)
        note_layout.setContentsMargins(14, 10, 14, 10)
        note_layout.setSpacing(0)

        note_label = QLabel("Made with ❤️ by Pratyay Biswas")
        note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note_label.setWordWrap(True)
        note_label.setStyleSheet(
            "QLabel{ background:transparent; border:none; font-size:14px; font-weight:700; }"
        )
        note_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        note_layout.addWidget(note_label, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(note_frame)

        root.addWidget(header_frame)

        #######################################################
        # URL BAR
        #######################################################

        url_layout = QHBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste or drop a video or playlist URL...")
        self.url_input.setAcceptDrops(True)
        self.url_input.dragEnterEvent = self._handle_url_drag_enter
        self.url_input.dropEvent = self._handle_url_drop
        self.url_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.analyze_button = QPushButton(" Analyze")
        self.analyze_button.setIcon(QIcon(str(ANALYZE_ICON)))
        self.refresh_button = QPushButton("New")
        self.refresh_button.setIcon(QIcon(str(REFRESH_ICON)))
        self.refresh_button.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Preferred,
        )
        self.refresh_button.clicked.connect(self.refresh_screen)

        self.analyze_button.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Preferred,
        )

        self.analyze_button.clicked.connect(self.analyze_video)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.analyze_button)
        url_layout.addWidget(self.refresh_button)
        url_layout.setStretch(0, 4)
        url_layout.setStretch(1, 1)
        url_layout.setStretch(2, 1)

        root.addLayout(url_layout)

        self.platform_frame = QFrame()
        self.platform_frame.setObjectName("PlatformDetection")
        platform_layout = QHBoxLayout(self.platform_frame)
        platform_layout.setContentsMargins(10, 6, 10, 6)
        platform_layout.setSpacing(8)

        platform_title = QLabel("Detected Platform:")
        platform_title.setObjectName("PlatformDetectionTitle")
        self.platform_value = QLabel()
        self.platform_value.setObjectName("PlatformDetectionValue")
        self.playlist_detected_value = QLabel("Playlist Detected")
        self.playlist_detected_value.setObjectName("PlaylistDetectedValue")
        self.playlist_detected_value.setVisible(False)

        platform_layout.addWidget(platform_title)
        platform_layout.addWidget(self.platform_value)
        platform_layout.addWidget(self.playlist_detected_value)
        platform_layout.addStretch()
        self.platform_frame.setVisible(False)
        root.addWidget(self.platform_frame)

        #######################################################
        # MAIN AREA
        #######################################################

        self.main_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.main_layout.setSpacing(12)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        root.addLayout(self.main_layout)

        self.build_left_panel()
        self.build_center_panel()
        self.build_right_panel()

        #######################################################
        # BOTTOM AREA
        #######################################################

        self.build_bottom_panel(root)
        self._update_responsive_layout(self.width())

    # --------------------------------------------------------
    # PANEL BUILDERS
    # --------------------------------------------------------

    def build_left_panel(self):
        build_left_panel(self)

    def build_center_panel(self):
        build_center_panel(self)

    def _save_download_settings(self):
        save_download_settings(self)

    def _update_format_controls(self):
        update_format_controls(self)

    def build_right_panel(self):
        build_right_panel(self)

    def build_bottom_panel(self, root):
        build_bottom_panel(self, root)

    def _update_responsive_layout(self, width: int):
        narrow_main = width < 1080
        narrow_header = width < 820

        self.main_layout.setDirection(
            QBoxLayout.Direction.TopToBottom
            if narrow_main
            else QBoxLayout.Direction.LeftToRight
        )

        self.header_layout.setDirection(
            QBoxLayout.Direction.TopToBottom
            if narrow_header
            else QBoxLayout.Direction.LeftToRight
        )

        self.header_layout.setSpacing(10 if narrow_header else 12)
        self.header_layout.setContentsMargins(10, 10, 10, 10) if narrow_header else self.header_layout.setContentsMargins(14, 12, 14, 12)

        self.header_layout.setStretch(1, 1 if narrow_header else 2)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_responsive_layout(event.size().width())

    def closeEvent(self, event):
        self.clipboard_timer.stop()

        download_worker = getattr(self, "download_worker", None)
        if download_worker is not None:
            download_worker.cancel()

        active_threads = [
            thread
            for thread in (
                getattr(self, "worker_thread", None),
                getattr(self, "download_thread", None),
            )
            if thread is not None and thread.isRunning()
        ]

        for thread in active_threads:
            thread.quit()
            if not thread.wait(5000):
                self.statusBar().showMessage("Waiting for background work to stop...")
                event.ignore()
                return

        event.accept()

    def _cleanup_analysis_thread(self, thread):
        if self.worker_thread is thread:
            self.worker_thread = None
            self.worker = None

    def _cleanup_download_thread(self, thread):
        if self.download_thread is thread:
            self.download_thread = None
            self.download_worker = None

    def eventFilter(self, watched, event):
        if (
            watched is getattr(self, "thumbnail_label", None)
            and event.type() in (QEvent.Type.Resize, QEvent.Type.Show)
        ):
            self._update_thumbnail_display()

        return super().eventFilter(watched, event)

    def _set_thumbnail_pixmap(self, pixmap: QPixmap):
        self._thumbnail_source = pixmap
        self._update_thumbnail_display()

    def _update_thumbnail_display(self):
        if self._thumbnail_source is None or self._thumbnail_source.isNull():
            return

        available_size = self.thumbnail_label.contentsRect().size()
        if available_size.width() <= 0 or available_size.height() <= 0:
            return

        self.thumbnail_label.setPixmap(
            self._thumbnail_source.scaled(
                available_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def format_duration(self, seconds):
        if not seconds:
            return "--"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours:
            return f"{hours:02}:{minutes:02}:{secs:02}"

        return f"{minutes:02}:{secs:02}"

    def analyze_video(self):
        url = self.url_input.text().strip()

        if not url:
            self.status.showMessage("Please enter a URL.")
            return

        self.analyze_button.setEnabled(False)
        self.status.showMessage("Analyzing video...")
        self.platform_frame.setVisible(False)

        self.download_playlist = False
        self.download_source_url = url

        self.worker = AnalyzeWorker(url)
        self.worker_thread = WorkerThread(self.worker)

        self.worker.finished.connect(self.analysis_finished)
        self.worker.error.connect(self.analysis_error)
        self.worker_thread.finished.connect(
            lambda thread=self.worker_thread: self._cleanup_analysis_thread(thread)
        )

        self.worker_thread.start()
        self.status.showMessage(
            "Analyzing playlist..." if self.download_playlist else "Analyzing video..."
        )

    def analysis_finished(self, result=None):
        self.status.showMessage("Analysis complete.")

        if result is not None:
            self.download_playlist = result.is_playlist
            self.populate_video(result)
            self._update_platform_detection(self.download_source_url)
            self.analyze_button.setEnabled(False)

    def analysis_error(self, error):
        self.analyze_button.setEnabled(True)
        self.status.showMessage(str(error))

    def format_views(self, views) -> str:
        try:
            views = int(views)

            if views >= 1_000_000_000:
                short = f"{views / 1_000_000_000:.2f}B".rstrip("0").rstrip(".")

            elif views >= 1_000_000:
                short = f"{views / 1_000_000:.1f}M".rstrip("0").rstrip(".")

            elif views >= 1_000:
                short = f"{views / 1_000:.1f}K".rstrip("0").rstrip(".")

            else:
                return f"{views:,}"

            return f"{short} ({views:,})"

        except Exception:
            return "-"    

    def populate_video(self, info):
        self.video_info = info
        self.title_label.setText(info.title)
        self.channel_label.setText(info.uploader)
        self.duration_label.setText(self.format_duration(info.duration))
        from datetime import datetime

        date = info.upload_date

        try:
            formatted_date = datetime.strptime(date, "%Y%m%d").strftime("%d %b %Y")
        except Exception:
            formatted_date = date

        self.upload_label.setText(formatted_date)
        self.views_label.setText(self.format_views(info.view_count))
        self.live_label.setText("Yes" if info.is_live else "No")
        self.video_information_group.setVisible(not info.is_playlist)
        self.playlist_summary_group.setVisible(info.is_playlist)
        if info.is_playlist:
            self.playlist_name_value.setText(info.playlist_title or info.title)
            self.playlist_uploader_value.setText(info.uploader or "-")
            self.playlist_videos_value.setText(str(info.playlist_count))
            self.playlist_duration_value.setText(
                self.format_duration(info.playlist_duration)
            )
            self.playlist_size_value.setText(
                DownloadWorker.format_size(info.playlist_estimated_size)
                if info.playlist_estimated_size
                else "Unknown"
            )
        self.update_format_information()

        self.quality_combo.clear()

        for fmt in info.formats:
            if fmt.is_video:
                self.quality_combo.addItem(
                    fmt.display_name,
                    fmt,
                )

        self.update_format_information()        

        if info.thumbnail:
            pixmap = ImageLoader.load_from_url(info.thumbnail)

            self._set_thumbnail_pixmap(pixmap)

        self.download_thumbnail_button.setEnabled(bool(info.thumbnail))

    def choose_playlist_items(self) -> list[int] | None:
        """Show a checklist and return the selected playlist positions."""
        entries = self.video_info.playlist_entries if self.video_info else []
        if not entries:
            QMessageBox.warning(self, "Playlist unavailable", "This playlist contains no selectable videos.")
            return None

        dialog = QDialog(self)
        dialog.setWindowTitle("Choose Playlist Videos")
        dialog.setModal(True)
        dialog.resize(620, 520)

        layout = QVBoxLayout(dialog)
        description = QLabel("Select the videos to download.")
        layout.addWidget(description)

        controls = QHBoxLayout()
        select_all_button = QPushButton("Select All")
        clear_button = QPushButton("Clear")
        selected_label = QLabel()
        controls.addWidget(select_all_button)
        controls.addWidget(clear_button)
        controls.addStretch()
        controls.addWidget(selected_label)
        layout.addLayout(controls)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(8, 8, 8, 8)
        checkboxes = []
        for entry in entries:
            duration = self.format_duration(entry.duration)
            checkbox = QCheckBox(f"{entry.position:03d}. {entry.title}  ({duration})")
            checkbox.setChecked(True)
            checkbox.setProperty("playlist_position", entry.position)
            checkbox.setToolTip(entry.title)
            list_layout.addWidget(checkbox)
            checkboxes.append(checkbox)
        list_layout.addStretch()
        scroll_area.setWidget(list_widget)
        layout.addWidget(scroll_area)

        def update_count():
            count = sum(box.isChecked() for box in checkboxes)
            selected_label.setText(f"{count} of {len(checkboxes)} selected")

        for checkbox in checkboxes:
            checkbox.toggled.connect(update_count)
        select_all_button.clicked.connect(lambda: [box.setChecked(True) for box in checkboxes])
        clear_button.clicked.connect(lambda: [box.setChecked(False) for box in checkboxes])
        update_count()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Download Selected")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        selected_items = [
            box.property("playlist_position") for box in checkboxes if box.isChecked()
        ]
        if not selected_items:
            QMessageBox.information(self, "No videos selected", "Select at least one video to start the download.")
            return None
        return selected_items

    def choose_duplicate_policy(self, quality_label: str) -> str | None:
        """Ask how to handle completed files matching this download."""
        video_info = self.video_info
        if video_info is None:
            return None

        output_folder = self.folder_input.text().strip() or self.settings.get(
            "download_folder", "downloads"
        )
        if self.download_playlist:
            selected_positions = set(self.selected_playlist_items or [])
            titles = [
                entry.title
                for entry in video_info.playlist_entries
                if entry.position in selected_positions
            ]
        else:
            titles = [video_info.title]

        matches = DownloadWorker.find_matching_output_files(
            output_folder, titles, quality_label
        )
        if not matches:
            return "overwrite"

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Existing Downloads Found")
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setText(f"Found {len(matches)} matching file(s) in the output folder.")
        preview = "\n".join(f"• {path.name}" for path in matches[:5])
        if len(matches) > 5:
            preview += f"\n• and {len(matches) - 5} more"
        dialog.setInformativeText(preview)

        skip_button = dialog.addButton("Skip Existing", QMessageBox.ButtonRole.AcceptRole)
        overwrite_button = dialog.addButton("Overwrite", QMessageBox.ButtonRole.DestructiveRole)
        cancel_button = dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.exec()

        if dialog.clickedButton() == skip_button:
            return "skip"
        if dialog.clickedButton() == overwrite_button:
            return "overwrite"
        if dialog.clickedButton() == cancel_button:
            return None
        return None

    def download_thumbnail(self):
        """Save the analyzed thumbnail without resizing its source image."""
        if self.video_info is None or not self.video_info.thumbnail:
            self.statusBar().showMessage("Analyze a video with a thumbnail first.")
            return

        try:
            path = ThumbnailDownloader.download(
                self.video_info.thumbnail,
                self.folder_input.text().strip() or "downloads",
                self.video_info.title,
            )
        except Exception as error:
            self.statusBar().showMessage(f"Could not download thumbnail: {error}")
            QMessageBox.warning(self, "Thumbnail Download Failed", str(error))
            return

        self.statusBar().showMessage(f"Original thumbnail saved: {path.name}")

    def download_video(self):

        if self.video_info is None:
            return

        selected = self.quality_combo.currentData()

        if selected is None:
            return

        thread = getattr(self, "download_thread", None)
        if thread is not None and thread.isRunning():
            return

        if self.download_playlist:
            selected_items = self.choose_playlist_items()
            if selected_items is None:
                return
            self.selected_playlist_items = selected_items

        quality_label = getattr(selected, "display_name", None) or selected.format_id
        if getattr(selected, "width", None) and getattr(selected, "height", None):
            quality_label = f"{selected.width}x{selected.height}"

        duplicate_policy = self.choose_duplicate_policy(quality_label)
        if duplicate_policy is None:
            self.statusBar().showMessage("Download cancelled.")
            return

        self._save_download_settings()

        self.download_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.resume_hint_label.setVisible(False)
        self.cancel_button.setEnabled(True)

        self.progress.setValue(0)
        self.progress.setFormat("%p%")

        self.downloaded_label.setText("-- / --")
        self.speed_label.setText("--")
        self.eta_label.setText("--")
        self.status_label.setText("Preparing...")

        audio_only = self.audio_combo.currentText() == "Audio Only"

        selected_audio_format = self.audio_combo.currentText()
        if audio_only:
            selected_audio_format = "Original (Included in video)"

        self.download_worker = DownloadWorker(
            self.download_source_url if self.download_playlist else self.video_info.webpage_url,
            selected.format_id,
            self.folder_input.text().strip() or self.settings.get("download_folder", "downloads"),
            quality_label,
            audio_only=audio_only,
            audio_format=selected_audio_format,
            resume=False,
            download_playlist=self.download_playlist,
            playlist_items=self.selected_playlist_items,
            duplicate_policy=duplicate_policy,
        )

        self.download_thread = DownloadThread(self.download_worker)

        self.download_worker.progress.connect(self.update_download_progress)
        self.download_worker.finished.connect(self.download_finished)
        self.download_worker.error.connect(self.download_error)
        self.download_thread.finished.connect(
            lambda thread=self.download_thread: self._cleanup_download_thread(thread)
        )

        self.download_thread.start()

    def cancel_download(self):

        worker = getattr(self, "download_worker", None)
        thread = getattr(self, "download_thread", None)

        if worker is not None:
            self.cancel_button.setEnabled(False)
            self.status_label.setText("Cancelling...")
            self.statusBar().showMessage("Cancelling download...")
            worker.cancel()

            self.resume_button.setEnabled(False)

    def resume_download(self):

        if self.video_info is None:
            return

        selected = self.quality_combo.currentData()
        if selected is None:
            return

        thread = getattr(self, "download_thread", None)
        if thread is not None and thread.isRunning():
            return

        self._save_download_settings()

        self.download_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.resume_hint_label.setVisible(False)
        self.cancel_button.setEnabled(True)

        self.progress.setFormat("%p%")
        self.status_label.setText("Resuming...")
        self.statusBar().showMessage("Resuming download...")

        quality_label = getattr(selected, "display_name", None) or selected.format_id
        if getattr(selected, "width", None) and getattr(selected, "height", None):
            quality_label = f"{selected.width}x{selected.height}"

        audio_only = self.audio_combo.currentText() == "Audio Only"

        selected_audio_format = self.audio_combo.currentText()
        if audio_only:
            selected_audio_format = "Original (Included in video)"

        self.download_worker = DownloadWorker(
            self.download_source_url if self.download_playlist else self.video_info.webpage_url,
            selected.format_id,
            self.folder_input.text().strip() or self.settings.get("download_folder", "downloads"),
            quality_label,
            audio_only=audio_only,
            audio_format=selected_audio_format,
            resume=True,
            download_playlist=self.download_playlist,
            playlist_items=self.selected_playlist_items,
        )

        self.download_thread = DownloadThread(self.download_worker)
        self.download_worker.progress.connect(self.update_download_progress)
        self.download_worker.finished.connect(self.download_finished)
        self.download_worker.error.connect(self.download_error)
        self.download_thread.finished.connect(
            lambda thread=self.download_thread: self._cleanup_download_thread(thread)
        )
        self.download_thread.start()

    def update_download_progress(
    self,
    percent,
    downloaded,
    total,
    speed,
    status,
    eta,
):

        self.progress.setValue(int(percent))

        if "Merging" in status:
            self.progress.setFormat("Merging...")
        else:
            self.progress.setFormat("%p%")

        self.downloaded_label.setText(
            f"{downloaded} / {total}"
        )

        self.speed_label.setText(speed)

        self.eta_label.setText(eta)

        self.status_label.setText(status)
        self.download_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.resume_hint_label.setVisible(False)
        self.cancel_button.setEnabled(True)

    def _add_history_item(self, entry):
        if isinstance(entry, dict):
            title = entry.get("title", "")
            thumbnail_url = entry.get("thumbnail_url")
        else:
            title = str(entry)
            thumbnail_url = None

        item = QListWidgetItem(title)
        item.setData(Qt.ItemDataRole.UserRole, entry)

        if thumbnail_url:
            try:
                pixmap = ImageLoader.load_from_url(thumbnail_url)
                scaled = pixmap.scaled(72, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                item.setIcon(QPixmap(scaled))
            except Exception:
                pass

        self.history_list.insertItem(0, item)

    def clear_history(self):
        self.history_store.clear()
        self.history_list.clear()
        self.history_list.addItem("No downloads yet")

    def download_finished(self):

        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        self.progress.setValue(100)

        self.progress.setFormat("Completed ✓")

        self.status_label.setText("Download Completed")
        self.resume_button.setEnabled(False)
        self.resume_hint_label.setVisible(False)

        self.statusBar().showMessage(
            "Download completed successfully."
        )
        title = self.title_label.text()

        if self.history_list.count() == 1 and self.history_list.item(0).text() == "No downloads yet":
            self.history_list.clear()

        entry = f"✓ {title}"
        video_info = getattr(self, "video_info", None)
        history_entry = {
            "title": entry,
            "thumbnail_url": video_info.thumbnail if video_info is not None else None,
        }
        self.history_store.add(history_entry)
        self._add_history_item(history_entry)
        play_download_complete_sound()
        self.show_download_complete_dialog()

    def download_error(self, message):

        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        if message == "Download Cancelled":
            self.progress.setValue(0)
            self.set_ready_status("Cancelled")
            self.statusBar().showMessage("Download cancelled.")
            self.resume_button.setEnabled(False)
            self.resume_hint_label.setVisible(False)
            return

        self.status_label.setText("Download Failed ✕")
        if self._has_resume_partial():
            self.statusBar().showMessage("Download interrupted. Resume available.")
        else:
            self.statusBar().showMessage(message)
        self._update_resume_button_state()

    def update_format_information(self):

        fmt = self.quality_combo.currentData()

        if fmt is None:
            return

        ####################################################
        # Center Panel
        ####################################################

        self.resolution_label.setText(
            f"{fmt.width} × {fmt.height}"
            if fmt.width and fmt.height
            else "-"
        )

        if fmt.extension:
            self.format_combo.clear()
            self.format_combo.addItem(fmt.extension.upper())
            self.format_combo.setCurrentIndex(0)
            self.format_combo.setEnabled(False)

        self.fps_label.setText(
            f"{int(fmt.fps)} FPS"
            if fmt.fps
            else "-"
        )

        if fmt.is_audio:
            self.type_label.setText("Audio Only")
        else:
            self.type_label.setText("Video")

        size = self.format_bytes(fmt.filesize)

        self.filesize_label.setText(size)

        ####################################################
        # Right Panel
        ####################################################

        self.codec_value.setText(
    fmt.video_codec if fmt.video_codec else "-"
)

        self.container_value.setText(
            fmt.extension.upper() if fmt.extension else "-"
        )

        if fmt.audio_codec and fmt.audio_codec != "none":
            self.audio_value.setText(fmt.audio_codec.upper())
        elif fmt.is_video:
            self.audio_value.setText("AAC (Merged)")
        else:
            self.audio_value.setText("Audio Only")

        
        if fmt.bitrate is not None:
            self.bitrate_value.setText(f"{fmt.bitrate:.0f} kbps")
        else:
            self.bitrate_value.setText("-")

        self.filesize2_value.setText(size)   
        self._update_playlist_estimated_size(fmt)

    def _update_playlist_estimated_size(self, fmt) -> None:
        video = getattr(self, "video_info", None)
        if video is None or not video.is_playlist:
            return

        estimate = video.playlist_size_estimates.get(fmt.height)
        if estimate is None:
            estimate = video.playlist_estimated_size
        self.playlist_size_value.setText(
            DownloadWorker.format_size(estimate) if estimate else "Unknown"
        )

    @staticmethod
    def format_bytes(size):

        if not size:
            return "Unknown"

        units = ["B", "KB", "MB", "GB", "TB"]

        i = 0

        while size >= 1024 and i < len(units) - 1:
            size /= 1024
            i += 1

        return f"{size:.2f} {units[i]}"
    def set_ready_status(self, status_text="Ready"):

        # Reset progress and status to ready state
        try:
            self.progress.setValue(0)
            self.progress.setFormat("%p%")
        except Exception:
            pass

        try:
            self.downloaded_label.setText("-- / --")
            self.speed_label.setText("--")
            self.eta_label.setText("--")
            self.status_label.setText(status_text)
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.resume_button.setEnabled(self._has_resume_partial())
            self.resume_hint_label.setVisible(self._has_resume_partial())
            self.resume_button.setToolTip(
                "Resume the existing partial download" if self._has_resume_partial() else "No partial download available"
            )
            self.statusBar().showMessage("Ready" if status_text == "Ready" else "Download cancelled.")
        except Exception:
            pass

    def _has_resume_partial(self) -> bool:
        if getattr(self, "download_playlist", False):
            return False

        selected = getattr(self, "quality_combo", None)
        if selected is None:
            return False

        selected = self.quality_combo.currentData()
        if selected is None or self.video_info is None:
            return False

        quality_label = getattr(selected, "display_name", None) or selected.format_id
        if getattr(selected, "width", None) and getattr(selected, "height", None):
            quality_label = f"{selected.width}x{selected.height}"

        folder = self.folder_input.text().strip() or self.settings.get("download_folder", "downloads")

        dummy_worker = DownloadWorker(
            self.video_info.webpage_url,
            selected.format_id,
            folder,
            quality_label,
            audio_only=self.audio_combo.currentText() == "Audio Only",
            audio_format=self.audio_combo.currentText() if self.audio_combo.currentText() != "Audio Only" else "Original",
        )
        return bool(dummy_worker.get_partial_paths())

    def _update_resume_button_state(self):
        if not hasattr(self, "resume_button") or not hasattr(self, "resume_hint_label"):
            return

        has_resume = self._has_resume_partial()
        self.resume_button.setEnabled(has_resume)

        active_download = getattr(self, "download_thread", None)
        is_downloading = bool(active_download and active_download.isRunning())

        self.resume_hint_label.setVisible(has_resume and not is_downloading)
        self.resume_button.setToolTip(
            "Resume the existing partial download" if has_resume else "No partial download available"
        )

        if has_resume and not is_downloading:
            self.status_label.setText("Resume available")
            self.statusBar().showMessage("Partial download found. Press Resume to continue.")
    
