import unittest

from ui.main_window import MainWindow


class PlatformDetectionTests(unittest.TestCase):
    def test_detects_youtube_urls(self):
        self.assertEqual(
            MainWindow._detect_platform("https://www.youtube.com/watch?v=abc123"),
            "YouTube",
        )
        self.assertEqual(
            MainWindow._detect_platform("https://youtu.be/abc123"),
            "YouTube",
        )

    def test_recognizes_youtube_playlist_urls(self):
        self.assertTrue(
            MainWindow._is_youtube_playlist_url(
                "https://youtube.com/playlist?list=PL123"
            )
        )
        self.assertTrue(
            MainWindow._is_youtube_playlist_url(
                "https://www.youtube.com/playlist/?list=PL123&index=1"
            )
        )
        self.assertTrue(
            MainWindow._is_youtube_playlist_url(
                "https://www.youtube.com/watch?v=abc123&list=PL123"
            )
        )
        self.assertTrue(
            MainWindow._is_youtube_playlist_url(
                "https://music.youtube.com/watch?v=abc123&list=PL123"
            )
        )
        self.assertFalse(
            MainWindow._is_youtube_playlist_url(
                "https://example.com/playlist?list=PL123"
            )
        )

    def test_detects_instagram_urls(self):
        self.assertEqual(
            MainWindow._detect_platform("https://www.instagram.com/reel/example/"),
            "Instagram",
        )

    def test_ignores_unknown_and_lookalike_hosts(self):
        self.assertIsNone(MainWindow._detect_platform("https://example.com/video"))
        self.assertIsNone(
            MainWindow._detect_platform("https://notyoutube.com/watch?v=abc123")
        )


if __name__ == "__main__":
    unittest.main()
