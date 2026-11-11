"""About tab - application information and credits."""

from PySide6.QtWidgets import QLabel, QWidget

from ..translations import get_translations
from ..widgets import tab_layout


class AboutTab(QWidget):
    """About and usage information tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "en"
        self._init_ui()
        self.update_language("en")

    def _init_ui(self) -> None:
        """Initialize UI components."""
        self.layout = tab_layout()

        # Title
        self.title = QLabel()
        self.title.setObjectName("title")
        self.layout.addWidget(self.title)

        # Version and author
        self.author = QLabel()
        self.author.setOpenExternalLinks(True)
        self.layout.addWidget(self.author)

        self.version = QLabel()
        self.version.setObjectName("version")
        self.layout.addWidget(self.version)

        # Description
        self.desc_title = QLabel()
        self.desc_title.setObjectName("fieldLabel")
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
