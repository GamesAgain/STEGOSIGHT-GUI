from __future__ import annotations

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..components import FileDropArea, MethodCard
from ..utils import infer_media_type_from_suffix


class ExtractTab(QWidget):
    """Extraction workflow with technique selection and result viewer."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.extract_context_stack: QStackedWidget | None = None
        self.extract_text_output: QPlainTextEdit | None = None
        self.extract_file_info_label: QLabel | None = None
        self.extract_encrypted_checkbox: QCheckBox | None = None
        self.extract_password_input: QLineEdit | None = None
        self.extract_button: QPushButton | None = None
        self.extract_drop: FileDropArea | None = None

        self.extract_method_container: QWidget | None = None
        self.extract_method_container_layout: QVBoxLayout | None = None

        self.extract_selected_media_type = "image"
        self.extract_selected_method = "adaptive"
        self.extract_method_definitions = self._build_extract_method_definitions()
        self.extract_method_cards: list[MethodCard] = []
        self.extract_method_card_map: dict[MethodCard, str] = {}

        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
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
        self.extract_text_output.setObjectName("ExtractTextOutput")
        text_layout.addWidget(self.extract_text_output)

        file_tab = QWidget()
        file_layout = QVBoxLayout(file_tab)
        self.extract_file_info_label = QLabel("ยังไม่มีไฟล์ที่ดึงได้")
        self.extract_file_info_label.setWordWrap(True)
        self.extract_file_info_label.setObjectName("ExtractFileInfo")
        save_button = QPushButton("บันทึกไฟล์ที่ดึงได้...")
        save_button.clicked.connect(lambda: print("[UI] Save extracted file"))
        file_layout.addWidget(self.extract_file_info_label)
        file_layout.addWidget(save_button)

        result_tabs.addTab(text_tab, "📝 ข้อความ")
        result_tabs.addTab(file_tab, "📄 ไฟล์")

        layout.addWidget(result_tabs)
        return widget

    # ------------------------------------------------------------------
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
        if self.extract_selected_media_type == media_type and self.extract_method_cards:
            return
        self.extract_selected_media_type = media_type
        self._populate_extract_method_cards(media_type)

    # ------------------------------------------------------------------
    def on_extract_file_selected(self, path: str) -> None:
        print(f"[Action] Extract target selected: {path}")
        media_type = infer_media_type_from_suffix(os.path.splitext(path)[1])
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


__all__ = ["ExtractTab"]
