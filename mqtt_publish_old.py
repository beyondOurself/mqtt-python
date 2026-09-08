import random
import time,json,uuid
from md5toolold import md5toolold

from paho.mqtt import client as mqtt_client
#基本链接数据同上
class Mqttpub():
    def __init__(self,host,topic):
        self.topic=topic
        self.host=host

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code: " + str(rc))

    def clicent_main(self,message: str,user,pwd):
        """
        客户端发布消息
        :param message: 消息主体
        :return:
        """
        # time_now = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
        # payload = {"msg": "%s" % message, "data": "%s" % time_now}
        # publish(主题：Topic; 消息内容)
        # client.publish(topic, json.dumps(payload, ensure_ascii=False))
        client = mqtt_client.Client()
        client.on_connect = self.on_connect
        client.username_pw_set(user, pwd)
        client.connect(self.host, 1883, 600)  # 连接mqtt服务 600为keepalive的时间间隔
        client.publish(self.topic, message)

        print("Successful send message!")
        return True
if __name__ == '__main__':
    # while True:
    # d_rtc = {"data":{"recordId":81029,"deviceType":"a8-b3","channelNo":"DJ0MJJ04F65SWRCZ-PC1756434205510","devicePosition":"测试可视对讲主机","callerType":"device","callerSn":"DJ0MJJ04F65SWRCZ","deviceName":"测试可视对讲主机"},"muid":"5565fc3e75c9-98b3-49ed-ac24-eae3d48b7dce","name":"dataToSupervisor","timestamp":"","version":"v2.0.0_1"}
    # d_rtc={"data":{"recordId":81042,"buildingName":"","receiverSn":"DJ0SNJ04F6564YJ3","channelNo":"DJ0GLJ04F65KUEQB-supervisorMachine-1756435394415","roomNo":"","devicePosition":"测试山语清晖管理机","callerType":"supervisorMachine","callerSn":"DJ0GLJ04F65KUEQB","deviceName":"测试山语清晖管理机"},"muid":"442590728973-44df-455b-b131-e81dbc04173d","name":"callDataToIndoor","timestamp":"","version":"v2.0.0_1"}
    # d_mac = {"data":{"time":"2025-01-22 14:37:18","status":0},"muid":"892154e3c425-97b6-4ce5-b0e2-c81c69b8b3bc","name":"timing","sn":"DJ0GLJ04E8A9DETA","timestamp":"1737517038540","version":"v2.1.1_1"}
    # d_mac = {"muid":"","name":"heartBeat","sn":"MJ0FRY04FEF4H8MP","timestamp":"","version":"v2.1.1_1"}
    # d_mac = d_mac = {"data":{"time":"2026-03-26 11:09:28","status":0},"muid":"","name":"timing","sn":"MJ0FRY04FEF4H8MP","timestamp":"","version":"v2.1.1_1"}
    d_mac = {"data":{"ownerType":3,"sendCenterStatus":0,"triggerInduction":"2026-08-27 10:42:00","snapUrl":"https://bsgoalsmartcloud.oss-cn-shenzhen.aliyuncs.com/AccessControl/1744353215604.jpg,https://bsgoalsmartcloud.oss-cn-shenzhen.aliyuncs.com/AccessControl/TD0TD204EB6QXKGV/2025-04-11/11000_20250411135944_rgb.jpg",
                     "eventType":1,"ownerId":10077,"triggerWarning":"2026-08-27 10:42:00","recordId":"","ownerName":"77","runUserNumber":3,"temperature":"36.5","keyType":1,"userNumber":1},"muid":"","name":"channelPersonAlert","sn":"TD0TD204FC3T9751","timestamp":"","version":"v2.0.0"}
        # d_mac = {"name": "banner","muid": "0220e2b513e2-2d8f-4d0e-a591-bbba0afead50","sn": "MJ0FRY04E318Z276",
        #     "data": {"bannerId":259,"type":2,"url":"https://bsgoalsmartcloud.oss-cn-shenzhen.aliyuncs.com/AccessControl/20241205/20241205133348_ex1y.MP4","serialNumber":2},"operator": "13068732224","version":"v2.0.0_1","timestamp":""}

        # d_mac = {"name": "delBanner","muid": "","sn": "MJ0FRY04E318Z276","data": {"bannerId":258},"operator": "13068732224","version":"v2.0.0_1","timestamp":"1673234090000"}


    d_mac['muid'] = str(uuid.uuid1())
    d_mac['sign'] = md5sign(d_mac)
    print(json.dumps(d_mac,ensure_ascii=False))
    # d_rtc['muid'] = str(uuid.uuid1())
    # d_rtc['sign'] = md5sign(d_rtc)
    # print(json.dumps(d_rtc, ensure_ascii=False))
    # Mqttpub("120.77.29.140","cloud/MJ0FRY04FEF4H8MP",).clicent_main(json.dumps(d_mac,ensure_ascii=False,separators=(',',':')),"test","Tt4@0#kA8")
    # Mqttpub("120.77.29.140","cloud/TD0TD204FAD3CPMG",).clicent_main(json.dumps(d_mac,ensure_ascii=False,separators=(',',':')),"test","Tt4@0#kA8")
    # Mqttpub("39.108.135.181","cloud/TD0TD204EE2EAWK6",).clicent_main(json.dumps(d_mac,ensure_ascii=False,separators=(',',':')),"test","test#12")
    # Mqttpub("192.168.3.86","cloud/TD0JY104F6AHMKNF",).clicent_main(json.dumps(d_mac,ensure_ascii=False,separators=(',',':')),"test2","test2")
    Mqttpub("192.168.110.19","cloud/TD0TD204FC3T9751",).clicent_main(json.dumps(d_mac,ensure_ascii=False,separators=(',',':')),"test","Tt4@0#kA8")
    # Mqttpub("39.108.135.181","deTD0TD204ECBXEM0Qv/rtc/DJ0GLJ04D0D7R3EW",).clicent_main(json.dumps(d_mac,ensure_ascii=False,separators=(',',':')),"test","test#12")
    # time.sleep(30)