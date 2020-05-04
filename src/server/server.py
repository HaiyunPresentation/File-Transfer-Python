# coding=utf-8
import os
import sys
import hashlib
import zipfile
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
            print('客户端可能中断了连接')
            return -1
        if data.decode() == '\01':
            print('End')
            return 0

        filePath = data.decode('utf-8')
        print('Received File Path: '+filePath)
        cliSock.send('Get path'.encode())
        is_compressed = int(cliSock.recv(BUFSIZ).decode())
        cliSock.send('if compressed received '.encode())
        fileSize = int(cliSock.recv(BUFSIZ).decode())
        cliSock.send('File size received '.encode())

        savePath = Path(dst_path).joinpath(filePath)
        tempPath = savePath.parent.joinpath(savePath.name+'.tmp')
        originalSavePath = ''
        Path(savePath.parent).mkdir(parents=True, exist_ok=True)
        if is_compressed == 1:
            #print('compressed')
            originalSavePath = savePath
            savePath = savePath.parent.joinpath(
                originalSavePath.name+'tempzip')

        uncomparessed_md5 = ''

        if is_compressed == 1:
            uncomparessed_md5 = cliSock.recv(BUFSIZ).decode()
            cliSock.send('uncomparessed_md5 received'.encode())

        md5 = cliSock.recv(BUFSIZ).decode()

        is_append = False
        if os.path.exists(savePath):
            if os.path.exists(tempPath):
                ftemp = open(tempPath, 'r')
                ftempList = ftemp.readlines()
                ftemp.close()
                oldmd5 = ftempList[0].rstrip('\n')
                received_packet_num = int(ftempList[1])
                if oldmd5 == md5:
                    print('准备断点续传')
                    cliSock.send(str(received_packet_num).encode())
                    is_append = True
                else:
                    print('old md5=', oldmd5, '$\nnew md5=', md5, '$')
                    print('客户端文件有更新')
                    cliSock.send('all'.encode())
            else:
                oldmd5 = getFileMD5(savePath)
                if oldmd5 == md5:
                    print('不必更新')
                    cliSock.send('none'.encode())
                    continue
                else:
                    print('客户端文件有更新')
                    cliSock.send('all'.encode())
        elif is_compressed == 1 and os.path.exists(originalSavePath):
            old_uncomparessed_md5 = getFileMD5(originalSavePath)
            if old_uncomparessed_md5 == uncomparessed_md5:
                print('不必更新')
                cliSock.send('none'.encode())
                continue
        else:
            cliSock.send('all'.encode())

        received_size = 0
        packet_num = 0
        if is_append:
            f = open(savePath, 'ab')
            packet_num += received_packet_num
            received_size += received_packet_num*BUFSIZ
        else:
            f = open(savePath, 'wb')

        # 断点续传大法
        while received_size < fileSize:
            data = cliSock.recv(BUFSIZ)
            if len(data) == 0:
                print('客户端可能中断了连接，等待下次连接断点续传。已传输包数：', packet_num)
                f.close()
                ftemp = open(savePath.parent.joinpath(
                    savePath.name+'.tmp'), 'w')
                ftemp.write(md5+'\n')
                ftemp.write(str(packet_num))
                ftemp.close()
                return -1
            packet_num += 1
            f.write(data)
            received_size += len(data)
            #print('已接收：', received_size)
        f.close()
        md5Dst = getFileMD5(savePath)
        if md5Dst == md5:
            print('Received MD5 = ', md5)
            if is_compressed == 1:
                zfile = zipfile.ZipFile(savePath)
                zfile.extractall(originalSavePath.parent)
                #zfile.extractall(Path(dst_path).joinpath(os.path.dirname(originalSavePath)))
                #print(os.path.dirname(originalSavePath).joinpath('\\'))
                zfile.close()
        else:
            print('Received MD5 in fact = ', md5Dst, ' but expected = ', md5)

        cliSock.send('Received '.encode())

        ##如果已经压缩文件且已经解压则删除压缩文件
        if originalSavePath != '' and os.path.exists(originalSavePath):
            os.remove(savePath)
        if os.path.exists(tempPath):
            os.remove(tempPath)


def usage():
    print('File Tranfer Server by HaiyunPresentation')
    print('Usage: ')
    print('  python server.py <dst_path> <ip_addr> <port>')
    print('  python3 is recommended in Linux.')
    print('  e.g:')
    print('    python3 server.py test 0.0.0.0 2000')


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
        print('IP地址不正确！')
    except OverflowError:
        print('端口号不正确！')
    except OSError as info:
        print('系统错误。\n', info)
    except ConnectionAbortedError:
        print('客户端连接中止...')
    except KeyboardInterrupt:
        print('强制中断...')
