from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QSizePolicy, QVBoxLayout

# --------------------------------------------------------

def build_bottom_panel(window, root):


    ########################################################
    # Progress
    ########################################################

    window.progress = QProgressBar()
    window.progress.setTextVisible(True)
    window.progress.setFormat("%p%")
    window.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.progress.setValue(0)
    window.progress.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Minimum,
    )

    root.addWidget(window.progress)

    ########################################################
    # Statistics
    ########################################################

    stats_container = QFrame()
    stats_container.setObjectName("StatsContainer")
    stats_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    stats_layout = QHBoxLayout(stats_container)
    stats_layout.setContentsMargins(10, 8, 10, 8)
    stats_layout.setSpacing(8)

    def add_stat(label_text, value_widget):
        card = QFrame()
        card.setObjectName("StatCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 6, 8, 6)
        card_layout.setSpacing(2)

        label = QLabel(label_text)
        label.setObjectName("StatLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_widget.setObjectName("StatValue")
        value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_widget.setWordWrap(True)

        card_layout.addWidget(label)
        card_layout.addWidget(value_widget)
        stats_layout.addWidget(card, 1)

    window.speed_label = QLabel("--")
    window.eta_label = QLabel("--")
    window.downloaded_label = QLabel("--")
    window.status_label = QLabel("Ready")

    add_stat("Speed", window.speed_label)
    add_stat("Downloaded", window.downloaded_label)
    add_stat("ETA", window.eta_label)
    add_stat("Status", window.status_label)

    root.addWidget(stats_container)
