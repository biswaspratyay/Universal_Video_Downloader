from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QVBoxLayout,
)

from ui.resources import CANCEL_ICON, DOWNLOAD_ICON, FOLDER_ICON, PLAY_ICON

def save_download_settings(window):
    window.settings.set("download_folder", window.folder_input.text().strip())
    window.settings.set("video_format", window.format_combo.currentText())
    window.settings.set("audio_format", window.audio_combo.currentText())
    window.settings.save()
    window._update_resume_button_state()


def update_format_controls(window):
    audio_only = window.audio_combo.currentText() == "Audio Only"
    window.quality_label.setVisible(not audio_only)
    window.quality_combo.setVisible(not audio_only)
    window.format_label.setVisible(not audio_only)
    window.format_combo.setVisible(not audio_only)


def build_center_panel(window):

    window.center_panel = QFrame()
    window.center_panel.setFrameShape(QFrame.Shape.StyledPanel)
    window.center_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    window.center_layout = QVBoxLayout(window.center_panel)
    window.center_layout.setSpacing(15)

    ########################################################
    # Download Settings
    ########################################################

    settings_group = QGroupBox("Download Settings")
    settings_group.setStyleSheet("""
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

    settings_layout = QGridLayout(settings_group)
    settings_layout.setVerticalSpacing(12)
    settings_layout.setHorizontalSpacing(10)

    row = 0

    # ----------------------------------------------------
    # Quality
    # ----------------------------------------------------

    window.quality_label = QLabel("Quality")
    window.quality_label.setStyleSheet("""
    font-size:13px;
    font-weight:600;
    color:palette(window-text);
    background:transparent;
    border:none;
    """)

    settings_layout.addWidget(
        window.quality_label,
        row,
        0
    )

    window.quality_combo = QComboBox()
    window.quality_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    window.quality_combo.currentIndexChanged.connect(window.update_format_information)
    window.quality_combo.currentIndexChanged.connect(window._update_resume_button_state)
    window.quality_combo.addItem("Analyze a Video First")

    settings_layout.addWidget(window.quality_combo, row, 1)

    row += 1

    # ----------------------------------------------------
    # Format
    # ----------------------------------------------------

    window.format_label = QLabel("Format")
    window.format_label.setStyleSheet("""
    font-size:13px ;
    font-weight:600;
    color:palette(window-text);
    background:transparent;
    border:none;
    """)

    settings_layout.addWidget(window.format_label, row, 0)

    window.format_combo = QComboBox()
    window.format_combo.addItem("Analyze a Video First")
    window.format_combo.setEnabled(False)
    window.format_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    settings_layout.addWidget(window.format_combo, row, 1)

    row += 1

    # ----------------------------------------------------
    # Audio Format
    # ----------------------------------------------------

    audio_label = QLabel("Audio")
    audio_label.setStyleSheet("""
    font-size:13px ;
    font-weight:600;
    color:palette(window-text);
    background:transparent;
    border:none;
    """)

    settings_layout.addWidget(audio_label, row, 0)

    window.audio_combo = QComboBox()
    window.audio_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    window.audio_combo.addItems([
        "Audio Only",
        "Original (Included in video)",
    ])
    window.audio_combo.setCurrentText(window.settings.get("audio_format", "Original (Included in video)"))
    window.audio_combo.currentTextChanged.connect(window._update_format_controls)
    window.audio_combo.currentTextChanged.connect(window._save_download_settings)

    settings_layout.addWidget(window.audio_combo, row, 1)

    row += 1

    # ----------------------------------------------------
    # Output Folder
    # ----------------------------------------------------

    save_label = QLabel("Save To")
    save_label.setStyleSheet("""
    font-size:13px ;
    font-weight:600;
    color:palette(window-text);
    background:transparent;
    border:none;
    """)

    settings_layout.addWidget(save_label, row, 0)

    folder_layout = QHBoxLayout()

    window.folder_input = QLineEdit()
    window.folder_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    window.folder_input.setText(window.settings.get("download_folder", "downloads"))
    window.folder_input.textChanged.connect(window._save_download_settings)

    window._update_format_controls()

    window.browse_button = QPushButton("Browse")
    window.browse_button.setIcon(QIcon(str(FOLDER_ICON)))
    window.browse_button.setSizePolicy(
        QSizePolicy.Policy.Minimum,
        QSizePolicy.Policy.Preferred,
    )
    window.browse_button.clicked.connect(window.browse_folder)

    folder_layout.addWidget(window.folder_input)
    folder_layout.addWidget(window.browse_button)
    folder_layout.setStretch(0, 1)

    settings_layout.addLayout(folder_layout, row, 1)

    row += 1

    ########################################################

    window.center_layout.addWidget(settings_group)

    ########################################################
    # Download Button
    ########################################################

    window.download_button = QPushButton("DOWNLOAD")

    window.download_button.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Minimum,
    )
    window.download_button.setStyleSheet("""
    font-size:15px;
    font-weight:bold;
    """)
    window.download_button.setIcon(QIcon(str(DOWNLOAD_ICON)))

    window.resume_button = QPushButton("RESUME")
    window.resume_button.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Minimum,
    )
    window.resume_button.setStyleSheet("""
    font-size:15px;
    font-weight:bold;
    """)
    window.resume_button.setIcon(QIcon(str(PLAY_ICON)))
    window.resume_button.setToolTip("No partial download available")
    window.resume_button.setEnabled(False)
    window.resume_button.clicked.connect(window.resume_download)

    window.cancel_button = QPushButton("CANCEL")
    window.cancel_button.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Minimum,
    )
    window.cancel_button.setIcon(QIcon(str(CANCEL_ICON)))
    window.cancel_button.setEnabled(False)
    window.cancel_button.clicked.connect(window.cancel_download)

    window.resume_hint_label = QLabel("Resume partial download available")
    window.resume_hint_label.setStyleSheet("""
    color: #F59E0B;
    font-size: 12px;
    margin-left: 10px;
    """)
    window.resume_hint_label.setVisible(False)

    window.center_layout.addStretch()

    button_row = QHBoxLayout()
    button_row.setSpacing(12)
    button_row.addWidget(window.download_button)
    button_row.addWidget(window.resume_button)
    button_row.addWidget(window.cancel_button)
    button_row.addWidget(window.resume_hint_label)
    button_row.setStretch(0, 2)
    button_row.setStretch(1, 2)
    button_row.setStretch(2, 1)

    window.center_layout.addLayout(button_row)
    window.download_button.clicked.connect(window.download_video)

    ########################################################

    window.main_layout.addWidget(window.center_panel, 2)
