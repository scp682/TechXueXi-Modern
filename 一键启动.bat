@echo off
setlocal EnableExtensions
chcp 65001 >nul
title TechXueXi-Modern
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

echo [启动检查]

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

echo   正在创建 Python 3.8 虚拟环境……
"%PYTHON_EXE%" -m venv "%VENV_DIR%"
if errorlevel 1 goto venv_failed

:check_dependencies
echo   正在检查 Python 依赖……
"%VENV_PY%" -c "import requests,lxml,colorama,bs4,selenium,pyhocon,PIL,telebot,socks,flask,flask_sqlalchemy,flask_cors,qrcode; from pyzbar import pyzbar" >nul 2>&1
if not errorlevel 1 goto check_browser

echo   正在安装缺少的依赖……
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
echo   正在检查 ChromeDriver……
if exist "%APP_DIR%\chrome\chromedriver.exe" goto run_app
where chromedriver.exe >nul 2>&1
if errorlevel 1 goto missing_driver

:run_app
if /i "%~1"=="--check" (
    echo   自检通过。此次仅检查启动环境。
    exit /b 0
)
echo   检查通过。关闭窗口可停止程序。
echo.
pushd "%APP_DIR%"
"%VENV_PY%" "%APP_SCRIPT%"
set "APP_EXIT=%ERRORLEVEL%"
popd

echo.
if not "%APP_EXIT%"=="0" echo [错误] 程序退出，退出码 %APP_EXIT%。
echo 按任意键关闭窗口。
pause >nul
exit /b %APP_EXIT%

:missing_python
echo.
echo [错误] 未找到 Python 3.8。
echo 安装 Python 3.8 x64 时勾选 "Add Python to PATH"，然后重新运行。
echo 下载地址：https://www.python.org/downloads/release/python-3810/
goto stop_with_error

:wrong_venv
echo.
echo [错误] 现有虚拟环境的 Python 版本不是 3.8。
echo 请重命名以下目录后重新运行：
echo %VENV_DIR%
goto stop_with_error

:missing_driver
echo.
echo [错误] 未找到 ChromeDriver。
echo 请在下列位置放置对应的 Chrome 和 ChromeDriver：
echo %APP_DIR%\chrome\chrome.exe
echo %APP_DIR%\chrome\chromedriver.exe
echo 两者的主版本号需一致。
goto stop_with_error

:missing_project
echo.
echo [错误] 缺少项目文件。请在完整解压的项目目录中运行本文件。
goto stop_with_error

:venv_failed
echo.
echo [错误] 创建虚拟环境失败。
goto stop_with_error

:dependency_failed
echo.
echo [错误] 安装 Python 依赖失败。请检查网络连接及上方的错误信息。
goto stop_with_error

:stop_with_error
echo.
echo 按任意键关闭窗口。
pause >nul
exit /b 1
