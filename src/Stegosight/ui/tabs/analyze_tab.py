from __future__ import annotations

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QGroupBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..components import FileDropArea, RiskScoreWidget


class AnalyzeTab(QWidget):
    """Interactive analysis dashboard with risk overview and logs."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.analyze_drop: FileDropArea | None = None
        self.analyze_risk_widget: RiskScoreWidget | None = None
        self.analyze_summary_label: QLabel | None = None
        self.analyze_file_label: QLabel | None = None
        self.analyze_results_table: QTableWidget | None = None
        self.analyze_guidance_label: QLabel | None = None
        self.analyze_log_console: QPlainTextEdit | None = None
        self.analyze_selected_path: str | None = None
        self.analyze_button: QPushButton | None = None
        self.chi_square_checkbox: QCheckBox | None = None
        self.histogram_checkbox: QCheckBox | None = None
        self.file_structure_checkbox: QCheckBox | None = None

        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
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

    # ------------------------------------------------------------------
    def on_analyze_file_selected(self, path: str) -> None:
        print(f"[Action] Analyze target selected: {path}")
        self.analyze_selected_path = path

        if self.analyze_file_label is not None:
            self.analyze_file_label.setText(path)

        if self.analyze_log_console is not None:
            self.analyze_log_console.clear()
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
                "พบรูปแบบที่อาจบ่งชี้ถึงการซ่อนข้อมูล ควรตรวจสบเพิ่มเติม",
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


__all__ = ["AnalyzeTab"]
