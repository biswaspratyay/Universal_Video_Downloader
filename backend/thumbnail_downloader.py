"""Download video thumbnails without changing their original image data."""

from __future__ import annotations

import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests


class ThumbnailDownloader:
    """Save the image served by a thumbnail URL at its native dimensions."""

    _FALLBACK_EXTENSION = ".jpg"

    @classmethod
    def download(cls, url: str, output_directory: str | Path, title: str = "thumbnail") -> Path:
        if not url:
            raise ValueError("No thumbnail is available for this video.")

        response = requests.get(url, timeout=20)
        response.raise_for_status()

        destination_dir = Path(output_directory).expanduser()
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = cls._available_path(
            destination_dir,
            cls._safe_stem(title),
            cls._extension(url, response.headers.get("Content-Type", "")),
        )
        destination.write_bytes(response.content)
        return destination

    @staticmethod
    def _safe_stem(title: str) -> str:
        stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title).strip(" .")
        return stem or "thumbnail"

    @classmethod
    def _extension(cls, url: str, content_type: str) -> str:
        suffix = Path(unquote(urlparse(url).path)).suffix.lower()
        if suffix and len(suffix) <= 5:
            return suffix

        mime_type = content_type.split(";", 1)[0].strip().lower()
        return mimetypes.guess_extension(mime_type) or cls._FALLBACK_EXTENSION

    @staticmethod
    def _available_path(directory: Path, stem: str, extension: str) -> Path:
        candidate = directory / f"{stem}_thumbnail{extension}"
        number = 1
        while candidate.exists():
            candidate = directory / f"{stem}_thumbnail ({number}){extension}"
            number += 1
        return candidate
