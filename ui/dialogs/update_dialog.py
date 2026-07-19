"""Dialogs used by the application update flow."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)

from backend.updater import UpdateInfo


class UpdateAvailableDialog(QDialog):
    """Present a newer release and let the user choose how to handle it."""

    def __init__(self, update: UpdateInfo, parent=None):
        super().__init__(parent)
        self.update = update
        self.choice = "later"

        self.setWindowTitle("Update Available")
        self.setModal(True)
        self.setMinimumSize(620, 460)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(14)

        title = QLabel("A new version is available")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        details = QFormLayout()
        details.setSpacing(10)
        details.addRow("Current Version", QLabel(f"v{self.update.current_version}"))
        details.addRow("Latest Version", QLabel(f"v{self.update.latest_version}"))
        details.addRow("Published", QLabel(self._format_published_date(self.update.published_at)))
        layout.addLayout(details)

        notes_label = QLabel("Release Notes")
        notes_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(notes_label)

        notes = QTextBrowser()
        notes.setOpenExternalLinks(True)
        notes.setPlainText(self.update.release_notes or "No release notes were provided.")
        notes.setMinimumHeight(180)
        layout.addWidget(notes)

        buttons = QHBoxLayout()
        buttons.addStretch()

        remind_button = QPushButton("Remind Me Later")
        remind_button.clicked.connect(self.reject)
        buttons.addWidget(remind_button)

        skip_button = QPushButton("Skip This Version")
        skip_button.clicked.connect(self._skip_version)
        buttons.addWidget(skip_button)

        download_button = QPushButton("Download Update")
        download_button.setDefault(True)
        download_button.clicked.connect(self._download_update)
        buttons.addWidget(download_button)

        layout.addLayout(buttons)

    @staticmethod
    def _format_published_date(value: str) -> str:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y")
        except ValueError:
            return value

    def _download_update(self) -> None:
        self.choice = "download"
        self.accept()

    def _skip_version(self) -> None:
        self.choice = "skip"
        self.accept()


class UpdateDownloadDialog(QDialog):
    """Show update download status and allow the user to cancel safely."""

    def __init__(self, cancel_callback: Callable[[], None], parent=None):
        super().__init__(parent)
        self._cancel_callback = cancel_callback
        self._is_downloading = True

        self.setWindowTitle("Downloading Update")
        self.setModal(True)
        self.setMinimumWidth(510)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(14)

        self.status_label = QLabel("Preparing update download...")
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        details = QFormLayout()
        details.setSpacing(8)
        self.downloaded_label = QLabel("0 B / --")
        self.speed_label = QLabel("--")
        self.eta_label = QLabel("--")
        details.addRow("Downloaded", self.downloaded_label)
        details.addRow("Speed", self.speed_label)
        details.addRow("Time Remaining", self.eta_label)
        layout.addLayout(details)

        buttons = QHBoxLayout()
        buttons.addStretch()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._request_cancel)
        buttons.addWidget(self.cancel_button)
        layout.addLayout(buttons)

    @Slot(int, int, str, str, str)
    def update_progress(
        self,
        downloaded: int,
        total: int,
        speed: str,
        downloaded_size: str,
        eta: str,
    ) -> None:
        percent = int((downloaded / total) * 100) if total else 0
        self.progress_bar.setValue(min(percent, 100))
        self.downloaded_label.setText(f"{downloaded_size} / {self._format_total(total)}")
        self.speed_label.setText(speed)
        self.eta_label.setText(eta)
        self.status_label.setText("Downloading update...")

    def show_error(self, message: str) -> None:
        self._is_downloading = False
        self.status_label.setText(message)
        self.cancel_button.setText("Close")
        self.cancel_button.clicked.disconnect()
        self.cancel_button.clicked.connect(self.reject)

    def show_completed(self) -> None:
        self._is_downloading = False
        self.progress_bar.setValue(100)
        self.status_label.setText("Download complete. The update is ready to install after restart.")
        self.eta_label.setText("Complete")
        self.cancel_button.setText("Close")
        self.cancel_button.clicked.disconnect()
        self.cancel_button.clicked.connect(self.accept)

    def close_for_result(self) -> None:
        """Close after a worker cancellation or failure without issuing another cancel."""

        self._is_downloading = False
        super().reject()

    def reject(self) -> None:
        if self._is_downloading:
            self._request_cancel()
            return
        super().reject()

    def _request_cancel(self) -> None:
        if not self._is_downloading:
            return
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Cancelling update download...")
        self._cancel_callback()

    @staticmethod
    def _format_total(total: int) -> str:
        units = ("B", "KB", "MB", "GB", "TB")
        value = float(total)
        unit_index = 0
        while value >= 1024 and unit_index < len(units) - 1:
            value /= 1024
            unit_index += 1
        return f"{value:.2f} {units[unit_index]}"
