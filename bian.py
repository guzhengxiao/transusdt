import config
import requests
import time
import hmac
import hashlib
import feishu

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
            "X-MBX-APIKEY": conf['api_key']
        }
        response = requests.put(url, headers=headers)
        if response.status_code == 200:
            pass
        else:
            # print("Keepalive 请求失败，可能需要重新生成 ListenKey。")
            generateKey()
            pass

# 获取服务器时间
def getServerTime():
    conf = config.config["monitor"]
    url = conf["api_url"]+"/fapi/v1/time"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['serverTime']
    else:
        print("无法获取服务器时间")
        return None

def notice(title , msg):
    feishuConf = config.config["follower"]["feishu_notice"]
    feishu.sendMsg(title,msg,feishuConf)

def sign(params, secret):
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return hmac.new(secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

def apiCall(path, params , method=None):
    conf = config.config["follower"]
    
    url = conf["api_url"] + path

    headers = {'X-MBX-APIKEY': conf["api_key"]}

    params['symbol'] = 'BTCUSDT'
    params["timestamp"] = getServerTime()
    params["signature"] = sign(params, conf["api_secret"])
    if method == "delete" :
        response = requests.delete(url, headers=headers, params=params)
    else:
        response = requests.post(url, headers=headers, params=params)
        
    return response
    # if response.status_code == 200:
    #     return True,response
    # else:
    #     print("操作失败：")
    #     print(response.status_code, response.text)
    #     return False , response

# 撤单操作
def cancelOrder( order_id):
    """
    撤单操作
    :param symbol: 交易对，例如 'BTCUSDT'
    :param order_id: 可选，提供特定订单ID撤销，否则会撤销第一个未完成的订单
    """
    params = {
        "origClientOrderId" : order_id
    }
    
    response = apiCall("/fapi/v1/order" , params , "delete")


    if response.status_code == 200:
        data = response.json()
        notice("跟单: 撤单","系统id: "+data["result"]["orderId"] +" 自定义id: " + order_id )
        # print(f"撤单成功，订单ID：{order_id}")
    else:
        notice("失败操作: 撤单",f"{order_id} :: {response.status_code} :: { response.text}" )
#         print(response.status_code,)


def setLeverage( leverage):
    """
    设置杠杆。
    :param symbol: 交易对，比如 "BTCUSDT"
    :param leverage: 设置的杠杆倍数
    """
    params = {
        "leverage": leverage,  # 设置杠杆倍数
    }

    # 发起请求
    response = apiCall("/fapi/v1/leverage" , params , "post")

    # 处理响应
    if response.status_code == 200:
        notice("杠杆设置成功",f"当前杠杆：{leverage}x")
    else:
        notice("设置杠杆失败：",f"{response.status_code} :: { response.text}" )



# 下单操作（开多，开空）
def openPosition(params): #id,side, position_side, order_type, quantity, price=None):
    """
    下单操作
    :param symbol: 交易对，例如 'BTCUSDT'
    :param side: 买入/卖出（'BUY' 或 'SELL'）
    :param position_side: 持仓方向（'LONG' 或 'SHORT'）
    :param order_type: 订单类型（'LIMIT' 或 'MARKET'）
    :param quantity: 交易数量
    :param price: 仅限限价单，提供价格
    
    
    newOrderRespType
    """
    # 订单参数
    # params = {
    #     'newClientOrderId' : oid,
    #     'side': side,
    #     'positionSide': position_side,
    #     'type': order_type,
    #     'quantity': quantity* config.max
    # }
    response = apiCall("/fapi/v1/order" , params , "post")

    # 处理响应
    if response.status_code == 200:
        notice(f"下单成功",f"{response.json()}")
    else:
        notice("下单失败",f"{response.status_code} :: { response.text}" )



def closeFirstPosition():
    """
    平仓操作：关闭第一个仓位，无论盈利还是亏损。
    """
    # 获取当前的仓位信息
    url = base_url + "/fapi/v2/positionRisk"
    params = {
        "timestamp": get_server_time(),
        'symbol':'BTCUSDT'
    }
    signature = generate_signature(params, api_secret)
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_key}

    response = requests.get(url, headers=headers, params=params)
    print(response.text)
    if response.status_code == 200:
        positions = response.json()
        # 查找 BTCUSDT 的仓位
        for position in positions:
            if position['symbol'] == 'BTCUSDT':
                position_side = position['positionSide']
                position_amt = float(position['positionAmt'])
                print(f"发现仓位: {position_side}，数量: {position_amt}")
                if position_side == "LONG" and position_amt > 0:
                    # 对于 "LONG" 仓位，执行卖出操作
                    print("Closing LONG position")
                    open_position("BTCUSDT", "SELL", "LONG", "MARKET", abs(position_amt))
                elif position_side == "SHORT" and position_amt < 0:
                    # 对于 "SHORT" 仓位，执行买入操作
                    print("Closing SHORT position")
                    open_position("BTCUSDT", "BUY", "SHORT", "MARKET", abs(position_amt))

        print(f"获取仓位信息失败：{response.status_code}, {response.text}")


