def stylesheet():
    return """
/* ============================================================
   UNIVERSAL VIDEO DOWNLOADER
   DARK THEME
============================================================ */

/* ============================================================
   GLOBAL
============================================================ */

QMainWindow{
    background:#111827;
}

QWidget{
    background:#111827;
    color:#F3F4F6;
    font-family:"Segoe UI";
    font-size:10pt;
}

/* ============================================================
   MENU BAR
============================================================ */

QMenuBar{

    background:#1F2937;

    border-bottom:1px solid #334155;
}

QMenuBar::item{

    background:transparent;

    padding:8px 14px;

    margin:4px;

    border-radius:6px;
}

QMenuBar::item:selected{

    background:#334155;
}

QMenu{

    background:#1F2937;

    border:1px solid #334155;

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

    background:#1F2937;

    border:1px solid #334155;

    border-radius:12px;

    margin-top:8px;

    padding:10px;

    font-size:14px;

    font-weight:700;
}

QGroupBox::title{

    color:#60A5FA;

    left:16px;

    padding:0 6px;

    subcontrol-origin:margin;

    background:#111827;
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

    background:#273449;

    border:1px solid #3B4B68;

    border-radius:8px;

    padding:8px;

    selection-background-color:#3B82F6;
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

    background:#475569;

    color:#94A3B8;
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

    background:#334155;
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

    background:#273449;

    border-radius:10px;

    text-align:center;

    min-height:24px;

    font-weight:600;

    color:white;
}

QProgressBar::chunk{

    background:#22C55E;

    border-radius:10px;
}

/* ============================================================
   STATUS BAR
============================================================ */

QStatusBar{

    background:#1F2937;

    border-top:1px solid #334155;
}

/* ============================================================
   FRAMES
============================================================ */

QFrame{

    background:#111827;

    border:none;
}

/* ============================================================
   SCROLL BARS
============================================================ */

QScrollBar:vertical{

    background:#1F2937;

    width:10px;

    border:none;
}

QScrollBar::handle:vertical{

    background:#475569;

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

    background:#1F2937;

    height:10px;

    border:none;
}

QScrollBar::handle:horizontal{

    background:#475569;

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

    background:#1F2937;

    color:white;

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
        stop:0 #1B2433,
        stop:1 #243146
    );

    border:1px solid #334155;

    border-radius:18px;
}

/* ============================================================
   DOWNLOAD STATISTICS
============================================================ */

QFrame#StatsContainer{
    background:#1F2937;
    border:1px solid #334155;
    border-radius:12px;
    padding:8px;
}

QFrame#StatCard{
    background:transparent;
    border:1px solid rgba(255, 255, 255, 0.08);
    border-radius:10px;
    padding:6px 8px;
}

QLabel#StatLabel{
    font-size:11px;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:0.4px;
    color:#3B82F6;
    background:transparent;
    border:none;
}

QLabel#StatValue{
    font-size:11px;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:0.4px;
    color:#61CF5A;
    background:transparent;
    border:none;
}

/* ============================================================
   PLATFORM DETECTION
============================================================ */

QFrame#PlatformDetection{
    background:#1F2937;
    border:1px solid #3B4B68;
    border-radius:8px;
}

QLabel#PlatformDetectionTitle{
    background:transparent;
    color:#94A3B8;
    font-size:11px;
    font-weight:700;
    text-transform:uppercase;
}

QLabel#PlatformDetectionValue{
    background:transparent;
    color:#60A5FA;
    font-size:12px;
    font-weight:700;
}

QLabel#PlaylistDetectedValue{
    background:transparent;
    color:#86EFAC;
    font-size:12px;
    font-weight:700;
}

"""
