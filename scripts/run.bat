@echo off

powershell -WindowStyle Hidden -Command "Start-Process uv -ArgumentList 'run python -O main.py' -WindowStyle Hidden -WorkingDirectory '%cd%'"
echo Running bot in the background...
