import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.downloader import DownloadWorker


class MetadataOptionTests(unittest.TestCase):
    def test_enables_requested_metadata_and_thumbnail_embedding(self):
        worker = DownloadWorker(
            "https://example.com/video", "137", "downloads",
            embed_metadata=True, embed_thumbnail=True,
        )

        options = worker.build_options()

        self.assertTrue(options["addmetadata"])
        self.assertTrue(options["writethumbnail"])
        self.assertTrue(options["embedthumbnail"])

    def test_can_skip_existing_output(self):
        options = DownloadWorker(
            "https://example.com/video", "137", "downloads", duplicate_policy="skip"
        ).build_options()
        self.assertFalse(options["overwrites"])

    def test_finds_completed_matching_output_files(self):
        with TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)
            matching_file = output_dir / "My Video_1920x1080.mp4"
            matching_file.touch()
            (output_dir / "My Video_1280x720.mp4").touch()
            (output_dir / "Another Video_1920x1080.mp4").touch()
            (output_dir / "My Video_1920x1080.mp4.part").touch()

            matches = DownloadWorker.find_matching_output_files(
                temporary_directory, ["My Video"], "1920x1080"
            )

            self.assertEqual(matches, [matching_file])
