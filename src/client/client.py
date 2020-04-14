import os
import sys
import hashlib
import zipfile
from socket import *
from pathlib import Path

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
    filesize = os.path.getsize(filename)
    #记录是否被压缩
    is_compressed = 0
    print("文件：", filename, "大小为：", str(filesize))
    if filesize>1024*1024*10:
        originalFilename = filename
        filename+="tempzip"
        with zipfile.ZipFile(filename, mode='w') as zfile:
            zfile.write(originalFilename,os.path.basename(originalFilename))
        filesize = os.path.getsize(filename)
        is_compressed = 1
    cliSock.send(str(is_compressed).encode())

    data = cliSock.recv(BUFSIZ)

    cliSock.send(str(filesize).encode())
    data = cliSock.recv(BUFSIZ)
    if is_compressed == 1:
        uncomparessed_md5 = getFileMD5(originalFilename)
        #print("uncomparessed MD5: ",uncomparessed_md5)
        cliSock.send(uncomparessed_md5.encode())
        sendInfo = cliSock.recv(BUFSIZ)
    md5 = getFileMD5(filename)
    print("MD5: ", md5)
    cliSock.send(md5.encode())
    sendInfo = cliSock.recv(BUFSIZ)
    if sendInfo == b'none':
        print('不必更新')
        return 0
    f = open(filename, "rb")
    if sendInfo == b'all':
        print("开始发送")
    else:  # 断点续传
        print(sendInfo)
        sent_packet_num = int(sendInfo)
        f.read(BUFSIZ*sent_packet_num)
        print("开始断点续传")
    while True:
        data = f.read(BUFSIZ)
        if not data:
            break
        cliSock.send(data)

    data = cliSock.recv(BUFSIZ)
    f.close()
    if is_compressed == 1:
        os.remove(filename)



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
    print("File Tranfer Client by HaiyunPresentation")
    print("Usage: ")
    print("  python client.py <src_path> <ip_addr> <port>")
    print("  python3 is recommended in Linux")


if __name__ == '__main__':
    if(len(sys.argv) < 4):
        usage()
        sys.exit(1)

    src_path = sys.argv[1]
    ip_addr = sys.argv[2]
    port = int(sys.argv[3])

    if os.path.exists(src_path) == False:
       print("文件夹不存在！")
       sys.exit(1)
    relativePath = getFileList(src_path)
    try:
        cliSock = socket(AF_INET, SOCK_STREAM)
        cliSock.connect((ip_addr, port))
        for filename in relativePath:
            send(cliSock, filename, src_path)
        print("传输完毕")
        cliSock.send("\01".encode())
        cliSock.close()
    except gaierror:
        print("IP地址不正确！")
    except OverflowError:
        print("端口号不正确！")
    except ConnectionAbortedError:
        print("服务器端连接中止...")
    except ConnectionResetError:
        print("连接已重置...")
    except ConnectionRefusedError:
        print("目标服务器拒绝建立连接！")
    except KeyboardInterrupt:
        print("强制中断...")
