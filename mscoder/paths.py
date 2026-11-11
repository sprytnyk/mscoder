"""Where the app's files are, from source and in a PyInstaller build."""

import sys
from pathlib import Path


def _base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # the build unpacks its files here
    return Path(__file__).resolve().parent.parent


ASSETS = _base() / "assets"
