from __future__ import annotations

import pytest

from dependency_injector import Scope
from dependency_injector.errors import DependencyLoopError

from . import ioc

pytestmark = pytest.mark.asyncio


class Service1:
    def __init__(self, service2: Service2):
        pass


class Service2:
    def __init__(self, service1: Service1):
        pass


async def test_dependency_loop(ioc):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(Service2, Scope.SINGLETON)

    with pytest.raises(DependencyLoopError):
        await ioc.get(Service2)
