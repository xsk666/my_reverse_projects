# encoding=utf-8
# %%
from binascii import a2b_base64
from Crypto.Cipher import DES, DES3
from hashlib import md5
import requests
import time
import json
# %%


class MiaoShang:
    def __init__(self) -> None:
        self.headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/4.9.3",
        }
        self.req = requests.Session()

    def chapterDecrypt(self, text):
        '''章节解密
        DES/ECB/PKCS5Padding
        '''
        cryptor = DES.new(b"ERG7F5KP", DES.MODE_ECB)
        plain_text = cryptor.decrypt(a2b_base64(text.encode("utf-8")))
        return plain_text.decode("utf-8").rstrip("\01").rstrip("\03")

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
        query = {"key": text, "page": page, "relationId": "", "relationType": 0, "appChannel": "normal", "appKey": "com.aster.zhbj", "appVersion": "v1.9.8.5", "clientTime": int(time.time()*1000), "deviceBrand": "Xiaomi",
                 "deviceType": "22041211AC", "ipAddr": "10.69.8.234", "netType": "NR", "platform": 0, "sign": "", "systemVersion": "12", "userId": "1526916a2f9a4b399b2434c8f70abce2", "uuid": "df82f15d18d8dc29bb5b65d407e64ddf", "versionCode": 35}
        res = self.req.post("http://43.248.116.78:20256/api/novel/search/books",
                            data=json.dumps(query), headers=self.headers).json()

        print(res["data"]["items"])
        return res["data"]["items"]
        # {'bookId': 'af0580069e7031e3f03f27fb4ff26cdb', 'bookName': '<word>擅长</word><word>捉弄</word><word>的</word><word>高木</word><word>同学</word>', 'authorName': '山本崇一朗', 'categoryName': '恋爱',
        #     'intro': '【此漫画的翻译由版权方提供】因为被对方捉弄所以要想尽办法捉弄回来，这不是理所当然的嘛！气定神闲地捉弄人的高木同学和总是计划失败被捉弄到满面通红的西片，在班上邻座的两人似乎有更多机会互相搞小动作，可是真的仅仅只是想要捉弄对方而已吗？这是擅长捉弄人的女孩子和傻乎乎被捉弄了之后一本正经想要“报仇”的男孩子，他们之间轻松愉快的故事。不过，好像也不仅仅是这样哦……\n每一次开场读者仿佛就能“看到结局”，但还是会让人忍不住看下去。大家一起为西片加油吧！', 'coverUrl': 'http://43.248.116.76:10132/covers/book/manku/af0580069e7031e3f03f27fb4ff26cdb.webp', 'finishedFlag': 0}

    def bookChapterInfo(self, bookId="af0580069e7031e3f03f27fb4ff26cdb"):
        res = self.req.get(
            f"http://43.248.116.76:20131/api/novel/book/chapters/{bookId}.json").json()

        d = json.loads(self.chapterDecrypt(res['safetyData']))
        for i in d["chapters"]:
            print(i)
        return d["chapters"]

    def getChapterPhotos(self, bookId="af0580069e7031e3f03f27fb4ff26cdb", chapterId="YWYwNTgwMDY5ZTcwMzFlM2YwM2YyN2ZiNGZmMjZjZGJfcGx1dG9fNGU3ODViMDFiMWNkNjE5ZWNiZDQwNmQwODc4OTU1YTc="):
        '''获取章节图片'''
        res = self.req.get(
            f"http://43.248.116.76:20131/api/novel/book/chapters/images/{bookId}/{chapterId}.json").json()

        data = json.loads(self.chapterDecrypt(res['safetyData']))["items"]
        for i in data:
            print(i)
        return data

    def download(self, url, path="./"):
        '''下载'''
        headers = {
            'swidth': '1440',
            'deviceId': 'df82f15d18d8dc29bb5b65d407e64ddf',
            'version': 'v1.9.8.5',
            'systemVersion': '12',
            'appChannel': 'normal',
            'ipAddr': '10.69.8.234',
            'versionCode': '35',
            'appKey': 'com.aster.zhbj',
            'time': '27890467',
            'sheight': '2931',
            'User-Agent': 'okhttp/4.9.3',
        }

        count = '0'  # 当前的数组下标
        size = '0'
        deviceId = 'df82f15d18d8dc29bb5b65d407e64ddf'
        timeUnix = str(int(time.time()*1000))
        sign = md5(
            f"{deviceId}|{timeUnix}|{count}|{size}|com.aster.zhbj".encode()).hexdigest()
        headers.update({"count": count, "size": size,
                        "timeUnix": timeUnix, "sign": sign})
        res = requests.get(url, headers=headers)

        with open(path, "wb") as f:
            decode = self.photoDecrypt(res.content)
            f.write(decode)
            print("下载完成")


if __name__ == "__main__":
    miao = MiaoShang()
    try:
        # miao.bookChapterInfo()
        allChapterPhotos = miao.getChapterPhotos()
        for i in range(len(allChapterPhotos)):
            miao.download(allChapterPhotos[i]["url"], path=f"./{i}.png")
    except Exception:
        import traceback
        traceback.print_exc()
