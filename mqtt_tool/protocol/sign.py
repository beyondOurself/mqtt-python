# -*- coding: utf-8 -*-
import hashlib
import json
import time


def md5sign(value, offset_ms=0):
    timestamp = str(int(time.time() * 1000 + int(offset_ms)))
    wd = hashlib.md5()
    value["timestamp"] = timestamp
    value = dict(sorted(value.items(), key=lambda x: x[0]))
    value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    wd.update(value.encode(encoding="utf-8"))
    return wd.hexdigest()
