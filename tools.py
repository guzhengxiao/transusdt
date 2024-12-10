import requests
import hmac
import hashlib
# Binance API 配置
api_key = ""
api_secret = ""

# Binance API 基础 URL
base_url = "https://fapi.binance.com"


# 获取服务器时间
def get_server_time():
    url = f"{base_url}/fapi/v1/time"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['serverTime']
    else:
        print("无法获取服务器时间")
        return None


# 签名生成函数
def generate_signature(params, secret):
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return hmac.new(secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()


# # 设置杠杆
# def set_leverage(symbol, leverage):
#     """
#     设置杠杆。
#     :param symbol: 交易对，比如 "BTCUSDT"
#     :param leverage: 设置的杠杆倍数
#     """
#     endpoint = "/fapi/v1/leverage"
#     url = base_url + endpoint

#     # 获取服务器时间
#     server_time = get_server_time()
#     if server_time is None:
#         return  # 如果获取服务器时间失败，终止函数

#     # 订单参数
#     params = {
#         "symbol": symbol,  # 交易对
#         "leverage": leverage,  # 设置杠杆倍数
#         "timestamp": server_time,  # 使用 Binance 服务器的时间戳
#     }

#     # 生成签名
#     signature = generate_signature(params, api_secret)
#     params["signature"] = signature

#     # 请求头
#     headers = {
#         "X-MBX-APIKEY": api_key
#     }

#     # 发起请求
#     response = requests.post(url, headers=headers, params=params)

#     # 处理响应
#     if response.status_code == 200:
#         print(f"杠杆设置成功，当前杠杆：{leverage}x")
#     else:
#         print("设置杠杆失败：")
#         print(response.status_code, response.text)


# 获取未完成的订单（撤单时用）
def get_open_orders(symbol):
    url = base_url + "/fapi/v1/openOrders"
    params = {
        'symbol': symbol,
        'timestamp': get_server_time()
    }
    signature = generate_signature(params, api_secret)
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': api_key}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取未完成订单失败：{response.status_code}, {response.text}")
        return []


# # 下单操作（开多，开空）
# def open_position(symbol, side, position_side, order_type, quantity, price=None):
#     """
#     下单操作
#     :param symbol: 交易对，例如 'BTCUSDT'
#     :param side: 买入/卖出（'BUY' 或 'SELL'）
#     :param position_side: 持仓方向（'LONG' 或 'SHORT'）
#     :param order_type: 订单类型（'LIMIT' 或 'MARKET'）
#     :param quantity: 交易数量
#     :param price: 仅限限价单，提供价格
#     """
#     endpoint = "/fapi/v1/order"
#     url = base_url + endpoint

#     # 获取服务器时间
#     server_time = get_server_time()
#     if server_time is None:
#         return

#     # 订单参数
#     params = {
#         'symbol': symbol,
#         'side': side,
#         'positionSide': position_side,
#         'type': order_type,
#         'quantity': quantity,
#         'timestamp': server_time
#     }

#     if order_type == 'LIMIT' and price:
#         params['price'] = price  # 仅限限价单时需要价格
#         params['timeInForce'] = 'GTC'  # Good Till Canceled（默认）

#     # 生成签名
#     signature = generate_signature(params, api_secret)
#     params['signature'] = signature

#     # 请求头
#     headers = {
#         'X-MBX-APIKEY': api_key
#     }

#     # 发起请求
#     response = requests.post(url, headers=headers, params=params)

#     # 处理响应
#     if response.status_code == 200:
#         print(f"下单成功: {side} {position_side}")
#         print(response.json())
#     else:
#         print("下单失败：")
#         print(response.status_code, response.text)



# # 撤单操作
# def cancel_order(symbol, order_id=None):
#     """
#     撤单操作
#     :param symbol: 交易对，例如 'BTCUSDT'
#     :param order_id: 可选，提供特定订单ID撤销，否则会撤销第一个未完成的订单
#     """
#     url = base_url + "/fapi/v1/order"
#     params = {
#         'symbol': symbol,
#         'timestamp': get_server_time()
#     }

#     if order_id is None:
#         open_orders = get_open_orders(symbol)
#         if open_orders:
#             order_id = open_orders[0]['orderId']  # 获取第一个未完成的订单ID
#         else:
#             print("没有未完成的订单可以撤销")
#             return

#     params['orderId'] = order_id
#     signature = generate_signature(params, api_secret)
#     params['signature'] = signature
#     headers = {'X-MBX-APIKEY': api_key}

#     response = requests.delete(url, headers=headers, params=params)

#     if response.status_code == 200:
#         print(f"撤单成功，订单ID：{order_id}")
#     else:
#         print("撤单失败：")
#         print(response.status_code, response.text)


# def close_first_position():
#     """
#     平仓操作：关闭第一个仓位，无论盈利还是亏损。
#     """
#     # 获取当前的仓位信息
#     url = base_url + "/fapi/v2/positionRisk"
#     params = {
#         "timestamp": get_server_time(),
#         'symbol':'BTCUSDT'
#     }
#     signature = generate_signature(params, api_secret)
#     params["signature"] = signature
#     headers = {"X-MBX-APIKEY": api_key}

#     response = requests.get(url, headers=headers, params=params)
#     print(response.text)
#     if response.status_code == 200:
#         positions = response.json()
#         # 查找 BTCUSDT 的仓位
#         for position in positions:
#             if position['symbol'] == 'BTCUSDT':
#                 position_side = position['positionSide']
#                 position_amt = float(position['positionAmt'])
#                 print(f"发现仓位: {position_side}，数量: {position_amt}")
#                 if position_side == "LONG" and position_amt > 0:
#                     # 对于 "LONG" 仓位，执行卖出操作
#                     print("Closing LONG position")
#                     open_position("BTCUSDT", "SELL", "LONG", "MARKET", abs(position_amt))
#                 elif position_side == "SHORT" and position_amt < 0:
#                     # 对于 "SHORT" 仓位，执行买入操作
#                     print("Closing SHORT position")
#                     open_position("BTCUSDT", "BUY", "SHORT", "MARKET", abs(position_amt))

#         print(f"获取仓位信息失败：{response.status_code}, {response.text}")


# 示例操作：设置杠杆，开多，平仓，撤单
#set_leverage(symbol, leverage)

# 开多操作
#open_position(symbol, 'BUY', 'LONG', 'LIMIT', 0.002, price=85000)

# 开空操作
#open_position(symbol, 'SELL', 'SHORT', 'LIMIT', 0.002, price=89350)

# 平仓操作
#close_first_position()

# 撤单操作
#cancel_order(symbol)
