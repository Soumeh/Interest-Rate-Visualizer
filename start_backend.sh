#!/usr/bin/env bash
python manage.py collectstatic
gunicorn --config gunicorn_config.py src.backend.wsgi:application
