# %%
from typing import List
from pydantic import BaseModel
import pymongo
import uvicorn
from fastapi import FastAPI
import os
os.system("title 三国杀答案查询")
app = FastAPI()
db = pymongo.MongoClient(
    "mongodb://username:password@127.0.0.1:5000")["sgs"]["questions"]

# %%
# 查询


@app.get("/getAnswer")
def check(qid: int) -> dict:
    data = db.find_one({"qid": qid})
    if data is None:
        print("未找到")
        return {"code": 100, "msg": "未找到"}
    else:
        data.pop("_id")
        return {"code": 0, "msg": "查询成功", "data": data}


@app.post("/test")
def test(data: dict) -> dict:
    print(data['data'])
    return {"code": 0}


class Item(BaseModel):
    newdata: List[dict]


@app.post("/addAnswer")
def answer(data: Item) -> dict:
    '''[
      {
         "answer" : "审荣",
         "qid" : 5,
         "question" : "曹操攻邺，谁引兵入城？",
         "type" : 1
      }
   ]'''

    try:
        for i in data.newdata:
            i["qid"]=int(i["qid"])
            if db.find_one({"qid": i["qid"]}) is None:
                db.insert_one(i)
                print(i["qid"], end=" ")
            else:
                print("已存在", end=" ")
        return {"code": 0, "msg": "记录成功"}
    except:
        return {"code": 100, "msg": "记录失败"}


if __name__ == "__main__":
    uvicorn.run(app="sgsAnswer:app", host="127.0.0.1", port=8002, debug=True)
