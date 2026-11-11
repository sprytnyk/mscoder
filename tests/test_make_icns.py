from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QImageReader

from scripts.make_icns import make_icns


def test_makes_an_icns_from_the_app_icon(app, tmp_path: Path):
    out = tmp_path / "icon.icns"
    make_icns(Path("assets/icon.ico"), out)

    reader = QImageReader(str(out))
    assert reader.format() == b"icns"
    sizes = []
    for i in range(reader.imageCount()):
        reader.jumpToImage(i)
        image = reader.read()
        assert image.hasAlphaChannel()
        sizes.append(image.width())
    # no bigger than the 128 px source, since scaling up only blurs it
    assert sorted(sizes) == [16, 32, 32, 64, 128]


def test_a_bigger_source_fills_the_bigger_sizes(app, tmp_path: Path):
    source = tmp_path / "big.png"
    image = QImage(600, 600, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.red)
    image.save(str(source))
    out = tmp_path / "icon.icns"
    make_icns(source, out)

    reader = QImageReader(str(out))
    sizes = []
    for i in range(reader.imageCount()):
        reader.jumpToImage(i)
        sizes.append(reader.read().width())
    assert sorted(sizes) == [16, 32, 32, 64, 128, 256, 256, 512, 512]
