# %%
import requests
import random
import time

heads = [
    {"Authorization": "Bearer eyJ0eXAiOiJKV1QUzI1NiJ9.eyZSD8"}
]


def echo(*args, sep=" ", end="\n"):
    print(time.strftime("%m-%d %H:%M:%S->"), *args, sep=sep, end=end)


echo("开始执行任务")
for head in heads:
    # data = {"code": "071o5G0w33OeRX2Dkn3w3POOn64o5G02"}
    # res = requests.post("https://wxforum.sanguosha.cn/api/authorizations/basic",json=data)

    try:
        # 每日签到
        res = requests.post("https://wxforum.sanguosha.cn/api/user/sign", headers=head).json()
        echo(res)
        # 未领取 {"code": 10000,"data": [],"msg": "操作成功"}
        # 已领取 {'code': 10008, 'msg': '请勿重复提交', 'data': []}

        # 获取今日任务并且开始自动任务
        res = requests.get(f"https://wxforum.sanguosha.cn/api/shop/tasks", headers=head).json()
        if res["code"] == 0:
            category2 = res["data"]["lists"]['category2']
            # 获取完成进度
            tasks = {
                "回复": 1 if category2[0]["is_finish"] else int(category2[0]['user_finish_num']),
                "点赞帖子": 10 if category2[1]["is_finish"] else int(category2[1]['user_finish_num']),
                "点赞回复": 10 if category2[3]["is_finish"] else int(category2[3]['user_finish_num']),
            }
        else:
            tasks = {
                "回复": 0,
                "点赞帖子": 0,
                "点赞回复": 0,
            }
        echo("任务进度：", tasks)
    except Exception as e:
        echo("异常:", e)
    # %%
    # 获取推荐列表
    try:
        url = "https://wxforum.sanguosha.cn/api/topics?page=1&category_id=1&include=user%2Clabel&has_label=0&just_video=0"
        res = requests.get(url, headers=head).json()
        # 获取出错就退出
        if res["code"] != 0:
            echo(res["msg"])
            exit()
        newdata = res["data"]
    except Exception as e:
        exit()

    # %%
    try:
        for item in newdata:
            # print(f"标题：{item['title']}\n回复数：{item['reply_count']}\n点赞数：{item['like_count']}\n发布时间：{item['created_at']}\n")
            if tasks["回复"] < 1:
                # 回复帖子
                res = requests.post(f"https://wxforum.sanguosha.cn/api/topics/{item['id']}/replies", json={"contents": "1"}, headers=head).json()
                if res["code"] == 0:
                    tasks["回复"] += 1
                    echo("回复成功")

            if tasks["点赞帖子"] < 10:
                # 点赞帖子
                res = requests.post(f"https://wxforum.sanguosha.cn/api/topics/{item['id']}/likes", headers=head).json()
                if res["code"] == 10000:
                    tasks["点赞帖子"] += 1
                    echo("点赞帖子成功 *", tasks["点赞帖子"])

            if tasks["点赞回复"] < 10:
                # 点赞回复
                res = requests.get(f"https://wxforum.sanguosha.cn/api/topics/{item['id']}/replies?include=user&onlyAuthor=0&page=1&sort=asc", headers=head).json()['data']
                # 回复数大于0
                if res["count"] != 0:
                    # 不知道这个api能干啥
                    # res = requests.get(f"https://wxforum.sanguosha.cn/api/user/{item['user_id']}/relate", headers=head).json()
                    # if res["code"] == 0:
                    # echo("切换成功")

                    # 评论区随便选一个
                    id = random.choice(res["list"])['id']
                    res2 = requests.put(f"https://wxforum.sanguosha.cn/api/replies/{id}/likes", headers=head).json()
                    if res2["code"] == 0:
                        tasks["点赞回复"] += 1
                        echo("点赞成功 *", tasks["点赞回复"])
        echo("任务完成")
    except Exception as e:
        echo("异常:", e)
    # %%
    # 等待10s
    time.sleep(10)
    try:
        # 检查所有的任务是否可以领取奖励
        res = requests.get(f"https://wxforum.sanguosha.cn/api/shop/tasks", headers=head).json()
        if res["code"] == 0:
            lists = res["data"]["lists"]
            cans = [1, 2, 7, 8]  # 可以完成的任务
            for can in cans:
                for i in lists[f"category{can}"]:
                    if i["is_finish"] and not i["is_bonus"]:
                        res2 = requests.post(f"https://wxforum.sanguosha.cn/api/shop/getTaskBonus/{i['id']}", headers=head).json()
                        if res2["code"] == 0:
                            echo("任务："+i["content"], f"{i['bonus']}咸豆", "领取成功")

            echo("领取完成")
    except Exception as e:
        echo("异常:", e)
