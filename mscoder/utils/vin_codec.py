import string
from collections.abc import Iterator

CHAR_MAP = string.digits + string.ascii_uppercase


def _chunk(data: bytes, size: int) -> Iterator[bytes]:
    """
    Split data into chunks of specified size.

    Args:
        data: Input bytes to chunk
        size: Size of each chunk

    Yields:
        Chunks of specified size
    """
    for i in range(0, len(data), size):
        yield data[i : i + size]


def vin_to_str(vin: bytes) -> str:
    """
    Convert VIN bytes to string representation.

    This decodes the proprietary VIN encoding used in BMW MS43 DMEs.

    Args:
        vin: Raw VIN bytes (13 bytes)

    Returns:
        17-character VIN string
    """
    vin = vin.rjust(15, b"\x00")
    chars = []

    for a, b, c in _chunk(vin, 3):
        x = (a << 16) | (b << 8) | c
        chars.extend(CHAR_MAP[(x >> s) & 0x3F] for s in (18, 12, 6, 0))

    return "".join(chars)[3:]


def vin_to_bytes(vin: str) -> bytes:
    """
    Convert VIN string to bytes representation.

    This encodes a standard VIN into the proprietary format used in BMW MS43 DMEs.

    Args:
        vin: 17-character VIN string

    Returns:
        13 bytes representing the encoded VIN

    Raises:
        ValueError: If VIN contains invalid characters
    """
    data = bytes(CHAR_MAP.index(c) for c in vin.upper()).rjust(20, b"\x00")
    out = bytearray()

    for a, b, c, d in _chunk(data, 4):
        x = (a << 18) | (b << 12) | (c << 6) | d
        out.extend((x >> 16, (x >> 8) & 0xFF, x & 0xFF))

    return bytes(out)[2:]
