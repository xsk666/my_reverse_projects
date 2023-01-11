import base64
import json
import random
import string
import time
from hashlib import md5

import requests
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms


class PrpCrypt(object):
    def __init__(self):
        self.key = '0123456789123456'.encode('utf-8')
        self.mode = AES.MODE_CBC
        self.iv = "2015030120123456".encode('utf-8')  # b'0102030405060708'
        # block_size 128位

    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16但是不是16的倍数，那就补足为16的倍数。
    def encrypt(self, text):

        cryptor = AES.new(self.key, self.mode, self.iv)
        text = text.encode('utf-8')

        # 这里密钥key 长度必须为16（AES-128）,24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用

        text = self.pkcs7_padding(text)

        self.ciphertext = cryptor.encrypt(text)

        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return base64.b64encode(self.ciphertext).decode("utf8")

    @staticmethod
    def pkcs7_padding(data):
        if not isinstance(data, bytes):
            data = data.encode()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()

        padded_data = padder.update(data) + padder.finalize()

        return padded_data

    @staticmethod
    def pkcs7_unpadding(padded_data):
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data)

        try:
            uppadded_data = data + unpadder.finalize()
        except ValueError:
            raise Exception('无效的加密信息!')
        else:
            return uppadded_data

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        #  偏移量'iv'
        cryptor = AES.new(self.key, self.mode, self.iv)
        plain_text = cryptor.decrypt(base64.b64decode(
            text.encode("utf8")))

        # plain_text = cryptor.decrypt(a2b_hex(text))
        # return plain_text.rstrip('\0')
        return bytes.decode(plain_text).rstrip("\x01").\
            rstrip("\x02").rstrip("\x03").rstrip("\x04").rstrip("\x05").\
            rstrip("\x06").rstrip("\x07").rstrip("\x08").rstrip("\x09").\
            rstrip("\x0a").rstrip("\x0b").rstrip("\x0c").rstrip("\x0d").\
            rstrip("\x0e").rstrip("\x0f").rstrip("\x10")

    def dict_json(self, d) -> str:
        '''python字典转json字符串, 去掉一些空格'''
        j = json.dumps(d).replace('": ', '":').replace(
            ', "', ',"').replace(", {", ",{")
        return j


def bindcode(code) -> None:
    now_time = str(int(time.time()*1000))
    # 随机16位android_id
    android_id = ''.join(random.sample("abcdef" + string.digits, 16))
    print("android_id", android_id)
    sign_text = "47Q8tBqO4YqrMHf4" + android_id + now_time  # 13时间戳
    sign = md5(sign_text.encode()).hexdigest().upper()  # 注意大写
    print("sign", sign)

    head = {
        'log-header': 'I am the log request header.',
        'app_id': 'huahuonew',
        'channel_code': 'hhsp_sp03',
        'cur_time': now_time,
        'device_id': android_id,
        'mob_mfr': 'xiaomi',
        'mobmodel': 'M2006J10C',
        'package_name': 'com.huahuo.hhspfilms',
        'sign': sign,
        'sys_platform': '2',
        'sysrelease': '11',
        'version': '22000',
        "token": "",
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '32',
        'Host': 'uty.micocc.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.10.0',
    }
    data = f'invited_by={code}&is_install=0'
    res = requests.post(
        'https://uty.micocc.com/api/public/init', headers=head, data=data)
    if res.text != "系统出问题啦~请稍后再试":
        pc = PrpCrypt()
        txt = json.loads(pc.decrypt(res.text))
        print(txt)
    else:
        print(res.text)


for i in range(1):
    print(i+1, end=" ")
    bindcode("39102016")
