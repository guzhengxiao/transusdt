
import json
import websocket
import threading
import config
import bian
import feishu
import datetime
import pytz
# import tools

# 第二步：定义 WebSocket 回调函数
def on_message(ws, message):
    # 处理订单更新消息
    data = json.loads(message)
    feishuConf = config.config["monitor"]["feishu_notice"]

    timestamp = data["E"]/1000
    timezone_str = "Asia/Shanghai"
    tz = pytz.timezone(timezone_str)
    dt_object = datetime.datetime.fromtimestamp(timestamp, tz)
    orderTime = dt_object.strftime("%Y-%m-%d %H:%M:%S")
     
    if 'e' in data and data['e'] == 'ORDER_TRADE_UPDATE':
        order_status = data['o']['x']  # 订单状态（如 NEW, FILLED, CANCELED 等）
        oid = data['o']['i']
        # 判断是否为撤单操作
        if order_status == "CANCELED":
            msg = f"""时间: {orderTime} 
订单id: {oid}"""
            threading.Thread(target=feishu.sendMsg, args=("操作: 撤单",msg ,feishuConf,), daemon=True).start()
            threading.Thread(target=bian.cancelOrder, args=(f"b-{oid}",), daemon=True).start()
            # tools.cancel_order('BTCUSDT')
            return  # 处理完成，退出函数
        elif order_status == "NEW":
            # 提取关键信息
            order_direction = data['o']['S']  # 订单方向（BUY/SELL）
            order_type = data['o']['o']  # 订单类型（LIMIT/MARKET 等）
            position_side = data['o']['ps']  # 持仓方向（LONG/SHORT）
            order_quantity = data['o']['q']  # 订单数量
            order_price = data['o']['p']  # 限价金额（对于市价单可能为 0）
            order_status = data['o']['x']  # 本次事件的执行类型（如 NEW、FILLED、CANCELED 等）
            is_close = data['o'].get('cp', False)  # 是否为平仓单
            # 根据方向和持仓判断是开仓还是平仓
            if position_side == "LONG":
                if order_direction == "BUY":
                    position = "开多"
                elif order_direction == "SELL":
                    position = "平多"
            elif position_side == "SHORT":
                if order_direction == "SELL":
                    position = "开空"
                elif order_direction == "BUY":
                    position = "平空"
            else:
                position = "未知"

            # 判断是否为平仓
            if is_close or order_status == "CLOSE_POSITION":
                position += "（平仓）"

            # 判断限价单还是市价单
            if order_type == "LIMIT":
                order_kind = "限价单"
            elif order_type == "MARKET":
                order_kind = "市价单"
            else:
                order_kind = "未知订单类型"
            if position == "开多":
                pass
                # tools.set_leverage(symbol, leverage)
                # tools.open_position('BTCUSDT', 'BUY', 'LONG', 'LIMIT', order_quantity * max, price=order_price)
            if position == "开空":
                pass
                # tools.set_leverage(symbol, leverage)
                # tools.open_position('BTCUSDT', 'SELL', 'SHORT', 'LIMIT', order_quantity * max, price=order_price)
            if position == '平空' or position == '平多':
                pass
                # tools.set_leverage(symbol, leverage)
                # tools.close_first_position()
            
            msg = f"""时间: {orderTime} 
订单id: {oid}
操作: {position}
订单类型: {order_kind}
订单方向: {'买入' if order_direction == 'BUY' else '卖出'}
数量: {order_quantity }
价格: {order_price if order_price != '0' else '市价'}"""
            threading.Thread(target=feishu.sendMsg, args=(f"操作: {position}",msg ,feishuConf,), daemon=True).start()
            # logger.info(f"操作: {position}, 订单类型: {order_kind},订单方向: {'买入' if order_direction == 'BUY' else '卖出'},数量: {order_quantity * config.max},价格: {order_price if order_price != '0' else '市价'}")
            pm = {
                'newClientOrderId' :  f"b-{oid}",
                'side': data['o']["S"],
                'positionSide': data['o']["ps"],
                'type': data['o']["o"],
                'quantity': data['o']["q"] * config.max,
            }
            if data['o']['o'] == "LIMIT":
                pm['price'] = data['o'].get("p")
            if data['o'].get("sp") and data['o'].get("sp") != "0": pm["stopPrice"] = data['o'].get("sp")
            if data['o'].get("cp"): pm["closePosition"] = data['o'].get("cp")
            # if data['o']['o'] == "TRAILING_STOP_MARKET":
            if data['o'].get("AP") and data['o'].get("AP") != "0": pm["activationPrice"] = data['o'].get("AP")
            if data['o'].get("cr"): pm["callbackRate"] = data['o'].get("cr")

            if data['o'].get("wt"): pm["workingType"] = data['o'].get("wt")
            if data['o'].get("pP"): pm["priceProtect"] = data['o'].get("pP")
            if data['o'].get("pm"): pm["priceMatch"] = data['o'].get("pm")
            if data['o'].get("f"): pm["timeInForce"] = data['o'].get("f")
            if data['o'].get("R"): pm["reduceOnly"] = data['o'].get("R")
            if data['o'].get("V"): pm["selfTradePreventionMode"] = data['o'].get("V")
            if data['o'].get("gtd") and data['o'].get("gtd") >0: pm["goodTillDate"] = data['o'].get("gtd")

            threading.Thread(target=bian.openPosition, args=(  pm, ), daemon=True ).start()

def on_error(ws, error):
    feishuConf = config.config["monitor"]["feishu_notice"]
    threading.Thread(target=feishu.sendMsg, args=(f"发生错误",str(error) ,feishuConf,), daemon=True).start()
    # print(f"发生错误：{error}")

def on_close(ws, close_status_code, close_msg):
    feishuConf = config.config["monitor"]["feishu_notice"]
    threading.Thread(target=feishu.sendMsg, args=(f"WebSocket 连接已关闭。","" ,feishuConf,), daemon=True).start()

def on_open(ws):
    feishuConf = config.config["monitor"]["feishu_notice"]
    threading.Thread(target=feishu.sendMsg, args=(f"开机运行","" ,feishuConf,), daemon=True).start()
    bian.setLeverage(config.leverage)

# 第四步：连接到 WebSocket，使用生成的 listen key
def start():
    listenkey = bian.generateKey()

    # 启动一个单独的线程保持连接活跃
    threading.Thread(target=bian.keepKey, args=(listenkey,), daemon=True).start()

    # WebSocket URL 使用 listen key
    socket_url = config.config["monitor"]["socket_url"]+listenkey

    # 启动 WebSocket 连接
    ws = websocket.WebSocketApp(socket_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
