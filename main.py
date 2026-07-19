import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.resources import APP_ICON


def main():

    # Enable High-DPI icons (Qt 6)
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    app.setApplicationName("Universal Video Downloader")
    app.setApplicationDisplayName("Universal Video Downloader")
    app.setApplicationVersion("1.2")

    app.setWindowIcon(QIcon(str(APP_ICON)))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
