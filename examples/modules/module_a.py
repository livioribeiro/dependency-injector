from asgikit.requests import HttpRequest
from asgikit.responses import JsonResponse

from selva.web import controller, get


@controller("/")
class Controller:
    @get
    def index(self) -> JsonResponse:
        return JsonResponse({"location": "index"})

    @get("/hello/{name}")
    async def hello(self, name: str, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"hello": name, "request": request.path})