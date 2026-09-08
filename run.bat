@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY=%~dp0.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo 首次运行，正在初始化环境…
  call "%~dp0setup.bat" nopause
  if errorlevel 1 exit /b 1
)

if not exist "%PY%" (
  echo 虚拟环境未就绪，请先运行 setup.bat
  pause
  exit /b 1
)

"%PY%" mqtt_gui.py
if errorlevel 1 pause
