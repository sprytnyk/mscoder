"""VIN Replacer tab - finds and replaces VINs in binary files."""

from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..translations import get_translations
from ..utils import vin_to_bytes

# Constants
VIN_LENGTH = 17
INPUT_HEIGHT = 30

# Styling constants
STYLE_TITLE = "font-weight: bold; font-size: 14px; margin-bottom: 10px;"
STYLE_INFO = "color: #666; margin-bottom: 15px;"


class VinReplacerTab(QWidget):
    """Tab for finding and replacing VINs in binary files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "en"
        self._init_ui()
        self.update_language("en")

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # Input fields
        self.original_vin_input = QLineEdit()
        self.replace_vin_input = QLineEdit()
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setMaximumWidth(600)

        self.original_vin_input.setFixedHeight(INPUT_HEIGHT)
        self.replace_vin_input.setFixedHeight(INPUT_HEIGHT)
        self.file_path_input.setFixedHeight(INPUT_HEIGHT)
        self.original_vin_input.setPlaceholderText("WBADT43452G112233")
        self.replace_vin_input.setPlaceholderText("WBAGN63452D123456")

        # Buttons
        self.btn_select_file = QPushButton()
        self.btn_process = QPushButton()
        self.btn_select_file.clicked.connect(self._select_file)
        self.btn_process.clicked.connect(self._process_file)

        # Labels
        self.description = QLabel()
        self.description.setStyleSheet(STYLE_TITLE)

        self.info = QLabel()
        self.info.setWordWrap(True)
        self.info.setStyleSheet(STYLE_INFO)

        self.supported_label = QLabel()
        self.supported_label.setStyleSheet("margin-bottom: 10px; color: #0066cc;")

        self.original_label = QLabel()
        self.replace_label = QLabel()
        self.file_label = QLabel()

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.supported_label)
        self.layout.addWidget(self.original_label)
        self.layout.addWidget(self.original_vin_input)
        self.layout.addWidget(self.replace_label)
        self.layout.addWidget(self.replace_vin_input)
        self.layout.addWidget(self.file_label)

        file_row = QHBoxLayout()
        file_row.addWidget(self.file_path_input)
        file_row.addWidget(self.btn_select_file)
        self.layout.addLayout(file_row)

        self.layout.addWidget(self.btn_process)
        self.layout.addWidget(self.status)

        self.setLayout(self.layout)

    def update_language(self, lang: str) -> None:
        """Update UI text for the specified language."""
        self.lang = lang
        self.t = get_translations(lang).REPLACER
        self.description.setText(self.t["title"])
        self.info.setText(self.t["description"])
        self.supported_label.setText(f"<b>{self.t['supported']}</b>")
        self.original_label.setText(self.t["original_vin"])
        self.replace_label.setText(self.t["replace_vin"])
        self.file_label.setText(self.t["binary_file"])
        self.btn_select_file.setText(self.t["btn_select"])
        self.btn_process.setText(self.t["btn_process"])

    def _select_file(self) -> None:
        """Open file dialog to select binary file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.t["select_file_title"], "", self.t["all_files"]
        )
        if file_path:
            self.file_path_input.setText(file_path)
            self.status.setText(self.t["file_selected"])

    def _process_file(self) -> None:
        """Find and replace VIN in the selected binary file."""
        try:
            original_vin = self.original_vin_input.text().strip()
            replace_vin = self.replace_vin_input.text().strip()
            file_path = self.file_path_input.text().strip()

            # Validate inputs
            if not original_vin or not replace_vin or not file_path:
                self.status.setText(self.t["error_required"])
                return

            if len(original_vin) != VIN_LENGTH:
                self.status.setText(self.t["error_original_length"])
                return

            if len(replace_vin) != VIN_LENGTH:
                self.status.setText(self.t["error_replace_length"])
                return

            # Convert VINs to hex bytes
            original_hex = vin_to_bytes(original_vin)
            replace_hex = vin_to_bytes(replace_vin)

            # Read the file
            with open(file_path, "rb") as f:
                data = bytearray(f.read())

            # Find and replace all occurrences
            occurrences = self._replace_in_data(data, original_hex, replace_hex)

            if occurrences == 0:
                self.status.setText(self.t["no_matches"])
                return

            # Save to new file with prefix
            new_file_path = self._get_modified_filepath(file_path)
            with open(new_file_path, "wb") as f:
                f.write(data)

            self.status.setText(self.t["success"].format(occurrences, new_file_path))
        except Exception as e:
            self.status.setText(f"Error: {str(e)}")

    @staticmethod
    def _replace_in_data(data: bytearray, original: bytes, replacement: bytes) -> int:
        """Replace all occurrences in bytearray and return count."""
        occurrences = 0
        pos = 0
        while True:
            pos = data.find(original, pos)
            if pos == -1:
                break
            data[pos : pos + len(original)] = replacement
            occurrences += 1
            pos += len(original)  # Advance by the length we just replaced
        return occurrences

    @staticmethod
    def _get_modified_filepath(original_path: str) -> str:
        """Generate modified file path with datetime suffix."""
        path = Path(original_path)
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        return str(path.parent / f"{path.stem}_{timestamp}{path.suffix}")
