from __future__ import annotations

import os
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QPalette, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QFileDialog,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTextBrowser,
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

        self.analyze_risk_widget: RiskScoreWidget | None = None
        self.analyze_results_browser: QTextBrowser | None = None

        self._build_ui()

    # ------------------------------------------------------------------
    def apply_modern_theme(self) -> None:
        palette = QPalette()
        dark_bg = QColor("#1e1e1e")
        light_text = QColor("#f0f0f0")
        highlight = QColor("#007acc")
        palette.setColor(QPalette.Window, dark_bg)
        palette.setColor(QPalette.WindowText, light_text)
        palette.setColor(QPalette.Base, QColor("#1a1a1a"))
        palette.setColor(QPalette.AlternateBase, dark_bg)
        palette.setColor(QPalette.Text, light_text)
        palette.setColor(QPalette.Button, QColor("#252526"))
        palette.setColor(QPalette.ButtonText, light_text)
        palette.setColor(QPalette.Highlight, highlight)
        palette.setColor(QPalette.HighlightedText, QColor("#0f0f0f"))
        QApplication.instance().setPalette(palette)

        qss = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #cccccc;
        }

        QLabel, QPlainTextEdit, QTextBrowser {
            color: #cccccc;
            background: transparent;
            font-size: 14px;
        }

        QGroupBox {
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            margin-top: 16px;
            padding: 16px;
            background-color: #252526;
            font-weight: 600;
            font-size: 15px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 4px;
            color: #f3f3f3;
        }

        #FileDropArea {
            border: 2px dashed rgba(0, 122, 204, 0.6);
            border-radius: 14px;
            padding: 32px 16px;
            background-color: rgba(0, 122, 204, 0.1);
            font-size: 15px;
        }

        #FileDropArea:hover {
            border-color: #4fc3f7;
            background-color: rgba(79, 195, 247, 0.12);
        }

        QPushButton {
            background-color: #2d2d2d;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 12px 20px;
            color: #e0e0e0;
            font-size: 15px;
        }

        QPushButton:hover {
            background-color: #3a3d41;
        }

        QPushButton[primary="true"] {
            background-color: #007acc;
            border: none;
            color: white;
            padding: 16px 24px;
            font-size: 16px;
            font-weight: 600;
        }

        QPushButton[primary="true"]:hover {
            background-color: #1f91e6;
        }

        QTabWidget::pane {
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 12px;
            background-color: #1f1f1f;
        }

        QTabBar::tab {
            background: transparent;
            color: #cccccc;
            padding: 12px 24px;
            margin: 4px;
            border-radius: 12px;
            font-size: 15px;
        }

        QTabBar::tab:selected {
            background-color: #007acc;
            color: white;
        }

        QTabBar::tab:hover {
            background-color: rgba(0, 122, 204, 0.45);
        }

        QLineEdit, QComboBox {
            background-color: #2a2a2a;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 10px;
            padding: 10px;
            color: #f3f3f3;
        }

        QPlainTextEdit, QTextBrowser {
            background-color: #1b1b1b;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }

        QCheckBox {
            spacing: 12px;
            font-size: 14px;
        }

        #RiskScoreWidget {
            background-color: #252526;
            border-radius: 18px;
            border: 1px solid rgba(0, 122, 204, 0.35);
        }

        #RiskScoreValue {
            font-size: 48px;
            font-weight: 700;
            color: #4fc3f7;
        }

        #RiskScoreLevel {
            font-size: 18px;
            font-weight: 600;
        }

        QProgressBar {
            border-radius: 12px;
            background-color: #2f2f2f;
            text-align: center;
            height: 24px;
        }

        QProgressBar::chunk {
            border-radius: 12px;
            background-color: #1f91e6;
        }
        """
        QApplication.instance().setStyleSheet(qss)

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
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["🤖 อัตโนมัติ (แนะนำ)", "🎯 กำหนดเอง"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.manual_combo = QComboBox()
        self.manual_combo.addItems(["LSB", "Append", "Parity"])
        self.manual_combo.setEnabled(False)
        self.manual_combo.currentTextChanged.connect(
            lambda text: print(f"[UI] Manual technique selected: {text}")
        )
        step4_layout.addWidget(self.mode_combo)
        step4_layout.addWidget(self.manual_combo)
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
        label.setStyleSheet("font-size: 22px; color: #808080;")
        layout.addWidget(label)
        return widget

    def _create_embed_file_state(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self.embed_preview_label = QLabel()
        self.embed_preview_label.setFixedHeight(280)
        self.embed_preview_label.setAlignment(Qt.AlignCenter)
        self.embed_preview_label.setStyleSheet(
            "border-radius: 16px; background-color: #1b1b1b;"
        )

        info_card = QFrame()
        info_card.setStyleSheet(
            "background-color: #252526; border-radius: 16px; padding: 18px;"
        )
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
        label.setStyleSheet("font-size: 20px;")

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
        card.setStyleSheet(
            "background-color: #1f4f66; border-radius: 20px; padding: 24px;"
        )
        card_layout = QVBoxLayout(card)
        success_label = QLabel("✅ ซ่อนข้อมูลสำเร็จ!")
        success_label.setAlignment(Qt.AlignCenter)
        success_label.setStyleSheet("font-size: 22px; font-weight: 600;")
        self.embed_risk_label = QLabel("Risk Score: -")
        self.embed_risk_label.setAlignment(Qt.AlignCenter)
        self.embed_risk_label.setStyleSheet("font-size: 18px;")
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
        label.setStyleSheet("font-size: 22px; color: #808080;")
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

        splitter = QSplitter(Qt.Horizontal)

        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(18)

        select_group = QGroupBox("เลือกไฟล์สำหรับวิเคราะห์")
        select_layout = QVBoxLayout(select_group)
        self.analyze_drop = FileDropArea("🖼️ ลากไฟล์มาวางสำหรับวิเคราะห์")
        self.analyze_drop.fileSelected.connect(self.on_analyze_file_selected)
        select_layout.addWidget(self.analyze_drop)
        control_layout.addWidget(select_group)

        technique_group = QGroupBox("เลือกเทคนิคการวิเคราะห์")
        technique_layout = QVBoxLayout(technique_group)
        self.chi_square_checkbox = QCheckBox("Chi-Square Attack")
        self.histogram_checkbox = QCheckBox("Histogram Analysis")
        self.file_structure_checkbox = QCheckBox("File Structure Analysis")
        for cb in (
            self.chi_square_checkbox,
            self.histogram_checkbox,
            self.file_structure_checkbox,
        ):
            cb.setChecked(True)
            label = cb.text()
            cb.toggled.connect(
                lambda state, name=label: print(
                    f"[UI] Analysis option '{name}' set to {state}"
                )
            )
        technique_layout.addWidget(self.chi_square_checkbox)
        technique_layout.addWidget(self.histogram_checkbox)
        technique_layout.addWidget(self.file_structure_checkbox)
        control_layout.addWidget(technique_group)

        control_layout.addStretch(1)

        self.analyze_button = QPushButton("🔬 เริ่มการวิเคราะห์")
        self.analyze_button.setProperty("primary", True)
        self.analyze_button.clicked.connect(self.on_analyze_clicked)
        control_layout.addWidget(self.analyze_button)

        splitter.addWidget(control_panel)

        context_panel = QWidget()
        context_layout = QVBoxLayout(context_panel)
        context_layout.setSpacing(18)

        self.analyze_risk_widget = RiskScoreWidget()
        context_layout.addWidget(self.analyze_risk_widget)

        self.analyze_results_browser = QTextBrowser()
        self.analyze_results_browser.setPlaceholderText("ผลการวิเคราะห์จะปรากฏที่นี่...")
        context_layout.addWidget(self.analyze_results_browser)

        splitter.addWidget(context_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        return container

    # ------------------------------------------------------------------
    # Slots & UI Updates ------------------------------------------------
    def on_cover_file_selected(self, path: str) -> None:
        print(f"[Action] Cover file selected: {path}")
        if self.embed_context_stack is not None:
            self.embed_context_stack.setCurrentIndex(1)
        self._update_embed_preview(path)

    def on_secret_file_selected(self, path: str) -> None:
        print(f"[Action] Secret file selected: {path}")

    def on_mode_changed(self, mode: str) -> None:
        manual_enabled = "กำหนดเอง" in mode
        print(f"[Action] Mode changed to {mode}; manual enabled = {manual_enabled}")
        if self.manual_combo is not None:
            self.manual_combo.setEnabled(manual_enabled)

    def on_embed_clicked(self) -> None:
        print("[Action] เริ่มการซ่อนข้อมูล...")
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

    def on_extract_clicked(self) -> None:
        print("[Action] เริ่มการดึงข้อมูล...")
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

    def on_analyze_clicked(self) -> None:
        print("[Action] เริ่มการวิเคราะห์...")
        if self.analyze_risk_widget is not None:
            self.analyze_risk_widget.update_score(
                62,
                "กลาง",
                "พบรูปแบบที่อาจบ่งชี้ถึงการซ่อนข้อมูล ควรตรวจสอบเพิ่มเติม",
            )
        if self.analyze_results_browser is not None:
            self.analyze_results_browser.setHtml(
                """
                <h3>ผลการวิเคราะห์โดยละเอียด</h3>
                <ul>
                    <li><b>Chi-Square Attack:</b> ค่าเบี่ยงเบน 0.42 (ปานกลาง)</li>
                    <li><b>Histogram Analysis:</b> พบความผิดปกติในช่วงค่าพิกเซล 120-140</li>
                    <li><b>File Structure Analysis:</b> ตรวจพบข้อมูลส่วนเพิ่มท้ายไฟล์</li>
                </ul>
                <h3>คำแนะนำ (Actionable Guidance)</h3>
                <ul>
                    <li>ดำเนินการวิเคราะห์เชิงลึกเพิ่มเติมด้วยเครื่องมือ forensic</li>
                    <li>เปรียบเทียบกับไฟล์ต้นฉบับเพื่อหาความแตกต่าง</li>
                    <li>พิจารณาถอดรหัสข้อมูลที่ฝังอยู่</li>
                </ul>
                """
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


__all__ = ["StegoSightApp", "FileDropArea", "RiskScoreWidget"]

