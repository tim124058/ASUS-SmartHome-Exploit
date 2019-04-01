import xml.etree.ElementTree as ET

device_type = {
    10:"DoorLock",
    81: "OnOffDevice",
    770: "T_H_Sensor",
    1026: {13:"MotionSensor",21:"WindowSensor",32777:"SmokeSensor"},
    1027:"Alarm"
}

# zbclusterid
device_ctrl = {
    "DoorLock": 257,
    "OnOffDevice": 6,
    "Alarm":1282,
    # "Notifier":0,
    # "Timedevice":0,
    "unknown":6,          # default => OnOffDevice
}

#zbclusterid, zbattrid
device_value = {
    "DoorLock": [257,0],
    "OnOffDevice": [6,0],
    "T_H_Sensor":[[1026,0],[1029,0]],
    "MotionSensor":[1280,2],
    "SmokeSensor":[1280,2],
    "WindowSensor":[1280,2],
    "Alarm":[1280,2],
    "unknown":[6,0],          # default => OnOffDevice
}

def getDeviceType(xml):
    zbdeviceid = xml.find("zbinfo/zbdeviceid")
    if zbdeviceid != None:
        zbdeviceid = int(zbdeviceid.text)
        if zbdeviceid != 1026:
            return device_type.get(zbdeviceid, "unknown")
        else:
            zbattrvalue = xml.find('zbinfo/zbclusterinfo[zbclusterid="1280"]/zbattributeinfo[zbattrid="1"]/zbattrvalue')
            if zbattrvalue != None:
                zbattrvalue = int(zbattrvalue.text)
                return device_type[1026].get(zbattrvalue,"unknown")
    return "unknown"

def getDeviceValue(xml, type):
    if type == "unknown": return "unknown"
    if type == "T_H_Sensor":
        temp = xml.find('zbinfo/zbclusterinfo[zbclusterid="1026"]/zbattributeinfo[zbattrid="0"]/zbattrvalue')
        if temp != None:
            temp = int(temp.text)/100
        humidity = xml.find('zbinfo/zbclusterinfo[zbclusterid="1029"]/zbattributeinfo[zbattrid="0"]/zbattrvalue')
        if humidity != None:
            humidity = int(humidity.text)/100
        return "T: %s ,H: %s" % (temp, humidity)
    t = device_value.get(type,None)
    if t == None: return "unknown"
    value = xml.find('zbinfo/zbclusterinfo[zbclusterid="%s"]/zbattributeinfo[zbattrid="%s"]/zbattrvalue' % (t[0],t[1]))
    if value == None: return "ERROR"
    value = value.text
    if type == "DoorLock":
        if value == "1":
            value = "0(lock)"
        elif value == "2":
            value = "1(unlock)"
    elif type == "OnOffDevice":
        if value == "0":
            value += "(Off)"
        elif value == "1":
            value += "(On)"
    elif (type == "WindowSensor") or (type == "Alarm"):
        if int(value)&1 == 0:
            value += "(Close)"
        elif int(value)&1 == 1:
            value += "(Open)"

    return "value: %s" % value


def parseDeviceInfo(xml):
    info = {
        'deviceid':-1,
        'devicename':"",
        'type':"",
        'value':""
    }
    deviceid = xml.find("deviceid")
    if deviceid != None:
        info['deviceid'] = int(deviceid.text)

    devicename = xml.find("devicename")
    if devicename != None:
        info['devicename'] = devicename.text
    try:
        info['type'] = getDeviceType(xml)
        info['value'] = getDeviceValue(xml, info['type'])
    except Exception as e:
        pass
    return info
