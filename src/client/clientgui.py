# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'servergui2.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!
import sys
import os
import hashlib
import zipfile
import time
from socket import *
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication
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


def send(self,cliSock, filename, src_path, mode):
    if not os.path.exists(filename):
        self.textBrowser.insertPlainText('找不到'+filename+'\n')
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
    self.textBrowser.insertPlainText('------\n文件：'+filename+'原始大小：'+str(filesize)+'\n')
    if mode=='compress' and filesize <= 1024*1024*10:
        originalFilename = filename
        filename += '.tempzip'
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
    self.textBrowser.insertPlainText('MD5: '+ md5+ '\n')
    cliSock.send(md5.encode())
    sendInfo = cliSock.recv(BUFSIZ)
    if sendInfo == b'none':
        self.textBrowser.insertPlainText('不必更新\n')
        if is_compressed == 1 and os.path.exists(filename):
            os.remove(filename)
        return 0
    f = open(filename, 'rb')

    #global total_datasize  # 引用全局变量

    if sendInfo == b'all':
        self.textBrowser.insertPlainText('开始发送\n')
        #total_datasize += filesize
    else:  # 断点续传
        self.textBrowser.insertPlainText(sendInfo+'\n')
        try:
            sent_packet_num = int(sendInfo)
        except ValueError:
            self.textBrowser.insertPlainText('收到的信息有误。可能原因：服务器协议不一致或连接超时。\n')
            f.close()
            return 2
        f.read(BUFSIZ*sent_packet_num)
        self.textBrowser.insertPlainText('开始断点续传\n')
        #total_datasize += (filesize-BUFSIZ*sent_packet_num)
    while True:
        data = f.read(BUFSIZ)
        if not data:
            break
        cliSock.send(data)
    f.close()
    data = cliSock.recv(BUFSIZ)
    #print(data.decode())
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(801, 432)
        Form.setFixedSize(801,432)
        #状态 标签
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, 751, 41))
        self.label.setObjectName("label")
        #显示框  输出信息
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(0, 50, 801, 192))
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setFontPointSize(13)
        #IP地址标签
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(30, 260, 72, 31))
        self.label_2.setObjectName("label_2")
        #编辑IP地址
        self.textEdit = QtWidgets.QTextEdit(Form)
        self.textEdit.setGeometry(QtCore.QRect(90, 260, 201, 31))
        self.textEdit.setObjectName("textEdit")
        #端口标签
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(320, 260, 72, 31))
        self.label_3.setObjectName("label_3")
        #编辑端口
        self.textEdit_2 = QtWidgets.QTextEdit(Form)
        self.textEdit_2.setGeometry(QtCore.QRect(360, 260, 121, 31))
        self.textEdit_2.setObjectName("textEdit_2")
        #打开文件目录 选择文件
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(500, 260, 93, 31))
        self.pushButton.setObjectName("pushButton")
        #编辑 文件路径
        self.textEdit_3 = QtWidgets.QTextEdit(Form)
        self.textEdit_3.setGeometry(QtCore.QRect(600, 260, 201, 31))
        self.textEdit_3.setObjectName("textEdit_3")
        #无用的分割线
        self.line = QtWidgets.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(0, 310, 801, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        #发送按钮，  点击开始传输文件
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(190, 347, 111, 41))
        self.pushButton_2.setObjectName("pushButton_2")
        #取消按钮， 传输过程中中断传输
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setGeometry(QtCore.QRect(492, 347, 101, 41))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setEnabled(False)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "状态栏"))
        self.label_2.setText(_translate("Form", "IP地址"))
        self.label_3.setText(_translate("Form", "端口"))
        self.pushButton.setText(_translate("Form", "打开文件夹"))
        self.pushButton_2.setText(_translate("Form", "发送"))
        self.pushButton_3.setText(_translate("Form", "取消"))
    #封装于按钮事件  recv
    '''
    不建议使用!   recv &send 函数里的提示信息， 暂时没有移植到 窗口，仍在console 输出。
    ''' 
    def btn_send(self):
        mode='normal'

        ip_addr = self.textEdit.toPlainText()
        port = int(self.textEdit_2.toPlainText())
        src_path = self.textEdit_3.toPlainText()

        if os.path.exists(src_path) == False:
            self.textBrowser.insertPlainText('文件夹不存在！\n')
            sys.exit(1)
        relativePath = getFileList(src_path)
        try:
            cliSock = socket(AF_INET, SOCK_STREAM)
            cliSock.connect((ip_addr, port))
            for filename in relativePath:
               if send(self,cliSock, filename, src_path, mode) == -1:
                   cliSock.close()
                   sys.exit(1)
            self.textBrowser.insertPlainText('------\n传输完毕\n')
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
            self.textBrowser.insertPlainText('IP地址不正确！\n')
        except OverflowError:
            self.textBrowser.insertPlainText('端口号不正确！\n')
        except ConnectionAbortedError:
            self.textBrowser.insertPlainText('服务器端连接中止...\n')
        except ConnectionResetError:
            self.textBrowser.insertPlainText('连接已重置...\n')
        except ConnectionRefusedError:
            self.textBrowser.insertPlainText('目标服务器拒绝建立连接！\n')
        except TimeoutError:
            self.textBrowser.insertPlainText('连接超时！\n')
        except KeyboardInterrupt:
            self.textBrowser.insertPlainText('强制中断...\n')
        # 异常中断理应清理.tempzip缓存
        relativePath = getFileList(src_path)
        for filename in relativePath:
            if os.path.exists(filename) and filename.endswith('.tempzip'):
                os.remove(filename)
        self.textBrowser.insertPlainText('已清理传输缓存。\n')
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
class MyMainServerForm(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MyMainServerForm, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Client")
        self.pushButton.clicked.connect(self.openFile)
        '''注释部分，即为 按钮添加 recv 函数 事件'''
        self.pushButton_2.clicked.connect(self.btn_send)
    def openFile(self):
        get_directory_path = QFileDialog.getExistingDirectory(self, "请选择文件夹路径", "C:\\")
        
        self.textEdit_3.setText(str(get_directory_path))
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainServerForm()
    myWin.show()
    sys.exit(app.exec_())