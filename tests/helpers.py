from pathlib import Path

from mscoder.tabs.copier import DME_CONFIGS

FIRMWARE_SIZE = 512 * 1024
ISN = bytes.fromhex("A1B2C3D4E5F6")


def firmware(
    dme: str,
    *,
    isn: bytes = bytes(6),
    version: str | None = None,
    patched: bool = False,
    size: int = FIRMWARE_SIZE,
) -> bytes:
    """A made-up firmware file: filler bytes, an ISN, a version string and the
    bytes the immobiliser patches look for."""
    config = DME_CONFIGS[dme]
    data = bytearray((i * 7 + 3) % 251 for i in range(FIRMWARE_SIZE))
    data[config["isn_address"] : config["isn_address"] + 6] = isn
    offset = config["version_check_offset"]
    data[offset : offset + 6] = (version or config["version_check_value"]).encode()
    for patch in config["immobiliser_patches"]:
        new = patch["patched" if patched else "original"]
        data[patch["address"] : patch["address"] + len(new)] = new
    return bytes(data[:size])


def with_isn(dme: str, data: bytes, isn: bytes) -> bytes:
    """What a target looks like after the copy: the ISN, then 0xFF padding."""
    config = DME_CONFIGS[dme]
    start, size = config["isn_address"], config["immo_padding_size"]
    out = bytearray(data)
    out[start : start + size] = isn + b"\xff" * (size - len(isn))
    return bytes(out)


def changed_offsets(old: bytes, new: bytes) -> set[int]:
    assert len(old) == len(new)
    return {i for i, (a, b) in enumerate(zip(old, new, strict=True)) if a != b}


def new_files(folder: Path, before: set[Path]) -> list[Path]:
    return sorted(set(folder.iterdir()) - before)
