"""Make assets/icon.ico and assets/icon.icns, the app icons, from assets/icon.svg.

Run with: make icons
"""

import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
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


def render(renderer: QSvgRenderer, size: int) -> bytes:
    """Draw the SVG at this size, so each size is sharp, and return it as PNG."""
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    data = QByteArray()
    buf = QBuffer(data)
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buf, "PNG")
    return bytes(data.data())


def write_ico(path: Path, images: list[tuple[int, bytes]]) -> None:
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries = b""
    for size, png in images:
        dim = 0 if size >= 256 else size  # 0 means 256
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png), offset)
        offset += len(png)
    path.write_bytes(header + entries + b"".join(png for _, png in images))


def write_icns(path: Path, images: list[tuple[bytes, bytes]]) -> None:
    entries = b"".join(
        kind + struct.pack(">I", 8 + len(png)) + png for kind, png in images
    )
    path.write_bytes(b"icns" + struct.pack(">I", 8 + len(entries)) + entries)


def make_icons(svg: Path, out: Path) -> None:
    renderer = QSvgRenderer(str(svg))
    if not renderer.isValid():
        raise ValueError(f"{svg} did not load")
    write_ico(out / "icon.ico", [(s, render(renderer, s)) for s in ICO_SIZES])
    write_icns(out / "icon.icns", [(k, render(renderer, s)) for k, s in ICNS_TYPES])


def main() -> int:
    QGuiApplication(sys.argv)
    make_icons(ASSETS / "icon.svg", ASSETS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
