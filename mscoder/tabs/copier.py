"""ISN Copier tab - copies ISN values between binary firmware files."""

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from ..paths import modified_path
from ..translations import get_translations
from ..widgets import StatusLabel, tab_layout

ISN_LENGTH = 6
VERSION_LENGTH = 6
PADDING_BYTE = 0xFF

DME_CONFIGS = {
    "MS42": {
        "isn_address": 0x3EDE,
        "immo_padding_size": 66,
        "min_firmware_size": 0x481A5,
        "version_check_offset": 0x48042,
        # the MS4x community patchlist makes the same bypass for both
        "version_check_values": ("0110C6", "0110C7"),
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
        "version_check_values": ("430069",),
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


class IsnCopierTab(QWidget):
    """Tab for copying ISN value between binary files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "en"
        self.t = None
        self._finishes_bypass = False  # the file holds part of the bypass already
        self._init_ui()
        self.update_language("en")

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # DME selector
        self.dme_selector = QComboBox()
        self.dme_selector.addItems(["MS42", "MS43"])
        self.dme_selector.setCurrentText("MS43")

        # Input fields
        self.source_file_input = QLineEdit()
        self.source_file_input.setReadOnly(True)
        self.target_file_input = QLineEdit()
        self.target_file_input.setReadOnly(True)
        self.isn_value_display = QLineEdit()
        self.isn_value_display.setReadOnly(True)
        self.isn_value_display.setObjectName("mono")
        self.status = StatusLabel()

        # Buttons
        self.btn_select_source = QPushButton()
        self.btn_select_target = QPushButton()
        self.btn_process = QPushButton()
        self.btn_select_source.clicked.connect(self._select_source_file)
        self.btn_select_target.clicked.connect(self._select_target_file)
        self.btn_process.clicked.connect(self._process_files)
        self.btn_process.setObjectName("primary")

        # Checkboxes
        self.immobiliser_bypass_checkbox = QCheckBox()
        self.immobiliser_revert_checkbox = QCheckBox()

        # Hide both initially until target file is selected
        self.immobiliser_bypass_checkbox.hide()
        self.immobiliser_revert_checkbox.hide()

        # Labels
        self.description = QLabel()
        self.description.setObjectName("title")

        self.info = QLabel()
        self.info.setWordWrap(True)
        self.info.setObjectName("info")

        self.dme_type_label = QLabel(objectName="fieldLabel")
        self.source_label = QLabel(objectName="fieldLabel")
        self.target_label = QLabel(objectName="fieldLabel")
        self.isn_label = QLabel(objectName="fieldLabel")

        # Layout
        self.layout = tab_layout()
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
        self.layout.addStretch()

        self.setLayout(self.layout)
        self.dme_selector.currentIndexChanged.connect(self._dme_type_changed)

    def _dme_type_changed(self) -> None:
        """Read both files again, since the ISN address and the bypass differ per DME type."""
        source = self.source_file_input.text().strip()
        target = self.target_file_input.text().strip()
        if source:
            self._read_isn_value(source)
        if target:
            warning = self._update_bypass_options(target)
            if warning:
                self.status.setText(warning)

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
        self._set_bypass_label()
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
            warning = self._update_bypass_options(file_path)
            self.status.setText(warning or self.t["target_selected"])

    def _read_file_data(self, file_path: str) -> bytes | None:
        """Read binary file data.

        Returns:
            File content as bytes, or None if reading fails
        """
        try:
            return Path(file_path).read_bytes()
        except OSError:
            return None

    def _bypass_is_made_for(self, data: bytes) -> bool:
        """Whether the file is big enough and has a software version the bypass is made for."""
        config = self._get_dme_config()
        offset = config["version_check_offset"]
        return (
            len(data) >= config["min_firmware_size"]
            and data[offset : offset + VERSION_LENGTH].decode("ascii", errors="ignore")
            in config["version_check_values"]
        )

    def _patch_state(self, data: bytes) -> tuple[str, list[int]]:
        """How much of the bypass the file holds.

        Returns "original" or "patched" when every patch area agrees, "partial" when
        some hold the patch and the rest the original bytes, and "unknown" when an
        area holds neither, with the addresses of those areas.
        """
        found, unknown = set(), []
        for patch in self._get_dme_config()["immobiliser_patches"]:
            area = data[patch["address"] : patch["address"] + len(patch["patched"])]
            if area == patch["original"]:
                found.add("original")
            elif area == patch["patched"]:
                found.add("patched")
            else:
                unknown.append(patch["address"])
        if unknown:
            return "unknown", unknown
        return (found.pop() if len(found) == 1 else "partial"), []

    def _set_bypass_label(self) -> None:
        """Name the bypass box after what it will do to the file."""
        key = "immobiliser_finish" if self._finishes_bypass else "immobiliser_bypass"
        self.immobiliser_bypass_checkbox.setText(self.t[key])

    def _update_bypass_options(self, file_path: str) -> str | None:
        """Offer the bypass, the rest of a half-done one, or its revert, whichever fits.

        Returns:
            A warning to show when a patch area holds bytes MSCoder doesn't expect
        """
        # A tick for one file must not apply to another.
        for checkbox in (
            self.immobiliser_bypass_checkbox,
            self.immobiliser_revert_checkbox,
        ):
            checkbox.setChecked(False)
            checkbox.hide()
        data = self._read_file_data(file_path)
        if data is None or not self._bypass_is_made_for(data):
            return None

        state, unknown = self._patch_state(data)
        if state == "unknown":
            addresses = ", ".join(f"0x{address:05X}" for address in unknown)
            return self.t["warning_unknown_patch_bytes"].format(addresses=addresses)
        if state == "patched":
            self.immobiliser_revert_checkbox.show()
        else:
            self._finishes_bypass = state == "partial"
            self._set_bypass_label()
            self.immobiliser_bypass_checkbox.show()
        return None

    def _read_isn_value(self, file_path: str) -> None:
        """Read ISN value from source file and display it."""
        try:
            isn_bytes = self._read_isn_from_source(file_path)
        except OSError as error:
            self.status.setText(f"Error reading file: {error}")
            self.isn_value_display.setText("")
            return

        if isn_bytes is None:
            self.isn_value_display.setText("")
            self.status.setText(self._too_small("error_file_too_small", ISN_LENGTH))
        else:
            self.isn_value_display.setText(isn_bytes.hex().upper())
            self.status.setText(self.t["source_selected"])

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

    def _process_files(self) -> None:
        """Copy ISN value from source to target file."""
        source_path = self.source_file_input.text().strip()
        target_path = self.target_file_input.text().strip()
        if not source_path or not target_path:
            self.status.setText(self.t["error_required"])
            return

        try:
            isn_bytes = self._read_isn_from_source(source_path)
            if isn_bytes is None:
                self.status.setText(self._too_small("error_file_too_small", ISN_LENGTH))
                return

            target_data = self._load_and_prepare_target(target_path, isn_bytes)
            if target_data is None:
                return

            if not self._apply_immobiliser_patches(target_data):
                return
            self._save_modified_file(target_path, target_data, isn_bytes)

        except OSError as error:
            self.status.setText(f"File error: {error}")

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

        if len(target_data) < isn_address + padding_size:
            # the area holds the ISN, then FF to its end
            filler = padding_size - ISN_LENGTH
            self.status.setText(self._too_small("error_target_too_small", filler))
            return None

        target_data[isn_address : isn_address + padding_size] = (
            bytes([PADDING_BYTE]) * padding_size
        )
        target_data[isn_address : isn_address + ISN_LENGTH] = isn_bytes

        return target_data

    def _bypass_fits(self, data: bytes, revert: bool) -> bool:
        """Whether the data can take the bypass, the rest of a half-done one, or its revert."""
        if not self._bypass_is_made_for(data):
            return False
        state, _ = self._patch_state(data)
        return state == "patched" if revert else state in ("original", "partial")

    def _apply_immobiliser_patches(self, target_data: bytearray) -> bool:
        """Apply or revert immobiliser bypass patches.

        This checks the file again, since it may have changed after the user chose it.

        Returns:
            False, with nothing changed, if the file can't take the patches
        """
        if not (
            self.immobiliser_bypass_checkbox.isChecked()
            or self.immobiliser_revert_checkbox.isChecked()
        ):
            return True

        revert = not self.immobiliser_bypass_checkbox.isChecked()
        if not self._bypass_fits(target_data, revert=revert):
            self.status.setText(self.t["error_bypass_unsupported"])
            return False

        patch_type = "original" if revert else "patched"
        for patch in self._get_dme_config()["immobiliser_patches"]:
            address = patch["address"]
            data = patch[patch_type]
            target_data[address : address + len(data)] = data
        return True

    def _save_modified_file(
        self, original_path: str, target_data: bytearray, isn_bytes: bytes
    ) -> None:
        """Save modified target file and update status."""
        new_file_path = modified_path(original_path)
        new_file_path.write_bytes(target_data)

        self.status.setText(
            self.t["success"].format(isn_bytes.hex().upper(), new_file_path.name)
        )

        self.immobiliser_bypass_checkbox.setChecked(False)
        self.immobiliser_revert_checkbox.setChecked(False)

    def _too_small(self, key: str, length: int) -> str:
        """Say which address and how many bytes after it this DME type needs."""
        address = self._get_dme_config()["isn_address"]
        return self.t[key].format(address=f"0x{address:04X}", length=length)

    def _get_dme_config(self) -> dict:
        """Get the configuration for the currently selected DME type."""
        dme_type = self.dme_selector.currentText()
        return DME_CONFIGS[dme_type]
