import config
import requests
import time

key = ""
def generateKey():
    global key
    conf = config.config["monitor"]
    headers = {
        "X-MBX-APIKEY": conf['api_key']
    }
    response = requests.post(conf["api_url"]+"/fapi/v1/listenKey", headers=headers)
    data = response.json()
    key = data['listenKey']
    return key


def keepKey(listenkey):
    conf = config.config["monitor"]
    while True:
        time.sleep(30)  # 每 30 秒发送一次 Keepalive 请求
        url = conf["api_url"]+f"/fapi/v1/listenKey?listenKey={listenkey}"
        headers = {
            "X-MBX-APIKEY": config.config['api_key']
        }
        response = requests.put(url, headers=headers)
        if response.status_code == 200:
            pass
        else:
            # print("Keepalive 请求失败，可能需要重新生成 ListenKey。")
            generateKey()
            pass

