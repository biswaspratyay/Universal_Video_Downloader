def stylesheet():
    return """
/* ============================================================
   UNIVERSAL VIDEO DOWNLOADER
   LIGHT THEME
============================================================ */

/* ============================================================
   GLOBAL
============================================================ */

QMainWindow{
    background:#F8FAFC;
}

QWidget{
    background:#F8FAFC;
    color:#0F172A;
    font-family:"Segoe UI";
    font-size:10pt;
}

/* ============================================================
   MENU BAR
============================================================ */

QMenuBar{
    background:#F1F5F9;
    border-bottom:1px solid #CBD5E1;
}

QMenuBar::item{
    background:transparent;
    padding:8px 14px;
    margin:4px;
    border-radius:6px;
}

QMenuBar::item:selected{
    background:#DBEAFE;
    color:#1D4ED8;
}

QMenu{
    background:#FFFFFF;
    border:1px solid #CBD5E1;
    padding:6px;
}

QMenu::item{
    padding:8px 28px;
    border-radius:6px;
}

QMenu::item:selected{
    background:#3B82F6;
    color:white;
}

/* ============================================================
   GROUP BOXES
============================================================ */

QGroupBox{
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:12px;
    margin-top:8px;
    padding:10px;
    font-size:14px;
    font-weight:700;
}

QGroupBox::title{
    color:#2563EB;
    left:16px;
    padding:0 6px;
    subcontrol-origin:margin;
    background:#F8FAFC;
}

/* ============================================================
   LABELS
============================================================ */

QLabel{
    background:transparent;
    border:none;
    padding:0px;
}

/* ============================================================
   INPUTS
============================================================ */

QLineEdit,
QComboBox,
QListWidget{
    background:#FFFFFF;
    border:1px solid #BFDBFE;
    border-radius:8px;
    padding:8px;
    selection-background-color:#3B82F6;
    color:#0F172A;
}

QLineEdit:focus,
QComboBox:focus{
    border:2px solid #60A5FA;
}

QComboBox::drop-down{
    border:none;
    width:28px;
}

QComboBox::down-arrow{
    image:none;
}

/* ============================================================
   BUTTONS
============================================================ */

QPushButton{
    background:#3B82F6;
    color:white;
    border:none;
    border-radius:8px;
    padding:10px 18px;
    font-weight:600;
    min-height:18px;
}

QPushButton:hover{
    background:#60A5FA;
}

QPushButton:pressed{
    background:#2563EB;
}

QPushButton:disabled{
    background:#CBD5E1;
    color:#475569;
}

/* ============================================================
   CHECK BOX
============================================================ */

QCheckBox{
    spacing:8px;
    background:transparent;
}

QCheckBox::indicator{
    width:18px;
    height:18px;
}

/* ============================================================
   LIST WIDGET
============================================================ */

QListWidget{
    outline:none;
}

QListWidget::item{
    padding:8px;
    border-radius:6px;
}

QListWidget::item:hover{
    background:#E0F2FE;
}

QListWidget::item:selected{
    background:#3B82F6;
    color:white;
}

/* ============================================================
   PROGRESS BAR
============================================================ */

QProgressBar{
    border:none;
    background:#E2E8F0;
    border-radius:10px;
    text-align:center;
    min-height:24px;
    font-weight:600;
    color:#0F172A;
}

QProgressBar::chunk{
    background:#22C55E;
    border-radius:10px;
}

/* ============================================================
   STATUS BAR
============================================================ */

QStatusBar{
    background:#F1F5F9;
    border-top:1px solid #CBD5E1;
}

/* ============================================================
   FRAMES
============================================================ */

QFrame{
    background:#F8FAFC;
    border:none;
}

/* ============================================================
   SCROLL BARS
============================================================ */

QScrollBar:vertical{
    background:#E2E8F0;
    width:10px;
    border:none;
}

QScrollBar::handle:vertical{
    background:#94A3B8;
    border-radius:5px;
    min-height:30px;
}

QScrollBar::handle:vertical:hover{
    background:#64748B;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical{
    height:0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical{
    background:none;
}

QScrollBar:horizontal{
    background:#E2E8F0;
    height:10px;
    border:none;
}

QScrollBar::handle:horizontal{
    background:#94A3B8;
    border-radius:5px;
    min-width:30px;
}

QScrollBar::handle:horizontal:hover{
    background:#64748B;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal{
    width:0px;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal{
    background:none;
}

/* ============================================================
   TOOLTIP
============================================================ */

QToolTip{
    background:#FFFFFF;
    color:#0F172A;
    border:1px solid #3B82F6;
    padding:6px;
    border-radius:6px;
}

/* ============================================================
   HEADER
============================================================ */

QFrame#HeaderFrame{
    background:qlineargradient(
        x1:0,
        y1:0,
        x2:1,
        y2:0,
        stop:0 #E0F2FE,
        stop:1 #DBEAFE
    );

    border:1px solid #BFDBFE;
    border-radius:18px;
}

/* ============================================================
   DOWNLOAD STATISTICS
============================================================ */

QFrame#StatsContainer{
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:12px;
    padding:8px;
}

QFrame#StatCard{
    background:transparent;
    border:1px solid #E2E8F0;
    border-radius:10px;
    padding:6px 8px;
}

QLabel#StatLabel{
    font-size:11px;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:0.4px;
    color:#2563EB;
    background:transparent;
    border:none;
}

QLabel#StatValue{
    font-size:11px;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:0.4px;
    color:#16A34A;
    background:transparent;
    border:none;
}

/* ============================================================
   PLATFORM DETECTION
============================================================ */

QFrame#PlatformDetection{
    background:#FFFFFF;
    border:1px solid #BFDBFE;
    border-radius:8px;
}

QLabel#PlatformDetectionTitle{
    background:transparent;
    color:#475569;
    font-size:11px;
    font-weight:700;
    text-transform:uppercase;
}

QLabel#PlatformDetectionValue{
    background:transparent;
    color:#2563EB;
    font-size:12px;
    font-weight:700;
}

QLabel#PlaylistDetectedValue{
    background:transparent;
    color:#15803D;
    font-size:12px;
    font-weight:700;
}
"""
