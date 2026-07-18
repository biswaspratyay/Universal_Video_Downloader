from pathlib import Path
import sys


# --------------------------------------------------------
# Base Path
# --------------------------------------------------------


def resource_path(relative_path: str) -> Path:
    """
    Returns the correct resource path for both development
    and PyInstaller builds.
    """

    if getattr(sys, "frozen", False):
        base_path = Path(getattr(sys, "_MEIPASS"))
    else:
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path


# --------------------------------------------------------
# Assets
# --------------------------------------------------------

ASSETS = resource_path("assets")

ICONS = ASSETS / "icons"
IMAGES = ASSETS / "images"


# --------------------------------------------------------
# Icons
# --------------------------------------------------------

APP_ICON = ICONS / "app.ico"

ANALYZE_ICON = ICONS / "analyze.svg"
DOWNLOAD_ICON = ICONS / "download.svg"
FOLDER_ICON = ICONS / "folder.svg"

PLAY_ICON = ICONS / "play.svg"
PAUSE_ICON = ICONS / "pause.svg"

REMOVE_ICON = ICONS / "remove.svg"
CLEAR_ICON = ICONS / "clear.svg"
DELETE_ICON = ICONS / "delete.svg"
REFRESH_ICON = ICONS / "refresh.svg"
CANCEL_ICON = ICONS / "cancel.svg"

SETTINGS_ICON = ICONS / "settings.svg"
INFO_ICON = ICONS / "info.svg"


# --------------------------------------------------------
# Images
# --------------------------------------------------------

LOGO = IMAGES / "logo.png"

BANNER = IMAGES / "banner.png"

THUMBNAIL_PLACEHOLDER = IMAGES / "thumbnail_placeholder.png"

# --------------------------------------------------------
# FFmpeg bundle
# --------------------------------------------------------

FFMPEG_FOLDER = resource_path("ffmpeg")
