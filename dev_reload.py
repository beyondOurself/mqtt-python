# -*- coding: utf-8 -*-
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "mqtt_gui.py"
SKIP = {"dev_reload.py"}


def watched_mtimes():
    out = {}
    for p in ROOT.glob("*.py"):
        if p.name in SKIP:
            continue
        try:
            out[str(p)] = p.stat().st_mtime
        except OSError:
            pass
    return out


def wait_stable_mtimes(timeout=4.0):
    prev = watched_mtimes()
    stable_since = time.time()
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(0.25)
        cur = watched_mtimes()
        if cur != prev:
            prev = cur
            stable_since = time.time()
        elif time.time() - stable_since >= 0.8:
            return cur
    return prev


def clear_pyc():
    cache = ROOT / "__pycache__"
    if not cache.is_dir():
        return
    for p in cache.glob("mqtt_gui*.pyc"):
        try:
            p.unlink()
        except OSError:
            pass


def start_app():
    clear_pyc()
    return subprocess.Popen(
        [sys.executable, "-B", str(TARGET)],
        cwd=str(ROOT),
    )


def stop_app(proc):
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)


def main():
    if not TARGET.is_file():
        print("缺少 mqtt_gui.py")
        sys.exit(1)
    print("开发模式：改 *.py 自动重启窗口（Ctrl+C 退出）")
    last = wait_stable_mtimes()
    proc = start_app()
    try:
        while True:
            time.sleep(0.5)
            if proc.poll() is not None:
                print("窗口已关闭，退出监听")
                break
            cur = watched_mtimes()
            if cur != last:
                print("检测到变更，等待保存完成…")
                stable = wait_stable_mtimes()
                if stable == last:
                    continue
                last = stable
                print("重启…")
                stop_app(proc)
                proc = start_app()
    except KeyboardInterrupt:
        print("\n已停止")
    finally:
        stop_app(proc)


if __name__ == "__main__":
    main()
