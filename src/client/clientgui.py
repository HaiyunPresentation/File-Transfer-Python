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
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QMessageBox

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
        Form.resize(780, 400)
        Form.setFixedSize(780, 400)

        #显示框  输出信息
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(20, 60, 560, 320))
        self.textBrowser.setObjectName("textBrowser")
        #IP地址标签
        self.ipLabel = QtWidgets.QLabel(Form)
        self.ipLabel.setGeometry(QtCore.QRect(600, 70, 50, 30))
        self.ipLabel.setObjectName("ipLabel")
        #编辑IP地址
        self.ipTextEdit = QtWidgets.QTextEdit(Form)
        self.ipTextEdit.setGeometry(QtCore.QRect(600, 110, 160, 30))
        self.ipTextEdit.setObjectName("ipTextEdit")
        #端口标签
        self.portLabel = QtWidgets.QLabel(Form)
        self.portLabel.setGeometry(QtCore.QRect(600, 160, 50, 30))
        self.portLabel.setObjectName("portLabel")
        #编辑端口
        self.portTextEdit = QtWidgets.QTextEdit(Form)
        self.portTextEdit.setGeometry(QtCore.QRect(600, 200, 160, 30))
        self.portTextEdit.setObjectName("portTextEdit")
        #打开文件目录 选择文件
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(660, 15, 100, 35))
        self.pushButton.setObjectName("pushButton")
        #编辑 文件路径
        self.pathTextEdit = QtWidgets.QTextEdit(Form)
        self.pathTextEdit.setGeometry(QtCore.QRect(20, 15, 625, 35))
        self.pathTextEdit.setObjectName("pathTextEdit")
        #发送按钮，  点击开始传输文件
        self.sendButton = QtWidgets.QPushButton(Form)
        self.sendButton.setGeometry(QtCore.QRect(630, 250, 100, 50))
        self.sendButton.setObjectName("sendButton")
        #取消按钮， 传输过程中中断传输
        self.cancelButton = QtWidgets.QPushButton(Form)
        self.cancelButton.setGeometry(QtCore.QRect(630, 320, 100, 50))
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setEnabled(False)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.ipLabel.setText(_translate("Form", "IP地址"))
        self.portLabel.setText(_translate("Form", "端口"))
        self.pushButton.setText(_translate("Form", "打开文件夹"))
        self.sendButton.setText(_translate("Form", "发送"))
        self.cancelButton.setText(_translate("Form", "取消"))


class MyMainServerForm(QMainWindow, Ui_Form):
    __signal = pyqtSignal(str)
    src_path = ''

    def __init__(self, parent=None):
        super(MyMainServerForm, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("FileTransfer Client by HaiyunPresentation")
        self.__signal.connect(self.mySignal)
        self.pushButton.clicked.connect(self.openFile)

        self.sendButton.clicked.connect(self.btn_send)
        self.cancelButton.clicked.connect(self.btn_cancel)

    def openFile(self):
        get_directory_path = QFileDialog.getExistingDirectory(
            self, "请选择文件夹路径", ".")

        self.pathTextEdit.setText(str(get_directory_path))

    def mySignal(self, string):
        self.textBrowser.insertPlainText(string)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
        QApplication.processEvents()  # 实时刷新

    def send(self, cliSock, filename, src_path, mode):
        if not os.path.exists(filename):
            self.__signal.emit('找不到'+filename+'\n')
            return 0
        filePath = Path(filename)
        rel_path = ''
        if(filePath.parent.name == ''):
            rel_path = filename
        else:
            rel_path = str(filePath.parent.relative_to(
                src_path).joinpath(filePath.name))
    
        pathLen = len(rel_path.encode('utf-8'))
    
        # 发送路径长度和相对路径
        cliSock.send(pathLen.to_bytes(4, byteorder='big'))
        cliSock.send(rel_path.encode('utf-8'))
    
        fileSize = os.path.getsize(filename)
    
        #记录是否被压缩
        is_compressed = 0
        #print('------\n文件：', filename, '原始大小：', str(fileSize))
        if mode == 'compress' and fileSize <= 1024*1024*10:
            originalFilename = filename
            filename += 'tempzip'
            with zipfile.ZipFile(filename, mode='w') as zfile:
                zfile.write(originalFilename, os.path.basename(originalFilename))
            fileSize = os.path.getsize(filename)
            is_compressed = 1
    
        # 发送是否压缩
        cliSock.send(is_compressed.to_bytes(1, byteorder='big'))
    
        # 发送传输文件（原始文件或压缩文件）大小
        cliSock.send(fileSize.to_bytes(8, byteorder='big'))

        sendInfo = cliSock.recv(3)
        if sendInfo == b'old':
            if is_compressed == 1:
                md5 = getFileMD5(originalFilename)
            else:
                md5 = getFileMD5(filename)
            # 发送原始文件MD5
            cliSock.send(md5.encode())
            sendInfo = cliSock.recv(3)
    
        if sendInfo == b'non':
            self.__signal.emit('------\n不必更新'+filename+'\n')
            if is_compressed == 1 and os.path.exists(filename):
                os.remove(filename)
            return 0
        f = open(filename, 'rb')
    
        #global total_datasize  # 引用全局变量
    
        sent_size = 0
        if sendInfo == b'all':
            self.__signal.emit('------\n开始发送'+filename+'\n')
            #total_datasize += filesize
        else:  # 断点续传
            self.__signal.emit(sendInfo)
            sendInfo=cliSock.recv(BUFSIZ).decode()
            self.__signal.emit(sendInfo)
            try:
                sent_packet_num = int(sendInfo)
            except ValueError:
                self.__signal.emit('收到的信息有误。可能原因：服务器协议不一致或连接超时。')
                f.close()
                return 2
            sent_size+=BUFSIZ*sent_packet_num
            f.read(BUFSIZ*sent_packet_num)
            self.__signal.emit('开始断点续传')
            #total_datasize += (filesize-BUFSIZ*sent_packet_num)
        while True:
            data = f.read(BUFSIZ)
            if not data:
                break
            cliSock.send(data)
            sent_size+=len(data)
            self.__signal.emit('\r已发送: '+str("%f" % (sent_size/fileSize*100))+'%')
    
        f.close()
        #print('\r已发送：'+str("%f" % (100))+'%')
    
        info = cliSock.recv(3)
        if info.decode()=='md5':
            md5 = getFileMD5(filename)
            # 发送原始文件MD5
            self.__signal.emit(md5)
            cliSock.send(md5.encode())
            sendInfo = cliSock.recv(3)
    
        if info.decode()=='trc':
            self.__signal.emit('True sent.')
        else:
            self.__signal.emit('False sent.'+filename)
            log = open('err.log', 'a')
            log.write(str(time.time())+' '+filename+' '+'False \n')
            log.close()
    
        if is_compressed == 1:
            os.remove(filename)
    
    def btn_send(self):
        mode = 'normal'

        self.cancelButton.setEnabled(True)
        ip_addr = self.ipTextEdit.toPlainText()
        portStr = self.portTextEdit.toPlainText()
        src_path = self.pathTextEdit.toPlainText()
        # 处理空值
        if ip_addr == '':
            QMessageBox.information(self, '错误', '未指定IP地址', QMessageBox.Yes)
            return False
        if portStr == '':
            QMessageBox.information(self, '错误', '未指定端口', QMessageBox.Yes)
            return False
        port = int(portStr)
        if port > 65535 | port < 0:
            QMessageBox.information(
                self, '错误', '端口不在正确范围(0~65535)', QMessageBox.Yes)
            return False
        if src_path == '':
            QMessageBox.information(self, '错误', '未指定路径', QMessageBox.Yes)
            return False
        if os.path.exists(src_path) == False:
            self.textBrowser.insertPlainText('文件夹不存在！\n')
            sys.exit(1)
        self.src_path = src_path
        relativePath = getFileList(src_path)
        try:
            cliSock = socket(AF_INET, SOCK_STREAM)
            cliSock.connect((ip_addr, port))
            for filename in relativePath:
                if self.send(cliSock, filename, src_path, mode) == -1:
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
            endLen = 0xffffffff
            cliSock.send(endLen.to_bytes(4, byteorder='big'))
            cliSock.close()
        except gaierror:
            self.textBrowser.insertPlainText('IP地址不正确！\n')
        except OverflowError:
            self.textBrowser.insertPlainText('端口号不正确！\n')
        except TypeError as info:
            self.textBrowser.insertPlainText(
                '类型错误。服务器端可能中断了连接。\n'+str(info)+'\n')
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
        # 异常中断理应清理tempzip缓存
        relativePath = getFileList(src_path)
        for filename in relativePath:
            if os.path.exists(filename) and filename.endswith('tempzip'):
                self.textBrowser.insertPlainText('删除'+filename+'\n')
                os.remove(filename)
        self.textBrowser.insertPlainText('已清理传输缓存。\n')
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)

    def btn_cancel(self):
        raise KeyboardInterrupt


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainServerForm()
    myWin.show()
    sys.exit(app.exec_())
