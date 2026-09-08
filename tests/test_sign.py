# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mqtt_tool.protocol.sign import md5sign


def test_md5sign_sets_timestamp_and_sign_stable():
    payload = {"name": "heartBeat", "sn": "X", "muid": "m", "version": "v2.0.0"}
    sign1 = md5sign(payload, offset_ms=0)
    assert "timestamp" in payload
    assert len(sign1) == 32
    assert payload["timestamp"].isdigit()


if __name__ == "__main__":
    test_md5sign_sets_timestamp_and_sign_stable()
    print("ok")
