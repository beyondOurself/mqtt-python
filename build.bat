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
"%PY%" -m PyInstaller --noconfirm mqtt_tool_v5.spec
if exist dist\templates.json goto done
if exist templates.json copy /Y templates.json dist\templates.json >nul
:done
echo.
echo 产物: dist\mqtt_tool_v5.exe
pause
