"""GitHub Releases API client used by the application updater."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import requests

from backend.version import (
    GITHUB_OWNER,
    GITHUB_REPOSITORY,
    LATEST_RELEASE_API,
)


class GitHubApiError(Exception):
    """A user-safe error returned while reading a GitHub release."""


@dataclass(frozen=True)
class ReleaseAsset:
    """A downloadable asset published with a GitHub release."""

    name: str
    download_url: str
    size: int


@dataclass(frozen=True)
class GitHubRelease:
    """The release fields required by the updater."""

    tag_name: str
    body: str
    published_at: str
    assets: tuple[ReleaseAsset, ...]


class GitHubReleaseClient:
    """Read release metadata from this application's GitHub repository."""

    def __init__(self, timeout: tuple[float, float] = (5.0, 20.0)):
        self.timeout = timeout

    def fetch_latest_release(self) -> GitHubRelease:
        """Return the latest published release or raise a friendly API error."""

        try:
            response = requests.get(
                LATEST_RELEASE_API,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "UniversalVideoDownloader-Updater",
                },
                timeout=self.timeout,
            )
        except requests.Timeout as error:
            raise GitHubApiError("The update check timed out. Please try again later.") from error
        except requests.ConnectionError as error:
            raise GitHubApiError("No internet connection is available for the update check.") from error
        except requests.RequestException as error:
            raise GitHubApiError("The update service could not be reached. Please try again later.") from error

        self._raise_for_response_error(response)

        try:
            payload = response.json()
        except ValueError as error:
            raise GitHubApiError("The update service returned an invalid response.") from error

        return self._parse_release(payload)

    @staticmethod
    def _raise_for_response_error(response: requests.Response) -> None:
        if response.status_code == 404:
            raise GitHubApiError("No published update is currently available.")

        if response.status_code in {403, 429}:
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                raise GitHubApiError("GitHub update checks are temporarily rate limited. Please try again later.")
            raise GitHubApiError("GitHub temporarily rejected the update check. Please try again later.")

        if not response.ok:
            raise GitHubApiError("The update service is currently unavailable. Please try again later.")

    @staticmethod
    def _parse_release(payload: Any) -> GitHubRelease:
        if not isinstance(payload, dict):
            raise GitHubApiError("The update service returned an invalid release.")

        tag_name = payload.get("tag_name")
        published_at = payload.get("published_at")
        assets_payload = payload.get("assets")

        if not isinstance(tag_name, str) or not tag_name.strip():
            raise GitHubApiError("The update release has no valid version tag.")
        if not isinstance(published_at, str) or not published_at.strip():
            raise GitHubApiError("The update release has no publication date.")
        if not isinstance(assets_payload, list):
            raise GitHubApiError("The update release has no downloadable files.")

        assets: list[ReleaseAsset] = []
        for asset_payload in assets_payload:
            asset = GitHubReleaseClient._parse_asset(asset_payload)
            if asset is not None:
                assets.append(asset)

        if not assets:
            raise GitHubApiError("The update release has no valid downloadable files.")

        body = payload.get("body")
        return GitHubRelease(
            tag_name=tag_name.strip(),
            body=body.strip() if isinstance(body, str) else "",
            published_at=published_at.strip(),
            assets=tuple(assets),
        )

    @staticmethod
    def _parse_asset(payload: Any) -> ReleaseAsset | None:
        if not isinstance(payload, dict):
            return None

        name = payload.get("name")
        download_url = payload.get("browser_download_url")
        size = payload.get("size")

        if not isinstance(name, str) or not name.strip():
            return None
        if not isinstance(download_url, str) or not GitHubReleaseClient._is_repository_asset_url(download_url):
            return None
        if not isinstance(size, int) or size <= 0:
            return None

        return ReleaseAsset(name=name.strip(), download_url=download_url, size=size)

    @staticmethod
    def _is_repository_asset_url(download_url: str) -> bool:
        parsed = urlparse(download_url)
        expected_prefix = f"/{GITHUB_OWNER}/{GITHUB_REPOSITORY}/releases/download/"
        return (
            parsed.scheme == "https"
            and parsed.netloc == "github.com"
            and parsed.path.startswith(expected_prefix)
        )
