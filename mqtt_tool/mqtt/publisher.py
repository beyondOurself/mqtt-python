# -*- coding: utf-8 -*-
import time

from paho.mqtt import client as mqtt_client


class Mqttpub(object):
    def __init__(self, host, topic, port=1883):
        self.topic = topic
        self.host = host
        self.port = port

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code: " + str(rc))

    def clicent_main(self, message, user, pwd):
        client = mqtt_client.Client()
        client.on_connect = self.on_connect
        client.username_pw_set(user, pwd)
        rc = client.connect(self.host, int(self.port), 60)
        if rc != 0:
            raise RuntimeError("MQTT 连接失败 rc=%s" % rc)
        info = client.publish(self.topic, message)
        t0 = time.time()
        while not info.is_published() and time.time() - t0 < 8:
            client.loop(timeout=0.2)
        client.disconnect()
        client.loop(timeout=0.2)
        if not info.is_published():
            raise RuntimeError("消息未发出（超时）")
        print("Successful send message!")
        return True
