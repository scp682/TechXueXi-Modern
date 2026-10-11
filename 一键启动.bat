@echo off
setlocal EnableExtensions
chcp 65001 >nul
title TechXueXi Launcher
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

cd /d "%~dp0"
set "ROOT_DIR=%~dp0"
set "APP_DIR=%ROOT_DIR%SourcePackages"
set "APP_SCRIPT=%APP_DIR%\pandalearning.py"
set "REQ_FILE=%ROOT_DIR%requirements-windows.txt"
set "VENV_DIR=%ROOT_DIR%.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "PYTHON_EXE="

echo ============================================================
echo TechXueXi one-click launcher
echo ============================================================

if not exist "%APP_SCRIPT%" goto missing_project
if not exist "%REQ_FILE%" goto missing_project

if exist "%VENV_PY%" (
    "%VENV_PY%" -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 8) else 1)" >nul 2>&1
    if errorlevel 1 goto wrong_venv
    goto check_dependencies
)

if exist "%ROOT_DIR%.runtime\python38\python.exe" set "PYTHON_EXE=%ROOT_DIR%.runtime\python38\python.exe"
if not defined PYTHON_EXE for /f "usebackq delims=" %%I in (`py -3.8 -c "import sys; print(sys.executable)" 2^>nul`) do set "PYTHON_EXE=%%I"

if not defined PYTHON_EXE (
    for %%P in (
        "C:\Python38\python.exe"
        "C:\Program Files\Python38\python.exe"
        "%LocalAppData%\Programs\Python\Python38\python.exe"
    ) do (
        if not defined PYTHON_EXE if exist "%%~P" set "PYTHON_EXE=%%~P"
    )
)

if not defined PYTHON_EXE goto missing_python

echo [1/3] Creating the Python 3.8 virtual environment...
"%PYTHON_EXE%" -m venv "%VENV_DIR%"
if errorlevel 1 goto venv_failed

:check_dependencies
echo [2/3] Checking Python dependencies...
"%VENV_PY%" -c "import requests,lxml,colorama,bs4,selenium,pyhocon,PIL,telebot,socks,flask,flask_sqlalchemy,flask_cors,qrcode; from pyzbar import pyzbar" >nul 2>&1
if not errorlevel 1 goto check_browser

echo Installing dependencies. This is only needed on the first run...
if exist "%ROOT_DIR%.runtime\wheels\pip-25.0.1-py3-none-any.whl" (
    "%VENV_PY%" -m pip install --no-index --find-links "%ROOT_DIR%.runtime\wheels" pip
    if errorlevel 1 goto dependency_failed
    "%VENV_PY%" -m pip install --no-index --find-links "%ROOT_DIR%.runtime\wheels" -r "%REQ_FILE%"
    if errorlevel 1 goto dependency_failed
    goto check_browser
)
"%VENV_PY%" -m pip install --upgrade pip "setuptools<81" wheel
if errorlevel 1 goto dependency_failed
"%VENV_PY%" -m pip install -r "%REQ_FILE%"
if errorlevel 1 goto dependency_failed

:check_browser
echo [3/3] Checking ChromeDriver...
if exist "%APP_DIR%\chrome\chromedriver.exe" goto run_app
where chromedriver.exe >nul 2>&1
if errorlevel 1 goto missing_driver

:run_app
if /i "%~1"=="--check" (
    echo Startup checks passed. Login was not started.
    exit /b 0
)
echo.
echo Starting TechXueXi...
echo Close this window to stop the program.
echo ============================================================
pushd "%APP_DIR%"
"%VENV_PY%" "%APP_SCRIPT%"
set "APP_EXIT=%ERRORLEVEL%"
popd

echo.
if not "%APP_EXIT%"=="0" echo TechXueXi exited with code %APP_EXIT%.
echo Press any key to close this window.
pause >nul
exit /b %APP_EXIT%

:missing_python
echo.
echo ERROR: Python 3.8 was not found.
echo Install Python 3.8 x64 and enable "Add Python to PATH", then run this file again.
echo Download: https://www.python.org/downloads/release/python-3810/
goto stop_with_error

:wrong_venv
echo.
echo ERROR: The existing .venv was not created with Python 3.8.
echo Rename or remove this folder, then run the launcher again:
echo %VENV_DIR%
goto stop_with_error

:missing_driver
echo.
echo ERROR: ChromeDriver was not found.
echo Put a matching Chrome and ChromeDriver pair in:
echo %APP_DIR%\chrome\chrome.exe
echo %APP_DIR%\chrome\chromedriver.exe
echo The Chrome and ChromeDriver major versions must match.
goto stop_with_error

:missing_project
echo.
echo ERROR: Required project files are missing.
echo Keep this BAT file in the TechXueXi-developing folder.
goto stop_with_error

:venv_failed
echo.
echo ERROR: Failed to create the virtual environment.
goto stop_with_error

:dependency_failed
echo.
echo ERROR: Failed to install Python dependencies.
echo Check the network connection and the error messages above.
goto stop_with_error

:stop_with_error
echo.
echo Press any key to close this window.
pause >nul
exit /b 1
