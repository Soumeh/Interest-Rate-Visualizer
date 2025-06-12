#!/usr/bin/bash
gunicorn src.backend.__main__:app run --bind 0.0.0.0:8000
