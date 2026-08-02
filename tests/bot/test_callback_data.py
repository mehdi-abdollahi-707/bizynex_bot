"""NavCallback must round-trip through pack/unpack exactly as aiogram will use it."""

from apps.bot.keyboards.callback_data import NavCallback


def test_pack_and_unpack_round_trip() -> None:
    packed = NavCallback(target="about").pack()
    assert NavCallback.unpack(packed) == NavCallback(target="about")


def test_pack_uses_the_nav_prefix() -> None:
    assert NavCallback(target="faq").pack().startswith("nav:")
