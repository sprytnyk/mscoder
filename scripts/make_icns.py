"""Make assets/icon.icns, the macOS app icon, from assets/icon.ico.

Run with: QT_QPA_PLATFORM=offscreen uv run python scripts/make_icns.py
"""

import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QImage, QImageReader

ASSETS = Path(__file__).resolve().parent.parent / "assets"
# macOS icon types that hold PNG data, and their sizes in pixels
ICNS_TYPES = [
    (b"icp4", 16),
    (b"icp5", 32),
    (b"ic11", 32),  # 16 on Retina
    (b"ic12", 64),  # 32 on Retina
    (b"ic07", 128),
    (b"ic13", 256),  # 128 on Retina
    (b"ic08", 256),
    (b"ic14", 512),  # 256 on Retina
    (b"ic09", 512),
    (b"ic10", 1024),  # 512 on Retina
]


def biggest_image(path: Path) -> QImage:
    reader = QImageReader(str(path))
    images = []
    for i in range(max(reader.imageCount(), 1)):
        reader.jumpToImage(i)
        image = reader.read()
        if not image.isNull():
            images.append(image)
    if not images:
        raise ValueError(f"{path} did not load")
    return max(images, key=QImage.width).convertToFormat(QImage.Format.Format_ARGB32)


def png(image: QImage, size: int) -> bytes:
    scaled = image.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    data = QByteArray()
    buf = QBuffer(data)
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    scaled.save(buf, "PNG")
    return bytes(data.data())


def make_icns(source: Path, out: Path) -> None:
    """Write every size up to the source's own; scaling up would only blur it."""
    image = biggest_image(source)
    entries = b""
    for kind, size in ICNS_TYPES:
        if size <= image.width():
            data = png(image, size)
            entries += kind + struct.pack(">I", 8 + len(data)) + data
    out.write_bytes(b"icns" + struct.pack(">I", 8 + len(entries)) + entries)


def main() -> int:
    QGuiApplication(sys.argv)
    make_icns(ASSETS / "icon.ico", ASSETS / "icon.icns")
    return 0


if __name__ == "__main__":
    sys.exit(main())
