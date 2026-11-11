import os
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QFileDialog


@pytest.fixture(scope="session")
def app(tmp_path_factory: pytest.TempPathFactory) -> QApplication:
    # Qt writes caches under the home folder; keep them out of the real one
    home = tmp_path_factory.mktemp("home")
    os.environ.update(
        HOME=str(home),
        XDG_CONFIG_HOME=str(home / ".config"),
        XDG_DATA_HOME=str(home / ".local" / "share"),
        XDG_CACHE_HOME=str(home / ".cache"),
        XDG_STATE_HOME=str(home / ".local" / "state"),
        QT_QPA_PLATFORM="offscreen",
    )
    return QApplication.instance() or QApplication([])


@pytest.fixture
def choose_file(monkeypatch: pytest.MonkeyPatch):
    """Answer the next file dialog with this path."""

    def choose(path: Path) -> None:
        monkeypatch.setattr(
            QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(path), "")
        )

    return choose
