"""ISN Copier tab - copies ISN values between binary firmware files."""

from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..translations import get_translations

# Constants
INPUT_HEIGHT = 30
ISN_ADDRESS = 0x3ED4
ISN_LENGTH = 6

# Styling constants
STYLE_TITLE = "font-weight: bold; font-size: 14px; margin-bottom: 10px;"
STYLE_INFO = "color: #666; margin-bottom: 15px;"


class IsnCopierTab(QWidget):
    """Tab for copying ISN value between binary files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "en"
        self._init_ui()
        self.update_language("en")

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # Input fields
        self.source_file_input = QLineEdit()
        self.source_file_input.setReadOnly(True)
        self.target_file_input = QLineEdit()
        self.target_file_input.setReadOnly(True)
        self.isn_value_display = QLineEdit()
        self.isn_value_display.setReadOnly(True)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setMaximumWidth(600)

        self.source_file_input.setFixedHeight(INPUT_HEIGHT)
        self.target_file_input.setFixedHeight(INPUT_HEIGHT)
        self.isn_value_display.setFixedHeight(INPUT_HEIGHT)

        # Buttons
        self.btn_select_source = QPushButton()
        self.btn_select_target = QPushButton()
        self.btn_process = QPushButton()
        self.btn_select_source.clicked.connect(self._select_source_file)
        self.btn_select_target.clicked.connect(self._select_target_file)
        self.btn_process.clicked.connect(self._process_files)

        # Checkboxes
        self.immobiliser_bypass_checkbox = QCheckBox()
        self.immobiliser_revert_checkbox = QCheckBox()

        # Hide both initially until target file is selected
        self.immobiliser_bypass_checkbox.hide()
        self.immobiliser_revert_checkbox.hide()

        # Labels
        self.description = QLabel()
        self.description.setStyleSheet(STYLE_TITLE)

        self.info = QLabel()
        self.info.setWordWrap(True)
        self.info.setStyleSheet(STYLE_INFO)

        self.ms43_warning = QLabel()
        self.ms43_warning.setStyleSheet("margin-bottom: 10px;")

        self.source_label = QLabel()
        self.target_label = QLabel()
        self.isn_label = QLabel()

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.ms43_warning)
        self.layout.addWidget(self.source_label)

        source_row = QHBoxLayout()
        source_row.addWidget(self.source_file_input)
        source_row.addWidget(self.btn_select_source)
        self.layout.addLayout(source_row)

        self.layout.addWidget(self.isn_label)
        self.layout.addWidget(self.isn_value_display)

        self.layout.addWidget(self.target_label)

        target_row = QHBoxLayout()
        target_row.addWidget(self.target_file_input)
        target_row.addWidget(self.btn_select_target)
        self.layout.addLayout(target_row)

        self.layout.addWidget(self.immobiliser_bypass_checkbox)
        self.layout.addWidget(self.immobiliser_revert_checkbox)
        self.layout.addWidget(self.btn_process)
        self.layout.addWidget(self.status)

        self.setLayout(self.layout)

    def update_language(self, lang: str) -> None:
        """Update UI text for the specified language."""
        self.lang = lang
        self.t = get_translations(lang).ISN_COPIER
        self.description.setText(self.t["title"])
        self.info.setText(self.t["description"])
        self.ms43_warning.setText(f"<b style='color: red;'>{self.t['ms43_only']}</b>")
        self.source_label.setText(self.t["source_file"])
        self.target_label.setText(self.t["target_file"])
        self.isn_label.setText(self.t["value_label"])
        self.btn_select_source.setText(self.t["btn_select"])
        self.btn_select_target.setText(self.t["btn_select"])
        self.btn_process.setText(self.t["btn_process"])
        self.immobiliser_bypass_checkbox.setText(self.t["immobiliser_bypass"])
        self.immobiliser_revert_checkbox.setText(self.t["immobiliser_revert"])

    def _select_source_file(self) -> None:
        """Open file dialog to select source binary file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.t["select_source_title"], "", self.t["all_files"]
        )
        if file_path:
            self.source_file_input.setText(file_path)
            self._read_isn_value(file_path)

    def _select_target_file(self) -> None:
        """Open file dialog to select target binary file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.t["select_target_title"], "", self.t["all_files"]
        )
        if file_path:
            self.target_file_input.setText(file_path)
            self._check_bypass_state(file_path)
            self.status.setText(self.t["target_selected"])

    def _check_bypass_state(self, file_path: str) -> None:
        """Check if immobiliser bypass is applied and show/hide checkboxes accordingly."""
        try:
            with open(file_path, "rb") as f:
                data = f.read()

            # Check if file is large enough
            if len(data) < 0x70A6F:
                # File too small, hide both checkboxes
                self.immobiliser_bypass_checkbox.hide()
                self.immobiliser_revert_checkbox.hide()
                return

            # Check if bypass is applied by looking for patched values
            bypass_applied = (
                data[0x2E2F0 : 0x2E2F0 + 4] == bytes([0xC2, 0xFE, 0x6E, 0x0A])
                or data[0x600D8 : 0x600D8 + 4] == bytes([0xDA, 0x0D, 0xF8, 0x3B])
                or data[0x53BF8 : 0x53BF8 + 8]
                == bytes([0xDA, 0x0A, 0xE4, 0xFC, 0x0E, 0x1A, 0xDB, 0x00])
                or data[0x70A6E] == 0x00
            )

            if bypass_applied:
                # Bypass is applied, show revert checkbox only
                self.immobiliser_bypass_checkbox.hide()
                self.immobiliser_revert_checkbox.show()
            else:
                # Bypass not applied, show bypass checkbox only
                self.immobiliser_bypass_checkbox.show()
                self.immobiliser_revert_checkbox.hide()
        except Exception:
            # On error, show both checkboxes
            self.immobiliser_bypass_checkbox.show()
            self.immobiliser_revert_checkbox.show()

    def _read_isn_value(self, file_path: str) -> None:
        """Read ISN value from source file and display it."""
        try:
            with open(file_path, "rb") as f:
                f.seek(ISN_ADDRESS)
                isn_bytes = f.read(ISN_LENGTH)

                if len(isn_bytes) < ISN_LENGTH:
                    self.status.setText(self.t["error_file_too_small"])
                    self.isn_value_display.setText("")
                    return

                # Display as hex string
                hex_value = "".join(f"{b:02X}" for b in isn_bytes)
                self.isn_value_display.setText(hex_value)
                self.status.setText(self.t["source_selected"])
        except Exception as e:
            self.status.setText(f"Error: {str(e)}")
            self.isn_value_display.setText("")

    def _process_files(self) -> None:
        """Copy ISN value from source to target file."""
        try:
            source_path = self.source_file_input.text().strip()
            target_path = self.target_file_input.text().strip()

            # Validate inputs
            if not source_path or not target_path:
                self.status.setText(self.t["error_required"])
                return

            # Read ISN from source
            with open(source_path, "rb") as f:
                f.seek(ISN_ADDRESS)
                isn_bytes = f.read(ISN_LENGTH)

                if len(isn_bytes) < ISN_LENGTH:
                    self.status.setText(self.t["error_file_too_small"])
                    return

            # Read target file
            with open(target_path, "rb") as f:
                target_data = bytearray(f.read())

            # Check target file size (need 76 bytes from ISN_ADDRESS)
            if len(target_data) < ISN_ADDRESS + 76:
                self.status.setText(self.t["error_target_too_small"])
                return

            # First, fill 76 bytes with 0xFF starting at ISN_ADDRESS
            target_data[ISN_ADDRESS : ISN_ADDRESS + 76] = bytes([0xFF] * 76)

            # Then write ISN to target (overwrites first 6 bytes)
            target_data[ISN_ADDRESS : ISN_ADDRESS + ISN_LENGTH] = isn_bytes

            # Check firmware size for immobiliser operations
            if (
                self.immobiliser_bypass_checkbox.isChecked()
                or self.immobiliser_revert_checkbox.isChecked()
            ):
                min_required_size = 0x70A6F  # Largest address we need to access + 1
                if len(target_data) < min_required_size:
                    self.status.setText(
                        f"Error: Firmware too small for immobiliser bypass (need at least {min_required_size} bytes)"
                    )
                    return

            # Apply immobiliser bypass if checkbox is checked
            if self.immobiliser_bypass_checkbox.isChecked():
                # Addr 2E2F0: C2 FE B9 0A -> C2 FE 6E 0A
                target_data[0x2E2F0 : 0x2E2F0 + 4] = bytes([0xC2, 0xFE, 0x6E, 0x0A])

                # Addr 600D8: DA 0A 6C DD -> DA 0D F8 3B
                target_data[0x600D8 : 0x600D8 + 4] = bytes([0xDA, 0x0D, 0xF8, 0x3B])

                # Addr 53BF8: 00 00 FF FF FF FF FF FF -> DA 0A E4 FC 0E 1A DB 00
                target_data[0x53BF8 : 0x53BF8 + 8] = bytes(
                    [0xDA, 0x0A, 0xE4, 0xFC, 0x0E, 0x1A, 0xDB, 0x00]
                )

                # Addr 70A6E: 02 -> 00
                target_data[0x70A6E] = 0x00

            # Revert immobiliser bypass if checkbox is checked and visible
            if (
                self.immobiliser_revert_checkbox.isChecked()
                and self.immobiliser_revert_checkbox.isVisible()
            ):
                # Addr 2E2F0: C2 FE 6E 0A -> C2 FE B9 0A
                target_data[0x2E2F0 : 0x2E2F0 + 4] = bytes([0xC2, 0xFE, 0xB9, 0x0A])

                # Addr 600D8: DA 0D F8 3B -> DA 0A 6C DD
                target_data[0x600D8 : 0x600D8 + 4] = bytes([0xDA, 0x0A, 0x6C, 0xDD])

                # Addr 53BF8: DA 0A E4 FC 0E 1A DB 00 -> 00 00 FF FF FF FF FF FF
                target_data[0x53BF8 : 0x53BF8 + 8] = bytes(
                    [0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                )

                # Addr 70A6E: 00 -> 02
                target_data[0x70A6E] = 0x02

            # Save modified target file
            new_file_path = self._get_modified_filepath(target_path)
            with open(new_file_path, "wb") as f:
                f.write(target_data)

            hex_value = "".join(f"{b:02X}" for b in isn_bytes)
            self.status.setText(self.t["success"].format(hex_value, new_file_path))
            
            # Clear checkbox states after successful processing
            self.immobiliser_bypass_checkbox.setChecked(False)
            self.immobiliser_revert_checkbox.setChecked(False)
        except Exception as e:
            self.status.setText(f"Error: {str(e)}")

    @staticmethod
    def _get_modified_filepath(original_path: str) -> str:
        """Generate modified file path with datetime suffix."""
        path = Path(original_path)
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        return str(path.parent / f"{path.stem}_{timestamp}{path.suffix}")
