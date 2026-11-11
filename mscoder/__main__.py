"""MS43 MSCoder - Main application window."""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Handle both direct execution and module execution
try:
    from . import theme
    from .paths import ASSETS
    from .tabs import AboutTab, IsnCopierTab, VinConverterTab, VinReplacerTab
    from .translations import get_translations
except ImportError:
    # Direct execution fallback
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from mscoder import theme
    from mscoder.paths import ASSETS
    from mscoder.tabs import AboutTab, IsnCopierTab, VinConverterTab, VinReplacerTab
    from mscoder.translations import get_translations

APP_ICON = str(ASSETS / "icon.ico")


class MSCoder(QMainWindow):
    """Main window with tabs."""

    def __init__(self):
        super().__init__()
        self.current_lang = "en"
        self._init_ui()
        self._update_ui_language()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle(get_translations(self.current_lang).COMMON["window_title"])
        self.resize(850, 740)  # tall enough for the ISN copier with a long message

        # Create central widget
        central_widget = QWidget()
        central_widget.setObjectName("central")
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(14, 12, 14, 14)
        main_layout.setSpacing(10)

        # Language selector at the top
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel(objectName="languageLabel")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("🇬🇧  English", "en")
        self.lang_combo.addItem("🇺🇦  Українська", "uk")
        self.lang_combo.currentIndexChanged.connect(self._change_language)
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        main_layout.addLayout(lang_layout)

        # Create tab widget
        self.tabs = QTabWidget()
        self.replacer_tab = VinReplacerTab(self)
        self.converter_tab = VinConverterTab(self)
        self.isn_copier_tab = IsnCopierTab(self)
        self.about_tab = AboutTab(self)

        self.tabs.addTab(self.replacer_tab, "")
        self.tabs.addTab(self.converter_tab, "")
        self.tabs.addTab(self.isn_copier_tab, "")
        self.tabs.addTab(self.about_tab, "")

        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)

        # Add keyboard shortcuts for tabs
        QShortcut(QKeySequence("Alt+1"), self).activated.connect(
            lambda: self.tabs.setCurrentIndex(0)
        )
        QShortcut(QKeySequence("Alt+2"), self).activated.connect(
            lambda: self.tabs.setCurrentIndex(1)
        )
        QShortcut(QKeySequence("Alt+3"), self).activated.connect(
            lambda: self.tabs.setCurrentIndex(2)
        )
        QShortcut(QKeySequence("Alt+4"), self).activated.connect(
            lambda: self.tabs.setCurrentIndex(3)
        )

    def _change_language(self, index: int) -> None:
        """Handle language change from combo box."""
        self.current_lang = self.lang_combo.itemData(index)
        self._update_ui_language()

    def _update_ui_language(self) -> None:
        """Update all UI elements for current language."""
        t = get_translations(self.current_lang).COMMON
        self.setWindowTitle(t["window_title"])
        self.lang_label.setText(t["language"])
        self.tabs.setTabText(0, t["tab_replacer"])
        self.tabs.setTabText(1, t["tab_converter"])
        self.tabs.setTabText(2, t["tab_isn_copier"])
        self.tabs.setTabText(3, t["tab_about"])

        # Update all tabs
        self.converter_tab.update_language(self.current_lang)
        self.replacer_tab.update_language(self.current_lang)
        self.isn_copier_tab.update_language(self.current_lang)
        self.about_tab.update_language(self.current_lang)


def main() -> None:
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("MSCoder")
    theme.install(app)
    icon = QIcon(APP_ICON)
    app.setWindowIcon(icon)

    window = MSCoder()
    window.setWindowIcon(icon)
    window.show()
    window.replacer_tab.original_vin_input.setFocus()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
