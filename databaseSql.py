import cv2
import face_recognition
import pymysql
import numpy as np
from PIL import Image, ImageDraw, ImageFont
# mysql登录指令：
# MYSQL -u root -p
# 再输入密码：1234

# 人脸特征编码集合
known_face_encodings = []

# 人脸特征姓名集合
known_face_names = []

def get_append():
    # 创建数据库连接对象
    conn = pymysql.connect(
        # 数据库的IP地址
        host="localhost",
        # 数据库用户名称
        user="root",
        # 数据库用户密码
        password="1234",
        # 数据库名称
        db="face",
        # 数据库端口名称
        port=3306,
        # 数据库的编码方式 注意是utf8
        charset="utf8"
    )

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()

    # SQL查询语句
    sql = "SELECT id FROM known_face \
    ORDER BY id DESC \
    LIMIT 1"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        # 返回的结果集为元组
        name = results[2]
        # print(name)
        encoding = results[1]
        # print(encoding)
        sb = str(encoding, encoding="utf8")
        # print("name=%s,encoding=%s" % (name, encoding))
        # 将字符串转为numpy ndarray类型，即矩阵
        # 转换成一个list
        dlist = sb.strip(' ').split(',')
        # 将list中str转换为float
        dfloat = list(map(float, dlist))
        arr = np.array(dfloat)

        # 将从数据库获取出来的信息追加到集合中
        known_face_encodings.append(arr)
        print("get_append:")
        print(arr)
        known_face_names.append(name)
        print("get_append:")
        print(name)

    except Exception as e:
        print(e)

        # 关闭数据库连接
        conn.close()
    print("get_append OVER")

def get_info():
    # 创建数据库连接对象
    conn = pymysql.connect(
        # 数据库的IP地址
        host="localhost",
        # 数据库用户名称
        user="root",
        # 数据库用户密码
        password="1234",
        # 数据库名称
        db="face",
        # 数据库端口名称
        port=3306,
        # 数据库的编码方式 注意是utf8
        charset="utf8"
    )

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()

    # SQL查询语句
    sql = "select * from known_face" # 可以改进为直接查询人脸数据
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        # 返回的结果集为元组
        for row in results:
            name = row[0]  # 名字是第一位
            print(name)
            encoding = row[1]  # 编码是第二位
            print(encoding)
            sb = str(encoding, encoding="utf8")
            # print("name=%s,encoding=%s" % (name, encoding))
            # 将字符串转为numpy ndarray类型，即矩阵
            # 转换成一个list
            dlist = sb.strip(' ').split(',')
            # 将list中str转换为float
            dfloat = list(map(float, dlist))
            arr = np.array(dfloat)

            # 将从数据库获取出来的信息追加到集合中
            known_face_encodings.append(arr)
            known_face_names.append(name)

    except Exception as e:
        print(e)

        # 关闭数据库连接
        conn.close()
    print("get_info OVER")


def load_image(input_image, id, input_name):
    # 加载本地图像文件到一个numpy ndarray类型的对象上
    image = face_recognition.load_image_file(input_image)

    # 返回图像中每个面的128维人脸编码
    # 图像中可能存在多张人脸，取下标为0的人脸编码，表示识别出来的最清晰的人脸
    image_face_encoding = face_recognition.face_encodings(image)[0]

    # 将numpy array类型转化为列表
    encoding__array_list = image_face_encoding.tolist()

    # 将列表里的元素转化为字符串
    encoding_str_list = [str(i) for i in encoding__array_list]

    # 拼接列表里的字符串
    encoding_str = ','.join(encoding_str_list)

    # 被识别者姓名
    name = input_name

    # 将人脸特征编码存进数据库
    save_encoding(encoding_str,id, name)
    #print("load_image OVER")


# 人脸特征信息保存
def save_encoding(encoding_str, id_num,name):
    # 创建数据库连接对象
    conn = pymysql.connect(
        # 数据库的IP地址
        host="localhost",
        # 数据库用户名称
        user="root",
        # 数据库用户密码
        password="1234",
        # 数据库名称
        db="face",
        # 数据库端口名称
        port=3306,
        # 数据库的编码方式 注意是utf8
        charset="utf8"
    )

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()

    # SQL插入语句
    insert_sql = "insert into known_face(id,encoding,name) values(%s,%s,%s)"
    try:
        # 执行sql语句
        cursor.execute(insert_sql, (id_num, encoding_str,name))
        # 提交到数据库执行
        conn.commit()
        print("succ")
    except Exception as e:
        # 如果发生错误则回滚并打印错误信息
        conn.rollback()
        print(e)

    # 关闭游标
    cursor.close()
    # 关闭数据库连接
    conn.close()
    print("save_encoding OVER")

# 返回数据库内存储的最后一个ID，用于下载云端新图片。云端图片名称 和 数据库内的ID是对应的，都是数字
def last_num():
    conn = pymysql.connect(
        # 数据库的IP地址
        host="localhost",
        # 数据库用户名称
        user="root",
        # 数据库用户密码
        password="1234",
        # 数据库名称
        db="face",
        # 数据库端口名称
        port=3306,
        # 数据库的编码方式 注意是utf8
        charset="utf8"
    )

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()
    sql = "SELECT id FROM known_face\
                ORDER BY id DESC\
                LIMIT 1"
    cursor.execute(sql)
    result = cursor.fetchall()
    n = result[0][0]

    conn.close()
    return n
    print("last_num OVER")


n = last_num()
print(int(n))