# -*- coding: UTF-8 -*-
import json,uuid
import time
import  hashlib,requests
import paho.mqtt.client as mqtt
def md5sign(value):
    timestamp = str(int((time.time()) * 1000-1000*60*4))
    wd = hashlib.md5()
    value['timestamp']=timestamp
    value=(dict(sorted(value.items(),key=lambda x: x[0])))#按key排序
    # data=(dict(sorted(value['data'].items(),key=lambda x: x[0])))
    # value['data']=data
    value=json.dumps(value,ensure_ascii=False, separators=(',',':'))
    wd.update(value.encode(encoding="utf-8"))
    sign = wd.hexdigest()
    return sign
def on_connect(self,client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))
if __name__ == '__main__':
    #登录上传信息
    # data={"name":"chargingLogin","muid":"0220e2b513e2-2d8f-4d0e-a591-bbba0afead53","sn":"CD0CCS04CF6BSP98","data":{"deviceUid":"02160030","pileType":1,"manufacturer":"test12","ratedPower":7000,"gunCount":2,"billingRuleId":1,"billingRuleVersion":"0","operatorCode":"0","password":"000000","devSoftVersion":"DC_2.0.1","devVersion":"PWD_OO_2020","protocolVersion":"2.0","extend":{}},"version":"v2.0.0_1","timestamp":""}
    #上传设备告警
    # data={"name":"chargingAlarm","muid":"0220e2b513e2-2d8f-4d0e-a591-bbba0afead50","sn":"CD0CCS064DB2FD2C","data":{"manufacturer":"test","deviceUid":"02160006","gunNo":1,"alarmTime":"202306281055","alarmStatus":1,"alarmValue":100.00,"extend":{}},"version":"v2.0.0_0","timestamp":"1673234090000"}
    #设备上传日志记录
    # data={"name":"chargingLog","muid":"0220e2b513e2-2d8f-4d0e-a591-bbba0afead50","sn":"CD0CCS064DB2FD2C","data":{"manufacturer":"test","deviceUid":"02160006","appVersion":"v1.0.0","log":"测试日志上传","time":"2023-01-12 12:12:12","extend":{}},"version":"v2.0.0_0","timestamp":"1673234090000"}
    #设备请求平台获取二维码内容URL
    # data={"name":"chargingQrCode","muid":"0220e2b513e2-2d8f-4d0e-a591-bbba0afead50","sn":"CD0CCS064DB2FD2C","data":{"manufacturer":"test","deviceUid":"02160006","gunNo":2},"version":"v2.0.0_1","timestamp":"1673234090000"}
    #设备上传心跳
    # data={"name":"chargingHeartbeat","muid":"0220e2b513e2-2d8f-4d0e-a591-bbba0afead50","sn":"CD0CCS04CF6BSP98","data":{"manufacturer":"test","deviceUid":"02160001","gunCount":2,"gunArray":[{"gunNo":1,"gunStatus":1},{"gunNo":2,"gunStatus":0}]},"version":"v2.0.0_1","timestamp":"1673234090000"}
    #充电记录上传
    # data={"name":"chargingRecord","muid":"0220e2b513e2-2d8f-4d0e-a591-bbba0afead50","sn":"CD0CCS064DB2FD2C","data":{"manufacturer":"test","deviceUid":"02160006","gunNo":2,"orderNo":"0216000612308251413481377","changingType":1,"customerNo":"000001","carVin":"000001","startChargingSoc":20,"stopChargingSoc":20,"stopReason":"充满停止","startTime":"2023-08-18 08:34:00","stopTime":time.strftime("%Y-%m-%d %H:%M:%S"),"startElectricMeter":100,"stopElectricMeter":100,"totalElectricity":100,"sharpElectricity":100,"peakElectricity":100,"normalElectricity":100,"valleyElectricity":100,"chargingAmount":0,"serviceFeeAmount":1,"reservationAmount":10,"parkingAmount":0,"electricityArray":[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],"billingRuleId":10,"billingRuleVersion":"1"},"version":"v2.0.3_1","timestamp":"1673234090000"}
    # 设备上传充电进度数据
    data={"name":"chargingProgress","muid":"0220e2b513e2-2d8f-4d0e-a591-bbba0afead50","sn":"CD0CCS04CF6BSP98","data":{"manufacturer":"test","deviceUid":"02160006","gunNo":2,"orderNo":"1702282742106326","chargingType":1,"customerNo":"000001","carVin":"000001","startTime":"2023-12-11 16:01:00","stopTime":time.strftime("%Y-%m-%d %H:%M:%S"),"totalElectricity":2,"sharpElectricity":100,"peakElectricity":100,"normalElectricity":100,"valleyElectricity":100,"chargingAmount":1,"serviceFeeAmount":2,"reservationAmount":4,"parkingAmount":0,"temperature":100,"gunTemperature":100,"inputVoltage":100,"inputCurrent":100,"outputVoltage":20000,"outputCurrent":1014,"voltageDemand":100,"currentDemand":100,"aPhaseVoltage":100,"bPhaseVoltage":100,"cPhaseVoltage":100,"aPhaseCurrent":100,"bPhaseCurrent":100,"cPhaseCurrent":100},"version":"v2.0.2_1","timestamp":"1673234090000"}
    #设备查询用户余额
    # data={"name":"chargingBalance","muid":"0220e2b513e2-2d8f-4d0e-a591-bbba0afead50","sn":"CD0CCS064DB2FD2C","data":{"manufacturer":"test","deviceUid":"02160006","orderNo":"0216000622308180921161478","chargingType":1,"customerNo":"000001"},"version":"v2.0.2_1","timestamp":"1673234090000"}
    #设备上传动态参数
    # data={"name":"chargingConfigInfo","muid":"0220e2b513e2-2d8f-4d0e-a591-bbba0afead50","sn":"CD0CCS064DB2FD2C","data":{"manufacturer":"test","deviceUid":"02160006","coordinate":1,"longitude":"","latitude":"","networkType":3,"operatorCode":"MCC","signalStrength":133,"iccid":""},"version":"v2.0.0_1","timestamp":"1673234090000"}
    # 设备上传BMS参数
    # data={"name":"chargingBMS","muid":"0220e2b513e2-2d8f-4d0e-a591-bbba0afead50","sn":"CD0CCS064DB2FD2C","data":{"manufacturer":"test","deviceUid":"02160006","gunNo":2,"orderNo":"0216000622308180921161478","bmsVersion":"1","bmsType":1,"totalEnergy":10000,"ratedCapacity":10000,"ratedTotalVoltage":10000,"batteryManufacturer":"","dateOfBattery":"2023-08-18","chargingCycles":100,"maxCurrent":5000,"maxVoltage":10000,"maxTemperature":8000,"singleMaxVoltage":5000,"batteryMaxVoltage":10000,"batteryMinVoltage":100},"version":"v2.0.2_1","timestamp":"1673234090000"}


    data['muid'] = str(uuid.uuid1())
    data['sign'] = md5sign(data)
    print(data)
    client = mqtt.Client()
    client.on_connect = on_connect
    client.username_pw_set("test", "test1")
    # client.connect("192.168.110.19", 1883, 600)  # 连接mqtt服务 600为keepalive的时间间隔
    client.connect("120.77.29.140", 1883, 600)  # 连接mqtt服务 600为keepalive的时间间隔
    client.publish("cloud/"+data['sn'], json.dumps(data,ensure_ascii=False,separators=(',',':')))##登录上传信息
    # client.publish("cloud/log/"+data['sn'], json.dumps(data,ensure_ascii=False,separators=(',',':')))#