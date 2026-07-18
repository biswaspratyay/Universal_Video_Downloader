from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFormLayout, QFrame, QGroupBox, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout,
)

from ui.resources import THUMBNAIL_PLACEHOLDER

# --------------------------------------------------------

def build_left_panel(window):

    window.left_panel = QFrame()

    window.left_panel.setFrameShape(QFrame.Shape.StyledPanel)

    window.left_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    window.left_layout = QVBoxLayout(window.left_panel)
    window.left_layout.setSpacing(15)

    ########################################################
    # Thumbnail
    ########################################################

    thumb_group = QGroupBox("Thumbnail")
    thumb_group.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding,
    )
    thumb_group.setStyleSheet("""
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

    thumb_layout = QVBoxLayout(thumb_group)
    thumb_layout.setContentsMargins(1, 1, 1, 1)

    window.thumbnail_label = QLabel()

    window.thumbnail_label.setAlignment(
        Qt.AlignmentFlag.AlignCenter
    )

    window.thumbnail_label.setStyleSheet("""
    QLabel{
        background:transparent;
        border:none;
    }
    """)
    window.thumbnail_label.installEventFilter(window)

    pixmap = QPixmap(str(THUMBNAIL_PLACEHOLDER))

    window.thumbnail_label.setMinimumSize(220, 126)
    window.thumbnail_label.setSizePolicy(
        QSizePolicy.Policy.Ignored,
        QSizePolicy.Policy.Ignored,
    )

    window._set_thumbnail_pixmap(pixmap)

    thumb_layout.addWidget(window.thumbnail_label)

    window.download_thumbnail_button = QPushButton("Download Original Thumbnail")
    window.download_thumbnail_button.setToolTip(
        "Save the source thumbnail at its original dimensions"
    )
    window.download_thumbnail_button.setEnabled(False)
    window.download_thumbnail_button.clicked.connect(window.download_thumbnail)
    thumb_layout.addWidget(window.download_thumbnail_button)

    window.left_layout.addWidget(thumb_group, stretch=3)

    ########################################################
    # Video Information
    ########################################################

    window.video_information_group = QGroupBox("Video Information")
    window.video_information_group.setStyleSheet("""
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

    window.video_information_group.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Preferred,
    )

    info_layout = QFormLayout(window.video_information_group)

    info_layout.setContentsMargins(12, 12, 12, 12)
    info_layout.setHorizontalSpacing(20)
    info_layout.setVerticalSpacing(8)

    def add_row(name):

        label = QLabel(name)

        label.setStyleSheet("""
            QLabel{
                font-size:15px;
                font-weight:600;
                color:palette(window-text);
                background:transparent;
                border:none;
            }
        """)

        value = QLabel("-")

        value.setStyleSheet("""
            QLabel{
                font-size:14px;
                color:palette(window-text);
                background:transparent;
                border:none;
            }
        """)

        value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        value.setWordWrap(True)

        value.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        info_layout.addRow(label, value)

        return value

    window.title_label = add_row("Title")
    window.channel_label = add_row("Channel")
    window.duration_label = add_row("Duration")
    window.resolution_label = add_row("Resolution")
    window.fps_label = add_row("FPS")
    window.filesize_label = add_row("File Size")
    window.upload_label = add_row("Upload Date")
    window.views_label = add_row("Views")
    window.type_label = add_row("Type")
    window.live_label = add_row("Live")

    window.left_layout.addWidget(window.video_information_group, stretch=2)

    window.playlist_summary_group = QGroupBox("Playlist Summary")
    playlist_layout = QFormLayout(window.playlist_summary_group)
    playlist_layout.setContentsMargins(12, 12, 12, 12)
    playlist_layout.setHorizontalSpacing(20)
    playlist_layout.setVerticalSpacing(8)

    def add_playlist_row(name):
        label = QLabel(name)
        label.setStyleSheet(
            "font-size:15px; font-weight:600; color:palette(window-text); "
            "background:transparent; border:none;"
        )
        value = QLabel("-")
        value.setStyleSheet(
            "font-size:14px; color:palette(window-text); "
            "background:transparent; border:none;"
        )
        value.setWordWrap(True)
        value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        playlist_layout.addRow(label, value)
        return value

    window.playlist_name_value = add_playlist_row("Name")
    window.playlist_uploader_value = add_playlist_row("Uploader")
    window.playlist_videos_value = add_playlist_row("Videos")
    window.playlist_duration_value = add_playlist_row("Total Duration")
    window.playlist_size_value = add_playlist_row("Estimated Size")
    window.playlist_summary_group.setVisible(False)
    window.left_layout.addWidget(window.playlist_summary_group, stretch=1)
    window.left_layout.addStretch()

    window.left_scroll_area = QScrollArea()
    window.left_scroll_area.setWidgetResizable(True)
    window.left_scroll_area.setWidget(window.left_panel)
    window.left_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
    window.left_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    window.left_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    window.left_scroll_area.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding,
    )
    window.main_layout.addWidget(window.left_scroll_area, 1)
