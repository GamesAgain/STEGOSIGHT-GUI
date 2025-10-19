from __future__ import annotations

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

from .styles import build_stylesheet, create_palette
from .tabs import AnalyzeTab, EmbedTab, ExtractTab


class StegoSightApp(QMainWindow):
    """Main application window composed of modular tab widgets."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("STEGOSIGHT - Stego & Anti-Stego Intelligent Guard")
        self.resize(1400, 900)
        self.setMinimumSize(1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("MainTabWidget")
        self.setCentralWidget(self.tabs)

        self.apply_modern_theme()

        self.embed_tab = EmbedTab(self)
        self.extract_tab = ExtractTab(self)
        self.analyze_tab = AnalyzeTab(self)

        self._build_tabs()

    # ------------------------------------------------------------------
    def apply_modern_theme(self) -> None:
        app = QApplication.instance()
        if app is None:
            return

        palette = create_palette()
        app.setPalette(palette)
        app.setStyleSheet(build_stylesheet())

    def _build_tabs(self) -> None:
        self.tabs.addTab(self.embed_tab, "ซ่อนข้อมูล")
        self.tabs.addTab(self.extract_tab, "ดึงข้อมูล")
        self.tabs.addTab(self.analyze_tab, "วิเคราะห์")


__all__ = ["StegoSightApp"]
