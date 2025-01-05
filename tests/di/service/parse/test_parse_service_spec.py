import pytest

from selva.di.error import InvalidServiceTypeError, NonInjectableTypeError
from selva.di.service.parse import parse_service_spec, _get_service_signature


def test_parse_invalid_service_should_fail():
    with pytest.raises(InvalidServiceTypeError):
        parse_service_spec(object())


def test_get_dependencies_invalid_service_should_fail():
    with pytest.raises(InvalidServiceTypeError):
        list(_get_service_signature(object()))