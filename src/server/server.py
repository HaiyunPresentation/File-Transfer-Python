import os
import sys
from socket import *
from time import ctime

BUFSIZ = 1024

def recv(cliSock):
    data = cliSock.recv(BUFSIZ)  # 接收文件名或错误信息
    if data.decode() == "\0\01":
        print("Sorry client's file not found")
        return -1
    
    filename = data.decode("utf-8")
    print("Received Filename:", filename)

    data = cliSock.recv(BUFSIZ)
    cliSock.send("File size received".encode())

    file_total_size = int(data.decode())
    received_size = 0
    f = open(filename, "wb")
    while received_size < file_total_size:
        data = cliSock.recv(BUFSIZ)
        f.write(data)
        received_size += len(data)
        print("已接收：", received_size)
    f.close()


def usage():
    print("Usage: ")
    print("  python server.py <path> <ip_addr> <port>")


if __name__ == '__main__':
    if(len(sys.argv) < 4):
        usage()
    else:
        ip_addr = sys.argv[2]
        port = int(sys.argv[3])
        serSock = socket(AF_INET, SOCK_STREAM)  # 定义套接字
        serSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serSock.bind((ip_addr, port))  # 绑定地址
        serSock.listen(5)  # 规定传入连接请求的最大数，适用于异步
        print('等待连接...')
        cliSock, addr = serSock.accept()
        print('...连接自:', addr)
        recv(cliSock)
        serSock.close()
