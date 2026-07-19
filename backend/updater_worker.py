"""Background Qt workers for update checks and update downloads."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import requests
from PySide6.QtCore import QObject, Signal, Slot

from backend.github_api import GitHubReleaseClient
from backend.updater import UpdateError, UpdateInfo, UpdateService


class UpdateCheckWorker(QObject):
    """Check GitHub Releases without blocking the user interface."""

    update_available = Signal(object)
    no_update = Signal()
    error = Signal(str)
    finished = Signal()

    @Slot()
    def run(self) -> None:
        try:
            update = UpdateService().check_for_update()
            if update is None:
                self.no_update.emit()
            else:
                self.update_available.emit(update)
        except UpdateError as error:
            self.error.emit(str(error))
        except Exception:
            self.error.emit("The update check could not be completed. Please try again later.")
        finally:
            self.finished.emit()


class UpdateDownloadWorker(QObject):
    """Download one verified update asset in a background thread."""

    progress = Signal(int, int, str, str, str)
    completed = Signal(object)
    cancelled = Signal()
    error = Signal(str)
    finished = Signal()

    def __init__(self, update: UpdateInfo):
        super().__init__()
        self.update = update
        self._cancel_requested = threading.Event()

    def cancel(self) -> None:
        """Request cancellation; safe to call directly from the GUI thread."""

        self._cancel_requested.set()

    @Slot()
    def run(self) -> None:
        target_file: Path | None = None

        try:
            target_file = self._download_update()
            self.completed.emit(target_file)
        except _DownloadCancelled:
            self.cancelled.emit()
        except UpdateError as error:
            self.error.emit(str(error))
        except Exception:
            self.error.emit("The update download failed. Please check your connection and try again.")
        finally:
            self.finished.emit()

    def _download_update(self) -> Path:
        asset = self.update.asset
        file_name = Path(asset.name).name
        if file_name != asset.name:
            raise UpdateError("The update file name is invalid.")
        if not GitHubReleaseClient._is_repository_asset_url(asset.download_url):
            raise UpdateError("The update download URL is not trusted.")

        target_directory = UpdateService.get_download_directory()
        target_file = target_directory / file_name
        partial_file = target_file.with_name(f"{target_file.name}.part")

        partial_file.unlink(missing_ok=True)
        target_file.unlink(missing_ok=True)

        try:
            with requests.get(
                asset.download_url,
                headers={"User-Agent": "UniversalVideoDownloader-Updater"},
                stream=True,
                timeout=(5.0, 30.0),
            ) as response:
                self._validate_response(response, asset.size)
                self._write_response(response, partial_file, asset.size)
        except _DownloadCancelled:
            partial_file.unlink(missing_ok=True)
            raise
        except requests.Timeout as error:
            partial_file.unlink(missing_ok=True)
            raise UpdateError("The update download timed out. Please try again later.") from error
        except requests.ConnectionError as error:
            partial_file.unlink(missing_ok=True)
            raise UpdateError("The update download was interrupted by a network error.") from error
        except requests.RequestException as error:
            partial_file.unlink(missing_ok=True)
            raise UpdateError("The update download could not be completed.") from error

        try:
            UpdateService.validate_download(partial_file, asset.size)
            partial_file.replace(target_file)
        except UpdateError:
            partial_file.unlink(missing_ok=True)
            target_file.unlink(missing_ok=True)
            raise

        return target_file

    @staticmethod
    def _validate_response(response: requests.Response, expected_size: int) -> None:
        if not response.ok:
            raise UpdateError("The update server could not provide the requested file.")

        content_length = response.headers.get("Content-Length")
        if content_length is None:
            return

        try:
            received_size = int(content_length)
        except ValueError as error:
            raise UpdateError("The update server returned an invalid file size.") from error

        if received_size != expected_size:
            raise UpdateError("The update file size does not match the published release.")

    def _write_response(
        self,
        response: requests.Response,
        partial_file: Path,
        total_size: int,
    ) -> None:
        downloaded = 0
        started_at = time.monotonic()

        with partial_file.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                if self._cancel_requested.is_set():
                    raise _DownloadCancelled()
                if not chunk:
                    continue

                handle.write(chunk)
                downloaded += len(chunk)
                self._emit_progress(downloaded, total_size, started_at)

        if self._cancel_requested.is_set():
            raise _DownloadCancelled()

    def _emit_progress(self, downloaded: int, total_size: int, started_at: float) -> None:
        elapsed = max(time.monotonic() - started_at, 0.001)
        bytes_per_second = downloaded / elapsed
        remaining = max(total_size - downloaded, 0)
        eta_seconds = int(remaining / bytes_per_second) if bytes_per_second else 0

        self.progress.emit(
            downloaded,
            total_size,
            f"{UpdateService.format_size(bytes_per_second)}/s",
            UpdateService.format_size(downloaded),
            self._format_eta(eta_seconds),
        )

    @staticmethod
    def _format_eta(seconds: int) -> str:
        if seconds <= 0:
            return "Less than a minute"

        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}h {minutes:02d}m remaining"
        if minutes:
            return f"{minutes}m {seconds:02d}s remaining"
        return f"{seconds}s remaining"


class _DownloadCancelled(Exception):
    """Internal control-flow signal for a cancelled update download."""
