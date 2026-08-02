"""PhoneNumber must accept every realistic way a Persian-speaking customer
types a mobile number, and reject everything else.
"""

import pytest

from core.domain.value_objects.phone_number import PhoneNumber


@pytest.mark.parametrize(
    "raw",
    [
        "09123456789",
        "9123456789",
        "+989123456789",
        "00989123456789",
        "989123456789",
        "0912 345 6789",
        "0912-345-6789",
        "۰۹۱۲۳۴۵۶۷۸۹",  # Persian digits
        "٠٩١٢٣٤٥٦٧٨٩",  # Arabic-Indic digits
        " 09123456789 ",
    ],
)
def test_accepts_realistic_inputs_and_normalizes_to_local_form(raw: str) -> None:
    assert PhoneNumber.parse(raw).value == "09123456789"


@pytest.mark.parametrize(
    "raw",
    [
        "02112345678",  # landline (Tehran area code), not mobile
        "0912345678",  # one digit short
        "091234567890",  # one digit too many
        "not a phone number",
        "",
        "09123abc789",
    ],
)
def test_rejects_invalid_input(raw: str) -> None:
    with pytest.raises(ValueError, match="not a valid Iranian mobile number"):
        PhoneNumber.parse(raw)


def test_str_returns_the_normalized_value() -> None:
    assert str(PhoneNumber.parse("9123456789")) == "09123456789"
