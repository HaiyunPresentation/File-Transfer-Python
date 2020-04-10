import os
import sys
from socket import *
from pathlib import Path
#from time import ctime

BUFSIZ = 1024


def recv(cliSock, folder_path):
    while True:
        data = cliSock.recv(BUFSIZ)  # 接收文件名或错误信息
        if data.decode() == "\01":
            print("End")
            return 0

        filePath = data.decode("utf-8")
        print("Received File Path: "+filePath)
        cliSock.send("Get path".encode())

        data = cliSock.recv(BUFSIZ)
        cliSock.send("File size received ".encode())

        savePath = Path(folder_path).joinpath(filePath)
        Path(savePath.parent).mkdir(parents=True, exist_ok=True)

        file_total_size = int(data.decode())
        received_size = 0
        f = open(savePath, "wb")
        while received_size < file_total_size:
            data = cliSock.recv(BUFSIZ)
            f.write(data)
            received_size += len(data)
            print("已接收：", received_size)
        f.close()
        cliSock.send("Receiced ".encode())


def usage():
    print("Usage: ")
    print("  python server.py <folder_path> <ip_addr> <port>")


if __name__ == '__main__':
    if(len(sys.argv) < 4):
        usage()
    else:
        folder_path = sys.argv[1]
        ip_addr = sys.argv[2]
        port = int(sys.argv[3])

        serSock = socket(AF_INET, SOCK_STREAM)  # 定义套接字
        serSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serSock.bind((ip_addr, port))  # 绑定地址
        serSock.listen(5)  # 规定传入连接请求的最大数，适用于异步
        print('等待连接...')
        cliSock, addr = serSock.accept()
        print('...连接自:', addr)

        recv(cliSock, folder_path)
        serSock.close()
