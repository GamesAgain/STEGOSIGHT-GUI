from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QFileDialog,
    QFrame,
    QLabel,
    QSizePolicy,
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
        self._prompt = prompt

    def setPrompt(self, prompt: str) -> None:
        """Update the displayed prompt text."""

        if prompt == self._prompt:
            return
        self._prompt = prompt
        self.setText(prompt)

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


class PreviewImageLabel(QLabel):
    """Image preview label that keeps aspect ratio on resize."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pixmap: QPixmap | None = None
        self._message: str | None = None
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("EmbedPreview")

    def setImage(self, pixmap: QPixmap | None) -> None:
        self._pixmap = pixmap if pixmap and not pixmap.isNull() else None
        if self._pixmap is None:
            self.clear()
            return
        self._message = None
        self._apply_scaled_pixmap()

    def clear(self) -> None:  # type: ignore[override]
        self._message = None
        super().clear()
        super().setPixmap(QPixmap())

    def showMessage(self, message: str) -> None:
        self._pixmap = None
        self._message = message
        super().setPixmap(QPixmap())
        super().setText(message)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self._pixmap is not None:
            self._apply_scaled_pixmap()

    def _apply_scaled_pixmap(self) -> None:
        if self._pixmap is None or self._pixmap.isNull():
            return
        scaled = self._pixmap.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        super().setPixmap(scaled)


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


__all__ = [
    "FileDropArea",
    "PreviewImageLabel",
    "RiskScoreWidget",
    "MethodCard",
]
