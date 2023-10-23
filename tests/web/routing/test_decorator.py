from http import HTTPMethod

import pytest

from selva.web.routing.decorator import (
    ACTION_ATTRIBUTE,
    CONTROLLER_ATTRIBUTE,
    ActionInfo,
    ActionType,
    ControllerInfo,
    controller,
    delete,
    get,
    patch,
    post,
    put,
    route,
    websocket,
)


def test_controller_decorator_without_path():
    class Controller:
        pass

    controller(Controller)

    assert hasattr(Controller, CONTROLLER_ATTRIBUTE)
    assert getattr(Controller, CONTROLLER_ATTRIBUTE) == ControllerInfo("")


def test_controller_decorator_with_path():
    class Controller:
        pass

    controller("path")(Controller)

    assert hasattr(Controller, CONTROLLER_ATTRIBUTE)
    assert getattr(Controller, CONTROLLER_ATTRIBUTE) == ControllerInfo("path")


def test_controller_decorator_on_non_class_should_fail():
    async def func():
        pass

    with pytest.raises(TypeError):
        controller(func)


@pytest.mark.parametrize(
    "decorator,action_type",
    [
        (get, ActionType.GET),
        (post, ActionType.POST),
        (put, ActionType.PUT),
        (patch, ActionType.PATCH),
        (delete, ActionType.DELETE),
        (websocket, ActionType.WEBSOCKET),
    ],
    ids=["get", "post", "put", "patch", "delete", "websocket"],
)
def test_route_decorator_without_path(decorator, action_type):
    async def handler(req):
        pass

    decorator(handler)

    assert hasattr(handler, ACTION_ATTRIBUTE)
    assert getattr(handler, ACTION_ATTRIBUTE) == ActionInfo(action_type, "")


@pytest.mark.parametrize(
    "decorator,action_type",
    [
        (get, ActionType.GET),
        (post, ActionType.POST),
        (put, ActionType.PUT),
        (patch, ActionType.PATCH),
        (delete, ActionType.DELETE),
        (websocket, ActionType.WEBSOCKET),
    ],
    ids=["get", "post", "put", "patch", "delete", "websocket"],
)
def test_route_decorator_with_path(decorator, action_type):
    async def handler(req):
        pass

    decorator("path")(handler)

    assert hasattr(handler, ACTION_ATTRIBUTE)
    assert getattr(handler, ACTION_ATTRIBUTE) == ActionInfo(action_type, "path")


def test_handler_with_less_than_one_parameter_should_fail():
    async def func0():
        pass

    async def func1(req):
        pass

    with pytest.raises(
        TypeError, match="Handler method must have at least 1 parameter"
    ):
        route(func0, method=HTTPMethod.GET, path="")

    route(func1, method=HTTPMethod.GET, path="")


def test_non_async_handler_should_fail():
    def handler(req):
        pass

    with pytest.raises(TypeError, match="Handler method must be async"):
        route(handler, method=HTTPMethod.GET, path="")