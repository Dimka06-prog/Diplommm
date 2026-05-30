from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QFont
from config import COLORS

# Carvix Design System - matching web styles
STYLESHEET = """
/* Main Window */
QWidget {
    background-color: #FBF8F3;
    color: #1C1B17;
}

QMainWindow {
    background-color: #FBF8F3;
}

/* Sidebar */
QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F1E8D5, stop:1 #E8DCC2);
    border-right: 1px solid #DCC9A8;
}

QPushButton#sidebar_btn {
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    color: #3F3D38;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#sidebar_btn:hover {
    background: rgba(28, 27, 23, 0.05);
}

QPushButton#sidebar_btn:checked {
    background: #1C1B17;
    color: #FBF8F3;
}

QPushButton#sidebar_btn:checked:hover {
    background: #3F3D38;
}

/* Header */
QFrame#header {
    background: #FFFFFF;
    border-bottom: 1px solid #E2E2E0;
}

QLabel#header_title {
    font-family: 'Georgia', serif;
    font-size: 24px;
    font-weight: 600;
    color: #1C1B17;
}

QLabel#user_info {
    color: #6F6D67;
    font-size: 13px;
}

/* Cards */
QFrame#card {
    background: rgba(255, 255, 255, 0.92);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.8);
}

QFrame#card_light {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E2E0;
}

/* Buttons */
QPushButton#primary_btn {
    background: #1C1B17;
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton#primary_btn:hover {
    background: #3F3D38;
}

QPushButton#primary_btn:pressed {
    background: #6F6D67;
}

QPushButton#secondary_btn {
    background: #F5EFE3;
    color: #1C1B17;
    border: 1px solid #DCC9A8;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#secondary_btn:hover {
    background: #ECE2CE;
}

QPushButton#danger_btn {
    background: #B23A3A;
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#danger_btn:hover {
    background: #8B2E2E;
}

QPushButton#success_btn {
    background: #4A7C59;
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#success_btn:hover {
    background: #3A6347;
}

/* Input Fields */
QLineEdit, QComboBox, QSpinBox, QDateEdit {
    background: #FFFFFF;
    border: 1px solid #E2E2E0;
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 14px;
    color: #1C1B17;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
    border: 2px solid #1C1B17;
}

QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDateEdit:hover {
    border-color: #C9C8C4;
}

/* Tables */
QTableView {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E2E0;
    gridline-color: #EFEFEE;
    selection-background-color: #F5EFE3;
    selection-color: #1C1B17;
}

QTableView::item {
    padding: 8px 12px;
}

QTableView::item:selected {
    background: #F5EFE3;
}

QHeaderView::section {
    background: #F7F7F7;
    color: #3F3D38;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid #E2E2E0;
    font-weight: 600;
    font-size: 13px;
}

QHeaderView::section:hover {
    background: #EFEFEE;
}

/* Labels */
QLabel#section_title {
    font-family: 'Georgia', serif;
    font-size: 28px;
    font-weight: 600;
    color: #1C1B17;
}

QLabel#card_title {
    font-size: 16px;
    font-weight: 600;
    color: #1C1B17;
}

QLabel#label_text {
    color: #6F6D67;
    font-size: 13px;
}

QLabel#value_text {
    color: #1C1B17;
    font-size: 14px;
    font-weight: 500;
}

QLabel#stat_value {
    font-family: 'Georgia', serif;
    font-size: 32px;
    font-weight: 600;
    color: #1C1B17;
}

QLabel#stat_label {
    color: #6F6D67;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* Status Badges */
QLabel#status_badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

QLabel#status_badge[status="active"] {
    background: #E8F5E9;
    color: #4A7C59;
}

QLabel#status_badge[status="warning"] {
    background: #FFF3E0;
    color: #e5a00d;
}

QLabel#status_badge[status="danger"] {
    background: #FFEBEE;
    color: #B23A3A;
}

QLabel#status_badge[status="info"] {
    background: #E3F2FD;
    color: #1976D2;
}

/* Scrollbar */
QScrollBar:vertical {
    background: #F7F7F7;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #C9C8C4;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #9A9892;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Dialog */
QDialog {
    background: #FBF8F3;
}

QDialog#auth_dialog {
    background: rgba(255, 255, 255, 0.92);
    border-radius: 28px;
}

QLabel#auth_title {
    font-family: 'Georgia', serif;
    font-size: 36px;
    font-weight: 600;
    color: #1C1B17;
}

QLabel#auth_subtitle {
    color: #6F6D67;
    font-size: 14px;
}

QLabel#field_label {
    color: #9A9892;
    font-size: 13px;
}

/* Tabs */
QTabWidget::pane {
    border: none;
    background: transparent;
}

QTabBar::tab {
    background: #F7F7F7;
    color: #6F6D67;
    padding: 12px 24px;
    border: none;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    font-size: 14px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background: #FFFFFF;
    color: #1C1B17;
}

QTabBar::tab:hover:!selected {
    background: #EFEFEE;
}

/* Group Box */
QGroupBox {
    background: #FFFFFF;
    border: 1px solid #E2E2E0;
    border-radius: 12px;
    padding-top: 20px;
    font-weight: 600;
    color: #1C1B17;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
}

/* Progress Bar */
QProgressBar {
    background: #EFEFEE;
    border-radius: 4px;
    border: none;
    height: 8px;
}

QProgressBar::chunk {
    background: #1C1B17;
    border-radius: 4px;
}

QProgressBar[status="warning"]::chunk {
    background: #e5a00d;
}

QProgressBar[status="danger"]::chunk {
    background: #B23A3A;
}

QProgressBar[status="success"]::chunk {
    background: #4A7C59;
}
"""

def apply_stylesheet(app):
    app.setStyleSheet(STYLESHEET)

def get_font(size=14, weight=QFont.Weight.Normal):
    font = QFont()
    font.setPointSize(size)
    font.setWeight(weight)
    return font

def get_header_font(size=24):
    font = QFont('Georgia', size)
    font.setWeight(QFont.Weight.Bold)
    return font
