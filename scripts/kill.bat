@echo off
set "ESCAPED_PATH=%cd:\=\\%"

echo Killing bot processes...
powershell -Command "Get-CimInstance Win32_Process -Filter \"Name = 'python.exe' AND CommandLine LIKE '%%%ESCAPED_PATH%%%'\" | Invoke-CimMethod -MethodName Terminate" >nul 2>&1