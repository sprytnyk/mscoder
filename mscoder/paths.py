"""Where the app's files are, from source and in a PyInstaller build."""

import sys
from datetime import UTC, datetime
from pathlib import Path


def _base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # the build unpacks its files here
    return Path(__file__).resolve().parent.parent


ASSETS = _base() / "assets"


def modified_path(original_path: str) -> Path:
    """Add a UTC timestamp to a filename, keeping its folder and extension."""
    path = Path(original_path)
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
    return path.parent / f"{path.stem}_{timestamp}{path.suffix}"
