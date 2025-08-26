import enum
from typing import Any, Dict, Optional, Union, TypeVar
from fastapi import HTTPException
from httpx import AsyncClient, HTTPError, Response
from pydantic import BaseModel, ValidationError

class Methods(enum.StrEnum):
    POST = "post"
    GET = "get"
    PATCH = "patch"
    DELETE = "delete"
    PUT = "put"

T = TypeVar("T", bound=BaseModel)

class APIClient:
    def __init__(self, client: AsyncClient):
        self.client = client

    def _validate_request(
        self, data: Any, request_schema: Optional[type[BaseModel]]
    ) -> Any:
        if request_schema and data is not None:
            validated = request_schema.model_validate(data, from_attributes=True)
            return validated.model_dump()
        return data

    def _validate_response(
        self, data: Any, response_schema: Optional[type[T]]
    ) -> Union[T, Any]:
        if response_schema:
            return response_schema.model_validate(data, from_attributes=True)
        return data

    def _handle_error_response(self, response: Response):
        try:
            error_data = response.json()
            detail = error_data.get(
                "error", error_data.get("message", "Request failed")
            )
        except:  # noqa: E722
            detail = f"HTTP {response.status_code}: {response.text[:100]}"

        raise HTTPException(status_code=response.status_code, detail=detail)

    async def request(
        self,
        method: Methods,
        url: str,
        /,
        *,
        data: Any,
        request_schema: Optional[type[BaseModel]] = None,
        response_schema: Optional[type[T]] = None,
        **kwargs,
    ):
        try:
            validated_data = self._validate_request(data, request_schema)

            # Get or Delete method
            input = {"params": validated_data}

            if method == Methods.POST or method == Methods.PATCH or method == Methods.PUT:
                input = {"json": validated_data}

            headers: dict[str, str] = kwargs.get("headers")
            if headers:
                content_type = headers.get("content-type")
                # Based on content-type, property 'data' could be used
                if content_type == "application/x-www-form-urlencoded":
                    input = {"data": validated_data}

            response = await self.client.request(method=method, url=url, **input, **kwargs)

            if not response.is_success:
                self._handle_error_response(response)

            result = response.json()

            return self._validate_response(result, response_schema)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
        except HTTPError as e:
            raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")

    async def post(
        self,
        url: str,
        data: Any = None,
        request_schema: Optional[type[BaseModel]] = None,
        response_schema: Optional[type[T]] = None,
        **kwargs,
    ) -> Union[T, Dict[str, Any]]:
        return await self.request(
            Methods.POST,
            url,
            data=data,
            request_schema=request_schema,
            response_schema=response_schema,
            **kwargs,
        )

    async def get(
        self,
        url: str,
        query: Any = None,
        request_schema: Optional[type[BaseModel]] = None,
        response_schema: Optional[type[T]] = None,
        **kwargs,
    ) -> Union[T, dict[str, Any]]:
        return await self.request(
            Methods.GET,
            url,
            data=query,
            request_schema=request_schema,
            response_schema=response_schema,
            **kwargs,
        )
