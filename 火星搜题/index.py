import json
from urllib.parse import quote
import requests
import uvicorn
import re
from fastapi import FastAPI
from pydantic import BaseModel
from fenbi import RsaUtil
from time import time



headers = {
    "User-Agent": "fenbi-android",
    "Connection": "Keep-Alive",
    "Content-Type": "multipart/form-data; boundary=130ed491-7420-46ee-984b-e3d71c35ab7a",
    "Cookie": "tourist=2ctB+TpAYHcNLfp/q3EI8w==; acw_tc=0b32974616626048811097841e0108bb8a2c7adcfb9019cf5a688cefa6e9de; userid=106564043; sid=-5668039259691547195"
}
private_key = "MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAMHuyCghJZoLukGIF5VF6cmUsMZiwOc9Qic6lU3S0/J1Rtj4woIAMznrJEr4Inf2xAahU/Dy/zCamCSB5V/y28hSsWSkO1uPwgVbIYMjtWCoebs078hhR88vVS71+4/FGaAadyja9acL4Jweps9NV0QKDkt0hTBNcO5IUQysPctFAgMBAAECgYBAyAbMgOYSo0BAi7l0/7mswKKcYniVxfzHJeah7H8oSsyzxcUTsAVsn4OsF19MO34XyORFZKaiEcIoz8tTVcjceN1KRB5jL/+bnX+/V66yedrOrUYyYgXUBVoRNST/2oG3jTE2cRpGk9xdYFyCdS8OSAEfOUtYgRwqjRWmtBpJgQJBAOlwm3nj4DLr19IPYzBOqLXNA3vw1za3etBWLHgRXIJw4h4+nCcyafo6bL94Wziyfqh3aMLtrPMUi2IG25abCX0CQQDUrMC6uo9CzAg+JQMY5Bjn/rVKFPok/r3bxILOG7ku5tXacLsTdMDzHg4bMfmyfeg9WH8gyv3OBx6L6wHGPzNpAkBzlA1mjCy1CZARsQyrHkbpvFe9RcFIlg94lzHtQKtM6hcKYnVt8sgF3Gd7ZVvE9ps/Td/Qo1y9/a4FGuAd8SUBAkBTf/wvlD3ZKQh3dcqwhCXvOEbvbisESWw7k/0TdTkQ3BrMqAQbUHTNP1ikfsuds+dx5oQLWQerU4o/vyY0Mu45AkA2h88bl0prq1Bata4XJ69ncWlI4+/1hpmAt7/V38ANWbQj4Ocby3j5KmEsmNwlOcl2JE2VCkqQ2mmRPDIJltOK"
rsautil = RsaUtil(private_key)


app = FastAPI()


class search(BaseModel):
    wd: str
    name: str = None


# @app.get("/api/searchApi")
@app.post("/api/searchApi")
def test(body: search = None, wd: str = None):
    if body is None and wd is None:
        return {"code": -1, "msg": "参数错误"}
    else:
        print(body, wd)
        searchText = quote(body.wd if body is not None else wd)
    data = f'''--130ed491-7420-46ee-984b-e3d71c35ab7a\r\nContent-Disposition: form-data; name="file"; filename="{time()}"\r\nContent-Type: image/jpeg\r\nContent-Length: 0\r\n\r\n\r\n--130ed491-7420-46ee-984b-e3d71c35ab7a--'''
    url = f"https://schoolapi.fenbi.com/college/android/search-item/search?format=ubb&searchType=2&text={searchText}&oq=&platform=android31&version=1.2.0&vendor=Taobao&app=souti&av=58&kav=23&hav=3&brand=Redmi&ua=22041211AC&deviceId=jfNBGVndXQZZCCrtHZ0tAw==&android_id=907157ccc3ab507a&client_context_id=0094403d57915e45495b"
    res = requests.post(url, data=data, headers=headers)
    print(res.text)
    res = res.json()
    if res["code"] != 1:
        return res
    answers_text = rsautil.decrypt(res["data"])
    # 删除多余的[p]和[/p]
    answers_text = re.sub(r"\[\/?p\]", "", answers_text)
    answers = json.loads(answers_text)["questionList"]
    newanswers = []
    for answer in answers[:10]:
        anstype = answer["type"]
        newanswer = {
            "type": anstype,
            "content": answer["content"]
        }
        if anstype in [1, 2]:
            newanswer["options"] = answer["accessories"][0]["options"]
            newanswer["answer"] = [
                chr(65 + int(i)) for i in set(answer["correctAnswer"]["choice"].split(","))]
            # newanswer["answer"] = list(
            #     set(answer["correctAnswer"]["choice"].split(",")))
        elif anstype == 5:
            newanswer["answer"] = answer["correctAnswer"]["choice"]
        elif anstype in [12, 15, 203]:
            newanswer["answer"] = answer["correctAnswer"]["answer"]
        else:
            newanswer["answer"] = answer["correctAnswer"]

        newanswers.append(newanswer)
    return {"code": 200, "data": newanswers}


if __name__ == "__main__":
    uvicorn.run(app="test:app", host="127.0.0.1",
                port=8000, debug=True, reload=True)
