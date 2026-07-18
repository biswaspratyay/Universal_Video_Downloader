from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QHBoxLayout,
)


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Getting Started")

        self.setMinimumSize(700, 600)

        self.setModal(True)

        self.build_ui()

    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(25, 20, 25, 20)

        layout.setSpacing(18)

        #######################################################
        # TITLE
        #######################################################

        title = QLabel("Universal Video Downloader")

        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))

        layout.addWidget(title)

        #######################################################

        subtitle = QLabel("Getting Started Guide")

        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle.setStyleSheet("""
            color:#60A5FA;
            font-size:13pt;
            font-weight:600;
        """)

        layout.addWidget(subtitle)

        #######################################################
        # CONTENT
        #######################################################

        browser = QTextBrowser()

        browser.setOpenExternalLinks(True)

        browser.setStyleSheet("""
            QTextBrowser{
                background:#1F2937;
                border:1px solid #334155;
                border-radius:10px;
                padding:12px;
                font-size:11pt;
            }
        """)

        browser.setHtml("""
        <h2>🚀 Getting Started</h2>

        <ol>
            <li><b>Paste</b> or <b>Drag & Drop</b> a supported video URL into the URL field.</li><br>

            <li>Click <b>Analyze</b> to retrieve all available download formats.</li><br>

            <li>Select your preferred
                <ul>
                    <li>Video Quality</li>
                    <li>Output Format</li>
                    <li>Audio Format</li>
                </ul>
            </li><br>

            <li>Choose your download folder using the <b>Browse</b> button.</li><br>

            <li>Click <b>DOWNLOAD</b> to begin downloading.</li>
        </ol>

        <hr>

        <h2>🎵 Audio Only</h2>

        Select <b>Audio Only</b> from the Audio options if you only want to download the soundtrack.

        <hr>

        <h2>🔄 Resume Interrupted Downloads</h2>

        If a download stops because of:

        <ul>
            <li>Internet Failure</li>
            <li>Power Cut</li>
            <li>Accidental Cancellation</li>
            <li>Application Crash</li>
        </ul>

        simply:

        <ol>
            <li>Paste the same URL</li>
            <li>Click <b>Analyze</b></li>
            <li>Press <b>Resume</b></li>
        </ol>

        The download will continue from the already downloaded portion whenever possible.

        <hr>

        <h2>💡 Tips</h2>

        <ul>
            <li>Drag & Drop video URLs directly into the URL field.</li>
            <li>Right-click downloaded files to open their folder (coming soon).</li>
            <li>Use Resume instead of restarting interrupted downloads.</li>
        </ul>

        <hr>

        <p align="center">
        <b>Enjoy downloading!</b><br><br>
        Thank you for using Universal Video Downloader.
        </p>
        """)

        layout.addWidget(browser)

        #######################################################
        # BUTTONS
        #######################################################

        buttons = QHBoxLayout()

        buttons.addStretch()

        close_btn = QPushButton("Close")

        close_btn.setMinimumWidth(120)

        close_btn.clicked.connect(self.accept)

        buttons.addWidget(close_btn)

        layout.addLayout(buttons)
