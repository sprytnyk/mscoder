"""English translations."""

# Common translations
COMMON = {
    "window_title": "MSCoder",
    "language": "Language:",
    "tab_converter": "Converter",
    "tab_replacer": "File Replacer",
    "tab_isn_copier": "ISN Copier",
    "tab_about": "About",
}

# Converter tab
CONVERTER = {
    "title": "VIN Converter",
    "description": "Convert VIN strings to hex format and vice versa for BMW DMEs.",
    "vin_string": "VIN string:",
    "hex_bytes": "HEX bytes:",
    "btn_to_hex": "STR → HEX",
    "btn_to_str": "HEX → STR",
    "error_vin_length": "Error: VIN must be 17 characters long",
    "error_hex_length": "Error: Hex must be 26 hex digits (13 bytes)",
    "error_hex_format": "Error: Invalid hex format",
    "error_hex_not_vin": "Error: These bytes aren't an encoded VIN",
    "warning_decoded": "Warning: Decoded VIN is {0} chars (expected 17)",
    "ok": "OK",
    "supported": "Supported: MS41, MS42, MS43",
}

# File Replacer tab
REPLACER = {
    "title": "VIN Replacer for Binary Files",
    "description": "Find and replace VIN hex patterns in binary files. The modified file will be saved with a UTC datetime suffix.",
    "original_vin": "Original VIN (string):",
    "replace_vin": "Replacement VIN (string):",
    "binary_file": "Binary file (512kb for MS42/MS43, 256kb for MS41):",
    "btn_select": "Select File",
    "btn_process": "Update VIN",
    "select_file_title": "Select Binary File",
    "all_files": "All Files (*.*)",
    "file_selected": "File selected",
    "error_required": "Error: All fields are required",
    "error_original_length": "Error: Original VIN must be 17 characters long",
    "error_replace_length": "Error: Replacement VIN must be 17 characters long",
    "no_matches": "No matches found in file",
    "success": "Success: {0} occurrence(s) replaced. Saved to: {1}",
    "supported": "Supported: MS41, MS42, MS43",
}

# ISN Copier tab
ISN_COPIER = {
    "title": "ISN Copier",
    "description": "Copy ISN value from one firmware file to another (512kb files for MS42/MS43). The ISN is 6 bytes located at different addresses depending on DME type.",
    "source_file": "Source file (read ISN from):",
    "target_file": "Target file (write ISN to):",
    "value_label": "ISN value from source:",
    "btn_select": "Select File",
    "btn_process": "Copy ISN to Target",
    "select_source_title": "Select Source Firmware File",
    "select_target_title": "Select Target Firmware File",
    "all_files": "All Files (*.*)",
    "source_selected": "Source file selected and ISN value read",
    "target_selected": "Target file selected",
    "error_required": "Error: Both source and target files are required",
    "error_file_too_small": "Error: Source file is too small (address 0x3ED4 + 6 bytes required)",
    "error_target_too_small": "Error: Target file is too small (address 0x3ED4 + 6 bytes required)",
    "success": "Success: ISN value {0} copied to target file. Saved to: {1}",
    "immobiliser_bypass": "Immobiliser bypass",
    "immobiliser_revert": "Revert immobiliser bypass",
    "error_bypass_unsupported": "Error: This target file doesn't fit the immobiliser change. Its size, software version or patch state is wrong. MSCoder saved nothing. Choose the file again to check it.",
}

# About tab
ABOUT = {
    "title": "MSCoder",
    "author": 'Author: <a href="https://sprytnyk.dev">https://sprytnyk.dev</a><br>GitHub: <a href="https://github.com/sprytnyk/mscoder">https://github.com/sprytnyk/mscoder</a>',
    "version": "Version: {version}",
    "header": "About",
}
