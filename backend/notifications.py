import platform
import sys

if sys.platform.startswith("win"):
    import winsound
else:
    winsound = None


def play_download_complete_sound() -> None:
    """Play a brief notification sound when a download completes."""
    if platform.system().lower() != "windows" or winsound is None:
        return

    winsound.MessageBeep(winsound.MB_ICONASTERISK)
