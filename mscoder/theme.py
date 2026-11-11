"""Light and dark looks in Calculon's colours. The app follows the system setting."""

import tempfile
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QGuiApplication, QPalette
from PySide6.QtWidgets import QApplication, QStyleFactory

from .paths import ASSETS


@dataclass(frozen=True)
class Theme:
    name: str
    window: str  # behind the tabs
    pane: str  # the open tab
    field: str  # text fields and dropdowns
    surface: str  # buttons, the selected tab, menus
    border: str
    text: str
    heading: str
    muted: str
    focus: str  # the main buttons, links and the field being typed in
    on_focus: str  # text on the main buttons
    selection: str
    error: str
    error_bg: str
    success: str
    success_bg: str
    warning: str
    warning_bg: str
    info_bg: str


DARK = Theme(
    name="dark",
    window="#1a1b20",
    pane="#212228",
    field="#1a1b20",
    surface="#2a2b33",
    border="#30323a",
    text="#e3e4e8",
    heading="#ffffff",
    muted="#7d808c",
    focus="#6cb6ff",
    on_focus="#10131a",
    selection="#3b3f4f",
    error="#ff8a8a",
    error_bg="#3a2326",
    success="#8fd6a4",
    success_bg="#1f3327",
    warning="#f2c46d",
    warning_bg="#3a3020",
    info_bg="#2a2b33",
)

LIGHT = Theme(
    name="light",
    window="#f1f1ee",
    pane="#fbfbf9",
    field="#ffffff",
    surface="#ffffff",
    border="#dddcd7",
    text="#24262b",
    heading="#111827",
    muted="#8a8d95",
    focus="#2563eb",
    on_focus="#ffffff",
    selection="#cfe0f5",
    error="#b91c1c",
    error_bg="#fdecec",
    success="#15803d",
    success_bg="#e8f5ec",
    warning="#a85b06",
    warning_bg="#fdf3e1",
    info_bg="#f1f1ee",
)

FONT_SCALE = 1.15  # a bit larger than the system default, as in Calculon
_base_font: list[QFont] = []


def for_scheme(scheme: Qt.ColorScheme) -> Theme:
    return DARK if scheme == Qt.ColorScheme.Dark else LIGHT


def icon_file(name: str, color: str) -> str:
    """A copy of an icon in one colour, since a stylesheet url() can't recolour it."""
    folder = Path(tempfile.gettempdir()) / "mscoder-icons"
    path = folder / f"{name}-{color.lstrip('#')}.svg"
    if not path.exists():
        folder.mkdir(parents=True, exist_ok=True)
        text = (ASSETS / "icons" / f"{name}.svg").read_text(encoding="utf-8")
        path.write_text(text.replace("currentColor", color), encoding="utf-8")
    return path.as_posix()


def stylesheet(t: Theme) -> str:
    down = icon_file("caret_down", t.muted)
    up = icon_file("caret_up", t.muted)
    check = icon_file("check", t.on_focus)
    mono = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()
    return f"""
    QMainWindow, QWidget#central {{ background: {t.window}; }}
    QLabel#languageLabel {{ color: {t.muted}; }}

    QTabWidget::pane {{ background: {t.pane}; border: 1px solid {t.border};
        border-radius: 10px; top: 6px; }}
    QTabWidget::tab-bar {{ left: 0; }}
    QTabBar {{ qproperty-drawBase: 0; }}
    QTabBar::tab {{ background: transparent; color: {t.muted}; border: 1px solid transparent;
        border-radius: 7px; padding: 6px 16px; margin-right: 4px; }}
    QTabBar::tab:hover {{ color: {t.text}; }}
    QTabBar::tab:selected {{ background: {t.surface}; color: {t.text};
        border-color: {t.border}; }}

    QWidget#tab {{ background: {t.pane}; }}
    QLabel {{ color: {t.text}; background: transparent; }}
    QLabel#title {{ color: {t.heading}; font-size: 15pt; font-weight: 600; }}
    QLabel#info {{ color: {t.muted}; }}
    QLabel#supported {{ color: {t.focus}; font-weight: 600; }}
    QLabel#fieldLabel {{ color: {t.text}; font-weight: 600; padding-top: 6px;
        qproperty-indent: 0; }}
    QLabel#status {{ border-radius: 7px; padding: 8px 12px; color: {t.text};
        background: {t.info_bg}; }}
    QLabel#status[kind="error"] {{ color: {t.error}; background: {t.error_bg}; }}
    QLabel#status[kind="success"] {{ color: {t.success}; background: {t.success_bg}; }}
    QLabel#status[kind="warning"] {{ color: {t.warning}; background: {t.warning_bg}; }}
    QLabel#version {{ color: {t.muted}; }}

    QLineEdit, QComboBox {{ background: {t.field}; color: {t.text};
        border: 1px solid {t.border}; border-radius: 7px; padding: 6px 10px;
        min-height: 22px; selection-background-color: {t.selection};
        selection-color: {t.text}; }}
    QLineEdit#mono {{ font-family: "{mono}"; }}
    QLineEdit:hover, QComboBox:hover {{ border-color: {t.muted}; }}
    QLineEdit:focus, QComboBox:focus, QComboBox:on {{ border-color: {t.focus}; }}
    QLineEdit:read-only {{ background: {t.pane}; }}
    QComboBox {{ combobox-popup: 0; }}
    QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: center right;
        width: 28px; border: none; background: transparent; }}
    QComboBox::down-arrow {{ image: url("{down}"); width: 12px; height: 12px; }}
    QComboBox::down-arrow:on {{ image: url("{up}"); }}
    QComboBox QAbstractItemView {{ background: {t.surface}; color: {t.text};
        border: 1px solid {t.border}; padding: 4px; outline: 0;
        selection-background-color: {t.selection}; selection-color: {t.text}; }}

    QPushButton {{ background: {t.surface}; color: {t.text}; border: 1px solid {t.border};
        border-radius: 7px; padding: 7px 18px; min-height: 22px; }}
    QPushButton:hover {{ border-color: {t.muted}; }}
    QPushButton:pressed {{ background: {t.selection}; }}
    QPushButton:focus {{ border-color: {t.focus}; }}
    QPushButton#primary {{ background: {t.focus}; border-color: {t.focus};
        color: {t.on_focus}; font-weight: 600; }}
    QPushButton#primary:hover {{ border-color: {t.text}; }}

    QCheckBox {{ color: {t.text}; spacing: 8px; padding: 4px 0; }}
    QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {t.muted};
        border-radius: 4px; background: {t.field}; }}
    QCheckBox::indicator:hover {{ border-color: {t.focus}; }}
    QCheckBox::indicator:checked {{ background: {t.focus}; border-color: {t.focus};
        image: url("{check}"); }}

    QToolTip {{ background: {t.surface}; color: {t.text}; border: 1px solid {t.border}; }}
    """


def palette(t: Theme) -> QPalette:
    p = QPalette()
    roles = {
        QPalette.ColorRole.Window: t.window,
        QPalette.ColorRole.WindowText: t.text,
        QPalette.ColorRole.Base: t.field,
        QPalette.ColorRole.AlternateBase: t.surface,
        QPalette.ColorRole.Text: t.text,
        QPalette.ColorRole.PlaceholderText: t.muted,
        QPalette.ColorRole.Button: t.surface,
        QPalette.ColorRole.ButtonText: t.text,
        QPalette.ColorRole.ToolTipBase: t.surface,
        QPalette.ColorRole.ToolTipText: t.text,
        QPalette.ColorRole.Highlight: t.selection,
        QPalette.ColorRole.HighlightedText: t.text,
        QPalette.ColorRole.Link: t.focus,
        QPalette.ColorRole.LinkVisited: t.focus,
    }
    for role, color in roles.items():
        p.setColor(role, QColor(color))
    return p


def apply(app: QApplication, t: Theme) -> None:
    app.setPalette(palette(t))
    app.setStyleSheet(stylesheet(t))


def install(app: QApplication) -> None:
    """Use Calculon's look, and switch between light and dark when the system does."""
    app.setStyle(QStyleFactory.create("Fusion"))
    if not _base_font:
        _base_font.append(QFont(app.font()))
        font = QFont(_base_font[0])
        font.setPointSizeF(max(10.5, font.pointSizeF() * FONT_SCALE))
        app.setFont(font)
    hints = QGuiApplication.styleHints()
    apply(app, for_scheme(hints.colorScheme()))
    hints.colorSchemeChanged.connect(lambda scheme: apply(app, for_scheme(scheme)))
