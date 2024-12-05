import config
import requests
import time

key = ""
def generate():
    global key
    headers = {
        "X-MBX-APIKEY": config.config['api_key']
    }
    response = requests.post(config.config["key_url"], headers=headers)
    data = response.json()
    print(data)
    key = data['listenKey']
    return key


def keep_alive(listenkey):
    while True:
        time.sleep(30)  # 每 30 秒发送一次 Keepalive 请求
        url = config.config["key_url"]+f"?listenKey={listenkey}"
        headers = {
            "X-MBX-APIKEY": config.config['api_key']
        }
        response = requests.put(url, headers=headers)
        if response.status_code == 200:
            pass
        else:
            # print("Keepalive 请求失败，可能需要重新生成 ListenKey。")
            generate()
            pass

