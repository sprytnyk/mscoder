"""VIN Replacer tab - finds and replaces VINs in binary files."""

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from ..paths import modified_path
from ..translations import get_translations
from ..utils import vin_to_bytes
from ..widgets import StatusLabel, tab_layout

VIN_LENGTH = 17


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
        self.status = StatusLabel()
        self.original_vin_input.setObjectName("mono")
        self.replace_vin_input.setObjectName("mono")
        self.original_vin_input.setPlaceholderText("WBADT43452G112233")
        self.replace_vin_input.setPlaceholderText("WBAGN63452D123456")

        # Buttons
        self.btn_select_file = QPushButton()
        self.btn_process = QPushButton()
        self.btn_select_file.clicked.connect(self._select_file)
        self.btn_process.clicked.connect(self._process_file)
        self.btn_process.setObjectName("primary")

        # Labels
        self.description = QLabel()
        self.description.setObjectName("title")

        self.info = QLabel()
        self.info.setWordWrap(True)
        self.info.setObjectName("info")

        self.supported_label = QLabel()
        self.supported_label.setObjectName("supported")

        self.original_label = QLabel(objectName="fieldLabel")
        self.replace_label = QLabel(objectName="fieldLabel")
        self.file_label = QLabel(objectName="fieldLabel")

        # Layout
        self.layout = tab_layout()
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
        self.layout.addStretch()

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
        original_vin = self.original_vin_input.text().strip()
        replace_vin = self.replace_vin_input.text().strip()
        file_path = self.file_path_input.text().strip()

        if not original_vin or not replace_vin or not file_path:
            self.status.setText(self.t["error_required"])
            return

        if len(original_vin) != VIN_LENGTH:
            self.status.setText(self.t["error_original_length"])
            return

        if len(replace_vin) != VIN_LENGTH:
            self.status.setText(self.t["error_replace_length"])
            return

        try:
            original_hex = vin_to_bytes(original_vin)
            replace_hex = vin_to_bytes(replace_vin)
        except ValueError as error:
            self.status.setText(f"Error: {error}")
            return

        try:
            data = bytearray(Path(file_path).read_bytes())
            occurrences = self._replace_in_data(data, original_hex, replace_hex)
            if occurrences == 0:
                self.status.setText(self.t["no_matches"])
                return

            new_file_path = modified_path(file_path)
            new_file_path.write_bytes(data)
        except OSError as error:
            self.status.setText(f"Error: {error}")
            return

        self.status.setText(self.t["success"].format(occurrences, new_file_path.name))

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
