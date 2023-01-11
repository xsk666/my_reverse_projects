# %%
import os
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives import padding
from binascii import b2a_hex, a2b_hex
from Crypto.Cipher import AES
import requests
import hashlib
import json
import easygui
# https://a4zh73d8.com/pc/index.html#/


class PrpCrypt:
    key = b'625202f9149maomi'
    mode = AES.MODE_CBC
    iv = b"5efd3f6060emaomi"
    # block_size 128位
    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16但是不是16的倍数，那就补足为16的倍数。

    @staticmethod
    def encrypt(text):
        cryptor = AES.new(PrpCrypt.key, PrpCrypt.mode, PrpCrypt.iv)
        text = text.encode('utf-8')
        # 这里密钥key 长度必须为16（AES-128）,24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
        text = PrpCrypt.pkcs7_padding(text)
        ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(ciphertext).decode().upper()

    @staticmethod
    def pkcs7_padding(data):
        if not isinstance(data, bytes):
            data = data.encode()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    @staticmethod
    def md5(sig):
        word = sig.encode()
        result = hashlib.md5(word)
        return result.hexdigest()

    # 解密后，去掉补足的空格用strip() 去掉
    @staticmethod
    def decrypt(text):
        #  偏移量'iv'
        cryptor = AES.new(PrpCrypt.key, PrpCrypt.mode, PrpCrypt.iv)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip("\x01").rstrip("\x02").rstrip("\x03").rstrip("\x04").rstrip("\x05").rstrip("\x06").rstrip("\x07").rstrip("\x08").rstrip("\x09").rstrip("\x0a").rstrip("\x0b").rstrip("\x0c").rstrip("\x0d").rstrip("\x0e").rstrip("\x0f").rstrip("\x10")


class Maomi:
    def __init__(self):
        self.headers = {
            "user-agent": "okhttp/4.0.1",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def get_post_data(self, data):
        # 去除空格
        data = json.dumps(data, separators=(',', ':'))
        # 需要加密的内容
        encrypt_data = PrpCrypt.encrypt(data)
        # 合并参数
        data = "_app_version=1.1.7&_device_type=22041211AC&_device_version=12&_sdk_version=31&data=" + encrypt_data
        # 生成签名
        sig = hashlib.md5((data+"maomi_pass_xyz").encode()).hexdigest()
        post_data = data + "&sig=" + sig
        return post_data

    def req(self, url, post_data):
        post_data = self.get_post_data(post_data)
        try:
            res = requests.post(
                "http://43.135.97.215:8099/api"+url, post_data, headers=self.headers, timeout=10)
            return json.loads(PrpCrypt.decrypt(res.text))
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e)
            return {"code": 500, "msg": "请求失败"}

    def listHot(self, page=1):
        fenye = {"page": 1, "perPage": 10, "uId": "99290596"}
        return self.req("/videos/listHot", fenye)
        # json.dump(maomi.listHot(), open("result.json", "w", encoding="utf-8"),
        #           indent=4, ensure_ascii=False)

    def listAll(self, page=1):
        fenye = {"page": page, "perPage": 10, "uId": "99290596"}
        return self.req("/videos/listAll", fenye)

    def get_mv_detail(self, id):
        detail = {"uId": "99290596", "mvId": id, "type": "2"}
        return self.req("/videos/detail", detail)

    def download_mv_by_id(self, id):
        res = self.get_mv_detail(id).get("data")
        self.download_mv_by_url(res.get("mv_title"), res.get("mv_play_url"))

    def download_mv_by_url(self, title, url):
        print("开始下载", title, url)
        try:
            # 域名改成video.amzvbn.com
            res = requests.get(url, timeout=10)
            # up.mmdz9hj.com
            # "http://video.amzvbn.com/uploads/2023-01-03/99462602/b4281900e0e8b975b771e26c8b44eb96_wm.mp4"
            # "http://119.28.204.36/uploads/2023-01-03/99462602/b4281900e0e8b975b771e26c8b44eb96_wm.mp4"
            # 写入二进制到文件
            with open(title + ".mp4", "wb") as f:
                f.write(res.content)
            print("下载成功")
        except Exception as e:
            print("下载失败")
            print(e)
            return {"code": 500, "msg": "下载失败"}

    def user_info(self, id):
        return self.req("/users/userdata", {"uId": str(id)})

    def gui(self):
        photos_path = os.path.join(os.getcwd(), "photos")
        if not os.path.exists(photos_path):
            os.mkdir(photos_path)
        video_list = self.listHot().get("data").get("list")
        index = 0
        while True:
            video_detail = video_list[index]
            if video_detail.get("is_cat_ads") == 1:
                print("广告")
                index -= 1
                continue
            name = video_detail.get("mv_id")+".jpg"
            path = os.path.join(photos_path, name)
            if os.path.exists(path):
                print("图片已存在")
            else:
                with open(path, "wb") as f:
                    res = requests.get(video_detail.get("mv_img_url")).content
                    f.write(res)
            data = easygui.buttonbox(
                video_detail.get("mv_title")+"\n", title=video_detail.get("mv_title"), image=path, choices=('上一张', "播放视频", '下一张'))
            if data == "上一张":
                if index == 0:
                    print("已经是第一张了")
                    continue
                index -= 1
                print("上一张")
            elif data == "播放视频":
                print("播放视频")
                res = self.get_mv_detail(video_detail.get("mv_id")).get("data")
                os.system(
                    '"E:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe" '+res.get("mv_play_url")+' --play-and-exit')
            elif data == "下一张":
                if index == len(video_list)-1:
                    print("已经是最后一张了")
                    continue
                index += 1
                print("下一张")
            elif data == None:
                print("退出")
                break

    def saomiao(self, start, end):
        if start > end:
            start, end = end, start
        for i in range(start, end):
            data = maomi.user_info(i).get("data")
            if data.get("is_vip", 0) == 0:
                print(i, data.get("mu_name", "")+" 不是会员")
            else:
                print(i, "信息为", data)
                break


if __name__ == "__main__":
    maomi = Maomi()
    # index = 101
    # for i in range(index, index+50):
    #     print("第", i, "页")
    #     json.dump(maomi.listAll(i), open("result"+str(i)+".json", "w", encoding="utf-8"),
    #               indent=4, ensure_ascii=False)

    # maomi.gui()
    for i in range(3165000, 3165294):
        data = maomi.get_mv_detail(str(i)).get("data")
        print(data)
    # maomi.download_mv_by_id("3172909")
