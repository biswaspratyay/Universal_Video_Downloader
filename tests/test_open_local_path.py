import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QUrl

from ui.main_window import open_local_path


class OpenLocalPathTests(unittest.TestCase):
    def test_opens_local_path_with_qt_desktop_services(self):
        path = Path("downloads")

        with patch("ui.main_window.QDesktopServices.openUrl", return_value=True) as open_url:
            opened = open_local_path(path)

        self.assertTrue(opened)
        expected_url = QUrl.fromLocalFile(str(path.resolve()))
        self.assertEqual(open_url.call_args.args[0], expected_url)


if __name__ == "__main__":
    unittest.main()
