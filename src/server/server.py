# coding=utf-8
import os
import re
import sys
import hashlib
import zipfile
from socket import *
from pathlib import Path
#import time

BUFSIZ = 1024


def getFileMD5(filename):
    m = hashlib.md5()
    with open(filename, 'rb') as fobj:
        while True:
            data = fobj.read(0x1000000)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


def recvHead(sock, length):
    data = b''
    while length > 0:
        frag = sock.recv(length)
        length -= len(frag)
        data = b''.join([data, frag])
    return data


def recv(cliSock, dst_path):
    while True:
        pathLen = cliSock.recv(4)  # 接收文件名或错误信息
        #print(pathLen)
        if len(pathLen) == 0:
            print('客户端可能中断了连接')
            return -1
        pathLen = int.from_bytes(pathLen, byteorder='big')
        #print('------\n相对路径长度：',pathLen)
        if pathLen == 0xffffffff:
            print('End')
            return 0

        filePath = cliSock.recv(pathLen).decode('utf-8')
        is_compressed = int.from_bytes(cliSock.recv(1), byteorder='big')
        fileSize = int.from_bytes(cliSock.recv(8), byteorder='big')
        print('------\n相对路径：', filePath, '\n是否压缩: ',
              is_compressed, '\n传输文件大小：', fileSize)

        filePath = filePath.replace('\\', '/')  # 适配Linux路径
        savePath = Path(dst_path).joinpath(filePath)
        tempPath = savePath.parent.joinpath(savePath.name+'fileinfotmp')
        originalSavePath = ''
        Path(savePath.parent).mkdir(parents=True, exist_ok=True)
        if is_compressed == 1:
            #print('compressed')
            originalSavePath = savePath
            savePath = savePath.parent.joinpath(
                originalSavePath.name+'tempzip')
        '''
        uncompressed_md5 = ''

        if is_compressed == 1:
            uncompressed_md5 = cliSock.recv(32).decode()

        md5 = cliSock.recv(32).decode()
        print('MD5=\'',md5,'\'')
        '''
        is_append = False
        if os.path.exists(savePath):
            if os.path.exists(tempPath):
                ftemp = open(tempPath, 'r')
                ftempList = ftemp.readlines()
                ftemp.close()
                #oldmd5 = ftempList[0].rstrip('\n')
                received_packet_num = int(ftempList[0])

                #cliSock.send('old'.encode())
                #md5 = cliSock.recv(32).decode()
                #if oldmd5 == md5:
                print('准备断点续传')
                cliSock.send('app'.encode())
                cliSock.send(str(received_packet_num).encode())
                is_append = True
                #else:
                #    print('old md5=', oldmd5, '$\nnew md5=', md5, '$')
                #    print('客户端文件有更新')
                #    cliSock.send('all'.encode())
            else:
                oldmd5 = getFileMD5(savePath)
                cliSock.send('old'.encode())
                md5 = cliSock.recv(32).decode()
                if oldmd5 == md5:
                    print('MD5=',md5,', 不必更新')
                    cliSock.send('non'.encode())
                    continue
                else:
                    print('客户端文件有更新')
                    cliSock.send('all'.encode())
        elif is_compressed == 1 and os.path.exists(originalSavePath):
            old_uncompressed_md5 = getFileMD5(originalSavePath)
            cliSock.send('old'.encode())
            uncompressed_md5 = cliSock.recv(32).decode()
            if old_uncompressed_md5 == uncompressed_md5:
                print('不必更新')
                cliSock.send('non'.encode())
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

        # beginTime = time.time()

        # 断点续传大法
        while received_size < fileSize:
            # nowTime = time.time()
            # print('\r已下载: '+str("%f" % (received_size/fileSize*100))+'%', end='')
            data = cliSock.recv(BUFSIZ)
            if len(data) == 0:
                print('客户端可能中断了连接，等待下次连接断点续传。已传输包数：', packet_num)
                f.close()
                ftemp = open(savePath.parent.joinpath(
                    savePath.name+'fileinfotmp'), 'w')
                # ftemp.write(md5+'\n')
                ftemp.write(str(packet_num))
                ftemp.close()
                return -1
            packet_num += 1
            f.write(data)
            received_size += len(data)

        f.close()
        print('\r已下载：'+str("%f" % (100))+'%')
        '''
        endTime = time.time()
        if (endTime-beginTime == 0):
            print('Speed=NaN MB/s')
        else:
            if(is_append):
                speed = (fileSize-received_packet_num*BUFSIZ) / \
                    (endTime-beginTime)
            else:
                speed = fileSize/(endTime-beginTime)
            print('Speed='+str(speed/1024/1024)+' MB/s')
        '''
        if is_append:
            md5= getFileMD5(savePath)
            cliSock.send('md5'.encode())
            src_md5 = cliSock.recv(32).decode()
            if src_md5 == md5:
                cliSock.send('trc'.encode())
                if is_compressed == 1:
                    zfile = zipfile.ZipFile(savePath)
                    zfile.extractall(originalSavePath.parent)
                    #zfile.extractall(Path(dst_path).joinpath(os.path.dirname(originalSavePath)))
                    #print(os.path.dirname(originalSavePath).joinpath('\\'))
                    zfile.close()
            else:
                cliSock.send('frc'.encode())
                print('False Received',savePath)
                log = open('err.log', 'a')
                log.write(str(time.time())+' '+filename+' '+'False Received\n')
                log.close()
                os.remove(savePath)
                if os.path.exists(tempPath):
                    os.remove(tempPath)
                    continue

        '''
        md5Dst = getFileMD5(savePath)
        if md5Dst == md5:
            print('Received MD5 = ', md5)
            if is_compressed == 1:
                zfile = zipfile.ZipFile(savePath)
                zfile.extractall(originalSavePath.parent)
                #zfile.extractall(Path(dst_path).joinpath(os.path.dirname(originalSavePath)))
                #print(os.path.dirname(originalSavePath).joinpath('\\'))
                zfile.close()
            cliSock.send('True Received '.encode())
        else:
            print('Received MD5 in fact = ', md5Dst, ' but expected = ', md5)
            cliSock.send('False Received '.encode())
        '''
        
        cliSock.send('trc'.encode())
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


def buildSock(dst_path, ip_addr, port):
    try:
        serSock = socket(AF_INET, SOCK_STREAM)  # 定义套接字
        serSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serSock.bind((ip_addr, port))  # 绑定地址
        serSock.listen(1)  # 规定传入连接请求的最大数，适用于异步
        print('等待连接...')

        cliSock, addr = serSock.accept()
        print('...连接自：', addr)
        recv(cliSock, dst_path)
        serSock.close()
        return 0
    except gaierror:
        print('IP地址不正确！')
        return -1
    except OverflowError:
        print('端口号不正确！')
        return -1
    except OSError as info:
        print('系统错误。\n', info)
        if re.match(r'\[WinError 10054\].+', str(info)):  # 远程主机强迫关闭了一个现有的连接
            return 1
        else:
            return -1
    except ValueError as info:
        print('值错误。客户端可能中断了连接。\n', info)
        return 1
    except TypeError as info:
        print('类型错误。客户端可能中断了连接。\n', info)
        return 1
    except ConnectionAbortedError:
        print('客户端连接中止...')
        return 1
    except KeyboardInterrupt:
        print('强制中断...')
        return -1


if __name__ == '__main__':
    if(len(sys.argv) < 4):
        usage()
        sys.exit(1)
    dst_path = sys.argv[1]
    ip_addr = sys.argv[2]
    port = int(sys.argv[3])
    status = buildSock(dst_path, ip_addr, port)
    while (status == 1):
        print('尝试重建socket...')
        status = buildSock(dst_path, ip_addr, port)
