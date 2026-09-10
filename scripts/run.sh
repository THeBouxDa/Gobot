#!/bin/bash

nohup uv run python -O main.py > /dev/null 2>&1 &
echo "Application started in the background."