# mqtt通信
import paho.mqtt.client as mqtt
import json
import SerialArduino as SA
import re
import time

import PhotoUpAndRec as PUR
import databaseSql as dsql


# 添加家庭成员
def addFamilyMember(img_address,number):  # 将传进来照片预处理后传入SQL
    dsql.load_image(img_address, number,'family')
    dsql.get_append()

# 连接成功时的信息
def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message01(mqttc, obj, msg):
    print("send:" + msg.topic + " " + str(msg.payload))
    datas = json.loads(msg.payload.decode('utf-8'))
    print(datas)

# 判断是否包含空格
def is_space(char):
    if re.search(u"\s", char):
        return True
    else:
        return False


# 1.判断指令，如果主人允许熟人进入，则开门并登录名字（熟人可自动开门，暂定，可删除）；
# 2.如果只是认识的人，只开门，不登陆，下次仍需主人同意；
# 3.其他人则不开门也不登陆。
def on_message02(mqttc, obj, msg):
    print("recv:" + msg.topic + " " + str(msg.payload))
    datas = json.loads(msg.payload.decode('utf-8'))
    print(datas)
    if datas == 0:  # 2.认识的人，只开门，下次进入仍需主人同意
        # openDoor()
        SA.ser.write(b's')
    elif datas == '3':
        # downloadImg()
        # 如何确定云端图片地址？
        print("number is coming :")
        number = dsql.last_num() + 1

        print(number)
        object_key = '/home/pi/code/recv_pic/{}.jpg'.format(number)  # 云端地址
        download_file = '/home/pi/code/recv_pic/{}.jpg'.format(number)  # 树莓派本地地址
        bd = PUR.Recv_Bd_Storage()
        bd.get_object(object_key, download_file)
        addFamilyMember(download_file,number)
    else:  # 3.不允许进入
        print("Please leave")


# 发送文字时的回调函数
def on_publish(mqttc, obj, mid):
    print("publish:" + "mid: " + str(mid))

# 接收文字时的回调函数
def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# 日志信息
def on_log(mqttc, obj, level, string):
    print(string)

# 断连时的信息
def on_disconnect(mqttc, obj, rc):
    print("unsuccess connect %s" % rc)


def send_word_device01():  # 发送文字消息
    HOST = 'ahekjhz.iot.gz.baidubce.com'
    PORT = 1883
    client_id = 'device1'
    username = 'thingidp@ahekjhz|device1|0|MD5'
    password = '899e2ee82299559b2d6f04497cfc42fb'
    topic = '$iot/device1/user/fortest'  # 能接受和发送
    mqttc = mqtt.Client(client_id)
    mqttc.username_pw_set(username, password)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message01 # 调用的仍然是on_message02,会和device02发生争抢
    mqttc.on_publish = on_publish
    # mqttc.on_subscribe = on_subscribe
    mqttc.on_disconnect = on_disconnect
    mqttc.connect(HOST, PORT, 600)
    global i
    photo_address = "/home/pi/code/pic/" + str(i) + ".jpg"
    #print("send:" + urls)
    payload = json.dumps(photo_address)
    mqttc.publish(topic, payload, 0)
    print("send message")
    time.sleep(1)


def recv_word_device02():  # 接收文字消息
    HOST = 'ahekjhz.iot.gz.baidubce.com'
    PORT = 1883
    client_id = 'server-test'
    username = 'thingidp@ahekjhz|server-test|0|MD5'
    password = 'c556f3ba7effc76db8225cfcb3e2cad1'
    topic = '$iot/server-test/user/fortest'  # 能接受和发送
    mqttc02 = mqtt.Client(client_id)
    mqttc02.username_pw_set(username, password)
    mqttc02.on_connect = on_connect
    mqttc02.on_message = on_message02
    # mqttc02.on_publish = on_publish
    mqttc02.on_subscribe = on_subscribe
    mqttc02.on_disconnect = on_disconnect
    mqttc02.connect(HOST, PORT, 600)
    mqttc02.subscribe(topic, 0)
    mqttc02.loop_forever()