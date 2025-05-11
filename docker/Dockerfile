FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /opt/banking-project

COPY src src
COPY pyproject.toml pyproject.toml

RUN uv sync

ENTRYPOINT [ "uv", "run" ]

RUN sh [ "start_etl.sh" ]
