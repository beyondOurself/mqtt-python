# -*- coding: utf-8 -*-
import os
import sys

_PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROJECT_ROOT = os.path.dirname(_PACKAGE_DIR)


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return _PROJECT_ROOT


def package_data_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "mqtt_tool", "data")
    return os.path.join(_PACKAGE_DIR, "data")
