from dataclasses import dataclass, field


@dataclass(slots=True)
class VideoFormat:
    format_id: str

    quality: str

    extension: str

    width: int

    height: int

    fps: float | None

    filesize: int | None

    video_codec: str

    audio_codec: str

    is_video: bool

    is_audio: bool

    display_name: str = ""

    bitrate: float | None = None

    tbr: float | None = None

    bitrate: float | None


audio_bitrate: float | None


@dataclass(slots=True)
class VideoInfo:
    title: str = ""
    uploader: str = ""
    duration: int = 0

    thumbnail: str = ""

    webpage_url: str = ""

    upload_date: str = ""

    view_count: int = 0

    is_live: bool = False

    is_playlist: bool = False
    playlist_title: str = ""
    playlist_count: int = 0
    playlist_duration: int = 0
    playlist_estimated_size: int = 0
    playlist_size_estimates: dict[int, int] = field(default_factory=dict)
    playlist_entries: list["PlaylistEntry"] = field(default_factory=list)

    formats: list[VideoFormat] = field(default_factory=list)


@dataclass(slots=True)
class PlaylistEntry:
    position: int = 0
    title: str = ""
    webpage_url: str = ""
    duration: int = 0
