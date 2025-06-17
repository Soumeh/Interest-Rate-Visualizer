#!/usr/bin/bash
uv export --no-hashes --format requirements-txt > requirements.txt
docker compose --env-file=".env" up --build
