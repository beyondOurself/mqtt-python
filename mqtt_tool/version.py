# -*- coding: utf-8 -*-
import json
import os
import sys

VERSION_FILE = "version.json"
APP_NAME = "MQTT发送工具"


def _roots():
    roots = []
    if getattr(sys, "frozen", False):
        roots.append(os.path.dirname(sys.executable))
    here = os.path.dirname(os.path.abspath(__file__))
    roots.append(here)
    roots.append(os.path.dirname(here))
    return roots


def version_file_path():
    for root in _roots():
        path = os.path.join(root, VERSION_FILE)
        if os.path.isfile(path):
            return path
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), VERSION_FILE)


def load_version_data():
    path = version_file_path()
    if not os.path.isfile(path):
        return {"major": 0, "minor": 0, "patch": 0, "build": 0}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_version_data(data, path=None):
    path = path or version_file_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def bump_build(path=None):
    path = path or version_file_path()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data["build"] = int(data.get("build", 0)) + 1
    save_version_data(data, path)
    return data


def format_semver(data=None):
    data = data or load_version_data()
    return "%d.%d.%d" % (int(data["major"]), int(data["minor"]), int(data["patch"]))


def format_full(data=None):
    data = data or load_version_data()
    return "%d.%d.%d.%d" % (
        int(data["major"]),
        int(data["minor"]),
        int(data["patch"]),
        int(data["build"]),
    )


def format_title(data=None):
    return "v%s" % format_full(data)


def exe_basename(data=None):
    data = data or load_version_data()
    return "%s_%s" % (APP_NAME, format_full(data))
