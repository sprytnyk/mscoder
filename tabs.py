import os
from datetime import datetime, timezone
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from meta import __version__
from translations import TRANSLATIONS
from vin_codec import vin_to_str, vin_to_bytes

# Constants
VIN_LENGTH = 17
HEX_LENGTH = 26  # 13 bytes * 2
INPUT_HEIGHT = 30

# Styling constants
STYLE_TITLE = "font-weight: bold; font-size: 14px; margin-bottom: 10px;"
STYLE_SUBTITLE = "font-weight: bold; font-size: 18px; margin-bottom: 10px;"
STYLE_INFO = "color: #666; margin-bottom: 15px;"
STYLE_META = "margin-bottom: 5px;"


class VinConverterTab(QWidget):
    """Tab for basic VIN ↔ HEX conversion."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "en"
        self._init_ui()
        self.update_language("en")

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # Input fields
        self.vin_input = QLineEdit()
        self.hex_input = QLineEdit()
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setMaximumWidth(600)

        self.vin_input.setFixedHeight(INPUT_HEIGHT)
        self.hex_input.setFixedHeight(INPUT_HEIGHT)
        self.vin_input.setPlaceholderText("WBADT43452G112233")
        self.hex_input.setPlaceholderText("B01144333452471122233300")

        # Buttons
        self.btn_to_hex = QPushButton()
        self.btn_to_str = QPushButton()
        self.btn_to_hex.clicked.connect(self._to_hex)
        self.btn_to_str.clicked.connect(self._to_str)

        # Labels
        self.description = QLabel()
        self.description.setStyleSheet(STYLE_TITLE)

        self.info = QLabel()
        self.info.setWordWrap(True)
        self.info.setStyleSheet(STYLE_INFO)

        self.vin_label = QLabel()
        self.hex_label = QLabel()

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.vin_label)
        self.layout.addWidget(self.vin_input)
        self.layout.addWidget(self.hex_label)
        self.layout.addWidget(self.hex_input)

        btns = QHBoxLayout()
        btns.addWidget(self.btn_to_hex)
        btns.addWidget(self.btn_to_str)
        self.layout.addLayout(btns)
        self.layout.addWidget(self.status)

        self.setLayout(self.layout)

    def update_language(self, lang: str) -> None:
        """Update UI text for the specified language."""
        self.lang = lang
        t = TRANSLATIONS[lang]
        self.description.setText(t["conv_title"])
        self.info.setText(t["conv_description"])
        self.vin_label.setText(t["conv_vin_string"])
        self.hex_label.setText(t["conv_hex_bytes"])
        self.btn_to_hex.setText(t["conv_btn_to_hex"])
        self.btn_to_str.setText(t["conv_btn_to_str"])

    def _to_hex(self) -> None:
        """Convert VIN string to hex bytes."""
        t = TRANSLATIONS[self.lang]
        try:
            vin = self.vin_input.text().strip()
            if len(vin) != VIN_LENGTH:
                self.status.setText(t["conv_error_vin_length"])
                return
            data = vin_to_bytes(vin)
            hex_result = "".join(f"{b:02X}" for b in data)
            self.hex_input.setText(hex_result)
            self.status.setText(t["conv_ok"])
        except Exception as e:
            self.status.setText(f"Error: {str(e)}")

    def _to_str(self) -> None:
        """Convert hex bytes to VIN string."""
        t = TRANSLATIONS[self.lang]
        try:
            hex_text = self.hex_input.text().strip().replace(" ", "")

            # Remove 0x prefix if present
            if hex_text.lower().startswith("0x"):
                hex_text = hex_text[2:]

            # Validate hex length
            if len(hex_text) != HEX_LENGTH:
                self.status.setText(t["conv_error_hex_length"])
                return

            # Parse hex string in pairs
            raw = bytes(
                int(hex_text[i : i + 2], 16)
                for i in range(0, len(hex_text), 2)
            )
            vin = vin_to_str(raw)

            if len(vin) != VIN_LENGTH:
                self.status.setText(t["conv_warning_decoded"].format(len(vin)))
            else:
                self.status.setText(t["conv_ok"])

            self.vin_input.setText(vin)
        except ValueError:
            self.status.setText(t["conv_error_hex_format"])
        except Exception as e:
            self.status.setText(f"Error: {str(e)}")


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

        self.original_label = QLabel()
        self.replace_label = QLabel()
        self.file_label = QLabel()

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.info)
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
        t = TRANSLATIONS[lang]
        self.description.setText(t["repl_title"])
        self.info.setText(t["repl_description"])
        self.original_label.setText(t["repl_original_vin"])
        self.replace_label.setText(t["repl_replace_vin"])
        self.file_label.setText(t["repl_binary_file"])
        self.btn_select_file.setText(t["repl_btn_select"])
        self.btn_process.setText(t["repl_btn_process"])

    def _select_file(self) -> None:
        """Open file dialog to select binary file."""
        t = TRANSLATIONS[self.lang]
        file_path, _ = QFileDialog.getOpenFileName(
            self, t["repl_select_file_title"], "", t["repl_all_files"]
        )
        if file_path:
            self.file_path_input.setText(file_path)
            self.status.setText(t["repl_file_selected"])

    def _process_file(self) -> None:
        """Find and replace VIN in the selected binary file."""
        t = TRANSLATIONS[self.lang]
        try:
            original_vin = self.original_vin_input.text().strip()
            replace_vin = self.replace_vin_input.text().strip()
            file_path = self.file_path_input.text().strip()

            # Validate inputs
            if not original_vin or not replace_vin or not file_path:
                self.status.setText(t["repl_error_required"])
                return

            if len(original_vin) != VIN_LENGTH:
                self.status.setText(t["repl_error_original_length"])
                return

            if len(replace_vin) != VIN_LENGTH:
                self.status.setText(t["repl_error_replace_length"])
                return

            # Convert VINs to hex bytes
            original_hex = vin_to_bytes(original_vin)
            replace_hex = vin_to_bytes(replace_vin)

            # Read the file
            with open(file_path, "rb") as f:
                data = bytearray(f.read())

            # Find and replace all occurrences
            occurrences = self._replace_in_data(
                data, original_hex, replace_hex
            )

            if occurrences == 0:
                self.status.setText(t["repl_no_matches"])
                return

            # Save to new file with prefix
            new_file_path = self._get_modified_filepath(file_path)
            with open(new_file_path, "wb") as f:
                f.write(data)

            self.status.setText(
                t["repl_success"].format(occurrences, new_file_path)
            )
        except Exception as e:
            self.status.setText(f"Error: {str(e)}")

    @staticmethod
    def _replace_in_data(
        data: bytearray, original: bytes, replacement: bytes
    ) -> int:
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
        dir_path = os.path.dirname(original_path)
        file_name = os.path.basename(original_path)
        name_without_ext, ext = os.path.splitext(file_name)
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        return os.path.join(dir_path, f"{name_without_ext}_{timestamp}{ext}")


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

        self.description = QLabel()
        self.description.setWordWrap(True)
        self.description.setStyleSheet("margin-bottom: 20px;")
        self.layout.addWidget(self.description)

        # Add stretch to push content to top
        self.layout.addStretch()

        self.setLayout(self.layout)

    def update_language(self, lang: str) -> None:
        """Update UI text for the specified language."""
        self.lang = lang
        t = TRANSLATIONS[lang]
        self.title.setText(t["about_title"])
        self.author.setText(t["about_author"])
        self.version.setText(t["about_version"].format(version=__version__))
        self.desc_title.setText(t["about_header"])
        self.description.setText(t["about_description"])
