from pathlib import Path

from PySide6.QtGui import QImageReader

from scripts.make_icons import make_icons

ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
# icp4, icp5, ic11, ic12, ic07, ic13, ic08, ic14, ic09, ic10
ICNS_SIZES = [16, 32, 32, 64, 128, 256, 256, 512, 512, 1024]


def sizes(path: Path, kind: bytes) -> list[int]:
    reader = QImageReader(str(path))
    assert reader.format() == kind
    found = []
    for i in range(reader.imageCount()):
        reader.jumpToImage(i)
        image = reader.read()
        assert image.hasAlphaChannel()
        assert image.width() == image.height()
        found.append(image.width())
    return sorted(found)


def test_makes_every_size_from_the_svg(app, tmp_path: Path):
    make_icons(Path("assets/icon.svg"), tmp_path)
    assert sizes(tmp_path / "icon.ico", b"ico") == ICO_SIZES
    assert sizes(tmp_path / "icon.icns", b"icns") == ICNS_SIZES


def test_the_committed_icons_have_every_size():
    # if this fails, run make icons and commit the result
    assert sizes(Path("assets/icon.ico"), b"ico") == ICO_SIZES
    assert sizes(Path("assets/icon.icns"), b"icns") == ICNS_SIZES
