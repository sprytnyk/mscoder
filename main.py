"""MS41/MS43 VinCoder - Main application window."""

__version__ = "0.0.1"
__author__ = "https://sprytnyk.dev"

import os
import sys

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
from PySide6.QtGui import QIcon, QShortcut, QKeySequence

from translations import TRANSLATIONS
from tabs import VinConverterTab, VinReplacerTab, AboutTab

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ICON = os.path.join(BASE_DIR, "assets", "icon.ico")


class VinCoder(QMainWindow):
    """Main window with tabs."""

    def __init__(self):
        super().__init__()
        self.current_lang = "en"
        self._init_ui()
        self._update_ui_language()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle(TRANSLATIONS[self.current_lang]["window_title"])
        self.resize(650, 500)  # Set default window size

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Language selector at the top
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("🇬🇧", "en")
        self.lang_combo.addItem("🇺🇦", "uk")
        self.lang_combo.currentIndexChanged.connect(self._change_language)
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        main_layout.addLayout(lang_layout)

        # Create tab widget
        self.tabs = QTabWidget()
        self.replacer_tab = VinReplacerTab(self)
        self.converter_tab = VinConverterTab(self)
        self.about_tab = AboutTab(self)

        self.tabs.addTab(self.replacer_tab, "")
        self.tabs.addTab(self.converter_tab, "")
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

    def _change_language(self, index: int) -> None:
        """Handle language change from combo box."""
        self.current_lang = self.lang_combo.itemData(index)
        self._update_ui_language()

    def _update_ui_language(self) -> None:
        """Update all UI elements for current language."""
        t = TRANSLATIONS[self.current_lang]
        self.setWindowTitle(t["window_title"])
        self.lang_label.setText(t["language"])
        self.tabs.setTabText(0, t["tab_replacer"])
        self.tabs.setTabText(1, t["tab_converter"])
        self.tabs.setTabText(2, t["tab_about"])

        # Update all tabs
        self.converter_tab.update_language(self.current_lang)
        self.replacer_tab.update_language(self.current_lang)
        self.about_tab.update_language(self.current_lang)


def main() -> None:
    app = QApplication(sys.argv)
    icon = QIcon(APP_ICON)
    app.setWindowIcon(icon)

    window = VinCoder()
    window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
