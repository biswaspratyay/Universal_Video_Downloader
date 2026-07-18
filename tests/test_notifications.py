import unittest
from unittest.mock import patch

from backend.notifications import play_download_complete_sound


class NotificationTests(unittest.TestCase):
    @patch("backend.notifications.winsound")
    def test_play_download_complete_sound_uses_windows_beep(self, mock_winsound):
        play_download_complete_sound()

        mock_winsound.MessageBeep.assert_called_once_with(mock_winsound.MB_ICONASTERISK)


if __name__ == "__main__":
    unittest.main()
