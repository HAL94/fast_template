FROM python:3.13-alpine3.21 AS dependencies

# operate in "unbuffered" mode for stdout and stderr
ENV PYTHONUNBUFFERED=1
#  install uv by copying the binary from the official distroless
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

ENV UV_COMPILE_BYTE=1
ENV UV_LINK_MODE=copy

WORKDIR /usr/src/app

COPY ./pyproject.toml ./uv.lock ./.python-version ./

# INSTALL DEPS
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

FROM dependencies AS base
# Copy the project into image
WORKDIR /usr/src/app
COPY ./app ./app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

CMD ["./.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]