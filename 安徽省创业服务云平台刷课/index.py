# %%
import requests
from bs4 import BeautifulSoup
import time
from multiprocessing import Process


def main(info):
    name = info["name"]
    req = requests.Session()
    req.headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.ahcy.gov.cn/PeiXun/ketangshipin/936f99bba0be4203842f665c27b7e3ba",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cookie": info["cookie"]
    }

    # %%
    res = req.get(f"https://www.ahcy.gov.cn//PeiXun/CourseDetail/{classid}")
    soup = BeautifulSoup(res.text, "html.parser")
    allvideo = soup.find_all(class_="keshi")
    for i in allvideo:
        tmp = i.find_all("a")
        id = tmp[1].get("id")
        classname = tmp[0].text
        while True:
            # 这里参数随便写无所谓，可以不改
            data = f"model%5BCurtime%5D=1043&model%5BChapterId%5D={id}&model%5BTotaltime%5D=1043"
            try:
                re2 = req.post(
                    "https://www.ahcy.gov.cn/PeiXun/SaveRecordShipin", data=data).json()
                if re2["Playtime"] == re2["Totletime"]:
                    print(name, classname, "已完成，跳转下一个")
                    time.sleep(2)
                    break
                else:
                    print(name, classname, round(re2["Playtime"] /
                                            re2["Totletime"], 2)*100, "%")
                    time.sleep(10)
            except:
                time.sleep(10)


if __name__ == "__main__":
    classid = "49c3b96eb45c4bde9ff648743dd44ab2"
    allinfo = [
        {
            "name": "用户1",
            "cookie": "填入cookie"
        },
        {
            "name": "用户2",
            "cookie": "填入cookie"
        },
    ]
    # 多进程刷课操作
    processes = []
    for i in allinfo:
        p = Process(target=main, args=(i,))
        processes.append(p)
        p.start()
    # 等待所有进程结束
    for p in processes:
        p.join()
