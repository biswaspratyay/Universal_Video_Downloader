from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QGroupBox, QLabel, QListWidget, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout,
)

from ui.resources import DELETE_ICON

def build_right_panel(window):

    window.right_panel = QFrame()
    window.right_panel.setFrameShape(QFrame.Shape.StyledPanel)

    window.right_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    window.right_layout = QVBoxLayout(window.right_panel)
    window.right_layout.setSpacing(15)

    ########################################################
    # Selected Format Details
    ########################################################

    details_group = QGroupBox("Selected Format Details")
    details_group.setStyleSheet("""
        QGroupBox {
            font-size: 15px;
            font-weight: 700;
            color: palette(window-text);
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            left: 0;
            margin-left: 0;
        }
    """)

    details_layout = QGridLayout(details_group)
    details_layout.setVerticalSpacing(12)
    details_layout.setHorizontalSpacing(15)

    row = 0

    def add_row(name):

        nonlocal row

        # Left label
        label = QLabel(name)
        label.setStyleSheet("""
            QLabel{
                font-size:12pt;
                font-weight:650;
                background:transparent;
                border:none;
            }
        """)

        details_layout.addWidget(label, row, 0)

        # Right value
        value = QLabel("-")
        value.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )
        value.setContentsMargins(10, 4, 10, 4)
        value.setStyleSheet("""
            QLabel{
                background:#273449;
                border:1px solid #3B4B68;
                border-radius:8px;
                padding:6px 10px;
                font-size:10pt;
                color:#F3F4F6;
            }
        """)

        details_layout.addWidget(value, row, 1)

        row += 1

        return value


    window.codec_value = add_row("Codec")
    window.container_value = add_row("Container")
    window.audio_value = add_row("Audio")
    window.bitrate_value = add_row("Bitrate")
    window.filesize2_value = add_row("Estimated Size")

    details_layout.setColumnStretch(0, 1)
    details_layout.setColumnStretch(1, 2)

    window.right_layout.addWidget(details_group)

########################################################
# Download History
########################################################

    history_group = QGroupBox("Download History")
    history_group.setStyleSheet("""
        QGroupBox {
            font-size: 15px;
            font-weight: 700;
            color: palette(window-text);
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            left: 0;
            margin-left: 0;
        }
    """)

    history_layout = QVBoxLayout(history_group)

    window.history_list = QListWidget()
    window.history_list.setIconSize(window.history_list.sizeHint())

    clear_button = QPushButton("Clear History")
    clear_button.setIcon(QIcon(str(DELETE_ICON)))
    clear_button.setStyleSheet("font-size:12px;")
    clear_button.clicked.connect(window.clear_history)
    history_layout.addWidget(clear_button)

    history_entries = window.history_store.load()
    if history_entries:
        for entry in history_entries:
            window._add_history_item(entry)
    else:
        window.history_list.addItem("No downloads yet")

    history_layout.addWidget(window.history_list)

    window.right_layout.addWidget(history_group)

    window.right_layout.addStretch()

    window.right_scroll_area = QScrollArea()
    window.right_scroll_area.setWidgetResizable(True)
    window.right_scroll_area.setWidget(window.right_panel)
    window.right_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
    window.right_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    window.right_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    window.right_scroll_area.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding,
    )
    window.main_layout.addWidget(window.right_scroll_area, 1)
