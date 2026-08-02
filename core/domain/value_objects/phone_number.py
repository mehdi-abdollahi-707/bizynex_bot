"""PhoneNumber: validates and normalizes an Iranian mobile number.

Accepts however a Persian-speaking customer is likely to type it — Persian
or Arabic-Indic digits, spaces/dashes, with or without a country code —
and normalizes to the local "09XXXXXXXXX" form Bizynex actually calls or
texts customers on.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_DIGIT_TRANSLATION = str.maketrans(
    _PERSIAN_DIGITS + _ARABIC_INDIC_DIGITS,
    "01234567890123456789",
)

# Iranian mobile numbers, without any leading zero/country code, are
# always 9XXXXXXXXX — a 9 followed by 9 more digits.
_MOBILE_CORE_PATTERN = re.compile(r"^9\d{9}$")
_COUNTRY_CODE_PREFIXES = ("+98", "0098", "98", "0")


@dataclass(frozen=True)
class PhoneNumber:
    value: str  # always normalized to "09XXXXXXXXX"

    @classmethod
    def parse(cls, raw: str) -> PhoneNumber:
        normalized = raw.translate(_DIGIT_TRANSLATION)
        digits_only = re.sub(r"[^\d+]", "", normalized)

        for prefix in _COUNTRY_CODE_PREFIXES:
            if digits_only.startswith(prefix):
                digits_only = digits_only[len(prefix) :]
                break

        if not _MOBILE_CORE_PATTERN.match(digits_only):
            raise ValueError(f"'{raw}' is not a valid Iranian mobile number")

        return cls(value=f"0{digits_only}")

    def __str__(self) -> str:
        return self.value
