from __future__ import annotations

import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..components import FileDropArea, MethodCard, PreviewImageLabel
from ..utils import estimate_capacity, format_file_size, infer_media_type_from_suffix


class EmbedTab(QWidget):
    """Modern embed workflow with dedicated controls and context panel."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.embed_context_stack: QStackedWidget | None = None
        self.embed_preview_label: PreviewImageLabel | None = None
        self.embed_file_info_label: QLabel | None = None
        self.embed_progress_bar: QProgressBar | None = None
        self.embed_risk_label: QLabel | None = None
        self.embed_method_summary_label: QLabel | None = None
        self.embed_hint_label: QLabel | None = None
        self.cover_support_label: QLabel | None = None
        self.cover_drop: FileDropArea | None = None

        self.secret_text_edit: QPlainTextEdit | None = None
        self.secret_file_drop: FileDropArea | None = None
        self.encrypt_checkbox: QCheckBox | None = None
        self.password_input: QLineEdit | None = None
        self.confirm_password_input: QLineEdit | None = None
        self.embed_button: QPushButton | None = None

        self.embed_method_container: QWidget | None = None
        self.embed_method_container_layout: QVBoxLayout | None = None

        self.embed_selected_media_type = "image"
        self.embed_selected_method = "content_adaptive"
        self.embed_method_definitions = self._build_embed_method_definitions()
        self.embed_method_cards: list[MethodCard] = []
        self.embed_method_card_map: dict[MethodCard, str] = {}
        self.embed_media_buttons: dict[str, QPushButton] = {}

        self.embed_media_supports = {
            "image": "รองรับไฟล์ภาพ: PNG, JPEG, JPG, BMP",
            "audio": "รองรับไฟล์เสียง: WAV, MP3, FLAC",
            "video": "รองรับไฟล์วิดีโอ: AVI, MP4, MKV, MOV, OGG, WMA, AAC",
        }
        self.embed_media_prompts = {
            "image": "🖼️ ลากไฟล์ภาพมาวาง หรือกดเพื่อเลือกไฟล์",
            "audio": "🎧 ลากไฟล์เสียงมาวาง หรือกดเพื่อเลือกไฟล์",
            "video": "🎞️ ลากไฟล์วิดีโอมาวาง หรือกดเพื่อเลือกไฟล์",
        }
        self.embed_media_summaries = {
            "image": "เทคนิคที่เหมาะกับไฟล์ภาพ เช่น Content-Adaptive, LSB Matching, PVD และ DCT",
            "audio": "เทคนิคที่ออกแบบมาสำหรับไฟล์เสียง ทั้ง Adaptive Audio, LSB และ Metadata",
            "video": "เทคนิคสำหรับไฟล์วิดีโอ ครอบคลุมการปรับอัตโนมัติ LSB และ Metadata",
        }
        self._embed_preview_source: str | None = None

        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        splitter = QSplitter(Qt.Horizontal)

        control_scroll = QScrollArea()
        control_scroll.setWidgetResizable(True)
        control_scroll.setFrameShape(QFrame.NoFrame)
        control_scroll.setMinimumWidth(380)

        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(18)

        # Step 1 ---------------------------------------------------------
        step1_group = QGroupBox("ขั้นตอนที่ 1: เลือกไฟล์ต้นฉบับ (Cover File)")
        step1_layout = QVBoxLayout(step1_group)
        step1_layout.setSpacing(12)
        prompt = self.embed_media_prompts.get(
            self.embed_selected_media_type,
            "🖼️ ลากไฟล์มาวางที่นี่ หรือกดเพื่อเลือกไฟล์",
        )
        self.cover_drop = FileDropArea(prompt)
        self.cover_drop.fileSelected.connect(self.on_cover_file_selected)
        step1_layout.addWidget(self.cover_drop)
        self.cover_support_label = QLabel()
        self.cover_support_label.setWordWrap(True)
        self.cover_support_label.setStyleSheet("color: #546e7a; font-size: 12px;")
        step1_layout.addWidget(self.cover_support_label)
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
        media_row = QHBoxLayout()
        media_row.setSpacing(8)
        media_row.addWidget(QLabel("เลือกประเภทไฟล์:"))
        for key, label in (
            ("image", "🖼️ ไฟล์ภาพ"),
            ("audio", "🎧 ไฟล์เสียง"),
            ("video", "🎞️ ไฟล์วิดีโอ"),
        ):
            button = QPushButton(label)
            button.setCheckable(True)
            button.setObjectName("toggleButton")
            button.clicked.connect(lambda _, media=key: self._set_embed_media_type(media))
            self.embed_media_buttons[key] = button
            media_row.addWidget(button)
        media_row.addStretch(1)
        step4_layout.addLayout(media_row)

        self.embed_method_summary_label = QLabel()
        self.embed_method_summary_label.setWordWrap(True)
        self.embed_method_summary_label.setStyleSheet("color: #455a64; font-size: 13px;")
        step4_layout.addWidget(self.embed_method_summary_label)

        self.embed_method_container = QWidget()
        self.embed_method_container_layout = QVBoxLayout(self.embed_method_container)
        self.embed_method_container_layout.setContentsMargins(0, 0, 0, 0)
        self.embed_method_container_layout.setSpacing(10)

        method_scroll = QScrollArea()
        method_scroll.setWidgetResizable(True)
        method_scroll.setWidget(self.embed_method_container)
        step4_layout.addWidget(method_scroll)

        self.embed_hint_label = QLabel(
            "โหมด Content-Adaptive จะเลือกค่าที่เหมาะสมให้โดยอัตโนมัติ แต่ยังสามารถเลือกวิธีเฉพาะได้"
        )
        self.embed_hint_label.setWordWrap(True)
        self.embed_hint_label.setStyleSheet("color: #546e7a; font-size: 12px;")
        step4_layout.addWidget(self.embed_hint_label)
        control_layout.addWidget(step4_group)

        control_layout.addStretch(1)

        self.embed_button = QPushButton("🔒 เริ่มการซ่อนข้อมูล")
        self.embed_button.setProperty("primary", True)
        self.embed_button.clicked.connect(self.on_embed_clicked)
        control_layout.addWidget(self.embed_button)

        control_scroll.setWidget(control_panel)
        splitter.addWidget(control_scroll)

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

        self._populate_embed_method_cards(self.embed_selected_media_type)
        self._update_embed_media_context(self.embed_selected_media_type)

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

        self.embed_preview_label = PreviewImageLabel()
        self.embed_preview_label.setMinimumHeight(260)

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
                    "desc": "ฝังข้อมูลใน Meta Tag (ID3/Tag สำหรับ MP3/FLAC)",
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
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
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
            self._update_embed_media_context(media_type)
            return
        self.embed_selected_media_type = media_type
        self._populate_embed_method_cards(media_type)
        self._update_embed_media_context(media_type)

    def _update_embed_media_context(self, media_type: str) -> None:
        prompt = self.embed_media_prompts.get(media_type)
        if prompt and self.cover_drop is not None:
            self.cover_drop.setPrompt(prompt)

        support_text = self.embed_media_supports.get(
            media_type, self.embed_media_supports.get("image")
        )
        if self.cover_support_label is not None:
            if support_text:
                self.cover_support_label.setText(support_text)
            else:
                self.cover_support_label.clear()

        summary_text = self.embed_media_summaries.get(
            media_type, self.embed_media_summaries.get("image")
        )
        if self.embed_method_summary_label is not None:
            if summary_text:
                self.embed_method_summary_label.setText(summary_text)
            else:
                self.embed_method_summary_label.clear()

        for key, button in self.embed_media_buttons.items():
            button.blockSignals(True)
            button.setChecked(key == media_type)
            button.blockSignals(False)

    # ------------------------------------------------------------------
    def on_cover_file_selected(self, path: str) -> None:
        print(f"[Action] Cover file selected: {path}")
        media_type = infer_media_type_from_suffix(os.path.splitext(path)[1])
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
        self._embed_preview_source = None
        image_exts = (".png", ".jpg", ".jpeg", ".bmp")
        if os.path.exists(path) and path.lower().endswith(image_exts):
            pixmap = QPixmap(path)
            if pixmap.isNull():
                self.embed_preview_label.setImage(None)
                self.embed_preview_label.showMessage("ไม่สามารถแสดงตัวอย่างไฟล์นี้ได้")
            else:
                self._embed_preview_source = path
                self.embed_preview_label.setImage(pixmap)
        else:
            self.embed_preview_label.setImage(None)
            fallback = (
                f"ไฟล์: {os.path.basename(path)}\n"
                f"ประเภท: {os.path.splitext(path)[1] or 'ไม่ทราบ'}"
            )
            self.embed_preview_label.showMessage(fallback)

        file_size = os.path.getsize(path) if os.path.exists(path) else 0
        info_text = (
            f"ชื่อไฟล์: {os.path.basename(path)}\n"
            f"ขนาดไฟล์: {format_file_size(file_size)}\n"
            f"ประเภทไฟล์: {os.path.splitext(path)[1] or 'ไม่ทราบ'}\n"
            f"ความจุโดยประมาณ: {estimate_capacity(file_size)}"
        )
        self.embed_file_info_label.setText(info_text)


__all__ = ["EmbedTab"]
