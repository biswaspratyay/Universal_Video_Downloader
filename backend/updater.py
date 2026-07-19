"""Core update discovery and downloaded-update validation services."""

from __future__ import annotations

import tarfile
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from packaging.version import InvalidVersion, Version

from backend.github_api import GitHubApiError, GitHubRelease, GitHubReleaseClient, ReleaseAsset
from backend.platform_utils import is_linux, is_windows
from backend.version import CURRENT_VERSION


class UpdateError(Exception):
    """A user-safe error raised while preparing an application update."""


@dataclass(frozen=True)
class UpdateInfo:
    """A verified newer release and the compatible downloadable asset."""

    current_version: Version
    latest_version: Version
    published_at: str
    release_notes: str
    asset: ReleaseAsset


class UpdateService:
    """Discover and validate updates without performing GUI work."""

    def __init__(self, release_client: GitHubReleaseClient | None = None):
        self.release_client = release_client or GitHubReleaseClient()

    def check_for_update(self) -> UpdateInfo | None:
        """Return a compatible newer release, or ``None`` when already current."""

        try:
            current_version = self._parse_version(CURRENT_VERSION, "installed application")
            release = self.release_client.fetch_latest_release()
            latest_version = self._parse_version(release.tag_name, "published release")
        except GitHubApiError as error:
            raise UpdateError(str(error)) from error

        if latest_version <= current_version:
            return None

        asset = self._select_platform_asset(release)
        return UpdateInfo(
            current_version=current_version,
            latest_version=latest_version,
            published_at=release.published_at,
            release_notes=release.body,
            asset=asset,
        )

    @staticmethod
    def get_download_directory() -> Path:
        """Return the dedicated, non-application temporary update directory."""

        if is_windows():
            base_directory = Path(tempfile.gettempdir())
        elif is_linux():
            base_directory = Path("/tmp")
        else:
            raise UpdateError("Automatic updates are not supported on this operating system.")

        directory = base_directory / "UniversalVideoDownloader"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @staticmethod
    def validate_download(file_path: Path, expected_size: int) -> None:
        """Confirm that an update asset is complete and readable before reporting success."""

        if not file_path.is_file():
            raise UpdateError("The update download did not create a file.")

        actual_size = file_path.stat().st_size
        if actual_size != expected_size:
            raise UpdateError("The update download is incomplete or corrupted.")

        try:
            if file_path.name.lower().endswith(".zip"):
                with zipfile.ZipFile(file_path) as archive:
                    if archive.testzip() is not None:
                        raise UpdateError("The downloaded Windows update is corrupted.")
            elif file_path.name.lower().endswith(".tar.gz"):
                with tarfile.open(file_path, mode="r:gz") as archive:
                    archive.getmembers()
            else:
                raise UpdateError("The downloaded update has an unsupported archive format.")
        except (OSError, tarfile.TarError, zipfile.BadZipFile) as error:
            raise UpdateError("The update archive is corrupted and was not prepared.") from error

    @staticmethod
    def format_size(size: int | float) -> str:
        """Format a byte count for the update dialog."""

        value = float(size)
        units = ("B", "KB", "MB", "GB", "TB")
        unit_index = 0

        while value >= 1024 and unit_index < len(units) - 1:
            value /= 1024
            unit_index += 1

        return f"{value:.2f} {units[unit_index]}"

    @staticmethod
    def _parse_version(value: str, source: str) -> Version:
        normalized = value.strip()
        if normalized.lower().startswith("v"):
            normalized = normalized[1:]

        try:
            return Version(normalized)
        except InvalidVersion as error:
            raise UpdateError(f"The {source} version is invalid and cannot be compared.") from error

    @staticmethod
    def _select_platform_asset(release: GitHubRelease) -> ReleaseAsset:
        if is_windows():
            suffix = "windows-x64.zip"
        elif is_linux():
            suffix = "linux-x64.tar.gz"
        else:
            raise UpdateError("Automatic updates are not supported on this operating system.")

        for asset in release.assets:
            if asset.name.lower().endswith(suffix):
                return asset

        raise UpdateError("This release does not include an update for your operating system.")
