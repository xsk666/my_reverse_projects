# %%
import requests
import random
import time
# me
heads = [
    {"user": "1", "Authorization": "Bearer rQ8pG4o"},
]
url = "http://127.0.0.1:8002"


def echo(*args, sep=" ", end="\n"):
    print(time.strftime("%m-%d %H:%M:%S->"), *args, sep=sep, end=end)


# 娱乐模式考试
echo("开始答题")
for head in heads:
    while True:
        req = requests.Session()
        req.headers = head
        res = req.post("https://wxforum.sanguosha.cn/api/exam/start").json()
        # code 1:咸豆不足; 10008:你有正在进行的考试;
        '''{
            "code" : 0,
            "data" : {
                "examNo" : "36a726258acaeae205612a2ee5624165",
                "symKey" : "b27f1343cf1c55257011424c4c001b5b"
            },
            "msg" : "操作成功"
        }
        '''
        print(res)
        if res["code"] == 1:
            echo(res["msg"])
            break

        # 第一题
        res = req.get("https://wxforum.sanguosha.cn/api/exam/question").json()
        '''{
            "code" : 0,
            "data" : {
                "costTime" : 0,
                "examNo" : "36a726258acaeae205612a2ee5624165",
                "order" : "1",
                "question" : {
                    "alternative" : [ "父子", "兄弟", "叔侄", "" ],
                    "id" : "6995",
                    "question" : "荀彧与荀攸的关系？"
                },
                "symKey" : "b27f1343cf1c55257011424c4c001b5b",
                "type" : "1"
            },
            "msg" : "操作成功"
        }
        '''
        # examNo放在这里获取，如果放在开始答题的时候，会出现获取不到exanNo问题(code=10008)
        examNo = res["data"]["examNo"]
        # 临时答题记录
        random_answer = []
        while True:
            if res["code"] == 0:
                echo("题目", res["data"]["order"], res["data"]["question"]["question"])
                if res["data"]["type"] != "1":
                    echo("出现了暂时不可回答的题目")
                # 答案去除无用选项
                # alternative = list(set(res["data"]["question"]["alternative"])-{""})
                alternative = list(filter(lambda x: x and x.strip(), res["data"]["question"]["alternative"]))
                print("选项", alternative)
                # 获取选项个数
                lens = len(alternative)
                qid = res["data"]["question"]["id"]
                print("qid", qid, end=" ")
                # 查询答案
                ans = -1
                try:
                    res2 = requests.get(url + f"/getAnswer?qid={qid}").json()
                    if res2["code"] == 0:
                        answer = res2["data"]["answer"]
                        try:
                            ans = alternative.index(answer)
                            print("正确答案", alternative[ans])
                        except:
                            print("答案索引错误")
                except:
                    print("题库请求出错")
                if ans == -1:
                    # 随机答案
                    ans = random.randint(0, lens-1)
                    print("随机答案", alternative[ans])
                # 存入临时答题记录
                random_answer.append({"qid": int(qid), "question": res["data"]["question"]["question"], "answer": alternative[ans], "type": res["data"]["type"]})
                is_end = 0
                if res["data"]["order"] == "10":
                    is_end = 1
                else:
                    time.sleep(0.2)
                # ans提交时下标+1
                ans += 1
                res = req.post(f"https://wxforum.sanguosha.cn/api/exam/answer", json={"answer": ans, "is_end": is_end, "qid": qid}).json()
                if res["code"] == 10000:
                    echo("答题完成", end=" ")
                    break
            else:
                break
        # 查询成绩
        res = req.get(f"https://wxforum.sanguosha.cn/api/exam/result?examNo={examNo}&type=1").json()
        '''{
            "code" : 0,
            "data" : {
                "best" : {
                    "rank" : 369571,
                    "right_count" : 4,
                    "score" : 40,
                    "start_time" : 1642793800,
                    "time" : 42,
                    "type" : 1
                },
                "result" : {
                    "right_count" : 1,
                    "score" : 10,
                    "time" : 50
                }
            },
            "msg" : "操作成功"
        }
        '''
        print("得分", res["data"]["result"]["score"])
        # 80分领取奖励
        if res["data"]["result"]["score"] >= 80: #and head.get("getTask"):
            req.post(f"https://wxforum.sanguosha.cn/api/shop/getTaskBonus/11").json()
            # head["getTask"] = 0
        #     key = "PDU4706TEd6QSECySOPqapuoeicILqxDsMNWBUZ0"
        #     try:
        #         test = requests.get(f"https://api2.pushdeer.com/message/push?pushkey={key}&text={head['user']}三国杀答题达到100分啦").json().get("success")
        #         if test:
        #             echo("->通知发送成功")
        #         else:
        #             echo("->通知发送失败")
        #     except:
        #         pass

        # 查询错题
        res = req.get(f"https://wxforum.sanguosha.cn/api/exam/errors?examNo={examNo}").json()
        '''{
            "code" : 0,
            "data" : [
                {
                    "alternative" : [ "父子", "兄弟", "叔侄", "" ],
                    "answer" : 3,
                    "order" : 1,
                    "qid" : 6995,
                    "question" : "荀彧与荀攸的关系？",
                    "type" : 1
                }
            ],
            "msg" : "操作成功"
        }
        '''
        if res["code"] == 0:
            print()
            echo("正确答案：")
            for i in res["data"]:
                # 修改错误答案
                random_answer[i["order"] - 1]["answer"] = i["alternative"][i["answer"]-1]
                print(i["order"], i["question"], i["alternative"][i["answer"]-1])

        # 记录答案
        try:
            res = requests.post(url + "/addAnswer", json={"newdata": random_answer}).json()
            print(res)
        except:
            print("记录异常，网络请求失败")
        print()
        time.sleep(30)
