import base64
import json
import sys
import time
from random import choice

import requests
from Crypto.Cipher import AES
from loguru import logger


class FileAES:
    def __init__(self, key):
        self.key = key  # 将密钥转换为字符型数据
        self.mode = AES.MODE_ECB  # 操作模式选择ECB

    def encrypt(self, text):
        """加密函数"""
        file_aes = AES.new(self.key, self.mode)  # 创建AES加密对象
        text = text.encode('utf-8')  # 明文必须编码成字节流数据，即数据类型为bytes
        while len(text) % 16 != 0:  # 对字节型数据进行长度判断
            text += b'\r'  # 如果字节型数据长度不是16倍整数就进行补充
        en_text = file_aes.encrypt(text)  # 明文进行加密，返回加密后的字节流数据
        # 将加密后得到的字节流数据进行base64编码并再转换为unicode类型
        return str(base64.b64encode(en_text), encoding='utf-8')

    def decrypt(self, text):
        """解密函数"""
        file_aes = AES.new(self.key, self.mode)
        text = bytes(text, encoding='utf-8')  # 将密文转换为bytes，此时的密文还是由basen64编码过的
        text = base64.b64decode(text)  # 对密文再进行base64解码
        de_text = file_aes.decrypt(text)  # 密文进行解密，返回明文的bytes
        # 将解密后得到的bytes型数据转换为str型，并去除末尾的填充
        return str(de_text, encoding='utf-8').strip()


class Luoli:
    def __init__(self, ip, deviceId, token):
        self.deviceId = deviceId
        self.token = token
        self.ip = ip
        self.data = '{"deviceId":"' + deviceId + '","token":"{' + token + '"}'
        self.aes = FileAES(b"c31b32364ce19c13")
        if token == "null":
            self.token = "null_null"
        if self.token.find("null") != -1:
            self.login()

    def register(self):
        # deviceId = "".join([choice("0123456789abcdef") for _ in range(16)])
        data = {
            "data": {
                "channel_code": "",
                "clipboard_text": "",
                "device_id": self.deviceId,
                "device_info": '{"product":"beyond1qlteue","display":"beyond1qlteue-user 9 PPR1.190810.011 900211026 release-keys","version.sdkInt":"28","isPhysicalDevice":"true","manufacturer":"samsung","version.codename":"REL","bootloader":"b1c1-0.1-4948814","host":"ubuntu","model":"SM-G973N","id":"PPR1.190810.011","version.release":"9","brand":"samsung","device":"beyond1q","board":"universal8895","hardware":"qcom"}',
            },
            "deviceId": self.deviceId,
            "token": self.token
        }
        res = self.getInfo("/system/info",
                           json.dumps(data, separators=(',', ':')))
        # res = res[:res.rfind("}") + 1]
        # res = json.loads(res)
        if res.get("status") == "y":
            '''"token": {
                        "token": "494868804d24d34c69273980a16d9429",
                        "user_id": "11630391",
                        "username": "HMA3K",
                        "expired_at": "18000"
                }'''
            data = res.get("data").get("token")
        else:
            print(res.get("error"))

    def login(self):
        login_data = {
            "data": {
                "device_id": self.deviceId
            },
            "deviceId": self.deviceId,
            "token": self.token
        }
        # 更新用户凭证
        sign_data = self.getInfo("/user/login", json.dumps(login_data))
        # 删去末尾不知道哪里来的四个\x04
        # sign_data = json.loads(sign_data.replace("\x04", ""))
        # print(sign_data)
        if sign_data.get("status", "") == "y":
            self.token = sign_data.get("data").get(
                "token") + "_" + sign_data.get("data").get("user_id")
            self.data = '{"deviceId":"' + self.deviceId + \
                        '","token":"' + self.token + '"}'
            print("更新成功", self.data)
        else:
            print("更新失败", sign_data)

    def info(self):
        return self.getInfo("/user/info", self.data)

    def sign(self):
        # 获取签到信息
        sign_data = self.getInfo("/user/sign", self.data)
        if sign_data.get("status") == "y":
            thisdata = sign_data.get("data")
            print("总金币数", thisdata.get("user").get("points"))
            if thisdata.get("today_has_sign") == "y":
                print("今日已签到")
            else:
                print("此次签到可获得", thisdata.get("sign_points"), "金币")
                """
                {"status": "n",  "error": "授权过期!",  "errorCode": 2002}
                {'status': 'n', 'error': '已经签到过了!', 'errorCode': 2001}
                {"status":"y","data":null,"time":"2022-07-16 00:00:43"}
                """
                dosign_data = self.getInfo("/user/doSign", self.data)
                if dosign_data.get("status") == "y":
                    print("签到成功，获得", thisdata.get("sign_points"), "金币")
                else:
                    print(dosign_data.get("error"))

    def bindParent(self, code: str = "HSMY8"):
        # 绑定邀请码
        bind_data = {
            "data": {
                "code": code
            },
            "deviceId": self.deviceId,
            "token": self.token
        }
        bind_data = json.dumps(bind_data, separators=(',', ':')) + "\x05" * 5
        share_data = self.getInfo("/user/bindParent", bind_data)
        # share_data = json.loads(share_data)
        if share_data.get("status") == "y":
            print("绑定成功")
            return True
        else:
            print("绑定失败")
            return False

    def movie_home(self):
        # 获取视频列表
        movie_data = self.getInfo("/movie/home", self.data)
        # print(sys._getframe().f_lineno, movie_data)
        # movie_data = json.loads(movie_data)
        if movie_data.get("status") == "y":
            print(movie_data.get("data"))
        else:
            print("获取视频列表失败")

    def movie_detail(self, id: str = "44250"):
        '''{"data":{"id":"57246"},"deviceId":"b9b6f3007dbe367d","token":"3598452c1a22dcecc194511f743df678_11630391"}'''
        # 获取视频信息
        movie_data = {
            "data": {
                "id": id
            },
            "deviceId": self.deviceId,
            "token": self.token
        }
        movie_data = json.dumps(movie_data, separators=(',', ':')) + "\x07" * 7
        detail_data = self.getInfo("/movie/detail", movie_data)
        return detail_data

    def getInfo(self, url, load_data):
        # 加密之后用base64编码
        loaddata = base64.b64decode(self.aes.encrypt(load_data))
        headers = {
            "deviceType": "android",
            "version": "2.1",
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Content-Type": "application/octet-stream",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android 2.1; en-us; Nexus One Build/ERD62) AppleDart/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17"
        }
        res = requests.post(self.ip + url, data=loaddata, headers=headers)
        # print(res.text)
        if res.text.find("安全性错误") != -1:
            self.login()
            data = json.loads(load_data)
            if data.get("token"):
                data["token"] = self.token
                load_data = json.dumps(data, separators=(',', ':'))
            return self.getInfo(url, load_data)
        # elif url.find("login") == -1:
        #     print(sys._getframe().f_lineno, ''.join(['%02x' % b for b in res.content]))
        try:
            # base64编码后 aes/ecb/pkcs5解码
            data = self.aes.decrypt(
                str(base64.b64encode(res.content), "utf-8"))
            try:
                # 如果可以直接编码json格式就返回
                return json.loads(data)
            except Exception:
                # 判断最后一个是不是}，不是就去除
                if data[-1] != "}":
                    data = data[:data.rfind("}") + 1]
                    return json.loads(data)
        except Exception:
            try:
                print(1, sys._getframe().f_lineno,)
                return res.text
            except Exception as e:
                logger.exception(e)
                return "{}"


'''link": [
            {
                "id": "2",
                "name": "VIP线路",
                "is_vip": "y",
                "link": "https://iossxbv.h17tao.com/media/m3u8/28e/28e8d743c934f4ba-18422/index.m3u8?_v=20210521&sign=1658064263-dcdcf1a1d03e09f1905de02176678bad-0-a504e9dc1be8cb28c1bcb41bb8723543"
            },
            {
                "id": "1",
                "name": "备用线路",
                "is_vip": "n",
                "link": "/media/m3u8/28e/28e8d743c934f4ba-18422/index.m3u8?_v=&sign=1658064263-dcdcf1a1d03e09f1905de02176678bad-0-a504e9dc1be8cb28c1bcb41bb8723543"
            },
            {
                "id": "1",
                "name": "普通线路",
                "is_vip": "n",
                "link": "https://iossxbv.h17tao.com/media/m3u8/28e/28e8d743c934f4ba-18422/index.m3u8?_v=20210521&sign=1658064263-dcdcf1a1d03e09f1905de02176678bad-0-a504e9dc1be8cb28c1bcb41bb8723543"
            }
        ],'''
if __name__ == '__main__':
    deviceId = "".join([choice("0123456789abcdef") for _ in range(16)])
    ip = "http://api-91cy.kffggnz.com/cxapi"  # 服务器ip
    luoli = Luoli(ip, deviceId, "null_null")
    # luoli.register()
    luoli.bindParent("8LFS9")
