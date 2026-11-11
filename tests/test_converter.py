import pytest

from mscoder.tabs.converter import VinConverterTab
from mscoder.translations import en
from mscoder.utils import vin_to_str

VIN = "WBADT43452G112233"
HEX = "202CA35D1031050900410820C3"


@pytest.fixture
def tab(app) -> VinConverterTab:
    return VinConverterTab()


def test_vin_to_hex(tab):
    tab.vin_input.setText(VIN)
    tab._to_hex()
    assert tab.hex_input.text() == HEX
    assert tab.status.text() == en.CONVERTER["ok"]


@pytest.mark.parametrize(
    "text",
    [HEX, HEX.lower(), "0x" + HEX, " ".join(HEX[i : i + 2] for i in range(0, 26, 2))],
)
def test_hex_to_vin(tab, text: str):
    tab.hex_input.setText(text)
    tab._to_str()
    assert tab.vin_input.text() == VIN
    assert tab.status.text() == en.CONVERTER["ok"]


def test_refuses_a_short_vin(tab):
    tab.vin_input.setText(VIN[:-1])
    tab._to_hex()
    assert tab.hex_input.text() == ""
    assert tab.status.text() == en.CONVERTER["error_vin_length"]


@pytest.mark.parametrize(
    ("text", "error"),
    [(HEX[:-2], "error_hex_length"), ("ZZ" + HEX[2:], "error_hex_format")],
)
def test_refuses_bad_hex(tab, text: str, error: str):
    tab.hex_input.setText(text)
    tab._to_str()
    assert tab.vin_input.text() == ""
    assert tab.status.text() == en.CONVERTER[error]


def test_the_hex_placeholder_is_the_vin_placeholder_encoded(tab):
    hex_hint = tab.hex_input.placeholderText()
    assert vin_to_str(bytes.fromhex(hex_hint)) == tab.vin_input.placeholderText()


def test_says_when_hex_is_not_an_encoded_vin(tab):
    tab.hex_input.setText("FF" * 13)
    tab._to_str()
    assert tab.vin_input.text() == ""
    assert tab.status.text() == en.CONVERTER["error_hex_not_vin"]
