import tempfile
import unittest
from pathlib import Path

from backend.history_store import DownloadHistoryStore


class DownloadHistoryStoreTests(unittest.TestCase):
    def test_add_and_load_persists_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "history.json"
            store = DownloadHistoryStore(path)

            store.add("✓ Sample video")
            store.add("✓ Another video")

            loaded = store.load()

            self.assertEqual(loaded[0]["title"], "✓ Another video")
            self.assertEqual(loaded[1]["title"], "✓ Sample video")

    def test_add_and_load_persists_thumbnail_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "history.json"
            store = DownloadHistoryStore(path)

            store.add({"title": "✓ Sample video", "thumbnail_url": "https://example.com/thumb.jpg"})

            loaded = store.load()

            self.assertEqual(loaded[0]["title"], "✓ Sample video")
            self.assertEqual(loaded[0]["thumbnail_url"], "https://example.com/thumb.jpg")


if __name__ == "__main__":
    unittest.main()
