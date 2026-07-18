import unittest
from unittest.mock import patch

from backend.analyzer import VideoAnalyzer


class _FakeYoutubeDL:
    def __init__(self, params):
        self.params = params

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def extract_info(self, _url, download=False):
        return {
            "_type": "playlist",
            "title": "Learning Playlist",
            "uploader": "Example Channel",
            "entries": [
                {
                    "title": "Episode 1",
                    "uploader": "Example Channel",
                    "duration": 120,
                    "webpage_url": "https://youtube.com/watch?v=one",
                        "filesize_approx": 1_000,
                        "formats": [{
                            "format_id": "137",
                        "vcodec": "avc1",
                        "acodec": "none",
                            "width": 1920,
                            "height": 1080,
                            "ext": "mp4",
                            "filesize_approx": 1_000,
                        }, {
                            "format_id": "136",
                            "vcodec": "avc1",
                            "acodec": "none",
                            "width": 1280,
                            "height": 720,
                            "ext": "mp4",
                            "filesize": 500,
                        }, {
                            "format_id": "140",
                            "vcodec": "none",
                            "acodec": "mp4a",
                            "filesize": 100,
                        }],
                },
                {
                    "title": "Episode 2",
                    "duration": 180,
                    "filesize": 2_000,
                    "formats": [{
                        "format_id": "137",
                        "vcodec": "avc1",
                        "acodec": "none",
                        "height": 1080,
                        "filesize": 2_000,
                    }, {
                        "format_id": "136",
                        "vcodec": "avc1",
                        "acodec": "none",
                        "height": 720,
                        "filesize": 800,
                    }, {
                        "format_id": "140",
                        "vcodec": "none",
                        "acodec": "mp4a",
                        "filesize": 200,
                    }],
                },
            ],
        }


class PlaylistAnalyzerTests(unittest.TestCase):
    @patch("backend.analyzer.YoutubeDL", _FakeYoutubeDL)
    def test_extracts_playlist_summary_and_first_video_formats(self):
        result = VideoAnalyzer().analyze("https://youtube.com/playlist?list=PL123")

        self.assertTrue(result.is_playlist)
        self.assertEqual(result.playlist_title, "Learning Playlist")
        self.assertEqual(result.playlist_count, 2)
        self.assertEqual(result.playlist_duration, 300)
        self.assertEqual(result.playlist_estimated_size, 3_000)
        self.assertEqual(result.playlist_size_estimates[1080], 3_300)
        self.assertEqual(result.playlist_size_estimates[720], 1_600)
        self.assertEqual(result.title, "Episode 1")
        self.assertEqual(result.formats[0].format_id, "137")
        self.assertEqual(result.playlist_entries[0].webpage_url, "https://youtube.com/watch?v=one")


if __name__ == "__main__":
    unittest.main()
