import tornado.ioloop
import tornado.web
import tornado.websocket
import time
import os
import threading
# from tornado.platform.asyncio import AnyThreadEventLoopPolicy
import asyncio

# 用于存储已连接的WebSocket客户端
clients = set()

# 模拟跟踪日志文件，读取新增的日志内容并发送给客户端
def follow_log_file(log_file_path):
    # asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())  # 设置线程可使用的事件循环策略
    loop = asyncio.new_event_loop()  # 为线程创建新的事件循环
    asyncio.set_event_loop(loop)  # 设置当前线程的事件循环
    with open(log_file_path, 'r') as file:
        file.seek(0, os.SEEK_END)
        while True:
            line = file.readline()
            if line:
                for client in clients:
                    try:
                        client.write_message(line.strip())
                    except:
                        pass
            else:
                time.sleep(0.1)

class LogHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("log.html")
class LogWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        # 当有客户端连接时，将其添加到客户端集合中
        clients.add(self)

    def on_close(self):
        # 当客户端断开连接时，从客户端集合中移除
        clients.remove(self)

    def check_origin(self, origin):
        # 允许跨域连接（在实际应用中可根据需求严格配置）
        return True

def make_app():
    return tornado.web.Application([
        (r"/log", LogHandler),  # 根路由，用于返回HTML页面
        (r"/logws", LogWebSocketHandler),  # WebSocket路由，用于推送日志消息
    ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),  # 设置模板路径
        static_path=os.path.join(os.path.dirname(__file__), "static")  # 设置静态资源路径
    )

def start():
    app = make_app()
    app.listen(80)
    # 这里假设日志文件名为app.log，你可以根据实际情况修改路径
    log_thread = threading.Thread(target=follow_log_file, args=('trans.log',))
    log_thread.start()
    tornado.ioloop.IOLoop.current().start()