FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /opt/banking-project

COPY src src
# COPY alembic.ini alembic.ini
COPY pyproject.toml pyproject.toml
# COPY logging.conf logging.conf
# COPY uv.lock uv.lock

RUN uv sync

ENTRYPOINT [ "uv", "run" ]

CMD ["src/main.py"]
