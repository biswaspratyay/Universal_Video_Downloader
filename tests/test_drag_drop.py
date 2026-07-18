import unittest

from PySide6.QtCore import QUrl
from PySide6.QtCore import QMimeData

from ui.main_window import extract_url_from_mime_data


class DragDropTests(unittest.TestCase):
    def test_extract_url_from_mime_data(self):
        mime_data = QMimeData()
        mime_data.setUrls([QUrl("https://www.youtube.com/watch?v=abc123")])

        self.assertEqual(
            extract_url_from_mime_data(mime_data),
            "https://www.youtube.com/watch?v=abc123",
        )


if __name__ == "__main__":
    unittest.main()
