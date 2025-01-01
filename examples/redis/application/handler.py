from typing import Annotated

from asgikit.responses import respond_json
from selva.di import Inject
from selva.web import get

from .service import RedisService


@get
async def index(request, redis_service: Annotated[RedisService, Inject]):
    number = await redis_service.get_incr()
    await respond_json(request.response, {"number": number})