# -*- coding: utf-8 -*-
import copy
import json
import os

from mqtt_tool.storage.paths import package_data_dir

DEFAULT_TEMPLATE = "channelPersonAlert"


def load_default_templates():
    path = os.path.join(package_data_dir(), "templates.default.json")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_templates(path, fallback=None):
    fallback = fallback if fallback is not None else load_default_templates()
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and data:
            return data
    return copy.deepcopy(fallback)
