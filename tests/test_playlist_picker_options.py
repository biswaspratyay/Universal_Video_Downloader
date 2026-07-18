import unittest

from backend.downloader import DownloadWorker


class PlaylistPickerOptionTests(unittest.TestCase):
    def test_limits_playlist_download_to_selected_positions(self):
        options = DownloadWorker(
            "https://example.com/playlist", "137", "downloads",
            download_playlist=True, playlist_items=[1, 3, 8],
        ).build_options()

        self.assertEqual(options["playlist_items"], "1,3,8")


if __name__ == "__main__":
    unittest.main()
