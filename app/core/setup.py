

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Self
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import Settings
from app.api import api_router


class FastApp(FastAPI):
    def __init__(self, settings: Settings, **kwargs: Any):
        self.settings = settings
        kwargs.setdefault("docs_url", None)
        kwargs.setdefault("redoc_url", None)
        kwargs.setdefault("lifespan", self._lifespan)
        super().__init__(**kwargs)

    @asynccontextmanager
    async def _lifespan(self, _: Self, /) -> AsyncGenerator[None, Any]:
        print("App has started")
        yield

    def _setup_middlewares(self) -> None:
        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routers(self) -> None:
        self.include_router(api_router)

    def setup(self) -> None:
        super().setup()

        self._setup_middlewares()
        self._setup_routers()
