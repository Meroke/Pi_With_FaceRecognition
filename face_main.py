# 人脸识别模块
import face_recognition
# opencv-python
import cv2
import numpy as np


# 多线程
import threading
from time import sleep
# 树莓派模块
import re
from multiprocessing import Process
import os
import pymysql
import sys
sys.path.append(r'/home/pi/code/CompleteProgramFaceRecogntion/CompleteProgramFaceRecogntion')
import databaseSql as dsql
import PhotoUpAndRec as PUR
import SerialArduino as SA
import PahoMqtt as PM
# 功能说明：
# 1.先进行人脸识别，识别到陌生人，拍照上传云端
# 2.再接收手机端指令，接收到yes指令自动开门

# recv_name 作为全局变量，需要接收mqtt传入的值,传进rec(),Recv_name是局部变量
names = globals()
global temp_face_encoding
recv_num = 0  # 接受图片的序号，作为云端图片的名称


# nikesong unknown test person
nike_image = face_recognition.load_image_file("03.jpg")
nike_face_encoding = face_recognition.face_encodings(nike_image)[0]

unknown_face_encodings = [
    nike_face_encoding
]

unknown_face_names = [
    "Nike"
]


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


# def addFamilyMember(img_address,number):# 将传进来照片预处理后传入SQL
# 
#     dsql.load_image(img_address, number,'family')
#     dsql.get_append()
    # family_image = face_recognition.load_image_file(img_address)
    # new_face_encoding = face_recognition.face_encodings(family_image)[0]
    # known_face_names.append("family")
    # known_face_names.append("family")
    # known_face_encodings.append(new_face_encoding)


# Initialize some variables
face_locations = []
face_encodings = []
face_names = []

#
i = 0
j = 0

temp_face_encoding = globals()


def cameraInit():
    t2 = threading.Thread(target=PM.recv_word_device02, args=())
    process_this_frame = True
    # 人脸识别部分
    video_capture = cv2.VideoCapture(0)
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
            global i
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
                    SA.ser.write(b's')
                    print('known!')

                elif unknown_matches[unknown_best_match_index]:
                    name = unknown_face_names[unknown_best_match_index]
                    print('unkown!')

                else:
                    # photo_address = 'E:/_TempPhoto/' + str(i) + '.jpg'
                    photo_address = '/home/pi/code/pic/' + str(i) + '.jpg'

                    cv2.imwrite(photo_address, frame)  # 识别到unkown时拍照
                    # t3 = threading.Thread(target=send_word_device01, args=())
                    # t3.start()
                    # t3.join()
                    # temp_face_encoding = face_encoding # 配合rec()
                    # 通过多线程使得流程不会停滞，持续的进行下去。本想加速过程，但是并没有大效果，推测是上传图片的速度比较慢
                    t1 = threading.Thread(target=PUR.send_photo, args=(photo_address,))
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
            # cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    t2.join()  # 监听结束

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

