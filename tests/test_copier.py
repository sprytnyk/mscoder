from pathlib import Path

import pytest

from mscoder.tabs.copier import DME_CONFIGS, IsnCopierTab
from mscoder.translations import en
from tests.helpers import ISN, firmware, new_files, with_isn

DMES = ["MS42", "MS43"]
T = en.ISN_COPIER


@pytest.fixture
def tab(app):
    tab = IsnCopierTab()
    tab.show()  # the copier looks at which boxes are visible
    yield tab
    tab.close()


def save(folder: Path, name: str, data: bytes) -> Path:
    path = folder / name
    path.write_bytes(data)
    return path


def pick(tab: IsnCopierTab, choose_file, *, source: Path | None = None, target: Path | None = None):
    if source:
        choose_file(source)
        tab._select_source_file()
    if target:
        choose_file(target)
        tab._select_target_file()


def copy(tab: IsnCopierTab, folder: Path) -> list[Path]:
    before = set(folder.iterdir())
    tab._process_files()
    return new_files(folder, before)


@pytest.mark.parametrize("dme", DMES)
def test_reads_the_isn_from_the_source(tab, choose_file, tmp_path, dme):
    tab.dme_selector.setCurrentText(dme)
    pick(tab, choose_file, source=save(tmp_path, "source.bin", firmware(dme, isn=ISN)))
    assert tab.isn_value_display.text() == "A1B2C3D4E5F6"
    assert tab.status.text() == T["source_selected"]


@pytest.mark.parametrize("dme", DMES)
def test_copies_the_isn_and_changes_nothing_else(tab, choose_file, tmp_path, dme):
    tab.dme_selector.setCurrentText(dme)
    source = save(tmp_path, "source.bin", firmware(dme, isn=ISN))
    target = save(tmp_path, "target.bin", firmware(dme))
    pick(tab, choose_file, source=source, target=target)

    [out] = copy(tab, tmp_path)
    assert out.name.startswith("target_") and out.suffix == ".bin"
    assert out.read_bytes() == with_isn(dme, firmware(dme), ISN)
    assert source.read_bytes() == firmware(dme, isn=ISN)
    assert target.read_bytes() == firmware(dme)
    assert tab.status.text() == T["success"].format("A1B2C3D4E5F6", out.name)


@pytest.mark.parametrize("dme", DMES)
def test_leaves_an_existing_bypass_alone(tab, choose_file, tmp_path, dme):
    tab.dme_selector.setCurrentText(dme)
    pick(
        tab,
        choose_file,
        source=save(tmp_path, "source.bin", firmware(dme, isn=ISN)),
        target=save(tmp_path, "target.bin", firmware(dme, patched=True)),
    )
    [out] = copy(tab, tmp_path)
    assert out.read_bytes() == with_isn(dme, firmware(dme, patched=True), ISN)


@pytest.mark.parametrize("dme", DMES)
def test_offers_the_bypass_for_a_supported_file(tab, choose_file, tmp_path, dme):
    tab.dme_selector.setCurrentText(dme)
    pick(tab, choose_file, target=save(tmp_path, "target.bin", firmware(dme)))
    assert tab.immobiliser_bypass_checkbox.isVisible()
    assert not tab.immobiliser_revert_checkbox.isVisible()


@pytest.mark.parametrize("dme", DMES)
def test_offers_to_revert_a_patched_file(tab, choose_file, tmp_path, dme):
    tab.dme_selector.setCurrentText(dme)
    pick(tab, choose_file, target=save(tmp_path, "target.bin", firmware(dme, patched=True)))
    assert not tab.immobiliser_bypass_checkbox.isVisible()
    assert tab.immobiliser_revert_checkbox.isVisible()


@pytest.mark.parametrize("dme", DMES)
@pytest.mark.parametrize("problem", ["wrong version", "too small"])
def test_offers_no_bypass_for_an_unsupported_file(tab, choose_file, tmp_path, dme, problem):
    tab.dme_selector.setCurrentText(dme)
    if problem == "wrong version":
        data = firmware(dme, version="999999")
    else:
        data = firmware(dme, size=DME_CONFIGS[dme]["min_firmware_size"] - 1)
    pick(tab, choose_file, target=save(tmp_path, "target.bin", data))
    assert not tab.immobiliser_bypass_checkbox.isVisible()
    assert not tab.immobiliser_revert_checkbox.isVisible()


@pytest.mark.parametrize("dme", DMES)
def test_bypass_writes_exactly_the_patches(tab, choose_file, tmp_path, dme):
    tab.dme_selector.setCurrentText(dme)
    pick(
        tab,
        choose_file,
        source=save(tmp_path, "source.bin", firmware(dme, isn=ISN)),
        target=save(tmp_path, "target.bin", firmware(dme)),
    )
    tab.immobiliser_bypass_checkbox.setChecked(True)

    [out] = copy(tab, tmp_path)
    assert out.read_bytes() == with_isn(dme, firmware(dme, patched=True), ISN)
    assert not tab.immobiliser_bypass_checkbox.isChecked()


@pytest.mark.parametrize("dme", DMES)
def test_revert_puts_back_the_original_bytes(tab, choose_file, tmp_path, dme):
    tab.dme_selector.setCurrentText(dme)
    pick(
        tab,
        choose_file,
        source=save(tmp_path, "source.bin", firmware(dme, isn=ISN)),
        target=save(tmp_path, "target.bin", firmware(dme, patched=True)),
    )
    tab.immobiliser_revert_checkbox.setChecked(True)

    [out] = copy(tab, tmp_path)
    assert out.read_bytes() == with_isn(dme, firmware(dme), ISN)


def test_needs_both_files(tab, choose_file, tmp_path):
    pick(tab, choose_file, source=save(tmp_path, "source.bin", firmware("MS43", isn=ISN)))
    assert copy(tab, tmp_path) == []
    assert tab.status.text() == T["error_required"]


def test_refuses_a_source_too_small_for_the_isn(tab, choose_file, tmp_path):
    pick(tab, choose_file, source=save(tmp_path, "source.bin", bytes(0x3ED4 + 5)))
    assert tab.isn_value_display.text() == ""
    assert tab.status.text() == T["error_file_too_small"]


@pytest.mark.parametrize("dme", DMES)
def test_writes_nothing_to_a_target_too_small_for_the_isn(tab, choose_file, tmp_path, dme):
    tab.dme_selector.setCurrentText(dme)
    config = DME_CONFIGS[dme]
    size = config["isn_address"] + config["immo_padding_size"] - 1
    pick(
        tab,
        choose_file,
        source=save(tmp_path, "source.bin", firmware(dme, isn=ISN)),
        target=save(tmp_path, "target.bin", firmware(dme, size=size)),
    )
    assert copy(tab, tmp_path) == []
    assert tab.status.text() == T["error_target_too_small"]


# A typo here would write the wrong bytes into a DME, and the tests above build their
# files from the same table, so pin it. Only change both together, and on purpose.
PINNED = {
    "MS42": (
        0x3EDE,
        66,
        0x481A5,
        0x48042,
        "0110C6",
        [
            (0x283BA, "8890 8860 8A0E 02F0 EA00", "DA07 C859 FE0E 2E0F DB00"),
            (0x481A4, "02", "00"),
            (0x29E8A, "C2FE E901", "C2FE A401"),
        ],
    ),
    "MS43": (
        0x3ED4,
        76,
        0x70A6F,
        0x70042,
        "430069",
        [
            (0x2E2F0, "C2FE B90A", "C2FE 6E0A"),
            (0x600D8, "DA0A 6CDD", "DA0D F83B"),
            (0x53BF8, "0000 FFFF FFFF FFFF", "DA0A E4FC 0E1A DB00"),
            (0x70A6E, "02", "00"),
        ],
    ),
}


@pytest.mark.parametrize("dme", DMES)
def test_dme_tables_are_unchanged(dme):
    config = DME_CONFIGS[dme]
    isn, padding, min_size, offset, version, patches = PINNED[dme]
    assert config["isn_address"] == isn
    assert config["immo_padding_size"] == padding
    assert config["min_firmware_size"] == min_size
    assert config["version_check_offset"] == offset
    assert config["version_check_value"] == version
    assert [
        (p["address"], p["original"].hex().upper(), p["patched"].hex().upper())
        for p in config["immobiliser_patches"]
    ] == [(a, o.replace(" ", ""), n.replace(" ", "")) for a, o, n in patches]


@pytest.mark.parametrize("dme", DMES)
def test_patches_fit_the_file_and_do_not_overlap(dme):
    config = DME_CONFIGS[dme]
    areas = [(config["isn_address"], config["immo_padding_size"])]
    areas.append((config["version_check_offset"], 6))
    for patch in config["immobiliser_patches"]:
        assert len(patch["original"]) == len(patch["patched"])
        assert patch["address"] + len(patch["patched"]) <= config["min_firmware_size"]
        areas.append((patch["address"], len(patch["patched"])))
    areas.sort()
    for (start, size), (next_start, _) in zip(areas, areas[1:], strict=False):
        assert start + size <= next_start
