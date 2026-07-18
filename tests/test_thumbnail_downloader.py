import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from backend.thumbnail_downloader import ThumbnailDownloader


class ThumbnailDownloaderTests(unittest.TestCase):
    @patch("backend.thumbnail_downloader.requests.get")
    def test_saves_original_response_bytes_with_safe_filename(self, mock_get):
        response = Mock(content=b"native-image-bytes", headers={"Content-Type": "image/webp"})
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        with tempfile.TemporaryDirectory() as temp_dir:
            path = ThumbnailDownloader.download(
                "https://example.com/image", temp_dir, 'A <video>: title'
            )

            self.assertEqual(path.name, "A _video__ title_thumbnail.webp")
            self.assertEqual(path.read_bytes(), b"native-image-bytes")

    @patch("backend.thumbnail_downloader.requests.get")
    def test_preserves_url_extension_and_avoids_overwriting(self, mock_get):
        response = Mock(content=b"image", headers={})
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            (directory / "Example_thumbnail.jpg").write_bytes(b"existing")
            path = ThumbnailDownloader.download("https://example.com/image.jpg", directory, "Example")

            self.assertEqual(path.name, "Example_thumbnail (1).jpg")
            self.assertEqual(path.read_bytes(), b"image")
