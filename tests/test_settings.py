import tempfile
import unittest
from pathlib import Path

from backend.settings import SettingsManager


class SettingsManagerTests(unittest.TestCase):
    def test_save_and_load_prefers_defaults(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = Path(temp_dir) / "settings.json"
            manager = SettingsManager(settings_path)

            manager.set("download_folder", "C:/Videos")
            manager.set("video_format", "MKV")
            manager.set("audio_format", "FLAC")
            manager.set("theme", "nord")
            manager.save()

            reloaded = SettingsManager(settings_path)

            self.assertEqual(reloaded.get("download_folder"), "C:/Videos")
            self.assertEqual(reloaded.get("video_format"), "MKV")
            self.assertEqual(reloaded.get("audio_format"), "FLAC")
            self.assertEqual(reloaded.get("theme"), "nord")


if __name__ == "__main__":
    unittest.main()
