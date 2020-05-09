# coding=utf-8
import os
import sys
import hashlib
import zipfile
from socket import *
from pathlib import Path
import time

BUFSIZ = 1024
#total_datasize = 0


def getFileMD5(filename):
    m = hashlib.md5()
    with open(filename, 'rb') as fobj:
        while True:
            data = fobj.read(8192)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


def send(cliSock, filename, src_path, mode):
    if not os.path.exists(filename):
        print('找不到', filename)
        return 0
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
    print('------\n文件：', filename, '原始大小：', str(filesize))
    if mode=='compress' and filesize <= 1024*1024*10:
        originalFilename = filename
        filename += 'tempzip'
        with zipfile.ZipFile(filename, mode='w') as zfile:
            zfile.write(originalFilename, os.path.basename(originalFilename))
        filesize = os.path.getsize(filename)
        is_compressed = 1
    cliSock.send(str(is_compressed).encode())

    data = cliSock.recv(BUFSIZ)

    cliSock.send(str(filesize).encode())
    data = cliSock.recv(BUFSIZ)
    if is_compressed == 1:
        uncomparessed_md5 = getFileMD5(originalFilename)
        #print('uncomparessed MD5: ',uncomparessed_md5)
        cliSock.send(uncomparessed_md5.encode())
        sendInfo = cliSock.recv(BUFSIZ)
    md5 = getFileMD5(filename)
    print('MD5: ', md5)
    cliSock.send(md5.encode())
    sendInfo = cliSock.recv(BUFSIZ)
    if sendInfo == b'none':
        print('不必更新')
        if is_compressed == 1 and os.path.exists(filename):
            os.remove(filename)
        return 0
    f = open(filename, 'rb')

    #global total_datasize  # 引用全局变量

    if sendInfo == b'all':
        print('开始发送')
        #total_datasize += filesize
    else:  # 断点续传
        print(sendInfo)
        try:
            sent_packet_num = int(sendInfo)
        except ValueError:
            print('收到的信息有误。可能原因：服务器协议不一致或连接超时。')
            f.close()
            return 2
        f.read(BUFSIZ*sent_packet_num)
        print('开始断点续传')
        #total_datasize += (filesize-BUFSIZ*sent_packet_num)
    while True:
        data = f.read(BUFSIZ)
        if not data:
            break
        cliSock.send(data)
    f.close()
    data = cliSock.recv(BUFSIZ)
    print(data.decode())
    if data.decode()=='False Received':
        log=open('err.log', 'a')
        log.write(str(time.time())+' '+filename+' '+'False \n')
        log.close()
    
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
    print('File Tranfer Client by HaiyunPresentation')
    print('Usage: ')
    print('  1. Normal mode (default)')
    print('    python client.py <src_path> <ip_addr> <port>')
    print('  2. Compression mode (for small files)')
    print('    python client.py <src_path> <ip_addr> <port> --compress')
    print('  \'python3\' is recommended in Linux')


if __name__ == '__main__':
    if len(sys.argv) < 4 or (len(sys.argv)>=5 and sys.argv[4]!='--compress'):
        usage()
        sys.exit(1)

    src_path = sys.argv[1]
    ip_addr = sys.argv[2]
    port = int(sys.argv[3])
    if len(sys.argv)==4:
        mode='normal'
    else:
        mode='compress'
        
    #beginTime = time.time()
    if os.path.exists(src_path) == False:
       print('文件夹不存在！')
       sys.exit(1)
    relativePath = getFileList(src_path)
    try:
        cliSock = socket(AF_INET, SOCK_STREAM)
        cliSock.connect((ip_addr, port))
        for filename in relativePath:
            if send(cliSock, filename, src_path, mode) == -1:
                cliSock.close()
                sys.exit(1)
        print('------\n传输完毕')
        '''
        endTime = time.time()
        print('总传输速率：', end='')
        if (endTime-beginTime == 0):
            print('NaN Mbps')
        else:
            print(str(total_datasize/(endTime-beginTime)/1024/1024*8)+' Mbps')
        '''
        cliSock.send('\01'.encode())
        cliSock.close()
    except gaierror:
        print('IP地址不正确！')
    except OverflowError:
        print('端口号不正确！')
    except TypeError as info:
        print('类型错误。服务器端可能中断了连接。\n', info)
    except ConnectionAbortedError:
        print('服务器端连接中止...')
    except ConnectionResetError:
        print('连接已重置...')
    except ConnectionRefusedError:
        print('目标服务器拒绝建立连接！')
    except TimeoutError:
        print('连接超时！')
    except KeyboardInterrupt:
        print('强制中断...')
    # 异常中断理应清理.tempzip缓存
    relativePath = getFileList(src_path)
    for filename in relativePath:
        if os.path.exists(filename) and filename.endswith('tempzip'):
            os.remove(filename)
    print('已清理传输缓存。')
