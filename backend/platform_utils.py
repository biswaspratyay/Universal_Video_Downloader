from __future__ import annotations

import platform
import shutil
from pathlib import Path

from ui.resources import resource_path


# ============================================================
# Platform Detection
# ============================================================


def is_windows() -> bool:
    return platform.system() == "Windows"


def is_linux() -> bool:
    return platform.system() == "Linux"


def is_macos() -> bool:
    return platform.system() == "Darwin"


# ============================================================
# Executable Naming
# ============================================================


def executable_name(name: str) -> str:
    """
    Returns executable filename for the current platform.

    Windows:
        ffmpeg.exe

    Linux/macOS:
        ffmpeg
    """

    return f"{name}.exe" if is_windows() else name


# ============================================================
# Bundled FFmpeg
# ============================================================


def get_bundled_ffmpeg_dir() -> Path:
    """
    Returns the bundled FFmpeg directory.

    Development:
        ffmpeg/
            windows/
            linux/

    Packaged application:
        ffmpeg/
            ffmpeg(.exe)
            ffprobe(.exe)

    The PyInstaller spec copies only the current platform's FFmpeg
    into the packaged application's ffmpeg directory.
    """
    return resource_path("ffmpeg")


def get_ffmpeg_executable() -> Path | None:
    exe = get_bundled_ffmpeg_dir() / executable_name("ffmpeg")
    return exe if exe.exists() else None


def get_ffprobe_executable() -> Path | None:
    exe = get_bundled_ffmpeg_dir() / executable_name("ffprobe")
    return exe if exe.exists() else None


# ============================================================
# System FFmpeg
# ============================================================


def get_system_ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def get_system_ffprobe() -> str | None:
    return shutil.which("ffprobe")


# ============================================================
# Preferred Locations
# ============================================================


def get_ffmpeg_location() -> str | None:
    """
    Returns the preferred FFmpeg directory.

    Priority:

    1. Bundled FFmpeg
    2. System-installed FFmpeg
    """

    bundled = get_ffmpeg_executable()

    if bundled:
        return str(bundled.parent)

    system = get_system_ffmpeg()

    if system:
        return str(Path(system).parent)

    return None


def get_ffmpeg_binary() -> str:
    """
    Returns absolute path to ffmpeg if bundled,
    otherwise returns the system executable name.

    Safe to pass directly to yt-dlp.
    """

    bundled = get_ffmpeg_executable()

    if bundled:
        return str(bundled)

    return "ffmpeg"


def get_ffprobe_binary() -> str:
    """
    Returns absolute path to ffprobe if bundled,
    otherwise returns the system executable name.
    """

    bundled = get_ffprobe_executable()

    if bundled:
        return str(bundled)

    return "ffprobe"
