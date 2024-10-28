#!/bin/sh

source /home/api/.venv/bin/activate

exec fastapi run /home/api/api_code/main.py
