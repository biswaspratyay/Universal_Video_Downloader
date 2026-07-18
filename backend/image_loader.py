import requests

from PySide6.QtGui import QPixmap


class ImageLoader:
    @staticmethod
    def load_from_url(url: str) -> QPixmap:

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        pixmap = QPixmap()
        pixmap.loadFromData(response.content)

        return pixmap
