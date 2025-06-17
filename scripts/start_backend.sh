#!/usr/bin/bash
#python -m src.backend
gunicorn -w 4 --bind 0.0.0.0:5000 'src.backend.__main__:app'
