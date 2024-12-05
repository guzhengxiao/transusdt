
import json
import websocket
import threading
import config
import listen_key
# import tools
import logging 
from logging.handlers import RotatingFileHandler 
import webserv

logger = logging.getLogger(__name__) 
logger.setLevel(logging.INFO) 
console_handler = logging.StreamHandler() 
file_handler = RotatingFileHandler('trans.log', maxBytes=1024*1024, backupCount = 3) 
logger.addHandler(console_handler) 
logger.addHandler(file_handler)


# 第二步：定义 WebSocket 回调函数
def on_message(ws, message):
    # 处理订单更新消息
    data = json.loads(message)
    if 'e' in data and data['e'] == 'ORDER_TRADE_UPDATE':
        order_status = data['o']['x']  # 订单状态（如 NEW, FILLED, CANCELED 等）
        # 判断是否为撤单操作
        if order_status == "CANCELED":
            # print(f"操作: 撤单")
            logger.info(f"操作: 撤单")
            # tools.cancel_order('BTCUSDT')
            return  # 处理完成，退出函数
        if order_status == "NEW":
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
            logger.info(f"操作: {position}, 订单类型: {order_kind},订单方向: {'买入' if order_direction == 'BUY' else '卖出'},数量: {order_quantity * config.max},价格: {order_price if order_price != '0' else '市价'}")

def on_error(ws, error):
    print(f"发生错误：{error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket 连接已关闭。")

def on_open(ws):
    print("WebSocket 连接已开启。")

# 第四步：连接到 WebSocket，使用生成的 listen key
def start_order_update_stream():
    listenkey = listen_key.generate()

    # 启动一个单独的线程保持连接活跃
    threading.Thread(target=listen_key.keep_alive, args=(listenkey,), daemon=True).start()

    # WebSocket URL 使用 listen key
    socket_url = config.config["socket_url"]+listenkey

    # 启动 WebSocket 连接
    ws = websocket.WebSocketApp(socket_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

# 启动监听订单更新事件
if __name__ == '__main__':
    config.loadConfig()
    log_thread = threading.Thread(target=webserv.start, args=())
    start_order_update_stream()
