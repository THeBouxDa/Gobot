@echo off
setlocal enabledelayedexpansion

set "target_file=%~dp0private\secrets.json"

:: Create the folder and parents if it doesn't exist
echo Creating any missing directories and files...
mkdir "%~dp0data\raw\characters" 2>nul
mkdir "%~dp0private" 2>nul
mkdir "%~dp0logs" 2>nul

if not exist "%target_file%" (
    (
        echo {
        echo     "token": "INSERT YOUR TOKEN HERE",
        echo     "test_guild_ids": {},
        echo     "authorized_users": {}
        echo }
    ) > "%target_file%"
)

:: Check if uv is installed by looking up its system path
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo 'uv' is not installed or not added to your PATH.
    echo Attempting install:

    :: Rephrased from https://docs.astral.sh/uv/getting-started/installation/#installation-methods
    @powershell -ExecutionPolicy Bypass -Command "Invoke-RestMethod -Uri 'https://astral.sh/uv/install.ps1' | Invoke-Expression"
    if %errorlevel% neq 0 goto :error
)

echo.
echo Synchronizing project dependencies...
uv sync
if %errorlevel% neq 0 goto :error
echo.

echo Locking dependencies...
uv lock
if %errorlevel% neq 0 goto :error
echo.

echo Setup complete.
goto :eof

:error
echo [ERROR] The last command failed with exit code %errorlevel%.
exit /b %errorlevel%