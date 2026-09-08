# -*- coding: utf-8 -*-
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCH_ROOT = ROOT / "mqtt_tool"
SKIP_NAMES = {"_migrate_layout.py"}


def watched_mtimes():
    out = {}
    for p in WATCH_ROOT.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        if p.name in SKIP_NAMES:
            continue
        try:
            out[str(p)] = p.stat().st_mtime
        except OSError:
            pass
    launch = ROOT / "launch.py"
    if launch.is_file():
        try:
            out[str(launch)] = launch.stat().st_mtime
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
    for cache in WATCH_ROOT.rglob("__pycache__"):
        for p in cache.glob("*.pyc"):
            try:
                p.unlink()
            except OSError:
                pass


def start_app():
    clear_pyc()
    return subprocess.Popen(
        [sys.executable, "-B", "-m", "mqtt_tool"],
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
    print("开发模式：改 mqtt_tool/**/*.py 自动重启窗口（Ctrl+C 退出）")
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
