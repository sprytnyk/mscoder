"""Widgets shared by the tabs."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout

# how messages start in each language, so the status line can colour them
_KINDS = {
    "error": ("Error", "Помилка"),
    "warning": ("Warning", "Попередження"),
    "success": ("Success", "Успішно", "OK"),
}


def kind_of(text: str) -> str:
    for kind, starts in _KINDS.items():
        if text.startswith(starts):
            return kind
    return "info"


class StatusLabel(QLabel):
    """The line under a tab's buttons. Red for errors, green for success, hidden when empty."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("status")
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.hide()

    def setText(self, text: str) -> None:
        super().setText(text)
        self.setProperty("kind", kind_of(text))
        self.setVisible(bool(text))
        # the stylesheet picks the colour by "kind", so it has to look again
        self.style().unpolish(self)
        self.style().polish(self)


def tab_layout() -> QVBoxLayout:
    """The same margins and gaps on every tab."""
    layout = QVBoxLayout()
    layout.setContentsMargins(24, 22, 24, 22)
    layout.setSpacing(8)
    return layout
