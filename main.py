import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow
from ui.resources import APP_ICON


def main():

    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(str(APP_ICON)))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
