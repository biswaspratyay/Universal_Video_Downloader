import unittest

from backend.downloader import DownloadWorker


class DownloadWorkerOutputTests(unittest.TestCase):
    def test_output_options_use_quality_label_and_overwrite(self):
        worker = DownloadWorker("https://example.com/video", "137", "downloads", "1080p")
        options = worker.build_options()

        self.assertIn("1080p", options["outtmpl"])
        self.assertTrue(options["overwrites"])

    def test_playlist_options_download_all_items_with_numbered_filenames(self):
        worker = DownloadWorker(
            "https://youtube.com/playlist?list=PL123",
            "137",
            "downloads",
            "1080p",
            download_playlist=True,
        )
        options = worker.build_options()

        self.assertFalse(options["noplaylist"])
        self.assertIn("%(playlist_title)s", options["outtmpl"])
        self.assertIn("%(playlist_index)03d", options["outtmpl"])
        self.assertEqual(options["format"], "bv*+ba/b")

    def test_playlist_uses_a_per_video_quality_selector(self):
        worker = DownloadWorker(
            "https://youtube.com/playlist?list=PL123",
            "137",
            "downloads",
            "1920x1080",
            download_playlist=True,
        )

        self.assertEqual(
            worker.build_options()["format"],
            "bv*[height<=1080]+ba/b[height<=1080]/b",
        )

    def test_reads_playlist_progress_position_from_yt_dlp_data(self):
        self.assertEqual(
            DownloadWorker._playlist_position({
                "info_dict": {"playlist_index": 7, "playlist_count": 42}
            }),
            (7, 42),
        )


if __name__ == "__main__":
    unittest.main()
