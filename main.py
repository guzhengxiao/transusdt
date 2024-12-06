
import json
import websocket
import threading
import config
import bian
# import tools
import logging 
from logging.handlers import RotatingFileHandler 
import webserv
import feishu
import monitor

# 启动监听订单更新事件
if __name__ == '__main__':
    config.loadConfig()
    # feishu.sendMsg( "aa","bb" , config.config["monitor"]["feishu_notice"])
    # quit()

    log_thread = threading.Thread(target=monitor.start, args=())
    log_thread.start()
    webserv.start()
    # log_thread = threading.Thread(target=webserv.start, args=())

    # start_order_update_stream()
