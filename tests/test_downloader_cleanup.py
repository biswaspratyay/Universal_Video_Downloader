from pathlib import Path

from backend.downloader import DownloadWorker


def test_cleanup_partial_files_removes_temp_parts(tmp_path: Path):
    output_dir = tmp_path / "downloads"
    output_dir.mkdir()

    completed_file = output_dir / "movie.mp4"
    completed_file.write_text("done", encoding="utf-8")

    partial_file = output_dir / "movie_format-id.mp4.part"
    partial_file.write_text("partial", encoding="utf-8")

    fragment_file = output_dir / "movie_format-id.f248.webm.part"
    fragment_file.write_text("partial", encoding="utf-8")

    keep_file = output_dir / "notes.txt"
    keep_file.write_text("keep", encoding="utf-8")

    worker = DownloadWorker("https://example.com/video", "format-id", str(output_dir))
    worker.cleanup_partial_files()

    assert completed_file.exists()
    assert keep_file.exists()
    assert not partial_file.exists()
    assert not fragment_file.exists()
