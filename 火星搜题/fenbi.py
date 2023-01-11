import json
from time import time
import requests

from base64 import b64decode

import Crypto
from Crypto.PublicKey import RSA
# 计算加密解密
from Crypto.Cipher import PKCS1_v1_5


class RsaUtil(object):
    def __init__(self, key):
        self.key = key

    def get_max_length(self, rsa_key, encrypt=True):
        """加密内容过长时 需要分段加密 换算每一段的长度.
            :param rsa_key: 钥匙.
            :param encrypt: 是否是加密.
        """
        blocksize = Crypto.Util.number.size(rsa_key.n) / 8
        reserve_size = 11  # 预留位为11
        if not encrypt:  # 解密时不需要考虑预留位
            reserve_size = 0
        maxlength = blocksize - reserve_size
        return maxlength

    def decrypt(self, msg):
        """ 使用私钥分段解密 """
        msg = b64decode(msg)
        length = len(msg)
        private_key = RSA.importKey(b64decode(self.key))
        max_length = int(self.get_max_length(private_key, False))
        # 私钥解密
        private_obj = PKCS1_v1_5.new(private_key)
        # 长度不用分段
        if length < max_length:
            return b''.join(private_obj.decrypt(msg, b''))
        # 需要分段
        offset = 0
        res = []
        while length - offset > 0:
            if length - offset > max_length:
                res.append(private_obj.decrypt(
                    msg[offset:offset + max_length], b''))
            else:
                res.append(private_obj.decrypt(msg[offset:], b''))
            offset += max_length
        return b''.join(res).decode('utf8')


headers = {
    "User-Agent": "fenbi-android",
    "Connection": "Keep-Alive",
    "Content-Type": "multipart/form-data; boundary=130ed491-7420-46ee-984b-e3d71c35ab7a",
    "Cookie": "tourist=2ctB+TpAYHcNLfp/q3EI8w==; acw_tc=0b32974616626048811097841e0108bb8a2c7adcfb9019cf5a688cefa6e9de; userid=106564043; sid=-5668039259691547195"
}
rsautil = RsaUtil()
private_key = "MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAMHuyCghJZoLukGIF5VF6cmUsMZiwOc9Qic6lU3S0/J1Rtj4woIAMznrJEr4Inf2xAahU/Dy/zCamCSB5V/y28hSsWSkO1uPwgVbIYMjtWCoebs078hhR88vVS71+4/FGaAadyja9acL4Jweps9NV0QKDkt0hTBNcO5IUQysPctFAgMBAAECgYBAyAbMgOYSo0BAi7l0/7mswKKcYniVxfzHJeah7H8oSsyzxcUTsAVsn4OsF19MO34XyORFZKaiEcIoz8tTVcjceN1KRB5jL/+bnX+/V66yedrOrUYyYgXUBVoRNST/2oG3jTE2cRpGk9xdYFyCdS8OSAEfOUtYgRwqjRWmtBpJgQJBAOlwm3nj4DLr19IPYzBOqLXNA3vw1za3etBWLHgRXIJw4h4+nCcyafo6bL94Wziyfqh3aMLtrPMUi2IG25abCX0CQQDUrMC6uo9CzAg+JQMY5Bjn/rVKFPok/r3bxILOG7ku5tXacLsTdMDzHg4bMfmyfeg9WH8gyv3OBx6L6wHGPzNpAkBzlA1mjCy1CZARsQyrHkbpvFe9RcFIlg94lzHtQKtM6hcKYnVt8sgF3Gd7ZVvE9ps/Td/Qo1y9/a4FGuAd8SUBAkBTf/wvlD3ZKQh3dcqwhCXvOEbvbisESWw7k/0TdTkQ3BrMqAQbUHTNP1ikfsuds+dx5oQLWQerU4o/vyY0Mu45AkA2h88bl0prq1Bata4XJ69ncWlI4+/1hpmAt7/V38ANWbQj4Ocby3j5KmEsmNwlOcl2JE2VCkqQ2mmRPDIJltOK"
data = f'''--130ed491-7420-46ee-984b-e3d71c35ab7a\r\nContent-Disposition: form-data; name="file"; filename="{time()}"\r\nContent-Type: image/jpeg\r\nContent-Length: 0\r\n\r\n\r\n--130ed491-7420-46ee-984b-e3d71c35ab7a--'''
# 此处填入你的问题
searchText="独占设备"
url = f"https://schoolapi.fenbi.com/college/android/search-item/search?format=ubb&searchType=2&text={searchText}&oq=&platform=android30&version=1.2.0&vendor=fenbi&app=souti&av=58&kav=23&hav=3&brand=Redmi&ua=M2006J10C&deviceId=wx+85ayo2Lb+TYx7l1s4wA==&android_id=07462c57a6dd4dce&client_context_id=90a395c9f39a90fda8bc"
res = requests.post(url, data=data, headers=headers)

try:
    res = res.json()
except Exception as e:
    print(e, res.text)
    exit()

if res["code"] == 1:
    answers_text = rsautil.long_decrypt_by_private_key(
        res["data"], private_key)
    answers = json.loads(answers_text)["questionList"]
    newanswers = []

    # with open("answer.txt", "w") as f:
    #     f.write(answers_text)
    for answer in answers[:10]:
        newanswer = {
            "type": answer["type"],
            "content": answer["content"]
        }
        anstypes = {
            1: "选择题",
            2: "多选题",
            5: "判断题",
            12: "填空题",
            15: "简答题",
        }
        anstype = answer["type"]
        print("题目类型", anstypes[anstype], anstype)
        # 题目类型 1.选择,2.多选,5.判断题,12.填空,15.长文本
        # type 1  ,accessories type 101 有options ,correctAnswer type 201 有 choice "2"
        # type 2  ,accessories type 101 有options ,correctAnswer type 201 有 choice "0,1,2"
        # type 5  ,accessories 为空               ,correctAnswer type 201 有 choice
        # type 12 ,accessories 为空               ,correctAnswer type 203 有 answer
        # type 15 ,accessories 为空               ,correctAnswer type 203 有 answer
        if anstype in [1, 2]:
            newanswer["options"] = answer["accessories"][0]["options"]
            newanswer["answer"] = list(
                set(answer["correctAnswer"]["choice"].split(",")))
        elif anstype == 5:
            newanswer["answer"] = answer["correctAnswer"]["choice"]
        elif anstype in [12, 15]:
            newanswer["answer"] = answer["correctAnswer"]["answer"]
        else:
            newanswer["answer"] = answer["correctAnswer"]

        newanswers.append(newanswer)

