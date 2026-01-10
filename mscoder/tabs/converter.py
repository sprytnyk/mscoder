"""VIN Converter tab - converts VIN strings to hex and vice versa."""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..translations import get_translations
from ..utils import vin_to_str, vin_to_bytes

# Constants
VIN_LENGTH = 17
HEX_LENGTH = 26  # 13 bytes * 2
INPUT_HEIGHT = 30

# Styling constants
STYLE_TITLE = "font-weight: bold; font-size: 14px; margin-bottom: 10px;"
STYLE_INFO = "color: #666; margin-bottom: 15px;"


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

        self.supported_label = QLabel()
        self.supported_label.setStyleSheet("margin-bottom: 10px; color: #0066cc;")

        self.vin_label = QLabel()
        self.hex_label = QLabel()

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.supported_label)
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
        self.t = get_translations(lang).CONVERTER
        self.description.setText(self.t["title"])
        self.info.setText(self.t["description"])
        self.supported_label.setText(f"<b>{self.t['supported']}</b>")
        self.vin_label.setText(self.t["vin_string"])
        self.hex_label.setText(self.t["hex_bytes"])
        self.btn_to_hex.setText(self.t["btn_to_hex"])
        self.btn_to_str.setText(self.t["btn_to_str"])

    def _to_hex(self) -> None:
        """Convert VIN string to hex bytes."""
        try:
            vin = self.vin_input.text().strip()
            if len(vin) != VIN_LENGTH:
                self.status.setText(self.t["error_vin_length"])
                return
            data = vin_to_bytes(vin)
            hex_result = "".join(f"{b:02X}" for b in data)
            self.hex_input.setText(hex_result)
            self.status.setText(self.t["ok"])
        except Exception as e:
            self.status.setText(f"Error: {str(e)}")

    def _to_str(self) -> None:
        """Convert hex bytes to VIN string."""
        try:
            hex_text = self.hex_input.text().strip().replace(" ", "")

            # Remove 0x prefix if present
            if hex_text.lower().startswith("0x"):
                hex_text = hex_text[2:]

            # Validate hex length
            if len(hex_text) != HEX_LENGTH:
                self.status.setText(self.t["error_hex_length"])
                return

            # Parse hex string in pairs
            raw = bytes(
                int(hex_text[i : i + 2], 16) for i in range(0, len(hex_text), 2)
            )
            vin = vin_to_str(raw)

            if len(vin) != VIN_LENGTH:
                self.status.setText(self.t["warning_decoded"].format(len(vin)))
            else:
                self.status.setText(self.t["ok"])

            self.vin_input.setText(vin)
        except ValueError:
            self.status.setText(self.t["error_hex_format"])
        except Exception as e:
            self.status.setText(f"Error: {str(e)}")
