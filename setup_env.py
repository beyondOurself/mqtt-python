# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
REQ_FILE = ROOT / "requirements.txt"
MIN_VERSION = (3, 8)


def _run(cmd, **kwargs):
    print(">", " ".join(str(x) for x in cmd))
    return subprocess.run(cmd, cwd=str(ROOT), **kwargs)


def _version_ok(version_info):
    return tuple(version_info[:2]) >= MIN_VERSION


def _check_tkinter(python):
    code = "import tkinter; tkinter.Tk().destroy()"
    r = _run([python, "-c", code], capture_output=True, text=True)
    return r.returncode == 0


def _check_paho(python):
    code = "from paho.mqtt import client as mqtt_client"
    r = _run([python, "-c", code], capture_output=True, text=True)
    return r.returncode == 0


def _venv_python():
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _ensure_venv(base_python):
    py = _venv_python()
    if py.is_file():
        return str(py)
    print("创建虚拟环境 .venv …")
    r = _run([base_python, "-m", "venv", str(VENV_DIR)])
    if r.returncode != 0:
        raise SystemExit("创建虚拟环境失败")
    if not py.is_file():
        raise SystemExit("虚拟环境创建后未找到 python")
    return str(py)


def _pip_install(python):
    reqs = [str(REQ_FILE)]
    if not REQ_FILE.is_file():
        reqs = ["paho-mqtt>=2.0.0"]
    steps = [
        [python, "-m", "pip", "install", "--upgrade", "pip"],
        [python, "-m", "pip", "install", "-r", *reqs] if REQ_FILE.is_file() else [python, "-m", "pip", "install", "paho-mqtt>=2.0.0"],
    ]
    for cmd in steps:
        r = _run(cmd)
        if r.returncode != 0:
            raise SystemExit("依赖安装失败")


def _verify(python):
    code = (
        "import sys\n"
        "assert sys.version_info[:2]>=%r\n"
        "import tkinter; tkinter.Tk().destroy()\n"
        "from paho.mqtt import client as mqtt_client\n"
        "from md5tool import md5sign\n"
        "from mqtt_publish import Mqttpub\n"
    ) % (MIN_VERSION,)
    r = _run([python, "-c", code], capture_output=True, text=True)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()
        if "tkinter" in err.lower() or "TclError" in err:
            raise SystemExit("当前 Python 缺少 Tkinter，请重装 Python 并勾选 tcl/tk")
        if "paho" in err.lower():
            raise SystemExit("paho-mqtt 未安装成功")
        raise SystemExit(err or "环境检查失败")
    print("环境检查通过:", python)


def check_only():
    py = str(_venv_python()) if _venv_python().is_file() else sys.executable
    if not Path(py).is_file():
        print("未找到 .venv，请先运行 setup.bat")
        return 1
    try:
        _verify(py)
    except SystemExit:
        return 1
    return 0


def install():
    if not _version_ok(sys.version_info):
        raise SystemExit("需要 Python %s+" % ".".join(map(str, MIN_VERSION)))
    if not _check_tkinter(sys.executable):
        raise SystemExit("当前 Python 缺少 Tkinter，请重装 Python 并勾选 tcl/tk")
    py = _ensure_venv(sys.executable)
    _pip_install(py)
    _verify(py)
    marker = ROOT / ".env_ready"
    marker.write_text(py + "\n", encoding="utf-8")
    print("初始化完成，Python:", py)
    return 0


def main():
    parser = argparse.ArgumentParser(description="MQTT 工具运行环境检查与安装")
    parser.add_argument("--check", action="store_true", help="仅检查 .venv 是否可用")
    parser.add_argument("--install", action="store_true", help="创建 .venv 并安装依赖")
    args = parser.parse_args()
    if args.check:
        raise SystemExit(check_only())
    if args.install:
        raise SystemExit(install())
    raise SystemExit(install() if not _venv_python().is_file() else check_only())


if __name__ == "__main__":
    main()
