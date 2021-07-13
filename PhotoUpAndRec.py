# 导入BOS相关模块
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.services.bos.bos_client import BosClient
# 发送图片到云端
class Bd_Storage(object):
    def __init__(self):
        # 设置BosClient的Host，Access Key ID和Secret Access Key
        self.bos_host = "bj.bcebos.com"  # 地址可以改，参考百度的python SDK文档
        self.access_key_id = "f882a84d6f2b4067bb071024347dbc17"
        self.secret_access_key = "2d9fb65a6bbc4a7bac7828850e3ca2ea"
        self.back_name = "bbbucket"

    # 上传本地图片到云端地址
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


# 发送图片，创建发送用的类对象
def send_photo(photo_address):
    with open(photo_address, 'rb') as f:
        s = f.read()
        bd = Bd_Storage()
        bd.up_image(photo_address, s)

# 用于接收图片
class Recv_Bd_Storage(object):
    def __init__(self):
        # 设置BosClient的Host，Access Key ID和Secret Access Key
        self.bos_host = "bj.bcebos.com"  # 地址可以改，参考百度的python SDK文档
        self.access_key_id = "f882a84d6f2b4067bb071024347dbc17"
        self.secret_access_key = "2d9fb65a6bbc4a7bac7828850e3ca2ea"
        self.back_name = "bbbucket"

    # 获取云端图片到本地地址
    def get_object(self, object_key, download_file):
        config = BceClientConfiguration(credentials=
                                        BceCredentials(self.access_key_id, self.secret_access_key),
                                        endpoint=self.bos_host)
        bos_client = BosClient(config)

        # 直接下载图片到本地
        bos_client.get_object_to_file('bbbucket', object_key, download_file)
        print("recv succ")