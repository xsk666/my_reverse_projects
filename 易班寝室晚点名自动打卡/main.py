import json
import requests
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from urllib.parse import quote
from pyquery import PyQuery as pq

class Yiban:
    def __init__(self,userinfo) -> None:
        self.req=requests.Session()
        self.req.headers={
                "X-Requested-With":"XMLHttpRequest",
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent":"Mozilla/5.0 (Linux; Android 11; M2006J10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046011 Mobile Safari/537.36 V1_AND_SQ_8.8.83_2654_YYB_D A_8088300 QQ/8.8.83.7540 NetType/4G WebP/0.3.0 Pixel/1080 StatusBarHeight/96 SimpleUISwitch/0 QQTheme/1000 InMagicWin/0 StudyMode/0 CurrentMode/0 CurrentFontScale/1.0 GlobalDensityScale/0.9818182 AppId/537114460"
            }
        self.userinfo=userinfo
    def encrypt_passwd(self,public_key,pwd)->str:
        cipher = PKCS1_v1_5.new(RSA.importKey(public_key))
        cipher_text = base64.b64encode(cipher.encrypt(bytes(pwd, encoding="utf8")))
        return quote(cipher_text.decode("utf-8"))

    def login(self)->bool:
        res=self.req.get("https://www.yiban.cn/login?go=https://f.yiban.cn/iapp587630")
        cookie=""
        for i in res.headers['set-cookie'].split(","):
            cookie+=i.split(";")[0]+";"
        self.req.headers["Cookie"]=cookie
        login_element=pq(res.text)("#login-pr")
        data=f"account={userinfo['account']}&password={self.encrypt_passwd(login_element.attr('data-keys'),userinfo['password'])}&captcha=&keysTime={login_element.attr('data-keys-time')}&is_rember=1"
        res=self.req.post("https://www.yiban.cn/login/doLoginAjax",data=data)
        if res.json()['code']==200:
            print(userinfo["name"],"登陆成功")
            self.req.headers["Cookie"]+=res.headers["set-cookie"].split(";")[0]+";"
            return True
        else:
            print(res.json()['message'])
            return False
    def get_user_id(self)->bool:
        url="https://www.yibanyun.cn/yibiaodan/index/recommend?page="
        i=1
        try:
            print("以下是学院id...")
            while True:
                res=self.req.get(url+str(i)).json()
                print(res["list"][0]["id"],res["list"][0]["title"])
                if res["tpage"]==i: 
                    break
                i+=1
            return True
        except Exception as e:
            print("获取失败",e)
            return False
        
    def get_cookie(self)->bool:
        try:
            #生成yibanyun的cookie
            res=self.req.get("https://www.yibanyun.cn/index/newapp",allow_redirects=False)
            tmp=res.headers["set-cookie"].split(";")
            # deviceid不知道哪里来的,应该是随机的
            cookie=tmp[0]+"; think_language=zh-CN; "+tmp[-2].split(",")[1]+";deviceid=1651761363496;"
            self.req.headers["Cookie"]=cookie
            # id=65即设置为 易表单/寝室晚点名 (post即可,不在乎返回值)
            self.req.post("https://www.yibanyun.cn/Mobile/index/pv",data="id=65&name=%E6%98%93%E8%A1%A8%E5%8D%95")
            return True
        except Exception as e:
            print(e)
            return False

    def daka(self):
        try:
            res=self.req.get("https://www.yibanyun.cn/yibiaodan/yibiaodan/index/id/222?sid=29024",allow_redirects=False)
            # print(res.headers["location"])
            if res.headers["location"]=="/yibiaodan/yibiaodan/success.html":
                print(userinfo['name'],"已完成打卡 或 当前非打卡时间")
                return False
            else:
                '''submit=提交&proid=222&gisx=118.309162&gisy=32.271191&gisaddress=滁州学院(会峰校区)(安徽省滁州市琅琊区丰乐大道1528号)&member[realname]=徐守康&essential=0&form_id[]=1413&form_item_val_0=网工202&essential=1&form_id[]=1388&form_item_val_1=2020211760&essential=2&form_id[]=1326&form_item_val_2=&essential=3&form_id[]=1327&form_item_val_3=621&essential=4&form_id[]=1389&form_item_val_4=是'''

                data=f"submit=%E6%8F%90%E4%BA%A4&proid=222&gisx={userinfo['gisx']}&gisy={userinfo['gisy']}&gisaddress=%E6%BB%81%E5%B7%9E%E5%AD%A6%E9%99%A2(%E4%BC%9A%E5%B3%B0%E6%A0%A1%E5%8C%BA)(%E5%AE%89%E5%BE%BD%E7%9C%81%E6%BB%81%E5%B7%9E%E5%B8%82%E7%90%85%E7%90%8A%E5%8C%BA%E4%B8%B0%E4%B9%90%E5%A4%A7%E9%81%931528%E5%8F%B7)&member%5Brealname%5D={quote(userinfo['name'])}&essential=0&form_id%5B%5D=1413&form_item_val_0=%E7%BD%91%E5%B7%A5202&essential=1&form_id%5B%5D=1388&form_item_val_1={userinfo['学号']}&essential=2&form_id%5B%5D=1326&form_item_val_2={userinfo['宿舍楼号']}&essential=3&form_id%5B%5D=1327&form_item_val_3={userinfo['宿舍号']}&essential=4&form_id%5B%5D=1389&form_item_val_4=%E6%98%AF"
                res=self.req.post("https://www.yibanyun.cn/yibiaodan/yibiaodan/join",data=data)
                if res.json()['errno']==0:
                    print(userinfo['name'],"打卡成功")
                    return True
                else:
                    print("打卡也许失败了？自行检查",res.text)
                    return False
        except Exception as e:
            print(e)
            return False


if __name__=="__main__":
    userinfos=json.load(open("users.json","r",encoding="utf-8"))
    for userinfo in userinfos:
        yb=Yiban(userinfo)
        if yb.login():
            yb.get_cookie()
            yb.daka()
            # 获取学院id请将 上一行注释 和 下面两行取消注释
            # 反之则进行正常打卡
            # if yb.get_user_id():
            #     break
