import os
import sys
import hashlib
from socket import *
from pathlib import Path
#from time import ctime

BUFSIZ = 1024


def getFileMD5(filename):
    m = hashlib.md5()
    with open(filename, 'rb') as fobj:
        while True:
            data = fobj.read(8192)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


def recv(cliSock, dst_path):
    while True:
        data = cliSock.recv(BUFSIZ)  # 接收文件名或错误信息
        if len(data) == 0:
            print("客户端可能中断了连接")
            return -1
        if data.decode() == "\01":
            print("End")
            return 0

        filePath = data.decode("utf-8")
        print("Received File Path: "+filePath)
        cliSock.send("Get path".encode())

        fileSize = int(cliSock.recv(BUFSIZ).decode())
        cliSock.send("File size received ".encode())
        md5 = cliSock.recv(BUFSIZ).decode()
        cliSock.send("md5 received".encode())

        savePath = Path(dst_path).joinpath(filePath)
        Path(savePath.parent).mkdir(parents=True, exist_ok=True)

        received_size = 0
        packet_num = 0
        f = open(savePath, "wb")

        # 断点续传大法
        while received_size < fileSize:
            data = cliSock.recv(BUFSIZ)
            if len(data) == 0:
                print("客户端可能中断了连接，等待下次连接断点续传。已传输包数：", packet_num)

                return -1
            packet_num += 1
            f.write(data)
            received_size += len(data)
            #print("已接收：", received_size)
        f.close()
        md5Dst = getFileMD5(savePath)
        if md5Dst == md5:
            print("Received MD5 = ", md5)
        else:
            print("Received MD5 = ", md5Dst, " but expected = ", md5)

        cliSock.send("Received ".encode())


def usage():
    print("File Tranfer Server by HaiyunPresentation")
    print("Usage: ")
    print("  python server.py <dst_path> <ip_addr> <port>")
    print("  python3 is recommended in Linux")


if __name__ == '__main__':
    if(len(sys.argv) < 4):
        usage()
        sys.exit(1)
    dst_path = sys.argv[1]
    ip_addr = sys.argv[2]
    port = int(sys.argv[3])
    try:
        serSock = socket(AF_INET, SOCK_STREAM)  # 定义套接字
        serSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serSock.bind((ip_addr, port))  # 绑定地址
        serSock.listen(5)  # 规定传入连接请求的最大数，适用于异步
        print('等待连接...')

        cliSock, addr = serSock.accept()
        print('...连接自：', addr)
        recv(cliSock, dst_path)
        serSock.close()
    except gaierror:
        print("IP地址不正确！")
    except OverflowError:
        print("端口号不正确！")
    except OSError:
        print("套接字访问被拒绝。端口可能被占用。")
    except ConnectionAbortedError:
        print("客户端连接中止...")
    except KeyboardInterrupt:
        print("强制中断...")
