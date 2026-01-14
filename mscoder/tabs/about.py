"""About tab - application information and credits."""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..translations import get_translations

# Styling constants
STYLE_SUBTITLE = "font-weight: bold; font-size: 18px; margin-bottom: 10px;"
STYLE_META = "margin-bottom: 5px;"
STYLE_INFO = "color: #666; margin-bottom: 15px;"
STYLE_TITLE = "font-weight: bold; font-size: 14px; margin-bottom: 10px;"


class AboutTab(QWidget):
    """About and usage information tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "en"
        self._init_ui()
        self.update_language("en")

    def _init_ui(self) -> None:
        """Initialize UI components."""
        self.layout = QVBoxLayout()

        # Title
        self.title = QLabel()
        self.title.setStyleSheet(STYLE_SUBTITLE)
        self.layout.addWidget(self.title)

        # Version and author
        self.author = QLabel()
        self.author.setStyleSheet(STYLE_META)
        self.author.setOpenExternalLinks(True)
        self.layout.addWidget(self.author)

        self.version = QLabel()
        self.version.setStyleSheet(STYLE_INFO + " margin-bottom: 20px;")
        self.layout.addWidget(self.version)

        # Description
        self.desc_title = QLabel()
        self.desc_title.setStyleSheet(STYLE_TITLE + " margin-top: 10px;")
        self.layout.addWidget(self.desc_title)

        # Add stretch to push content to top
        self.layout.addStretch()

        self.setLayout(self.layout)

    def update_language(self, lang: str) -> None:
        """Update UI text for the specified language."""
        from .. import __version__

        self.lang = lang
        self.t = get_translations(lang).ABOUT
        self.title.setText(self.t["title"])
        self.author.setText(self.t["author"])
        self.version.setText(self.t["version"].format(version=__version__))
