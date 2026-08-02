"""Every ServiceType member must resolve to a non-empty Persian label."""

import pytest

from core.domain.value_objects.service_type import ServiceType


@pytest.mark.parametrize("service_type", list(ServiceType))
def test_every_member_has_a_persian_label(service_type: ServiceType) -> None:
    assert service_type.label_fa
    assert isinstance(service_type.label_fa, str)


def test_exactly_six_services_are_defined() -> None:
    assert len(list(ServiceType)) == 6
