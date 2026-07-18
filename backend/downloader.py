import re
from pathlib import Path
from typing import Any, cast

from yt_dlp import YoutubeDL

from PySide6.QtCore import QObject, Signal

from ui.resources import FFMPEG_FOLDER


class DownloadCancelled(Exception):
    """Raised when the user cancels the download."""

    pass


class DownloadWorker(QObject):
    # percent, downloaded, total, speed, status, eta
    progress = Signal(float, str, str, str, str, str)

    finished = Signal()

    error = Signal(str)

    def __init__(
        self,
        url: str,
        format_id: str,
        output_folder: str,
        quality_label: str | None = None,
        audio_only: bool = False,
        audio_format: str | None = None,
        resume: bool = False,
        download_playlist: bool = False,
        playlist_items: list[int] | None = None,
        duplicate_policy: str = "overwrite",
        embed_metadata: bool = False,
        embed_thumbnail: bool = False,
    ):
        super().__init__()

        self.url = url
        self.format_id = format_id
        self.output_folder = output_folder
        self.quality_label = quality_label or format_id
        self.audio_only = audio_only
        self.audio_format = audio_format or "Original"
        self.resume = resume
        self.download_playlist = download_playlist
        self.playlist_items = playlist_items
        self.duplicate_policy = duplicate_policy
        self.embed_metadata = embed_metadata
        self.embed_thumbnail = embed_thumbnail

        # Cancel flag
        self.cancel_requested = False

    ########################################################
    # Cancel Download
    ########################################################

    def cancel(self):
        self.cancel_requested = True

    ########################################################
    # Helpers
    ########################################################

    @staticmethod
    def format_size(size: int | float) -> str:

        if not size:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]

        value = float(size)

        unit = 0

        while value >= 1024 and unit < len(units) - 1:
            value /= 1024
            unit += 1

        return f"{value:.2f} {units[unit]}"

    @staticmethod
    def format_eta(seconds) -> str:

        if seconds is None:
            return "--"

        seconds = int(seconds)

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours:
            return f"{hours}h {minutes:02d}m"

        if minutes:
            return f"{minutes}m {secs:02d}s"

        return f"{secs}s"

    def cleanup_partial_files(self) -> None:
        for path in self.get_partial_paths():
            try:
                path.unlink()
            except FileNotFoundError:
                continue

    def get_partial_paths(self) -> list[Path]:
        output_dir = Path(self.output_folder)

        if not output_dir.exists():
            return []

        safe_label = re.sub(r"[^A-Za-z0-9]+", "_", self.quality_label).strip("_").lower()
        partial_paths: list[Path] = []

        for path in output_dir.iterdir():
            if not path.is_file():
                continue

            if path.suffix.lower() != ".part":
                continue

            if f"_{safe_label}." in path.name.lower():
                partial_paths.append(path)

        return partial_paths

    @staticmethod
    def find_matching_output_files(
        output_folder: str,
        titles: list[str],
        quality_label: str,
    ) -> list[Path]:
        """Find completed files produced for the requested videos and quality."""
        output_dir = Path(output_folder)
        if not output_dir.exists():
            return []

        def normalize(value: str) -> str:
            return re.sub(r"[^a-z0-9]+", "", value.casefold())

        title_tokens = [normalize(title) for title in titles if normalize(title)]
        quality_token = normalize(quality_label)
        if not title_tokens or not quality_token:
            return []

        matches: list[Path] = []
        for path in output_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() == ".part":
                continue
            name_token = normalize(path.stem)
            if quality_token in name_token and any(
                title_token in name_token for title_token in title_tokens
            ):
                matches.append(path)
        return matches

    ########################################################
    # Progress Hook
    ########################################################

    def progress_hook(self, data):

        # Stop download immediately if requested
        if self.cancel_requested:
            raise DownloadCancelled()

        status = data.get("status")

        ########################################################
        # Downloading
        ########################################################

        if status == "downloading":
            downloaded = data.get("downloaded_bytes", 0)

            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0

            percent = 0

            if total:
                percent = downloaded / total * 100

            playlist_index, playlist_count = self._playlist_position(data)
            status_text = "Downloading..."
            if playlist_index and playlist_count:
                percent = ((playlist_index - 1) + percent / 100) / playlist_count * 100
                status_text = f"Video {playlist_index} of {playlist_count} — Downloading..."

            downloaded_text = self.format_size(downloaded)

            total_text = self.format_size(total) if total else "Unknown"

            speed = data.get("speed")

            speed_text = "--"

            if speed:
                speed_text = f"{speed / 1024 / 1024:.2f} MB/s"

            eta_text = self.format_eta(data.get("eta"))

            self.progress.emit(
                percent,
                downloaded_text,
                total_text,
                speed_text,
                status_text,
                eta_text,
            )

        ########################################################
        # Finished
        ########################################################

        elif status == "finished":
            playlist_index, playlist_count = self._playlist_position(data)
            status_text = "Merging Audio & Video..."
            if playlist_index and playlist_count:
                status_text = f"Video {playlist_index} of {playlist_count} — Merging..."
            self.progress.emit(
                100,
                "",
                "",
                "",
                status_text,
                "--",
            )

    ########################################################
    # Run
    ########################################################

    def build_options(self) -> dict[str, Any]:
        safe_label = re.sub(r"[^A-Za-z0-9]+", "_", self.quality_label).strip("_")
        filename = f"%(title)s_{safe_label}.%(ext)s"
        if self.download_playlist:
            filename = f"%(playlist_title)s/%(playlist_index)03d - {filename}"
        output_template = str(Path(self.output_folder) / filename)

        bundled_ffmpeg_dir = Path(FFMPEG_FOLDER)
        ffmpeg_location = str(bundled_ffmpeg_dir)
        if not bundled_ffmpeg_dir.exists() or not (bundled_ffmpeg_dir / "ffmpeg.exe").exists():
            ffmpeg_location = "C:/ffmpeg/bin"

        options: dict[str, Any] = {
            "outtmpl": output_template,
            "progress_hooks": [self.progress_hook],
            "noplaylist": not self.download_playlist,
            "ffmpeg_location": ffmpeg_location,
            "quiet": True,
            "no_warnings": True,
            "overwrites": self.duplicate_policy == "overwrite",
            "writethumbnail": False,
            "continuedl": True,
            "nopart": False,
        }

        if self.download_playlist and self.playlist_items:
            options["playlist_items"] = ",".join(
                str(item) for item in self.playlist_items
            )

        if self.embed_metadata:
            options["addmetadata"] = True
        if self.embed_thumbnail:
            options["writethumbnail"] = True
            options["embedthumbnail"] = True

        if self.audio_only:
            options["format"] = "bestaudio/best"
            options["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": self._preferred_audio_codec(),
                "preferredquality": "0",
            }]
            options["postprocessor_args"] = ["-vn"]
            options["keepvideo"] = False
            options["merge_output_format"] = self._preferred_audio_codec()
            if self._preferred_audio_codec() in {"mp3", "m4a", "ogg", "wav", "flac", "aac", "opus"}:
                options["outtmpl"] = output_template
        else:
            if self.download_playlist:
                options["format"] = self._playlist_format_selector()
            else:
                options["format"] = f"{self.format_id}+bestaudio/best"
            options["merge_output_format"] = "mp4"

        return options

    @staticmethod
    def _playlist_position(data: dict[str, Any]) -> tuple[int, int]:
        info = data.get("info_dict") or {}
        index = info.get("playlist_index") or data.get("playlist_index") or 0
        count = (
            info.get("playlist_count")
            or info.get("n_entries")
            or data.get("playlist_count")
            or 0
        )
        try:
            return int(index), int(count)
        except (TypeError, ValueError):
            return 0, 0

    def _playlist_format_selector(self) -> str:
        """Choose the requested quality for each playlist item when possible.

        Format IDs are specific to a video. Reusing the first video's ID for a
        playlist makes the whole download fail as soon as another item lacks
        that exact format. The selected quality label includes the height
        (for example, ``1920x1080``), so use it as a per-video constraint.
        """
        match = re.search(r"(?:x|^)(\d{3,4})$", self.quality_label)
        if match:
            height = match.group(1)
            return f"bv*[height<={height}]+ba/b[height<={height}]/b"

        return "bv*+ba/b"

    def _preferred_audio_codec(self) -> str:
        mapping = {
            "Original": "m4a",
            "MP3": "mp3",
            "AAC": "aac",
            "FLAC": "flac",
            "WAV": "wav",
            "OPUS": "opus",
            "OGG": "ogg",
        }
        return mapping.get(self.audio_format, "m4a")

    def run(self):

        try:
            Path(self.output_folder).mkdir(
                parents=True,
                exist_ok=True,
            )

            options = self.build_options()

            with YoutubeDL(cast(Any, options)) as ydl:
                ydl.download([self.url])

            if not self.cancel_requested:
                self.finished.emit()

        except DownloadCancelled:
            self.cleanup_partial_files()
            self.error.emit("Download Cancelled")

        except Exception as e:
            import traceback

            traceback.print_exc()

            self.error.emit(str(e))
