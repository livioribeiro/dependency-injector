# Project Selva

Selva is a Python ASGI web framework built on top of [asgikit](https://github.com/livioribeiro/asgikit)
and inspired by Spring Boot, AspNet Core and FastAPI.

## Usage

Create an application and controller

```python
from asgikit.responses import PlainTextResponse
from selva.web import Application, controller, get


@controller("/")
class Controller:
    @get
    def hello(self) -> PlainTextResponse:
        return PlainTextResponse("Hello, World!")


app = Application()
app.register(Controller)
```

Add a service

```python
from asgikit.responses import PlainTextResponse
from selva.di import service
from selva.web import Application, controller, get


@service
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


@controller("/")
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get
    def hello(self) -> PlainTextResponse:
        greeting = self.greeter.greet("World")
        return PlainTextResponse(greeting)


app = Application()
app.register(Controller, Greeter)
```

Get parameters from path

```python
from asgikit.responses import JsonResponse
from selva.di import service
from selva.web import Application, controller, get


@service
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


@controller("/")
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get("hello/{name}")
    def hello(self, name: str) -> JsonResponse:
        greeting = self.greeter.greet(name)
        return JsonResponse({"greeting": greeting})


app = Application()
app.register(Controller, Greeter)
```

Configurations with [Pydantic](https://pydantic-docs.helpmanual.io/usage/settings/)

```python
from asgikit.requests import HttpRequest
from asgikit.responses import JsonResponse
from selva.di import service
from selva.web import Application, controller, get
from pydantic import BaseSettings


class Settings(BaseSettings):
    DEFAULT_NAME: str


@service
def settings_factory() -> Settings:
    return Settings()


@service
class Greeter:
    def __init__(self, settings: Settings):
        self.default_name = settings.DEFAULT_NAME

    def greet(self, name: str | None) -> str:
        name = name or self.default_name
        return f"Hello, {name}!"


@controller("/")
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get("hello/{name}")
    def hello(self, name: str) -> JsonResponse:
        greeting = self.greeter.greet(name)
        return JsonResponse({"greeting": greeting})

    @get("hello")
    def hello_optional(self, request: HttpRequest) -> JsonResponse:
        name = request.query.get("name")
        greeting = self.greeter.greet(name)
        return JsonResponse({"greeting": greeting})


app = Application()
app.register(Controller, Greeter)
```

Manage services lifecycle (e.g [Databases](https://www.encode.io/databases/))

```python
from asgikit.requests import HttpRequest
from asgikit.responses import JsonResponse
from selva.di import service, initializer, finalizer
from selva.web import Application, controller, get
from pydantic import BaseSettings, PostgresDsn
from databases import Database


class Settings(BaseSettings):
    DEFAULT_NAME: str
    DATABASE_URL: PostgresDsn


@service
def settings_factory() -> Settings:
    return Settings()


@service
class Repository:
    def __init__(self, settings: Settings):
        self.database = Database(settings.DATABASE_URL)

    async def get_greeting(self, name: str) -> str:
        result = await self.database.fetch_one(
            query="select text from greeting where name = :name",
            values={"name": name}
        )

        return result.text

    @initializer
    async def initialize(self):
        await self.database.connect()
        print("Database connection opened")

    @finalizer
    async def finalize(self):
        await self.database.disconnect()
        print("Database connection closed")


@service
class Greeter:
    def __init__(self, repository: Repository, settings: Settings):
        self.repository = repository
        self.default_name = settings.DEFAULT_NAME

    async def greet(self, name: str | None) -> str:
        name = name or self.default_name
        return await self.repository.get_greeting(name)


@controller("/")
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get("hello/{name}")
    def hello(self, name: str) -> JsonResponse:
        greeting = self.greeter.greet(name)
        return JsonResponse({"greeting": greeting})

    @get("hello")
    def hello_optional(self, request: HttpRequest) -> JsonResponse:
        name = request.query.get("name")
        greeting = self.greeter.greet(name)
        return JsonResponse({"greeting": greeting})


app = Application()
app.register(Controller, Greeter)
```

Define controllers and services in separate modules

```
├───modules
│   ├───controllers.py
│   ├───repository.py
│   ├───services.py
│   └───settings.py
└───main.py
```

```python
### modules/settings.py
from selva.di import service
from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    DEFAULT_NAME: str
    DATABASE_URL: PostgresDsn


@service
def settings_factory() -> Settings:
    return Settings()
```

```python
### modules/repository.py
from selva.di import service, initializer, finalizer
from databases import Database
from .settings import Settings

@service
class Repository:
    def __init__(self, settings: Settings):
        self.database = Database(settings.DATABASE_URL)

    async def get_greeting(self, name: str) -> str:
        result = await self.database.fetch_one(
            query="select text from greeting where name = :name",
            values={"name": name}
        )

        return result.text

    @initializer
    async def initialize(self):
        await self.database.connect()
        print("Database connection opened")

    @finalizer
    async def finalize(self):
        await self.database.disconnect()
        print("Database connection closed")
```

```python
### modules/services.py
from selva.di import service
from .settings import Settings
from .repository import Repository


@service
class Greeter:
    def __init__(self, repository: Repository, settings: Settings):
        self.repository = repository
        self.default_name = settings.DEFAULT_NAME

    async def greet(self, name: str | None) -> str:
        name = name or self.default_name
        return await self.repository.get_greeting(name)
```

```python
### modules/controllers.py
from asgikit.requests import HttpRequest
from asgikit.responses import JsonResponse
from selva.web import controller, get
from .services import Greeter

@controller("/")
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get("hello/{name}")
    def hello(self, name: str) -> JsonResponse:
        greeting = self.greeter.greet(name)
        return JsonResponse({"greeting": greeting})

    @get("hello")
    def hello_optional(self, request: HttpRequest) -> JsonResponse:
        name = request.query.get("name")
        greeting = self.greeter.greet(name)
        return JsonResponse({"greeting": greeting})
```

```python
### main.py
from selva.web import Application
from . import modules


app = Application()
app.register(modules)
```

Also supports websockets

```python
from http import HTTPStatus
from pathlib import Path
from asgikit.websockets import WebSocket
from asgikit.responses import HttpResponse, FileResponse
from asgikit.errors.websocket import WebSocketDisconnectError
from selva.web import Application, controller, get, websocket

@controller("/")
class WebSocketController:
    @get
    def index(self) -> FileResponse:
        return FileResponse(Path(__file__).parent / "index.html")

    @get("/favicon.ico")
    def favicon(self) -> HttpResponse:
        return HttpResponse(status=HTTPStatus.NOT_FOUND)

    @websocket("/chat")
    async def chat(self, client: WebSocket):
        await client.accept()
        print(f"[open] Client connected")

        self.handler.clients.append(client)

        while True:
            try:
                message = await client.receive()
                print(f"[message] {message}")
                await client.send_text(message)
            except WebSocketDisconnectError:
                print("[close] Client disconnected")
                break


app = Application()
app.register(WebSocketController)
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WebSocket chat</title>
</head>
<body>
<form id="chat-form">
    <textarea name="message-list" id="message-list" cols="30" rows="10" readonly></textarea>
    <p>
        <input type="text" name="message-box" id="message-box" />
        <button type="submit">Send</button>
    </p>
</form>

<script>
    const messages = [];

    const chat = document.getElementById("chat-form");
    const textarea = document.getElementById("message-list");
    textarea.value = "";
    const messageInput = document.getElementById("message-box");

    const socket = new WebSocket("ws://localhost:8000/chat");

    function addMessage(message) {
        messages.push(message)
        textarea.value = `${messages.join("\n")}`;
        textarea.scrollTop = textarea.scrollHeight;
    }

    chat.onsubmit = (event) => {
        event.preventDefault();
        const message = messageInput.value;
        socket.send(message);
        messageInput.value = "";
    };

    socket.onopen = (event) => {
        console.log("[open] Client connected");
    };

    socket.onmessage = (event) => {
        const message = event.data;
        console.log(`[message] "${message}"`)
        addMessage(message);
    };

    socket.onclose = (event) => {
        if (event.wasClean) {
            console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
            console.log('[close] Connection died');
        }
    };

    socket.onerror = function(error) {
        console.log(`[error] ${error.message}`);
    };
</script>
</body>
</html>
```
