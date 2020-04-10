import os
import sys
from socket import *

BUFSIZ = 1024


def Send(cliSock):
    filename = input('> ')
    if os.path.exists(filename):
        cliSock.send(bytes(filename, 'utf-8'))

        filesize = str(os.path.getsize(filename))
        print("文件大小为：", filesize)
        cliSock.send(filesize.encode())
        data = cliSock.recv(BUFSIZ)  # 挂起发送，确保伺服端单独收到文件大小数据，避免粘包
        print("开始发送")
        
        f = open(filename, "rb")
        for line in f:
            cliSock.send(line)   
    else:
        print("Given filename not found!")
        cliSock.send("\0\01".encode())
        return -1


def usage():
    print("Usage: ")
    print("  python client.py <path> <ip_addr> <port>")


if __name__ == '__main__':
    if(len(sys.argv) < 4):
        usage()
    else:
        filename = sys.argv[1]
        ip_addr = sys.argv[2]
        port = int(sys.argv[3])
        cliSock = socket(AF_INET, SOCK_STREAM)
        cliSock.connect((ip_addr, port))
        Send(cliSock)
        cliSock.close()
