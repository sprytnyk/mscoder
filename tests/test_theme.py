from pathlib import Path

import pytest
from PySide6.QtCore import Qt

from mscoder import theme
from mscoder.__main__ import MSCoder
from mscoder.widgets import StatusLabel


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        ("Error: VIN must be 17 characters", "error"),
        ("Помилка: VIN повинен бути 17 символів", "error"),
        ("Error reading file: denied", "error"),
        ("Success: ISN value copied", "success"),
        ("Успішно: значення ISN скопійовано", "success"),
        ("OK", "success"),
        ("Warning: Decoded VIN is 16 chars", "warning"),
        ("Попередження: Декодований VIN", "warning"),
        ("Target file selected", "info"),
    ],
)
def test_the_status_line_is_coloured_by_what_it_says(app, text, kind):
    label = StatusLabel()
    label.setText(text)
    assert label.text() == text
    assert label.property("kind") == kind


def test_an_empty_status_line_is_hidden(app):
    label = StatusLabel()
    label.setText("OK")
    assert not label.isHidden()
    label.setText("")
    assert label.isHidden()


def test_every_tab_uses_the_status_line(app):
    window = MSCoder()
    for tab in (window.replacer_tab, window.converter_tab, window.isn_copier_tab):
        assert isinstance(tab.status, StatusLabel)
    window.close()


@pytest.mark.parametrize(
    ("scheme", "expected"),
    [
        (Qt.ColorScheme.Dark, theme.DARK),
        (Qt.ColorScheme.Light, theme.LIGHT),
        (Qt.ColorScheme.Unknown, theme.LIGHT),
    ],
)
def test_follows_the_system_light_or_dark_setting(scheme, expected):
    assert theme.for_scheme(scheme) is expected


@pytest.mark.parametrize("t", [theme.DARK, theme.LIGHT])
def test_the_stylesheet_points_at_icons_that_exist(app, t):
    sheet = theme.stylesheet(t)
    urls = [part.split('")')[0] for part in sheet.split('url("')[1:]]
    assert len(urls) == 3  # the dropdown's two carets and the check mark
    for url in urls:
        assert Path(url).is_file()
        assert t.muted in Path(url).read_text() or t.on_focus in Path(url).read_text()
