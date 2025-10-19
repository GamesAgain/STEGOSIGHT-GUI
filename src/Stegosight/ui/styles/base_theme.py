from __future__ import annotations

from PyQt5.QtGui import QColor, QPalette

BASE_THEME = """
QWidget {
    font-family: "Sarabun", "Segoe UI", "Tahoma";
}

QMainWindow {
    background-color: #f5f5f5;
    color: #333333;
}

QLabel, QPlainTextEdit, QTextBrowser {
    color: #424242;
    background: transparent;
    font-size: 14px;
}

QGroupBox {
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    margin-top: 12px;
    padding: 18px;
    background-color: #ffffff;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px 8px 8px;
    color: #1E88E5;
    font-size: 14px;
}

QFrame#MethodCard {
    border: 1px solid #d0d7de;
    border-radius: 12px;
    background-color: #ffffff;
    transition: all 120ms ease-in-out;
}

QFrame#MethodCard:hover {
    border-color: #64b5f6;
}

QFrame#MethodCard[selected="true"] {
    border: 2px solid #1E88E5;
    background-color: #e3f2fd;
    box-shadow: 0 6px 18px rgba(30, 136, 229, 0.18);
}

QFrame#MethodCard QLabel[role="title"] {
    font-weight: 600;
    font-size: 14px;
    color: #1b1b1b;
}

QFrame#MethodCard QLabel[role="description"] {
    font-size: 13px;
    color: #616161;
}

#FileDropArea {
    border: 2px dashed #90caf9;
    border-radius: 12px;
    padding: 28px 16px;
    background-color: #f0f7ff;
    color: #1565c0;
    font-size: 15px;
}

#FileDropArea:hover {
    border-color: #1E88E5;
    background-color: #e3f2fd;
}

QPushButton {
    background-color: #ffffff;
    border: 1px solid #1E88E5;
    border-radius: 8px;
    padding: 10px 18px;
    color: #1E88E5;
    font-size: 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #e3f2fd;
}

QPushButton[primary="true"] {
    background-color: #1E88E5;
    border: none;
    color: white;
    padding: 14px 24px;
    font-size: 15px;
    font-weight: 700;
}

QPushButton[primary="true"]:hover {
    background-color: #1565C0;
}

QTabWidget::pane {
    border: 1px solid #e0e0e0;
    border-radius: 14px;
    padding: 12px;
    background-color: #ffffff;
}

QTabBar {
    background-color: #f0f0f0;
}

QTabBar::tab {
    background: transparent;
    color: #616161;
    padding: 14px 26px;
    margin: 4px;
    border-radius: 10px;
    font-size: 14px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #1E88E5;
    border: 2px solid #1E88E5;
}

QTabBar::tab:hover {
    background-color: #e3f2fd;
    color: #1E88E5;
}

QLineEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #d0d5dd;
    border-radius: 8px;
    padding: 10px;
    color: #1b1b1b;
    font-size: 14px;
}

QPlainTextEdit, QTextBrowser {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #d0d5dd;
}

QCheckBox {
    spacing: 10px;
    font-size: 14px;
    color: #424242;
}

QProgressBar {
    border-radius: 8px;
    background-color: #e0e0e0;
    text-align: center;
    height: 20px;
}

QProgressBar::chunk {
    border-radius: 8px;
    background-color: #1E88E5;
}

QScrollArea {
    border: none;
    background: transparent;
}

QHeaderView::section {
    background-color: #f5f5f5;
    border: 1px solid #e0e0e0;
    padding: 6px;
}
"""


def create_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f5f5f5"))
    palette.setColor(QPalette.WindowText, QColor("#1b1b1b"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.Text, QColor("#1b1b1b"))
    palette.setColor(QPalette.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ButtonText, QColor("#1b1b1b"))
    palette.setColor(QPalette.Highlight, QColor("#1E88E5"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    return palette


__all__ = ["BASE_THEME", "create_palette"]
