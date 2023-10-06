# encoding=utf-8
# %%
from binascii import a2b_base64, b2a_base64
from Crypto.Cipher import DES, DES3
from hashlib import md5
import jpype
import requests
import time
import json
import os
# %%
# 解密DES
class PrpCrypt(object):
    def __init__(self, key=""):
        self.key = key.encode('utf-8')
        self.mode = DES.MODE_ECB

    def changeKey(self, key):
        self.key = key.encode('utf-8')

    def encrypt(self, text):
        text = text.encode('utf-8')
        cryptor = DES.new(self.key, self.mode)
        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            text = text + ('\07' * add).encode('utf-8')
            print(text)
        elif count > length:
            add = (length - (count % length))
            text = text + ('\07' * add).encode('utf-8')
            print(text)
        self.ciphertext = cryptor.encrypt(text)
        return b2a_base64(self.ciphertext)

    # DES3解密
    def decrypt(self, text):
        cryptor = DES.new(self.key, self.mode)
        plain_text = cryptor.decrypt(a2b_base64(text))
        return plain_text.decode("utf-8").rstrip("\01").rstrip("\03")


class MiaoShang:
    def __init__(self) -> None:
        self.headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/4.9.3",
        }
        # 跟随设备固定,抓包自己找
        self.deviceId = "df82xxxxxxe64ddf"
        self.userId = "15269xxxxxxc8f70abce2"
        self.psign = "cf5a2xxxxxxxdaff3a59"
        self.req = requests.Session()
        self.des = PrpCrypt()
        self.signUtil = MiaoShang.signUtil()

    @staticmethod
    def signUtil():
        path = os.path.dirname(os.path.abspath(__file__))
        # jar包存放地址
        jarpath = path + "\\unidbg-android.jar"
        jpype.startJVM(jpype.getDefaultJVMPath(), "-ea",
                       "-Djava.class.path={}".format(jarpath), convertStrings=False)
        print("jvm启动成功")
        # 找到调用方法
        jpype.addClassPath(jarpath)
        SignutilClass = jpype.JClass("com.aster.zhbj.Signutil")
        # 实例化对象
        return SignutilClass()

    def photoDecrypt(self, decrData):
        '''图片解密
        DES3/CBC/PKCS5Padding'''
        key = "OW84U8Eerdb99rtsTXWSILEC"  # 初始化密钥
        iv = b'SK8bncVu'  # 偏移量
        des3de = DES3.new(key, DES3.MODE_CBC, iv)
        return des3de.decrypt(decrData)

    def search(self, text="擅长捉弄的高木同学", page=1):
        '''搜索'''
        if text == "":
            text = "擅长捉弄的高木同学"
        query = {
            'key': text,
            'appChannel': 'normal',
            'appKey': 'com.aster.zhbj',
            'appVersion': 'v1.10.5',
            'clientTime': str(int(time.time()*1000)),
            'deviceBrand': 'Xiaomi',
            'deviceType': '22041211AC',
            'ipAddr': '192.168.0.221',
            'netType': 'WIFI',
            'platform': 0,
            'sign': '',
            'systemVersion': '12',
            'userId': self.userId,
            'uuid': self.deviceId,
            'versionCode': 48
        }
        res = self.req.post('http://43.248.116.78:20256/api/novel/search/associate',
                            json= query).json()
        # print(res)
        token = res['safety']["token"][0][-1:0:-1]
        self.des.changeKey(token)
        # 解密之后，移除多余的填充和<word></word>（unicode）
        result = self.des.decrypt(res['safetyData'])\
            .replace("\x08", "")\
            .replace("\\u003Cword\\u003E", "").replace("\\u003C/word\\u003E", "")
        result = json.loads(result)
        return result
        # {'bookId': 'af0580069e7031e3f03f27fb4ff26cdb', 'bookName': '<word>擅长</word><word>捉弄</word><word>的</word><word>高木</word><word>同学</word>', 'authorName': '山本崇一朗', 'categoryName': '恋爱',
        #     'intro': '【此漫画的翻译由版权方提供】因为被对方捉弄所以要想尽办法捉弄回来，这不是理所当然的嘛！气定神闲地捉弄人的高木同学和总是计划失败被捉弄到满面通红的西片，在班上邻座的两人似乎有更多机会互相搞小动作，可是真的仅仅只是想要捉弄对方而已吗？这是擅长捉弄人的女孩子和傻乎乎被捉弄了之后一本正经想要“报仇”的男孩子，他们之间轻松愉快的故事。不过，好像也不仅仅是这样哦……\n每一次开场读者仿佛就能“看到结局”，但还是会让人忍不住看下去。大家一起为西片加油吧！', 'coverUrl': 'http://43.248.116.76:10132/covers/book/manku/af0580069e7031e3f03f27fb4ff26cdb.webp', 'finishedFlag': 0}

    def bookChapterInfo(self, bookId="af0580069e7031e3f03f27fb4ff26cdb"):
        res = self.req.get(
            f"http://43.248.116.76:20131/api/novel/book/chapters/{bookId}.json").json()
        token = res['safety']["token"][0][-1:0:-1]
        self.des.changeKey(token)
        # 将unicode转utf8: .encode().decode('unicode_escape')
        result = self.des.decrypt(res['safetyData']).replace("\x08", "")
        result = json.loads(result)
        # for i in result["chapters"]:
        #     print(i)
        return result["chapters"]

    def getChapterPhotos(self, bookId="af0580069e7031e3f03f27fb4ff26cdb", chapterId="YWYwNTgwMDY5ZTcwMzFlM2YwM2YyN2ZiNGZmMjZjZGJfcGx1dG9fNGU3ODViMDFiMWNkNjE5ZWNiZDQwNmQwODc4OTU1YTc=", chapterName=""):
        '''获取章节图片'''
        res = self.req.get(
            f"http://43.248.116.76:20131/api/novel/book/chapters/images/{bookId}/{chapterId}.json").json()
        token = res['safety']["token"][0][-1:0:-1]
        self.des.changeKey(token)
        data = json.loads(self.des.decrypt(res['safetyData']))["items"]
        # for i in data:
        #     print(i)
        return data

    def download(self, url, path="./"):
        '''下载'''
        # 13位时间戳
        rtime = str(int(time.time()*1000))
        headers = {
            'swidth': '1440',
            # 上次观看时间
            'rtime': rtime,
            'swidth': '1080',
            'stime': rtime,
            'ecount': '1',
            # 跟随设备固定
            'psign': self.psign,
            # 抓包自己找
            'userId': self.userId,
            'deviceId': self.deviceId,
            'version': 'v1.10.5',
            'systemVersion': '12',
            'appChannel': 'normal',
            'ipAddr': '10.69.8.234',
            'versionCode': '48',
            'appKey': 'com.aster.zhbj',
            'time': str(int(time.time()) // 60),
            'timeUnix': rtime,
            'ptime': rtime,
            'sheight': '2931',
            'User-Agent': 'okhttp/4.9.3',
        }

        count = '13'  # 当前错误尝试次数？
        size = '2459112'
        # 调用java方法，使用unidbg模拟运行so文件
        sign = self.signUtil.getShortSign(
            f"{self.deviceId}|{headers['timeUnix']}|{count}|{size}|com.aster.zhbj")
        sign1 = self.signUtil.getSign(
            f"{rtime}|{headers['userId']}|{headers['ptime']}")

        headers.update({"count": count, "size": size,
                        "sign": str(sign), "sign1": str(sign1)})
        print(headers)
        res = requests.get(url, headers=headers)
        if res.headers["Content-Length"] == "49200":
            print("下载错误")
            print("请求头",headers)
            print("响应体长度",res.headers["Content-Length"])
            raise Exception("下载错误")
        with open(path, "wb") as f:
            decode = self.photoDecrypt(res.content)
            f.write(decode)
            print("下载成功")


if __name__ == "__main__":
    miao = MiaoShang()
    try:
        search_result = miao.search(input("请输入搜索漫画名称："))
        for index, result in enumerate(search_result):
            print("序号:", index+1, "漫画名称:", result["key"], "作者：", json.loads(
                result['extra'])["authorName"])
        select_book = search_result[int(input("请输入你要查看的序号："))-1]
        bookName = select_book["key"]
        bookId = select_book["relationId"]
        # bookId = "af0580069e7031e3f03f27fb4ff26cdb"

        bookChapterInfo = miao.bookChapterInfo(bookId)
        print("章节列表：")
        for index, chapter in enumerate(bookChapterInfo):
            print("序号:", index+1, "章节名称:", chapter["chapterName"])
        # 是否需要下载
        if input("是否需要下载,请输入y/n：") == "y":
            print("默认只下载第一章节，如有需求自己搜索此处输出，修改代码")
            for chapter in bookChapterInfo[0:1]:
                print("正在下载..." + chapter["chapterName"] + "\n")
                allChapterPhotos = miao.getChapterPhotos(
                    bookId, chapterId=chapter["chapterId"], chapterName=chapter["chapterName"])
                # 文件夹不存在则创建
                if not os.path.exists(f'{bookName}/{chapter["chapterName"]}'):
                    os.makedirs(f'{bookName}/{chapter["chapterName"]}')
                for index, photo in enumerate(allChapterPhotos):
                    if os.path.exists(f"./{bookName}/{chapter['chapterName']}/{index+1}.png"):
                        print(f"已存在...{index+1}/{len(allChapterPhotos)}")
                        continue
                    print(f"正在下载...{index+1}/{len(allChapterPhotos)}", end="\r")
                    miao.download(
                        photo["url"], path=f"./{bookName}/{chapter['chapterName']}/{index+1}.png")

        # allChapterPhotos = miao.getChapterPhotos()
        # miao.download(
        #     "http://43.248.116.102:30133/img8/af0580069e7031e3f03f27fb4ff26cdb/4e785b01b1cd619ecbd406d0878955a7/20?t=1689571599606",'1.jpg')
        # for i in range(len(allChapterPhotos)):
        #     miao.download(allChapterPhotos[i]["url"], path=f"./{i}.png")
            # break
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
            print("关闭jvm")
