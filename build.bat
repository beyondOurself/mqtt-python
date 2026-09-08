@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY=%~dp0.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo 首次打包，正在初始化环境…
  call "%~dp0setup.bat" nopause
  if errorlevel 1 exit /b 1
)

if not exist "%PY%" (
  echo 虚拟环境未就绪，请先运行 setup.bat
  pause
  exit /b 1
)

"%PY%" -m pip install -q -r requirements-dev.txt
"%PY%" scripts\build_release.py
if errorlevel 1 (
  echo 打包失败
  pause
  exit /b 1
)
echo.
if exist .build_out.txt type .build_out.txt
pause
