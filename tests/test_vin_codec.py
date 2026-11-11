import pytest

from mscoder.utils import vin_to_bytes, vin_to_str

# the VIN placeholder in the app and its bytes as the DME stores them
VIN = "WBADT43452G112233"
VIN_BYTES = bytes.fromhex("202CA35D1031050900410820C3")


def test_encodes_a_vin_to_13_bytes():
    assert vin_to_bytes(VIN) == VIN_BYTES


def test_decodes_13_bytes_to_a_vin():
    assert vin_to_str(VIN_BYTES) == VIN


@pytest.mark.parametrize(
    "vin", ["WBAGN63452D123456", "WBAEV33452KR12345", "00000000000000000", "ZZZZZZZZZZZZZZZZZ"]
)
def test_round_trip(vin: str):
    data = vin_to_bytes(vin)
    assert len(data) == 13
    assert vin_to_str(data) == vin


def test_lowercase_vin_is_read_as_uppercase():
    assert vin_to_bytes(VIN.lower()) == VIN_BYTES


@pytest.mark.parametrize("vin", ["WBADT43452G11223-", "WBADT43452G1122 3", "WBADT43452G11223Ä"])
def test_characters_outside_digits_and_letters_are_refused(vin: str):
    with pytest.raises(ValueError):
        vin_to_bytes(vin)
