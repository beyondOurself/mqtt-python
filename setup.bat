@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal EnableDelayedExpansion
if /i "%~1"=="nopause" set "NO_PAUSE=1"

echo.
echo ========================================
echo   MQTT 发送工具 - 环境初始化
echo ========================================
echo.

set "LAUNCHER="
where py >nul 2>&1
if !errorlevel!==0 (
  py -3 -c "import sys" >nul 2>&1
  if !errorlevel!==0 set "LAUNCHER=py -3"
)
if not defined LAUNCHER (
  where python >nul 2>&1
  if !errorlevel!==0 set "LAUNCHER=python"
)

if not defined LAUNCHER (
  echo [1/2] 未检测到 Python，尝试通过 winget 安装 Python 3.12 …
  where winget >nul 2>&1
  if !errorlevel! neq 0 (
    echo.
    echo 错误：未找到 Python，且系统无 winget。
    echo 请手动安装 Python 3.8+ 并勾选 Tcl/Tk：
    echo   https://www.python.org/downloads/
    echo 安装时勾选 "Add python.exe to PATH"。
    echo.
    if not defined NO_PAUSE pause
    exit /b 1
  )
  winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  if !errorlevel! neq 0 (
    echo winget 安装失败，请手动安装 Python 后重试 setup.bat
    if not defined NO_PAUSE pause
    exit /b 1
  )
  echo.
  echo Python 已安装，请关闭本窗口后重新运行 setup.bat 以刷新 PATH。
  echo 若仍失败，注销或重启电脑后再试。
  echo.
  if not defined NO_PAUSE pause
  exit /b 0
)

echo [1/2] 使用解释器: !LAUNCHER!
echo [2/2] 创建虚拟环境并安装依赖 …
echo.

!LAUNCHER! setup_env.py --install
if !errorlevel! neq 0 (
  echo.
  echo 初始化失败，请检查上方错误信息。
  if not defined NO_PAUSE pause
  exit /b 1
)

echo.
echo 环境就绪。可运行：
echo   run.bat     启动 GUI
echo   dev.bat     开发模式（热重载）
echo   build.bat   打包 exe
echo.
if not defined NO_PAUSE pause
exit /b 0
