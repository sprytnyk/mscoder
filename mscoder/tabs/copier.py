"""ISN Copier tab - copies ISN values between binary firmware files."""

from datetime import UTC, datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..translations import get_translations

# UI Constants
INPUT_HEIGHT = 30

# Binary data constants
ISN_LENGTH = 6
VERSION_LENGTH = 6
PADDING_BYTE = 0xFF

# DME Configurations
DME_CONFIGS = {
    "MS42": {
        "isn_address": 0x3EDE,
        "immo_padding_size": 66,
        "min_firmware_size": 0x481A5,
        "version_check_offset": 0x48042,
        "version_check_value": "0110C6",
        "immobiliser_patches": [
            {
                "address": 0x283BA,
                "original": bytes(
                    [0x88, 0x90, 0x88, 0x60, 0x8A, 0x0E, 0x02, 0xF0, 0xEA, 0x00]
                ),
                "patched": bytes(
                    [0xDA, 0x07, 0xC8, 0x59, 0xFE, 0x0E, 0x2E, 0x0F, 0xDB, 0x00]
                ),
            },
            {
                "address": 0x481A4,
                "original": bytes([0x02]),
                "patched": bytes([0x00]),
            },
            {
                "address": 0x29E8A,
                "original": bytes([0xC2, 0xFE, 0xE9, 0x01]),
                "patched": bytes([0xC2, 0xFE, 0xA4, 0x01]),
            },
        ],
    },
    "MS43": {
        "isn_address": 0x3ED4,
        "immo_padding_size": 76,
        "min_firmware_size": 0x70A6F,
        "version_check_offset": 0x70042,
        "version_check_value": "430069",
        "immobiliser_patches": [
            {
                "address": 0x2E2F0,
                "original": bytes([0xC2, 0xFE, 0xB9, 0x0A]),
                "patched": bytes([0xC2, 0xFE, 0x6E, 0x0A]),
            },
            {
                "address": 0x600D8,
                "original": bytes([0xDA, 0x0A, 0x6C, 0xDD]),
                "patched": bytes([0xDA, 0x0D, 0xF8, 0x3B]),
            },
            {
                "address": 0x53BF8,
                "original": bytes([0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
                "patched": bytes([0xDA, 0x0A, 0xE4, 0xFC, 0x0E, 0x1A, 0xDB, 0x00]),
            },
            {
                "address": 0x70A6E,
                "original": bytes([0x02]),
                "patched": bytes([0x00]),
            },
        ],
    },
}

# Styling constants
STYLE_TITLE = "font-weight: bold; font-size: 14px; margin-bottom: 10px;"
STYLE_INFO = "color: #666; margin-bottom: 15px;"


class IsnCopierTab(QWidget):
    """Tab for copying ISN value between binary files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "en"
        self.t = None
        self._init_ui()
        self.update_language("en")

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # DME selector
        self.dme_selector = QComboBox()
        self.dme_selector.addItems(["MS42", "MS43"])
        self.dme_selector.setCurrentText("MS43")
        self.dme_selector.setFixedHeight(INPUT_HEIGHT)

        # Input fields
        self.source_file_input = QLineEdit()
        self.source_file_input.setReadOnly(True)
        self.target_file_input = QLineEdit()
        self.target_file_input.setReadOnly(True)
        self.isn_value_display = QLineEdit()
        self.isn_value_display.setReadOnly(True)
        self.status = QLabel()
        self.status.setWordWrap(True)

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

        self.dme_type_label = QLabel()
        self.source_label = QLabel()
        self.target_label = QLabel()
        self.isn_label = QLabel()

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.dme_type_label)
        self.layout.addWidget(self.dme_selector)
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
        self.dme_selector.currentIndexChanged.connect(self._dme_type_changed)

    def _dme_type_changed(self) -> None:
        """Read both files again, since the ISN address and the bypass differ per DME type."""
        source = self.source_file_input.text().strip()
        target = self.target_file_input.text().strip()
        if source:
            self._read_isn_value(source)
        if target:
            self._update_bypass_options(target)

    def update_language(self, lang: str) -> None:
        """Update UI text for the specified language."""
        self.lang = lang
        self.t = get_translations(lang).ISN_COPIER
        self.description.setText(self.t["title"])
        self.info.setText(self.t["description"])
        self.dme_type_label.setText(self.t.get("dme_type", "DME Type:"))
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
            self._update_bypass_options(file_path)
            self.status.setText(self.t["target_selected"])

    def _read_file_data(self, file_path: str) -> bytes | None:
        """Read binary file data.

        Returns:
            File content as bytes, or None if reading fails
        """
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except OSError:
            return None

    def _is_file_large_enough(self, data: bytes, required_size: int) -> bool:
        """Check if file data meets minimum size requirement."""
        return len(data) >= required_size

    def _extract_version_string(self, data: bytes, offset: int) -> str:
        """Extract version string from binary data at given offset."""
        version_bytes = data[offset : offset + VERSION_LENGTH]
        return version_bytes.decode("ascii", errors="ignore")

    def _check_version_compatibility(self, file_path: str) -> bool:
        """Check if the target file has compatible software version for bypass.

        Returns:
            True if version is compatible, False otherwise
        """
        try:
            config = self._get_dme_config()
            version_offset = config.get("version_check_offset")
            expected_version = config.get("version_check_value")

            if not version_offset or not expected_version:
                return False

            data = self._read_file_data(file_path)
            if data is None:
                return False

            min_size = version_offset + VERSION_LENGTH
            if not self._is_file_large_enough(data, min_size):
                return False

            version_string = self._extract_version_string(data, version_offset)
            return version_string == expected_version

        except Exception:
            return False

    def _is_bypass_applied(self, data: bytes, patches: list) -> bool:
        """Check if immobiliser bypass patches are already applied.

        Returns:
            True if any patch is applied, False otherwise
        """
        return any(
            data[patch["address"] : patch["address"] + len(patch["patched"])]
            == patch["patched"]
            for patch in patches
        )

    @staticmethod
    def _hide(checkbox: QCheckBox) -> None:
        """Hide a checkbox and untick it, so a tick for one file can't apply to another."""
        checkbox.setChecked(False)
        checkbox.hide()

    def _hide_all_bypass_options(self) -> None:
        """Hide both bypass checkboxes."""
        self._hide(self.immobiliser_bypass_checkbox)
        self._hide(self.immobiliser_revert_checkbox)

    def _show_bypass_option(self) -> None:
        """Show bypass checkbox, hide revert."""
        self.immobiliser_bypass_checkbox.show()
        self._hide(self.immobiliser_revert_checkbox)

    def _show_revert_option(self) -> None:
        """Show revert checkbox, hide bypass."""
        self._hide(self.immobiliser_bypass_checkbox)
        self.immobiliser_revert_checkbox.show()

    def _update_bypass_options(self, file_path: str) -> None:
        """Update bypass/revert checkbox visibility based on file state."""
        try:
            config = self._get_dme_config()
            data = self._read_file_data(file_path)

            if data is None:
                self._hide_all_bypass_options()
                return

            # Validate file size
            if not self._is_file_large_enough(data, config["min_firmware_size"]):
                self._hide_all_bypass_options()
                return

            # Validate software version
            if not self._check_version_compatibility(file_path):
                self._hide_all_bypass_options()
                return

            # Determine if bypass is already applied
            if self._is_bypass_applied(data, config["immobiliser_patches"]):
                self._show_revert_option()
            else:
                self._show_bypass_option()

        except Exception:
            self._hide_all_bypass_options()

    def _bytes_to_hex_string(self, data: bytes) -> str:
        """Convert bytes to uppercase hex string."""
        return "".join(f"{b:02X}" for b in data)

    def _read_isn_value(self, file_path: str) -> None:
        """Read ISN value from source file and display it."""
        try:
            isn_bytes = self._read_isn_from_source(file_path)
            if isn_bytes:
                hex_value = self._bytes_to_hex_string(isn_bytes)
                self.isn_value_display.setText(hex_value)
                self.status.setText(self.t["source_selected"])
            else:
                self.isn_value_display.setText("")
                self.status.setText(self.t["error_file_too_small"])
        except OSError as e:
            self.status.setText(f"Error reading file: {str(e)}")
            self.isn_value_display.setText("")
        except Exception as e:
            self.status.setText(f"Error: {str(e)}")
            self.isn_value_display.setText("")

    def _read_isn_from_source(self, file_path: str) -> bytes | None:
        """Read ISN bytes from file at configured address.

        Returns:
            ISN bytes if successful, None if file is too small
        """
        config = self._get_dme_config()
        with open(file_path, "rb") as f:
            f.seek(config["isn_address"])
            isn_bytes = f.read(ISN_LENGTH)
            return isn_bytes if len(isn_bytes) == ISN_LENGTH else None

    def _validate_file_paths(self, source_path: str, target_path: str) -> bool:
        """Validate that both file paths are provided.

        Returns:
            True if both paths are valid, False otherwise
        """
        if not source_path or not target_path:
            self.status.setText(self.t["error_required"])
            return False
        return True

    def _process_files(self) -> None:
        """Copy ISN value from source to target file."""
        try:
            source_path = self.source_file_input.text().strip()
            target_path = self.target_file_input.text().strip()

            if not self._validate_file_paths(source_path, target_path):
                return

            isn_bytes = self._read_isn_from_file(source_path)
            if isn_bytes is None:
                return

            target_data = self._load_and_prepare_target(target_path, isn_bytes)
            if target_data is None:
                return

            if not self._apply_immobiliser_patches(target_data):
                return
            self._save_modified_file(target_path, target_data, isn_bytes)

        except OSError as e:
            self.status.setText(f"File error: {str(e)}")
        except Exception as e:
            self.status.setText(f"Error: {str(e)}")

    def _read_isn_from_file(self, file_path: str) -> bytes | None:
        """Read ISN value from source file.

        Returns:
            ISN bytes if successful, None on error
        """
        isn_bytes = self._read_isn_from_source(file_path)
        if isn_bytes is None:
            self.status.setText(self.t["error_file_too_small"])
        return isn_bytes

    def _fill_immo_area(self, data: bytearray, address: int, size: int) -> None:
        """Fill immobiliser area with padding bytes."""
        data[address : address + size] = bytes([PADDING_BYTE] * size)

    def _write_isn_to_data(
        self, data: bytearray, address: int, isn_bytes: bytes
    ) -> None:
        """Write ISN bytes to data at specified address."""
        data[address : address + ISN_LENGTH] = isn_bytes

    def _load_and_prepare_target(
        self, file_path: str, isn_bytes: bytes
    ) -> bytearray | None:
        """Load target file and write ISN value.

        Returns:
            Modified data as bytearray, or None on error
        """
        config = self._get_dme_config()
        data = self._read_file_data(file_path)

        if data is None:
            self.status.setText("Error reading target file")
            return None

        target_data = bytearray(data)
        isn_address = config["isn_address"]
        padding_size = config["immo_padding_size"]

        if not self._is_file_large_enough(target_data, isn_address + padding_size):
            self.status.setText(self.t["error_target_too_small"])
            return None

        self._fill_immo_area(target_data, isn_address, padding_size)
        self._write_isn_to_data(target_data, isn_address, isn_bytes)

        return target_data

    def _should_apply_patches(self) -> bool:
        """Check if any immobiliser patches should be applied."""
        return (
            self.immobiliser_bypass_checkbox.isChecked()
            or self.immobiliser_revert_checkbox.isChecked()
        )

    def _apply_patches(
        self, target_data: bytearray, patches: list, patch_type: str
    ) -> None:
        """Apply a list of patches to target data.

        Args:
            target_data: Data to modify
            patches: List of patch dictionaries
            patch_type: Either 'patched' or 'original'
        """
        for patch in patches:
            addr = patch["address"]
            data = patch[patch_type]
            target_data[addr : addr + len(data)] = data

    def _bypass_fits(self, data: bytes, applied: bool) -> bool:
        """Whether the data can take the bypass, or its revert when applied is True."""
        config = self._get_dme_config()
        offset = config["version_check_offset"]
        return (
            self._is_file_large_enough(data, config["min_firmware_size"])
            and self._extract_version_string(data, offset)
            == config["version_check_value"]
            and self._is_bypass_applied(data, config["immobiliser_patches"]) == applied
        )

    def _apply_immobiliser_patches(self, target_data: bytearray) -> bool:
        """Apply or revert immobiliser bypass patches.

        This checks the file again, since it may have changed after the user chose it.

        Returns:
            False, with nothing changed, if the file can't take the patches
        """
        if not self._should_apply_patches():
            return True

        revert = not self.immobiliser_bypass_checkbox.isChecked()
        if not self._bypass_fits(target_data, applied=revert):
            self.status.setText(self.t["error_bypass_unsupported"])
            return False

        patches = self._get_dme_config()["immobiliser_patches"]
        self._apply_patches(target_data, patches, "original" if revert else "patched")
        return True

    def _clear_bypass_selections(self) -> None:
        """Clear all bypass checkbox selections."""
        self.immobiliser_bypass_checkbox.setChecked(False)
        self.immobiliser_revert_checkbox.setChecked(False)

    def _save_modified_file(
        self, original_path: str, target_data: bytearray, isn_bytes: bytes
    ) -> None:
        """Save modified target file and update status."""
        new_file_path = self._get_modified_filepath(original_path)
        with open(new_file_path, "wb") as f:
            f.write(target_data)

        hex_value = self._bytes_to_hex_string(isn_bytes)
        filename = Path(new_file_path).name
        self.status.setText(self.t["success"].format(hex_value, filename))

        self._clear_bypass_selections()

    def _get_dme_config(self) -> dict:
        """Get the configuration for the currently selected DME type."""
        dme_type = self.dme_selector.currentText()
        return DME_CONFIGS[dme_type]

    @staticmethod
    def _get_modified_filepath(original_path: str) -> str:
        """Generate modified file path with datetime suffix."""
        path = Path(original_path)
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
        new_filename = f"{path.stem}_{timestamp}{path.suffix}"
        new_path = path.parent / new_filename
        return str(new_path)
