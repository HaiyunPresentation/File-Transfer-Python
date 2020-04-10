import os
import sys
from socket import *
from pathlib import Path

BUFSIZ = 1024


def send(cliSock, filename, src_path):
    filePath = Path(filename)
    rel_path = ''
    if(filePath.parent.name == ''):
        rel_path = filename
    else:
        rel_path = str(filePath.parent.relative_to(
            src_path).joinpath(filePath.name))
    cliSock.send(bytes(rel_path, 'utf-8'))
    data = cliSock.recv(BUFSIZ)
    filesize = str(os.path.getsize(filename))
    print("文件大小为：", filesize)
    cliSock.send(filesize.encode())
    data = cliSock.recv(BUFSIZ)  # 挂起发送，确保伺服端单独收到文件大小数据，避免粘包
    print("开始发送")

    f = open(filename, "rb")
    for line in f:
        cliSock.send(line)
    data = cliSock.recv(BUFSIZ)


'''
    else:
        print("Given folder path of client not found!")
        cliSock.send("\0\01".encode())
        return -1
'''


def getFileList(folder_path):
    if os.path.isfile(folder_path):  # 文件
        return [folder_path]
    fileList = []
    rootdir = folder_path
    list = os.listdir(rootdir)  # 列出文件夹下所有目录与文件

    for i in range(0, len(list)):
        com_path = os.path.join(rootdir, list[i])
        if os.path.isfile(com_path):
            fileList.append(com_path)
        if os.path.isdir(com_path):
            fileList.extend(getFileList(com_path))
    return fileList


def usage():
    print("Usage: ")
    print("  python client.py <src_path> <ip_addr> <port>")


if __name__ == '__main__':
    if(len(sys.argv) < 4):
        usage()
        sys.exit(1)

    src_path = sys.argv[1]
    ip_addr = sys.argv[2]
    port = int(sys.argv[3])

    if os.path.exists(src_path) == False:
       print("Given folder error!")
       sys.exit(1)
    relativePath = getFileList(src_path)

    cliSock = socket(AF_INET, SOCK_STREAM)
    cliSock.connect((ip_addr, port))

    for filename in relativePath:
        send(cliSock, filename, src_path)
    print("传输完毕")
    cliSock.send("\01".encode())
    cliSock.close()
