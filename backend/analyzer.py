from yt_dlp import YoutubeDL

from backend.models import PlaylistEntry, VideoFormat, VideoInfo
from backend.format_processor import FormatProcessor


class VideoAnalyzer:
    def analyze(self, url: str) -> VideoInfo:

        options = {
            "quiet": True,
            "skip_download": True,
            "no_warnings": True,
            "noplaylist": False,
        }

        with YoutubeDL(params=options) as ydl:
            info = ydl.extract_info(url, download=False)

        is_playlist = info.get("_type") == "playlist" or "entries" in info
        entries = list(info.get("entries") or []) if is_playlist else []
        first_entry = next((entry for entry in entries if entry), {})
        display_info = first_entry if is_playlist else info

        video = VideoInfo()

        # Use "or" to ensure we never assign None to fields that expect concrete types
        # Playlists have no downloadable formats of their own. Use the first
        # available video to populate the existing quality controls.
        video.title = display_info.get("title") or info.get("title") or ""
        video.uploader = display_info.get("uploader") or info.get("uploader") or ""
        video.duration = display_info.get("duration") or 0
        video.thumbnail = display_info.get("thumbnail") or info.get("thumbnail") or ""
        video.webpage_url = display_info.get("webpage_url") or ""
        video.upload_date = display_info.get("upload_date") or ""
        video.view_count = display_info.get("view_count") or 0
        video.is_live = display_info.get("is_live") or False

        video.is_playlist = is_playlist
        video.playlist_title = info.get("title") or "" if is_playlist else ""
        video.playlist_count = len(entries) if is_playlist else 0
        video.playlist_duration = sum(int(entry.get("duration") or 0) for entry in entries)
        video.playlist_estimated_size = sum(
            int(entry.get("filesize") or entry.get("filesize_approx") or 0)
            for entry in entries
        )
        video.playlist_entries = [
            PlaylistEntry(
                position=index,
                title=entry.get("title") or "Untitled video",
                webpage_url=entry.get("webpage_url") or entry.get("url") or "",
                duration=int(entry.get("duration") or 0),
            )
            for index, entry in enumerate(entries, start=1)
            if entry
        ]
        video.formats = FormatProcessor.process(display_info.get("formats", []))
        video.playlist_size_estimates = self._playlist_size_estimates(
            entries,
            display_info.get("formats", []),
        )

        return video

    @staticmethod
    def _playlist_size_estimates(entries, reference_formats) -> dict[int, int]:
        """Estimate total playlist sizes for each quality offered in the UI."""
        heights = {
            int(fmt.get("height") or 0)
            for fmt in reference_formats
            if fmt.get("vcodec") not in (None, "none") and fmt.get("height")
        }
        estimates: dict[int, int] = {}

        for height in heights:
            total = 0
            for entry in entries:
                formats = entry.get("formats") or []
                video_formats = [
                    fmt for fmt in formats
                    if fmt.get("vcodec") not in (None, "none")
                    and (fmt.get("height") or 0) <= height
                    and (fmt.get("filesize") or fmt.get("filesize_approx"))
                ]
                audio_formats = [
                    fmt for fmt in formats
                    if fmt.get("vcodec") in (None, "none")
                    and fmt.get("acodec") not in (None, "none")
                    and (fmt.get("filesize") or fmt.get("filesize_approx"))
                ]
                if video_formats:
                    best_video = max(
                        video_formats,
                        key=lambda fmt: ((fmt.get("height") or 0), fmt.get("filesize") or fmt.get("filesize_approx") or 0),
                    )
                    total += int(best_video.get("filesize") or best_video.get("filesize_approx") or 0)
                    if audio_formats:
                        best_audio = max(
                            audio_formats,
                            key=lambda fmt: fmt.get("filesize") or fmt.get("filesize_approx") or 0,
                        )
                        total += int(best_audio.get("filesize") or best_audio.get("filesize_approx") or 0)
                else:
                    total += int(entry.get("filesize") or entry.get("filesize_approx") or 0)

            if total:
                estimates[height] = total

        return estimates
