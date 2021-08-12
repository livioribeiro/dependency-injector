import pytest

from dependency_injector.errors import DependencyLoopError

from . import ioc
from .services import dependency_loop as module

pytestmark = pytest.mark.asyncio


async def test_dependency_loop(ioc):
    ioc.scan_packages(module)
    with pytest.raises(DependencyLoopError):
        await ioc.get(module.Service2)
