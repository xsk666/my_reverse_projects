# %%
import string
import random
import json
from Crypto.Cipher import DES3
import base64
import requests


class EncryptDate:
    def __init__(self, key):
        self.key = key  # 初始化密钥
        self.iv = 'SK8bncVu'.encode()  # 偏移量
        self.length = DES3.block_size  # 初始化数据块大小
        self.des3 = DES3.new(self.key, DES3.MODE_CBC,
                             self.iv)  # 初始化AES,CBC模式的实例
        # 截断函数，去除填充的字符
        self.unpad = lambda date: date[0:-ord(date[-1])]

    def pad(self, text):
        """
        #填充函数，使被加密数据的字节码长度是block_size的整数倍
        """
        count = len(text.encode('utf-8'))
        add = self.length - (count % self.length)
        entext = text + (chr(add) * add)
        return entext

    def encrypt(self, encrData):  # 加密函数

        res = self.des3.encrypt(self.pad(encrData).encode("utf8"))
        msg = str(base64.b64encode(res), encoding="utf8")
        # msg =  res.hex()
        return msg

    def decrypt(self, decrData):  # 解密函数
        res = base64.decodebytes(decrData.encode("utf8"))
        # res = bytes.fromhex(decrData)
        msg = self.des3.decrypt(res).decode("utf8")
        return self.unpad(msg)


def bindcode(code):
    reqUrl = "https://lb.zhihu66.com/UserShareAction.aspx"
    head = {
        "Accept-Language": "zh-CN,zh;q=0.8",
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-cn; SM-K086N Build/QP1A.190711.020) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
        "Content-Type": "multipart/form-data; boundary=kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip, deflate"
    }
    value = ''.join(random.sample(string.ascii_lowercase + string.digits, 16))
    updata = {
        "deviceno": value,
        "sourceType": "moive",
        "platform": "android",
        "packageName": "cn.ikanys.xxys.classic",
        "version": "2.0.0803.01",
        "channel": "lb",
        "ts": "2022-08-10",
        "code": code
    }
    des3 = EncryptDate("OW84U8Eerdb99rtsTXWSILDO")  # 这里密钥的长度必须是16的倍数
    data = des3.encrypt(json.dumps(updata))

    payload = f"--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\nverifycode\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"data\"\r\n\r\n{data}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n"
    res = requests.post(reqUrl, headers=head, data=payload)
    print("response", res.text)


for i in range(1):
    print(i+1, end=" ")
    bindcode("23072111")
