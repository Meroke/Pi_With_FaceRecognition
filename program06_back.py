# 人脸识别模块
import face_recognition
# opencv-python
import cv2
import numpy as np
# 导入BOS相关模块
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.services.bos.bos_client import BosClient
# mqtt通信
import paho.mqtt.client as mqtt
import json
# 多线程
import threading
from time import sleep
# 树莓派模块
import RPi.GPIO as GPIO
import re
import sys
from multiprocessing import Process
import os
import serial
import pymysql
import databaseSql as dsql

# 功能说明：
# 1.先进行人脸识别，识别到陌生人，拍照上传云端
# 2.再接收手机端指令，接收到yes指令自动开门

# recv_name 作为全局变量，需要接收mqtt传入的值,传进rec(),Recv_name是局部变量
names = globals()
global temp_face_encoding
ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
recv_num = 0  # 接受图片的序号，作为云端图片的名称


# 人脸识别部分
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
obama_image = face_recognition.load_image_file("obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
biden_image = face_recognition.load_image_file("02.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# nikesong unknown test person
nike_image = face_recognition.load_image_file("03.jpg")
nike_face_encoding = face_recognition.face_encodings(nike_image)[0]

# Create arrays of known face encodings and their names
dsql.known_face_encodings.append(obama_face_encoding)
dsql.known_face_encodings.append(biden_face_encoding)
dsql.known_face_names.append("Barack Obama")
dsql.known_face_names.append("zhang")


unknown_face_encodings = [
    nike_face_encoding
]

unknown_face_names = [
    "Nike"
]







# 发送图片到云端
class Bd_Storage(object):
    def __init__(self):
        # 设置BosClient的Host，Access Key ID和Secret Access Key
        self.bos_host = "bj.bcebos.com"  # 地址可以改，参考百度的python SDK文档
        self.access_key_id = "f882a84d6f2b4067bb071024347dbc17"
        self.secret_access_key = "2d9fb65a6bbc4a7bac7828850e3ca2ea"
        self.back_name = "bbbucket"

    def up_image(self, key_name, file):
        config = BceClientConfiguration(credentials=
                                        BceCredentials(self.access_key_id, self.secret_access_key),
                                        endpoint=self.bos_host)
        client = BosClient(config)

        key_name = key_name
        try:
            res = client.put_object_from_string(bucket=self.back_name, key=key_name, data=file)
        except Exception as e:
            return None
        else:
            #result = res.__dict__
            #if result['metadata']:
                #url = 'https://' + self.back_name + '.bj.bcebos.com' + key_name
                #print(url)
                #t3 = threading.Thread(target=send_word_device01, args=(url,))
                #t3.start()
                #t3.join()
               # send_word_device01(url)
            print('put success!')



def send_photo(photo_address):
    with open(photo_address, 'rb') as f:
        s = f.read()
        bd = Bd_Storage()
        bd.up_image(photo_address, s)


def add_unknown_person(img_encoding):
    names['person' + str(i - 1)] = img_encoding  # 批量命名person 1 2 3…… 变量，将人脸编码赋值给变量
    exec('unknown_face_encodings.append(person{})'.format(i - 1))
    unknown_face_names.append('Unknow{}'.format(i - 1))


# # 接受人名信息，添加熟人
# def rec(Recv_name, img_encoding):
#     # while True:
#     # try:
#     #     new_name = phone.recv(1024)
#     # except BlockingIOError as e:
#     #     new_name = None
#     if Recv_name == "unknown":
#         print("this is unknown")
#         # pass
#     else:
#         print("loading people: " + Recv_name)
#         # NEW_name = Recv_name
#         print(Recv_name)
#         unknown_face_encodings.pop()
#         unknown_face_names.pop()
#         known_face_encodings.append(img_encoding)
#         known_face_names.append(Recv_name)


def setServoAngle(servo, angle):
    pwm = GPIO.PWM(servo, 50)
    pwm.start(8)# 设置占空比
    dutyCycle = angle / 18. + 3.
    pwm.ChangeDutyCycle(dutyCycle) # 设置更新频率
    sleep(0.5)
    pwm.stop()

def servo():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    servo = 22 # int(sys.argv[1])
    GPIO.setup(servo, GPIO.OUT)
    setServoAngle(servo, 90)
    sleep(5)

    setServoAngle(servo, 0)
    GPIO.cleanup()

def servo02():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    servo = 27 # int(sys.argv[1])
    GPIO.setup(servo, GPIO.OUT)
    setServoAngle(servo, 38)
    sleep(5)

    setServoAngle(servo, 128)
    GPIO.cleanup()


def openDoor():
    t1 = threading.Thread(target=servo, args=())
    t2 = threading.Thread(target=servo02, args=())

    # 开启新线程
    t1.start()
    t2.start()
    t1.join()
    t2.join()




def addFamilyMember(img_address,number):# 将传进来照片预处理后传入SQL

    dsql.load_image(img_address, number,'family')
    dsql.get_append()
    # family_image = face_recognition.load_image_file(img_address)
    # new_face_encoding = face_recognition.face_encodings(family_image)[0]
    # known_face_names.append("family")
    # known_face_names.append("family")
    # known_face_encodings.append(new_face_encoding)



class Recv_Bd_Storage(object):
    def __init__(self):
        # 设置BosClient的Host，Access Key ID和Secret Access Key
        self.bos_host = "bj.bcebos.com"  # 地址可以改，参考百度的python SDK文档
        self.access_key_id = "f882a84d6f2b4067bb071024347dbc17"
        self.secret_access_key = "2d9fb65a6bbc4a7bac7828850e3ca2ea"
        self.back_name = "bbbucket"

    def get_object(self, object_key, download_file):
        config = BceClientConfiguration(credentials=
                                        BceCredentials(self.access_key_id, self.secret_access_key),
                                        endpoint=self.bos_host)
        bos_client = BosClient(config)

        # 直接下载图片到本地
        bos_client.get_object_to_file('bbbucket', object_key, download_file)
        print("recv succ")


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
    # if is_space(str(msg.payload)): # 通过is_space（）函数判断传入的信息是否包含空格
    #     n0 = str(datas).split()[0]  # 接收的数据格式必须为"yes" + " " + "name",希望能在手机端上进行是否开门的判定
    #     n1 = str(datas).split()[1]
    #     print(n0)
    #     print(n1)
    #     if n0 == "yes":  # 1.识别通过，开门
    #         # openDoor()
    #         ser.write(b's')
    #         rec(n1, temp_face_encoding)
    #     else:
    #         pass
    if datas == 0:  # 2.认识的人，只开门，下次进入仍需主人同意
        # openDoor()
        ser.write(b's')
    elif datas == 3:
        # downloadImg()
        # 如何确定云端图片地址？如何确定
        print("number is coming :")
        number = dsql.last_num() + 1

        print(number)
        object_key = '/home/pi/code/recv_pic/{}.jpg'.format(number)  # 云端地址
        download_file = '/home/pi/code/recv_pic/{}.jpg'.format(number)  # 树莓派本地地址
        bd = Recv_Bd_Storage()
        bd.get_object(object_key, download_file)
        addFamilyMember(download_file,number)
    else:  # 3.不允许进入
        print("Please leave")
    # # 接收人名，添加熟人
    # global recv_name
    # recv_name = datas


def on_publish(mqttc, obj, mid):
    print("publish:" + "mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


def on_disconnect(mqttc, obj, rc):
    print("unsuccess connect %s" % rc)


def send_word_device01():
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
    sleep(1)
    # bmqttc.subscribe(topic, 0)
    #mqttc.loop_forever()


def recv_word_device02():
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




# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
#
i = 0
j = 0

temp_face_encoding = globals()

t2 = threading.Thread(target=recv_word_device02, args=())


# 开启新线程
t2.start()  # 开始监听信息
dsql.get_info()  # 获取数据库人脸数据

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        j = i
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(dsql.known_face_encodings, face_encoding, 0.45)
            unknown_matches = face_recognition.compare_faces(unknown_face_encodings, face_encoding, 0.6)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(dsql.known_face_encodings, face_encoding)
            unknown_face_distances = face_recognition.face_distance(unknown_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            unknown_best_match_index = np.argmin(unknown_face_distances)
            if matches[best_match_index]:
                name = dsql.known_face_names[best_match_index]
                # openDoor()
                ser.write(b's')

            elif unknown_matches[unknown_best_match_index]:
                name = unknown_face_names[unknown_best_match_index]

            else:
                # photo_address = 'E:/_TempPhoto/' + str(i) + '.jpg'
                photo_address = '/home/pi/code/pic/' + str(i) + '.jpg'

                cv2.imwrite(photo_address, frame)  # 识别到unkown时拍照
                # t3 = threading.Thread(target=send_word_device01, args=())
                # t3.start()
                # t3.join()
                # temp_face_encoding = face_encoding # 配合rec()
                # 通过多线程使得流程不会停滞，持续的进行下去。本想加速过程，但是并没有大效果，推测是上传图片的速度比较慢
                t1 = threading.Thread(target=send_photo, args=(photo_address,))
                t1.start()
                t1.join()
                os.remove(photo_address)
                i += 1
            # 传回未知人姓名，添加

            # rec(recv_name, temp_face_encoding)

            # trd = threading.Thread(target=rec, args=(phone, face_encoding))
            # trd.start()
            face_names.append(name)

    process_this_frame = not process_this_frame
    if i > j:
        add_unknown_person(face_encoding)

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

t2.join()  # 监听结束

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

