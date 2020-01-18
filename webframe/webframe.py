"""
模拟后端应用

从httpserver接收具体请求
根据请求进行逻辑处理和数据处理
将需要的数据反馈给httpserver
"""
from socket import *
import json
from threading import Thread
from settings import *
from urls import *

# 应用功能
class Application:
    def __init__(self):
        self.address = (HOST, PORT)
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

    # 服务启动
    def run(self):
        self.sockfd.listen(3)
        print("Running server on %d.." % self.port)
        while True:
            connfd, addr = self.sockfd.accept()
            print("Connect from", addr)
            t = Thread(target=self.handle,
                       args=(connfd,))
            t.setDaemon(True)
            t.start()

    # 具体处理请求
    def handle(self,connfd):
        request = connfd.recv(1024).decode()
        request = json.loads(request)
        # request-> {'method':'GET','info':XX}
        if request['method'] == 'GET':
            if request['info'] == '/' or request['info'][-5:] == '.html':
                # 请求网页
                response = self.get_html(request['info'])
            else:
                # 请求的不是网页
                response = self.get_data(request['info'])
        elif request['method'] == 'POST':
            pass
        # response--> {'status':'200','data':xxxx}
        response = json.dumps(response)
        connfd.send(response.encode()) # 给httpserver

    # 处理网页 info: 请求内容
    def get_html(self,info):
        if info == '/':
            filename = DIR + "/index.html"
        else:
            filename = DIR + info
        try:
            fd = open(filename)
        except:
            with open(DIR+'/404.html') as f:
                return {'status':'404','data':f.read()}
        else:
            return {'status':'200', 'data':fd.read()}

    # 处理数据
    def get_data(self,info):
        for url,func in urls:
            # url --> '/time'
            # func --> get_time
            if info == url:
                return {'status':'200','data':func()}
        # 如果info请求没有
        return {'status': '404', 'data':'Sorry...'}



if __name__ == '__main__':
    app = Application()
    app.run() # 运行服务
