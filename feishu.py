import hashlib
import base64
import hmac

import time
import requests
import json

def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign

# {
#         "timestamp": "1599360473",        // 时间戳。
#         "sign": "xxxxxxxxxxxxxxxxxxxxx",  // 得到的签名字符串。
#         "msg_type": "text",
#         "content": {
#                 "text": "request example"
#         }
# }

def sendMsg(title,msg,conf):
    timestamp = int( time.time() )
    data = {
        "timestamp": f"{timestamp}",
        "sign": gen_sign(timestamp,conf["key"]),
        "msg_type": "post",
        "content": {
            "post" : {
                "zh_cn" :{
                    "title":title,
                    "content" :[
                        [{
                            "tag": "text",
                            "text": msg
                        }]
                    ],
                }
            }
        }
    }
    headers = {'Content-type': 'application/json'}
    json_data = json.dumps(data)
    response = requests.post(conf["api"], data = json_data, headers = headers)
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
    else:
        print("请求出错，状态码:", response.status_code)