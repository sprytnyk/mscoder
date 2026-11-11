from pathlib import Path

import pytest

from mscoder.tabs.replacer import VinReplacerTab
from mscoder.translations import en
from mscoder.utils import vin_to_bytes
from tests.helpers import changed_offsets, new_files

OLD_VIN = "WBADT43452G112233"
NEW_VIN = "WBAGN63452D123456"
FIRST, SECOND = 0x1000, 0x3F000  # where the made-up file holds the VIN


@pytest.fixture
def tab(app) -> VinReplacerTab:
    return VinReplacerTab()


@pytest.fixture
def dump(tmp_path: Path) -> Path:
    data = bytearray((i * 13 + 5) % 251 for i in range(256 * 1024))
    for at in (FIRST, SECOND):
        data[at : at + 13] = vin_to_bytes(OLD_VIN)
    path = tmp_path / "ms41.bin"
    path.write_bytes(bytes(data))
    return path


def run(tab: VinReplacerTab, choose_file, path: Path, old: str, new: str) -> None:
    choose_file(path)
    tab._select_file()
    tab.original_vin_input.setText(old)
    tab.replace_vin_input.setText(new)
    tab._process_file()


def test_replaces_every_copy_of_the_vin(tab, choose_file, dump: Path, tmp_path: Path):
    original = dump.read_bytes()
    before = set(tmp_path.iterdir())
    run(tab, choose_file, dump, OLD_VIN, NEW_VIN)

    [out] = new_files(tmp_path, before)
    assert out.name.startswith("ms41_") and out.suffix == ".bin"
    data = out.read_bytes()
    for at in (FIRST, SECOND):
        assert data[at : at + 13] == vin_to_bytes(NEW_VIN)
    allowed = set(range(FIRST, FIRST + 13)) | set(range(SECOND, SECOND + 13))
    assert changed_offsets(original, data) <= allowed
    assert dump.read_bytes() == original
    assert tab.status.text() == en.REPLACER["success"].format(2, out.name)


def test_writes_nothing_when_the_vin_is_not_there(tab, choose_file, dump, tmp_path):
    before = set(tmp_path.iterdir())
    run(tab, choose_file, dump, "WBAEV33452KR12345", NEW_VIN)
    assert new_files(tmp_path, before) == []
    assert tab.status.text() == en.REPLACER["no_matches"]


@pytest.mark.parametrize(
    ("old", "new", "error"),
    [
        (OLD_VIN[:-1], NEW_VIN, "error_original_length"),
        (OLD_VIN, NEW_VIN + "7", "error_replace_length"),
        ("", NEW_VIN, "error_required"),
    ],
)
def test_writes_nothing_for_a_bad_vin(tab, choose_file, dump, tmp_path, old, new, error):
    before = set(tmp_path.iterdir())
    run(tab, choose_file, dump, old, new)
    assert new_files(tmp_path, before) == []
    assert tab.status.text() == en.REPLACER[error]
