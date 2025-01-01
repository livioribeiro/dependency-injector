from http import HTTPStatus

import pydantic
from asgikit.requests import Body, read_form, read_json
from pydantic import BaseModel as PydanticModel

from selva.web.converter.decorator import register_converter
from selva.web.exception import HTTPBadRequestException, HTTPException


@register_converter(Body, dict)
class RequestBodyDictConverter:
    async def convert(self, body: Body, original_type: type) -> dict:
        if "application/json" in body.content_type:
            return await read_json(body)
        elif "application/x-www-form-urlencoded" in body.content_type:
            return await read_form(body)
        else:
            raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)


@register_converter(Body, PydanticModel)
class RequestBodyPydanticConverter:
    async def convert(
        self,
        body: Body,
        original_type: type[PydanticModel],
    ) -> PydanticModel:
        # TODO: make request body decoding extensible
        if "application/json" in body.content_type:
            data = await read_json(body)
        elif "application/x-www-form-urlencoded" in body.content_type:
            data = await read_form(body)
        else:
            raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        try:
            return original_type.model_validate(data)
        except pydantic.ValidationError as err:
            raise HTTPBadRequestException() from err


@register_converter(Body, list[PydanticModel])
class RequestBodyPydanticListConverter:
    async def convert(
        self,
        body: Body,
        original_type: type[list[PydanticModel]],
    ) -> list[PydanticModel]:
        if "application/json" in body.content_type:
            data = await read_json(body)
        else:
            raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        adapter = pydantic.TypeAdapter(original_type)

        try:
            return adapter.validate_python(data)
        except pydantic.ValidationError as err:
            raise HTTPBadRequestException() from err