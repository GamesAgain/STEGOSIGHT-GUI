from __future__ import annotations

import os
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QPalette, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class FileDropArea(QLabel):
    """Drop zone widget that also opens a file dialog on click."""

    fileSelected = pyqtSignal(str)

    def __init__(self, prompt: str, parent: QWidget | None = None) -> None:
        super().__init__(prompt, parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setObjectName("FileDropArea")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

    # Drag & drop support -------------------------------------------------
    def dragEnterEvent(self, event):  # type: ignore[override]
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            print("[UI] Drag entered drop area")
        else:
            event.ignore()

    def dropEvent(self, event):  # type: ignore[override]
        urls = event.mimeData().urls()
        if urls:
            local_path = urls[0].toLocalFile()
            if local_path:
                print(f"[UI] File dropped: {local_path}")
                self.fileSelected.emit(local_path)
        event.acceptProposedAction()

    def mousePressEvent(self, event):  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            print("[UI] Drop area clicked – opening file dialog")
            file_path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์")
            if file_path:
                self.fileSelected.emit(file_path)
        super().mousePressEvent(event)


class RiskScoreWidget(QFrame):
    """Displays a large risk score and contextual summary."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("RiskScoreWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.score_label = QLabel("0")
        self.score_label.setObjectName("RiskScoreValue")
        self.score_label.setAlignment(Qt.AlignCenter)

        self.level_label = QLabel("ระดับความเสี่ยง: -")
        self.level_label.setObjectName("RiskScoreLevel")
        self.level_label.setAlignment(Qt.AlignCenter)

        self.summary_label = QLabel("ยังไม่มีการวิเคราะห์")
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.score_label)
        layout.addWidget(self.level_label)
        layout.addWidget(self.summary_label)

    def update_score(self, score: int, level: str, summary: str) -> None:
        self.score_label.setText(str(score))
        self.level_label.setText(f"ระดับความเสี่ยง: {level}")
        self.summary_label.setText(summary)


class MethodCard(QFrame):
    """Selectable card for choosing techniques in embed/extract flows."""

    clicked = pyqtSignal()

    def __init__(self, title: str, description: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selected = False
        self.setObjectName("MethodCard")
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        self.title_label.setProperty("role", "title")

        self.description_label = QLabel(description)
        self.description_label.setWordWrap(True)
        self.description_label.setProperty("role", "description")

        layout.addWidget(self.title_label)
        layout.addWidget(self.description_label)

        self.setSelected(False)

    def setSelected(self, selected: bool) -> None:
        if self._selected == selected:
            return
        self._selected = selected
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event):  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class StegoSightApp(QMainWindow):
    """Main application window for the modernised StegoSight UI."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("STEGOSIGHT")
        self.resize(1200, 800)

        self.apply_modern_theme()

        self.tabs = QTabWidget()
        self.tabs.setObjectName("MainTabWidget")

        self.embed_context_stack: QStackedWidget | None = None
        self.embed_preview_label: QLabel | None = None
        self.embed_file_info_label: QLabel | None = None
        self.embed_progress_bar: QProgressBar | None = None
        self.embed_risk_label: QLabel | None = None

        self.extract_context_stack: QStackedWidget | None = None
        self.extract_text_output: QPlainTextEdit | None = None
        self.extract_file_info_label: QLabel | None = None

        self.embed_selected_media_type = "image"
        self.embed_selected_method = "content_adaptive"
        self.embed_method_definitions = self._build_embed_method_definitions()
        self.embed_method_cards: list[MethodCard] = []
        self.embed_method_card_map: dict[MethodCard, str] = {}
        self.embed_method_container_layout: QVBoxLayout | None = None
        self.embed_method_container: QWidget | None = None

        self.extract_selected_media_type = "image"
        self.extract_selected_method = "adaptive"
        self.extract_method_definitions = self._build_extract_method_definitions()
        self.extract_method_cards: list[MethodCard] = []
        self.extract_method_card_map: dict[MethodCard, str] = {}
        self.extract_method_container_layout: QVBoxLayout | None = None
        self.extract_method_container: QWidget | None = None

        self.analyze_risk_widget: RiskScoreWidget | None = None
        self.analyze_summary_label: QLabel | None = None
        self.analyze_file_label: QLabel | None = None
        self.analyze_results_table: QTableWidget | None = None
        self.analyze_guidance_label: QLabel | None = None
        self.analyze_log_console: QPlainTextEdit | None = None
        self.analyze_selected_path: str | None = None
        self.analyze_button: QPushButton | None = None

        self._build_ui()

    # ------------------------------------------------------------------
    def apply_modern_theme(self) -> None:
        app = QApplication.instance()
        if app is None:
            return

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
        app.setPalette(palette)

        qss = """
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

        #RiskScoreWidget {
            background-color: #f9f9f9;
            border-radius: 14px;
            border: 1px solid #e0e0e0;
        }

        #RiskScoreValue {
            font-size: 56px;
            font-weight: 700;
            color: #1E88E5;
        }

        #RiskScoreLevel {
            font-size: 16px;
            font-weight: 600;
            color: #424242;
        }

        #RiskScoreWidget QLabel {
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

        #EmbedPreview {
            border: 2px dashed #cfd8dc;
            border-radius: 16px;
            background-color: #fafafa;
            color: #90a4ae;
        }

        #InfoPanel {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 18px;
        }

        #SuccessCard {
            background-color: #e8f5e9;
            border: 1px solid #c8e6c9;
            border-radius: 18px;
            padding: 24px;
        }

        #SuccessHeadline {
            font-size: 22px;
            font-weight: 700;
            color: #2e7d32;
        }

        #EmbedRiskLabel {
            font-size: 16px;
            color: #2e7d32;
        }

        #SuccessCard QPushButton {
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
        }

        #AnalyzeGuidanceFrame {
            background-color: #e3f2fd;
            border: 1px solid #bbdefb;
            border-left: 4px solid #1E88E5;
            border-radius: 8px;
            padding: 12px;
        }

        #AnalyzeGuidanceLabel {
            color: #1e3a5f;
            font-size: 13px;
        }

        #AnalyzeFileLabel, #AnalyzeSummaryLabel {
            color: #424242;
            font-size: 13px;
        }

        QTableWidget {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
        }

        QTableWidget::item {
            padding: 6px;
        }
        """
        app.setStyleSheet(qss)

    # ------------------------------------------------------------------
    def _build_embed_method_definitions(self) -> dict[str, dict[str, dict[str, str]]]:
        return {
            "image": {
                "content_adaptive": {
                    "title": "✨ Content-Adaptive (แนะนำ)",
                    "desc": "วิเคราะห์ขอบและพื้นผิวเพื่อเลือกพื้นที่ฝังที่แนบเนียน",
                },
                "lsb": {
                    "title": "🔹 LSB Matching",
                    "desc": "ปรับ LSB เพื่อลดความผิดปกติทางสถิติ (เหมาะกับ PNG/BMP)",
                },
                "pvd": {
                    "title": "🔸 Pixel Value Differencing",
                    "desc": "กำหนดจำนวนบิตจากความต่างพิกเซล เพิ่มปริมาณข้อมูล",
                },
                "dct": {
                    "title": "📊 Discrete Cosine Transform",
                    "desc": "ฝังข้อมูลในสัมประสิทธิ์ DCT สำหรับ JPEG ทนการบีบอัดซ้ำ",
                },
                "append": {
                    "title": "📎 ต่อท้ายไฟล์ (Tail Append)",
                    "desc": "พ่วง payload ต่อท้ายไฟล์ต้นฉบับ (เหมาะกับ PNG/BMP)",
                },
            },
            "audio": {
                "audio_adaptive": {
                    "title": "✨ Adaptive Audio",
                    "desc": "วิเคราะห์ไดนามิกเสียง เลือกตำแหน่งฝังที่แนบเนียน",
                },
                "audio_lsb": {
                    "title": "🎧 LSB ในสัญญาณเสียง",
                    "desc": "ซ่อนข้อมูลด้วย LSB สำหรับ WAV/MP3/FLAC",
                },
                "audio_metadata": {
                    "title": "🏷️ Metadata Tagging",
                    "desc": "ฝังข้อมูลในเมทาดาทาของไฟล์เสียง (ID3/Tag)",
                },
            },
            "video": {
                "video_adaptive": {
                    "title": "✨ Adaptive Video",
                    "desc": "ประเมินเฟรมวิดีโอและเลือกพื้นที่ที่ยากต่อการสังเกต",
                },
                "video_lsb": {
                    "title": "🎞️ Frame LSB",
                    "desc": "ซ่อนข้อมูลทีละเฟรมด้วย LSB (รองรับ MP4/AVI/MKV/MOV)",
                },
                "video_metadata": {
                    "title": "🏷️ Metadata Tagging",
                    "desc": "ฝังข้อมูลในเมทาดาทาของไฟล์วิดีโอ (MP4/MKV/MOV)",
                },
            },
        }

    def _build_extract_method_definitions(self) -> dict[str, dict[str, dict[str, str]]]:
        return {
            "image": {
                "adaptive": {
                    "title": "✨ ตรวจจับอัตโนมัติ (แนะนำ)",
                    "desc": "ลองถอดข้อมูลด้วยหลายเทคนิคเช่น LSB, PVD, DCT และ Tail Append",
                },
                "lsb": {
                    "title": "🔹 LSB Matching",
                    "desc": "ดึงข้อมูลจากการฝังแบบ LSB (เหมาะกับ PNG/BMP)",
                },
                "pvd": {
                    "title": "🔸 Pixel Value Differencing",
                    "desc": "ใช้ความต่างของพิกเซลเพื่อตีความบิตที่ซ่อนอยู่",
                },
                "dct": {
                    "title": "📊 Discrete Cosine Transform",
                    "desc": "กู้ข้อมูลที่ฝังในสัมประสิทธิ์ DCT ของไฟล์ JPEG",
                },
                "append": {
                    "title": "📎 Tail Append",
                    "desc": "ตรวจสอบข้อมูลที่อาจถูกต่อท้ายไฟล์",
                },
            },
            "audio": {
                "audio_adaptive": {
                    "title": "✨ ตรวจจับอัตโนมัติ",
                    "desc": "ทดลอง LSB และเทคนิคเฉพาะเสียงของ STEGOSIGHT",
                },
                "audio_lsb": {
                    "title": "🎧 LSB ในสัญญาณเสียง",
                    "desc": "ถอดข้อมูลที่ซ่อนในบิตต่ำสุดของสัญญาณ PCM",
                },
            },
            "video": {
                "video_adaptive": {
                    "title": "✨ ตรวจจับอัตโนมัติ",
                    "desc": "ลองกู้ข้อมูลจากเฟรมวิดีโอโดยอัตโนมัติ",
                },
                "video_lsb": {
                    "title": "🎞️ Frame LSB",
                    "desc": "ดึงข้อมูลจากบิตต่ำสุดของแต่ละพิกเซลในเฟรม",
                },
            },
        }

    # ------------------------------------------------------------------
    def _populate_embed_method_cards(self, media_type: str) -> None:
        layout = self.embed_method_container_layout
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        methods = self.embed_method_definitions.get(media_type, {})
        self.embed_method_cards = []
        self.embed_method_card_map = {}

        for key, meta in methods.items():
            card = MethodCard(meta["title"], meta["desc"])
            card.clicked.connect(lambda _, c=card: self._select_embed_method_card(c))
            layout.addWidget(card)
            self.embed_method_cards.append(card)
            self.embed_method_card_map[card] = key

        layout.addStretch(1)

        if not methods:
            self.embed_selected_method = ""
            return

        if self.embed_selected_method not in methods:
            self.embed_selected_method = next(iter(methods))

        self._update_embed_method_selection(self.embed_selected_method)

    def _select_embed_method_card(self, card: MethodCard) -> None:
        method_key = self.embed_method_card_map.get(card)
        if not method_key:
            return

        self.embed_selected_method = method_key
        self._update_embed_method_selection(method_key)
        print(f"[UI] Embed method selected: {method_key}")

    def _update_embed_method_selection(self, method_key: str) -> None:
        for card, key in self.embed_method_card_map.items():
            card.setSelected(key == method_key)

    def _set_embed_media_type(self, media_type: str) -> None:
        if media_type not in self.embed_method_definitions:
            return
        if self.embed_selected_media_type == media_type and self.embed_method_cards:
            return
        self.embed_selected_media_type = media_type
        self._populate_embed_method_cards(media_type)

    def _populate_extract_method_cards(self, media_type: str) -> None:
        layout = self.extract_method_container_layout
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        methods = self.extract_method_definitions.get(media_type, {})
        self.extract_method_cards = []
        self.extract_method_card_map = {}

        for key, meta in methods.items():
            card = MethodCard(meta["title"], meta["desc"])
            card.clicked.connect(lambda _, c=card: self._select_extract_method_card(c))
            layout.addWidget(card)
            self.extract_method_cards.append(card)
            self.extract_method_card_map[card] = key

        layout.addStretch(1)

        if not methods:
            self.extract_selected_method = ""
            return

        if self.extract_selected_method not in methods:
            self.extract_selected_method = next(iter(methods))

        self._update_extract_method_selection(self.extract_selected_method)

    def _select_extract_method_card(self, card: MethodCard) -> None:
        method_key = self.extract_method_card_map.get(card)
        if not method_key:
            return

        self.extract_selected_method = method_key
        self._update_extract_method_selection(method_key)
        print(f"[UI] Extract method selected: {method_key}")

    def _update_extract_method_selection(self, method_key: str) -> None:
        for card, key in self.extract_method_card_map.items():
            card.setSelected(key == method_key)

    def _set_extract_media_type(self, media_type: str) -> None:
        if media_type not in self.extract_method_definitions:
            return
        if (
            self.extract_selected_media_type == media_type
            and self.extract_method_cards
        ):
            return
        self.extract_selected_media_type = media_type
        self._populate_extract_method_cards(media_type)

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.setCentralWidget(self.tabs)
        self.tabs.addTab(self._create_embed_tab(), "ซ่อนข้อมูล")
        self.tabs.addTab(self._create_extract_tab(), "ดึงข้อมูล")
        self.tabs.addTab(self._create_analyze_tab(), "วิเคราะห์")

    # ------------------------------------------------------------------
    def _create_embed_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        splitter = QSplitter(Qt.Horizontal)

        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(18)

        # Step 1 ---------------------------------------------------------
        step1_group = QGroupBox("ขั้นตอนที่ 1: เลือกไฟล์ต้นฉบับ (Cover File)")
        step1_layout = QVBoxLayout(step1_group)
        self.cover_drop = FileDropArea("🖼️ ลากไฟล์มาวางที่นี่ หรือกดเพื่อเลือกไฟล์")
        self.cover_drop.fileSelected.connect(self.on_cover_file_selected)
        step1_layout.addWidget(self.cover_drop)
        control_layout.addWidget(step1_group)

        # Step 2 ---------------------------------------------------------
        step2_group = QGroupBox("ขั้นตอนที่ 2: เตรียมข้อมูลลับ (Secret Data)")
        step2_layout = QVBoxLayout(step2_group)
        secret_tabs = QTabWidget()
        secret_tabs.setTabPosition(QTabWidget.North)

        self.secret_text_edit = QPlainTextEdit()
        self.secret_text_edit.setPlaceholderText("พิมพ์ข้อความลับที่นี่...")
        self.secret_text_edit.textChanged.connect(
            lambda: print("[UI] Secret text updated")
        )

        secret_text_tab = QWidget()
        secret_text_layout = QVBoxLayout(secret_text_tab)
        secret_text_layout.addWidget(self.secret_text_edit)

        secret_file_tab = QWidget()
        secret_file_layout = QVBoxLayout(secret_file_tab)
        self.secret_file_drop = FileDropArea("📄 ลากไฟล์ลับมาวาง หรือกดเพื่อเลือก")
        self.secret_file_drop.fileSelected.connect(self.on_secret_file_selected)
        secret_file_layout.addWidget(self.secret_file_drop)

        secret_tabs.addTab(secret_text_tab, "📝 พิมพ์ข้อความ")
        secret_tabs.addTab(secret_file_tab, "📄 เลือกไฟล์")

        step2_layout.addWidget(secret_tabs)
        control_layout.addWidget(step2_group)

        # Step 3 ---------------------------------------------------------
        step3_group = QGroupBox("ขั้นตอนที่ 3: ตั้งค่าความปลอดภัย")
        step3_layout = QVBoxLayout(step3_group)
        self.encrypt_checkbox = QCheckBox("เปิด/ปิด การเข้ารหัส AES-256-GCM")
        self.encrypt_checkbox.setChecked(True)
        self.encrypt_checkbox.toggled.connect(
            lambda state: print(f"[UI] Encryption toggled: {state}")
        )
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("รหัสผ่าน")
        self.password_input.textChanged.connect(
            lambda text: print(f"[UI] Password updated (length {len(text)})")
        )
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("ยืนยันรหัสผ่าน")
        self.confirm_password_input.textChanged.connect(
            lambda text: print(
                f"[UI] Password confirmation updated (length {len(text)})"
            )
        )
        step3_layout.addWidget(self.encrypt_checkbox)
        step3_layout.addWidget(self.password_input)
        step3_layout.addWidget(self.confirm_password_input)
        control_layout.addWidget(step3_group)

        # Step 4 ---------------------------------------------------------
        step4_group = QGroupBox("ขั้นตอนที่ 4: เลือกเทคนิคการซ่อน")
        step4_layout = QVBoxLayout(step4_group)
        step4_layout.setSpacing(12)

        method_desc = QLabel(
            "เลือกเทคนิคที่ใช้ซ่อนข้อมูลให้ตรงกับไฟล์ หรือใช้โหมด Content-Adaptive"
        )
        method_desc.setWordWrap(True)
        step4_layout.addWidget(method_desc)

        self.embed_method_container = QWidget()
        self.embed_method_container_layout = QVBoxLayout(self.embed_method_container)
        self.embed_method_container_layout.setContentsMargins(0, 0, 0, 0)
        self.embed_method_container_layout.setSpacing(10)
        step4_layout.addWidget(self.embed_method_container)

        self._populate_embed_method_cards(self.embed_selected_media_type)

        embed_hint = QLabel(
            "โหมด Content-Adaptive จะเลือกค่าที่เหมาะสมให้โดยอัตโนมัติ แต่ยังสามารถเลือกวิธีเฉพาะได้"
        )
        embed_hint.setWordWrap(True)
        embed_hint.setStyleSheet("color: #546e7a; font-size: 13px;")
        step4_layout.addWidget(embed_hint)
        control_layout.addWidget(step4_group)

        control_layout.addStretch(1)

        self.embed_button = QPushButton("🔒 เริ่มการซ่อนข้อมูล")
        self.embed_button.setProperty("primary", True)
        self.embed_button.clicked.connect(self.on_embed_clicked)
        control_layout.addWidget(self.embed_button)

        splitter.addWidget(control_panel)

        # Context panel --------------------------------------------------
        self.embed_context_stack = QStackedWidget()
        self.embed_context_stack.addWidget(self._create_embed_idle_state())
        self.embed_context_stack.addWidget(self._create_embed_file_state())
        self.embed_context_stack.addWidget(self._create_embed_processing_state())
        self.embed_context_stack.addWidget(self._create_embed_success_state())

        splitter.addWidget(self.embed_context_stack)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        return container

    def _create_embed_idle_state(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel("🕒 รอการเลือกไฟล์...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 22px; color: #9e9e9e;")
        layout.addWidget(label)
        return widget

    def _create_embed_file_state(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self.embed_preview_label = QLabel()
        self.embed_preview_label.setFixedHeight(280)
        self.embed_preview_label.setAlignment(Qt.AlignCenter)
        self.embed_preview_label.setObjectName("EmbedPreview")

        info_card = QFrame()
        info_card.setObjectName("InfoPanel")
        info_layout = QVBoxLayout(info_card)
        self.embed_file_info_label = QLabel("ยังไม่มีข้อมูลไฟล์")
        self.embed_file_info_label.setWordWrap(True)
        info_layout.addWidget(self.embed_file_info_label)

        layout.addWidget(self.embed_preview_label)
        layout.addWidget(info_card)
        layout.addStretch(1)
        return widget

    def _create_embed_processing_state(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        label = QLabel("กำลังซ่อนข้อมูล...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; color: #1E88E5;")

        self.embed_progress_bar = QProgressBar()
        self.embed_progress_bar.setRange(0, 0)
        self.embed_progress_bar.setFixedWidth(320)

        layout.addWidget(label)
        layout.addWidget(self.embed_progress_bar, alignment=Qt.AlignCenter)
        return widget

    def _create_embed_success_state(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        card = QFrame()
        card.setObjectName("SuccessCard")
        card_layout = QVBoxLayout(card)
        success_label = QLabel("✅ ซ่อนข้อมูลสำเร็จ!")
        success_label.setAlignment(Qt.AlignCenter)
        success_label.setObjectName("SuccessHeadline")
        self.embed_risk_label = QLabel("Risk Score: -")
        self.embed_risk_label.setAlignment(Qt.AlignCenter)
        self.embed_risk_label.setObjectName("EmbedRiskLabel")
        card_layout.addWidget(success_label)
        card_layout.addWidget(self.embed_risk_label)

        action_layout = QHBoxLayout()
        save_button = QPushButton("💾 บันทึกไฟล์")
        save_button.clicked.connect(lambda: print("[UI] Save stego file"))
        analyze_button = QPushButton("วิเคราะห์เชิงลึก")
        analyze_button.clicked.connect(
            lambda: print("[UI] Requesting deep analysis")
        )
        action_layout.addWidget(save_button)
        action_layout.addWidget(analyze_button)
        card_layout.addLayout(action_layout)

        layout.addWidget(card)
        layout.addStretch(1)
        return widget

    # ------------------------------------------------------------------
    def _create_extract_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        splitter = QSplitter(Qt.Horizontal)

        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(18)

        step1_group = QGroupBox("ขั้นตอนที่ 1: เลือกไฟล์ที่ต้องการตรวจสอบ")
        step1_layout = QVBoxLayout(step1_group)
        self.extract_drop = FileDropArea("🖼️ ลากไฟล์ Stego มาวาง หรือกดเพื่อเลือก")
        self.extract_drop.fileSelected.connect(self.on_extract_file_selected)
        step1_layout.addWidget(self.extract_drop)
        control_layout.addWidget(step1_group)

        step2_group = QGroupBox("ขั้นตอนที่ 2: ตั้งค่าการถอดรหัส")
        step2_layout = QVBoxLayout(step2_group)
        self.extract_encrypted_checkbox = QCheckBox("ข้อมูลอาจถูกเข้ารหัส")
        self.extract_encrypted_checkbox.toggled.connect(
            lambda state: print(f"[UI] Extraction encryption toggled: {state}")
        )
        self.extract_password_input = QLineEdit()
        self.extract_password_input.setEchoMode(QLineEdit.Password)
        self.extract_password_input.setPlaceholderText("รหัสผ่าน (ถ้ามี)")
        self.extract_password_input.textChanged.connect(
            lambda text: print(
                f"[UI] Extraction password updated (length {len(text)})"
            )
        )
        step2_layout.addWidget(self.extract_encrypted_checkbox)
        step2_layout.addWidget(self.extract_password_input)
        control_layout.addWidget(step2_group)

        step3_group = QGroupBox("ขั้นตอนที่ 3: เลือกเทคนิคการดึงข้อมูล")
        step3_layout = QVBoxLayout(step3_group)
        step3_layout.setSpacing(12)

        extract_desc = QLabel(
            "เลือกเทคนิคให้ตรงกับตอนฝังข้อมูล หรือใช้โหมดตรวจจับอัตโนมัติ"
        )
        extract_desc.setWordWrap(True)
        step3_layout.addWidget(extract_desc)

        self.extract_method_container = QWidget()
        self.extract_method_container_layout = QVBoxLayout(self.extract_method_container)
        self.extract_method_container_layout.setContentsMargins(0, 0, 0, 0)
        self.extract_method_container_layout.setSpacing(10)
        step3_layout.addWidget(self.extract_method_container)

        self._populate_extract_method_cards(self.extract_selected_media_type)

        extract_hint = QLabel(
            "ระบบจะลองหลายเทคนิคเมื่อเลือกโหมดตรวจจับอัตโนมัติ"
        )
        extract_hint.setWordWrap(True)
        extract_hint.setStyleSheet("color: #546e7a; font-size: 13px;")
        step3_layout.addWidget(extract_hint)

        control_layout.addWidget(step3_group)

        control_layout.addStretch(1)

        self.extract_button = QPushButton("🔓 เริ่มการดึงข้อมูล")
        self.extract_button.setProperty("primary", True)
        self.extract_button.clicked.connect(self.on_extract_clicked)
        control_layout.addWidget(self.extract_button)

        splitter.addWidget(control_panel)

        self.extract_context_stack = QStackedWidget()
        self.extract_context_stack.addWidget(self._create_extract_idle_state())
        self.extract_context_stack.addWidget(self._create_extract_result_state())

        splitter.addWidget(self.extract_context_stack)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        return container

    def _create_extract_idle_state(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel("⌛ รอการดึงข้อมูล...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 22px; color: #9e9e9e;")
        layout.addWidget(label)
        return widget

    def _create_extract_result_state(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        result_tabs = QTabWidget()
        text_tab = QWidget()
        text_layout = QVBoxLayout(text_tab)
        self.extract_text_output = QPlainTextEdit()
        self.extract_text_output.setReadOnly(True)
        text_layout.addWidget(self.extract_text_output)

        file_tab = QWidget()
        file_layout = QVBoxLayout(file_tab)
        self.extract_file_info_label = QLabel("ยังไม่มีไฟล์ที่ดึงได้")
        self.extract_file_info_label.setWordWrap(True)
        save_button = QPushButton("บันทึกไฟล์ที่ดึงได้...")
        save_button.clicked.connect(lambda: print("[UI] Save extracted file"))
        file_layout.addWidget(self.extract_file_info_label)
        file_layout.addWidget(save_button)

        result_tabs.addTab(text_tab, "📝 ข้อความ")
        result_tabs.addTab(file_tab, "📄 ไฟล์")

        layout.addWidget(result_tabs)
        return widget

    # ------------------------------------------------------------------
    def _create_analyze_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(18)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(18)

        select_group = QGroupBox("ขั้นตอนที่ 1: เลือกไฟล์สำหรับวิเคราะห์")
        select_layout = QVBoxLayout(select_group)
        self.analyze_drop = FileDropArea(
            "🖼️ ลากไฟล์มาวางสำหรับวิเคราะห์ หรือคลิกเพื่อเลือก"
        )
        self.analyze_drop.fileSelected.connect(self.on_analyze_file_selected)
        select_layout.addWidget(self.analyze_drop)

        self.analyze_file_label = QLabel("ยังไม่มีไฟล์ที่ถูกเลือก")
        self.analyze_file_label.setWordWrap(True)
        self.analyze_file_label.setObjectName("AnalyzeFileLabel")
        select_layout.addWidget(self.analyze_file_label)

        control_layout.addWidget(select_group)

        technique_group = QGroupBox("ขั้นตอนที่ 2: เลือกเทคนิคการวิเคราะห์")
        technique_layout = QVBoxLayout(technique_group)
        self.chi_square_checkbox = QCheckBox("Chi-Square Attack")
        self.histogram_checkbox = QCheckBox("Histogram Analysis")
        self.file_structure_checkbox = QCheckBox("File Structure Analysis")
        for checkbox in (
            self.chi_square_checkbox,
            self.histogram_checkbox,
            self.file_structure_checkbox,
        ):
            checkbox.setChecked(True)
            label = checkbox.text()
            checkbox.toggled.connect(
                lambda state, name=label: print(
                    f"[UI] Analysis option '{name}' set to {state}"
                )
            )
            technique_layout.addWidget(checkbox)

        technique_hint = QLabel(
            "สามารถเลือกหลายเทคนิคพร้อมกันเพื่อเพิ่มความแม่นยำของผลลัพธ์"
        )
        technique_hint.setWordWrap(True)
        technique_layout.addWidget(technique_hint)

        control_layout.addWidget(technique_group)

        control_layout.addStretch(1)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.analyze_button = QPushButton("🔬 เริ่มการวิเคราะห์")
        self.analyze_button.setProperty("primary", True)
        self.analyze_button.clicked.connect(self.on_analyze_clicked)
        self.analyze_button.setEnabled(False)
        button_row.addWidget(self.analyze_button)
        button_row.addStretch(1)
        control_layout.addLayout(button_row)

        splitter.addWidget(control_panel)

        result_panel = QWidget()
        result_layout = QVBoxLayout(result_panel)
        result_layout.setSpacing(18)

        overview_group = QGroupBox("ภาพรวมผลการวิเคราะห์")
        overview_layout = QVBoxLayout(overview_group)
        overview_layout.setSpacing(12)

        self.analyze_risk_widget = RiskScoreWidget()
        self.analyze_risk_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Maximum
        )
        overview_layout.addWidget(self.analyze_risk_widget)

        self.analyze_summary_label = QLabel(
            "เลือกไฟล์แล้วกดปุ่มเริ่มการวิเคราะห์เพื่อดูผลลัพธ์"
        )
        self.analyze_summary_label.setWordWrap(True)
        self.analyze_summary_label.setObjectName("AnalyzeSummaryLabel")
        overview_layout.addWidget(self.analyze_summary_label)

        result_layout.addWidget(overview_group)

        detail_group = QGroupBox("รายละเอียดเชิงลึก")
        detail_layout = QVBoxLayout(detail_group)
        detail_layout.setSpacing(12)

        self.analyze_results_table = QTableWidget(0, 3)
        self.analyze_results_table.setHorizontalHeaderLabels(
            ["Technique", "Result", "Confidence"]
        )
        self.analyze_results_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.analyze_results_table.verticalHeader().setVisible(False)
        self.analyze_results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.analyze_results_table.setSelectionMode(QTableWidget.NoSelection)
        self.analyze_results_table.setMinimumHeight(200)
        detail_layout.addWidget(self.analyze_results_table)

        guidance_frame = QFrame()
        guidance_frame.setObjectName("AnalyzeGuidanceFrame")
        guidance_frame.setFrameShape(QFrame.StyledPanel)
        guidance_layout = QVBoxLayout(guidance_frame)
        guidance_layout.setSpacing(6)
        guidance_layout.setContentsMargins(12, 8, 12, 8)

        guidance_title = QLabel("คำแนะนำเพิ่มเติม")
        guidance_title.setStyleSheet("font-weight: 600;")
        guidance_layout.addWidget(guidance_title)

        self.analyze_guidance_label = QLabel(
            "คำแนะนำจะปรากฏหลังจากที่ระบบทำการวิเคราะห์เสร็จสิ้น"
        )
        self.analyze_guidance_label.setWordWrap(True)
        self.analyze_guidance_label.setObjectName("AnalyzeGuidanceLabel")
        guidance_layout.addWidget(self.analyze_guidance_label)

        detail_layout.addWidget(guidance_frame)

        result_layout.addWidget(detail_group)

        log_group = QGroupBox("บันทึกสถานะการทำงาน")
        log_layout = QVBoxLayout(log_group)
        log_layout.setSpacing(12)

        self.analyze_log_console = QPlainTextEdit()
        self.analyze_log_console.setReadOnly(True)
        self.analyze_log_console.setPlaceholderText(
            "ระบบจะบันทึกขั้นตอนและคำเตือนในการวิเคราะห์ที่นี่"
        )
        self.analyze_log_console.setMinimumHeight(220)
        log_layout.addWidget(self.analyze_log_console)

        result_layout.addWidget(log_group)

        splitter.addWidget(result_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        scroll_layout.addWidget(splitter)
        scroll_layout.addStretch(1)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        return container

    # ------------------------------------------------------------------
    # Slots & UI Updates ------------------------------------------------
    def on_cover_file_selected(self, path: str) -> None:
        print(f"[Action] Cover file selected: {path}")
        media_type = self._infer_media_type_from_suffix(os.path.splitext(path)[1])
        if media_type:
            self._set_embed_media_type(media_type)
        if self.embed_context_stack is not None:
            self.embed_context_stack.setCurrentIndex(1)
        self._update_embed_preview(path)

    def on_secret_file_selected(self, path: str) -> None:
        print(f"[Action] Secret file selected: {path}")

    def on_embed_clicked(self) -> None:
        print(
            f"[Action] เริ่มการซ่อนข้อมูล... (method={self.embed_selected_method})"
        )
        if self.embed_context_stack is not None:
            self.embed_context_stack.setCurrentIndex(2)
        QTimer.singleShot(1500, self._complete_embedding)

    def _complete_embedding(self) -> None:
        print("[Result] การซ่อนข้อมูลเสร็จสมบูรณ์")
        if self.embed_context_stack is not None:
            self.embed_context_stack.setCurrentIndex(3)
        if self.embed_risk_label is not None:
            self.embed_risk_label.setText("Risk Score: 18 (ต่ำ)")

    def _update_embed_preview(self, path: str) -> None:
        if not self.embed_preview_label or not self.embed_file_info_label:
            return
        self.embed_preview_label.clear()
        if os.path.exists(path) and path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.embed_preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self.embed_preview_label.setPixmap(scaled)
            else:
                self.embed_preview_label.setText("ไม่สามารถแสดงตัวอย่างไฟล์นี้ได้")
        else:
            self.embed_preview_label.setText("ไม่สามารถแสดงตัวอย่างไฟล์นี้ได้")

        file_size = os.path.getsize(path) if os.path.exists(path) else 0
        info_text = (
            f"ชื่อไฟล์: {os.path.basename(path)}\n"
            f"ขนาดไฟล์: {self._format_file_size(file_size)}\n"
            f"ประเภทไฟล์: {os.path.splitext(path)[1] or 'ไม่ทราบ'}\n"
            f"ความจุโดยประมาณ: {self._estimate_capacity(file_size)}"
        )
        self.embed_file_info_label.setText(info_text)

    def on_extract_file_selected(self, path: str) -> None:
        print(f"[Action] Extract target selected: {path}")
        media_type = self._infer_media_type_from_suffix(os.path.splitext(path)[1])
        if media_type:
            self._set_extract_media_type(media_type)

    def on_extract_clicked(self) -> None:
        print(
            f"[Action] เริ่มการดึงข้อมูล... (method={self.extract_selected_method})"
        )
        if self.extract_context_stack is not None:
            self.extract_context_stack.setCurrentIndex(1)
        if self.extract_text_output is not None:
            self.extract_text_output.setPlainText(
                "ผลลัพธ์ตัวอย่าง: \n" "พบข้อความลับที่ถูกถอดรหัสเรียบร้อย"
            )
        if self.extract_file_info_label is not None:
            self.extract_file_info_label.setText(
                "ไฟล์ลับ: secret_document.txt\nขนาด: 4.2 KB"
            )
        print("[Result] การดึงข้อมูลเสร็จสมบูรณ์")

    def on_analyze_file_selected(self, path: str) -> None:
        print(f"[Action] Analyze target selected: {path}")
        self.analyze_selected_path = path

        if self.analyze_file_label is not None:
            if os.path.exists(path):
                size_text = self._format_file_size(os.path.getsize(path))
                self.analyze_file_label.setText(
                    f"ไฟล์: {os.path.basename(path)}\nขนาดไฟล์: {size_text}"
                )
            else:
                self.analyze_file_label.setText("ไม่พบไฟล์ที่เลือก กรุณาตรวจสอบอีกครั้ง")

        if self.analyze_risk_widget is not None:
            self.analyze_risk_widget.update_score(
                0, "-", "พร้อมสำหรับการวิเคราะห์ เมื่อพร้อมกดปุ่มด้านล่าง"
            )

        if self.analyze_summary_label is not None:
            self.analyze_summary_label.setText(
                "ไฟล์พร้อมสำหรับการวิเคราะห์ เลือกเทคนิคที่ต้องการแล้วกดปุ่มเริ่ม"
            )

        if self.analyze_log_console is not None:
            self.analyze_log_console.appendPlainText(
                f"[READY] เตรียมวิเคราะห์ไฟล์: {os.path.basename(path)}"
            )

        if self.analyze_button is not None:
            self.analyze_button.setEnabled(True)

    def on_analyze_clicked(self) -> None:
        print("[Action] เริ่มการวิเคราะห์...")

        if not self.analyze_selected_path or not os.path.exists(
            self.analyze_selected_path
        ):
            if self.analyze_log_console is not None:
                self.analyze_log_console.clear()
                self.analyze_log_console.appendPlainText(
                    "[WARN] กรุณาเลือกไฟล์ก่อนเริ่มการวิเคราะห์"
                )
            if self.analyze_summary_label is not None:
                self.analyze_summary_label.setText(
                    "กรุณาเลือกไฟล์ที่ต้องการวิเคราะห์ก่อนเริ่มทำงาน"
                )
            return

        if self.analyze_log_console is not None:
            self.analyze_log_console.clear()
            self.analyze_log_console.appendPlainText("[INFO] เริ่มการวิเคราะห์ไฟล์...")
            self.analyze_log_console.appendPlainText(
                "[RUN] กำลังประมวลผลเทคนิค: Chi-Square, Histogram, Structure"
            )

        if self.analyze_risk_widget is not None:
            self.analyze_risk_widget.update_score(
                62,
                "กลาง",
                "พบรูปแบบที่อาจบ่งชี้ถึงการซ่อนข้อมูล ควรตรวจสอบเพิ่มเติม",
            )

        if self.analyze_summary_label is not None:
            summary_lines = [
                "คะแนนความเสี่ยงโดยรวม 62/100 (ระดับกลาง)",
                "Chi-Square ให้ค่าผิดปกติสูงในช่วงพิกเซล 120-140",
                "พบข้อมูลต่อท้ายไฟล์และ Metadata จำนวนหนึ่ง",
            ]
            self.analyze_summary_label.setText("\n".join(summary_lines))

        if self.analyze_results_table is not None:
            results = [
                ("Chi-Square Attack", "ค่าเบี่ยงเบน 0.42 (ปานกลาง)", "65%"),
                ("Histogram Analysis", "พบความผิดปกติในช่วง 120-140", "58%"),
                ("File Structure Analysis", "ตรวจพบข้อมูลต่อท้ายไฟล์", "92%"),
            ]
            self.analyze_results_table.setRowCount(len(results))
            for row_index, row in enumerate(results):
                for column_index, value in enumerate(row):
                    item = QTableWidgetItem(value)
                    if column_index == 2:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.analyze_results_table.setItem(row_index, column_index, item)

        if self.analyze_guidance_label is not None:
            guidance_html = """
                <ul>
                    <li>เปรียบเทียบไฟล์นี้กับต้นฉบับเพื่อตรวจสอบความแตกต่างของพิกเซล</li>
                    <li>ดำเนินการดึงข้อมูลด้วยเทคนิค LSB หรือ Tail Append ในแท็บ Extract</li>
                    <li>สำรวจ Metadata เพื่อค้นหาข้อมูลเพิ่มเติมที่อาจถูกซ่อน</li>
                </ul>
            """
            self.analyze_guidance_label.setText(guidance_html.strip())

        if self.analyze_log_console is not None:
            self.analyze_log_console.appendPlainText(
                "[DONE] การวิเคราะห์เสร็จสิ้น พบสัญญาณที่ควรตรวจสอบต่อ"
            )

        print("[Result] การวิเคราะห์เสร็จสมบูรณ์")

    # ------------------------------------------------------------------
    @staticmethod
    def _format_file_size(size: int) -> str:
        units = ["B", "KB", "MB", "GB"]
        value = float(size)
        for unit in units:
            if value < 1024 or unit == units[-1]:
                return f"{value:.2f} {unit}"
            value /= 1024
        return f"{value:.2f} TB"

    @staticmethod
    def _estimate_capacity(size: int) -> str:
        approx = size * 0.15
        return f"~{StegoSightApp._format_file_size(int(approx))} ของข้อมูลลับ"


    @staticmethod
    def _infer_media_type_from_suffix(suffix: str) -> str | None:
        suffix = (suffix or "").lower()
        image_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
        audio_exts = {".wav", ".mp3", ".flac", ".aac", ".ogg", ".wma"}
        video_exts = {
            ".avi",
            ".mp4",
            ".mkv",
            ".mov",
            ".ogv",
            ".wmv",
            ".m4v",
            ".mpeg",
            ".mpg",
        }

        if suffix in image_exts:
            return "image"
        if suffix in audio_exts:
            return "audio"
        if suffix in video_exts:
            return "video"
        return None


__all__ = ["StegoSightApp", "FileDropArea", "RiskScoreWidget", "MethodCard"]

