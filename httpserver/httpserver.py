"""
httpserver主要功能

获取http请求
解析http请求
将请求发送给WebFrame
从WebFrame接收反馈数据
将数据组织为Response格式发送给客户端
"""
from socket import *
from config import *
from threading import Thread
import json
import re

# 和应用交互
def connect_frame(env):
    # tcp客户端
    s = socket()
    try:
        s.connect((frame_ip,frame_port))
    except Exception as e:
        print(e)
        return
    # 将env发送给webframe
    data = json.dumps(env) # 将字典转换为json
    s.send(data.encode())
    data = s.recv(1024*1024*10).decode()
    try:
        data = json.loads(data)
        return data
    except:
        return {'status':'500','data':'Error!'}

# 主体功能类
class HTTPServer:
    # 初始化对象即完成套接字创建,绑定,和部分属性的设置
    def __init__(self):
        self.address = (HOST,PORT)
        self.create_socket()
        self.bind()

    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET,
                               SO_REUSEADDR,
                               DEBUG)

    def bind(self):
        self.sockfd.bind(self.address)
        self.host = HOST
        self.port = PORT

    # 启动服务 多线程并发
    def serve_forever(self):
        self.sockfd.listen(3)
        print("Listen the port %d.."%self.port)
        while True:
            connfd,addr = self.sockfd.accept()
            print("Connect from",addr)
            t = Thread(target=self.handle,
                       args=(connfd,))
            t.setDaemon(True)
            t.start()

    def handle(self,connfd):
        # 接受HTTP请求
        request = connfd.recv(4096).decode()
        # 给webframe {'method':'GET','info':XX}
        pattern=r"(?P<method>[A-Z]+)\s+(?P<info>/\S*)"
        try:
            env = re.match(pattern,request).groupdict()
        except:
            connfd.close()
            return
        else:
            # 将env 发送给webframe得到数据
            data = connect_frame(env)
            if data:
                self.response(connfd,data)

    # 将数据组织为响应给浏览器发送
    def response(self,connfd,data):
        # data--> {'status':'200','data':'xxxx'}
        if data['status'] == '200':
            content = "HTTP/1.1 200 OK\r\n"
            content += "Content-Type:text/html\r\n"
            content += "\r\n"
            content += data['data']
        elif data['status'] == '404':
            content = "HTTP/1.1 404 Not Found\r\n"
            content += "Content-Type:text/html\r\n"
            content += "\r\n"
            content += data['data']
        elif data['status'] == '500':
            content = "HTTP/1.1 500 Server Error\r\n"
            content += "Content-Type:text/html\r\n"
            content += "\r\n"
            content += data['data']
        connfd.send(content.encode()) # 给浏览器


if __name__ == '__main__':
    # host = '0.0.0.0'
    # port = 8888
    #
    httpd = HTTPServer()
    httpd.serve_forever() # 启动服务

