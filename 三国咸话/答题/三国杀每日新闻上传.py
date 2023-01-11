import requests
from io import BytesIO
from PIL import Image
head = {"Authorization": "Bearer eyJ08pG4o"}


try:
    res = requests.get("https://api.03c3.cn/zb/api.php")
    if res.status_code != 200:
        raise Exception("请求失败")
    res = res.json()
    if res.get("code") == 200:
        datatime = res["datatime"]
        print("新闻图片获取成功")
        photo = requests.get(res["imageUrl"])
        # 压缩图片
        if int(photo.headers["Content-Length"]) > 1048576:
            im = Image.open(BytesIO(photo.content))
            w, h = im.size
            im.thumbnail((w //4 *3, h // 4*3))
            img = BytesIO()
            im.save(img, 'PNG')
            img=img.getvalue()
        else:
            img = photo.content
            
    else:
        raise Exception("新闻图片获取失败")
    
    # 上传图片
    file = {
        "type": (None, "topic"),
        "image": ("filename", img, 'image/png')
    }
    res = requests.post("https://wxforum.sanguosha.cn/api/upload", headers=head, files=file).json()
    if res["code"] == 0:
        print("图片上传成功")
    else:
        print(res)
        raise Exception("图片上传失败")
    
    # 发布帖子
    data = {"title": f"{datatime}新闻来喽",
            "body": "来看看今天发生什么啦",
            "category_id": 5,
            "theme": "每日新闻",
            "theme_id": "",
            "body_image": [res["data"]["path"]]}
    res = requests.post("https://wxforum.sanguosha.cn/api/topics", headers=head, json=data).json()
    if res["code"] == 0:
        print(datatime, "发布成功")
    else:
        raise Exception("帖子发布失败")
except Exception as e:
    print(e)
