# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'servergui2.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!
import sys
from socket import *
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication
BUFSIZ = 1024
import server
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
        self.pushButton_2.setText(_translate("Form", "接收"))
        self.pushButton_3.setText(_translate("Form", "取消"))
    #封装于按钮事件  recv
    '''
    不建议使用!   recv &send 函数里的提示信息， 暂时没有移植到 窗口，仍在console 输出。
    '''
    def btn_recv(self):
        '''
        dst_path=self.textEdit_3.toPlainText()
        ip_addr = self.textEdit.toPlainText()
        temp = self.textEdit_2.toPlainText()
        port = 6000
        serSock = socket(AF_INET, SOCK_STREAM)  # 定义套接字
        serSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serSock.bind((ip_addr, port))  # 绑定地址
        serSock.listen(5)  # 规定传入连接请求的最大数，适用于异步
        print('等待连接...')
        cliSock, addr = serSock.accept()
        print('...连接自:', addr)

        server.recv(cliSock, dst_path)
        serSock.close()
        print(ip_addr+" "+dst_path+" ")
        print(port)
    def btn_send(self):
        return
        '''
class MyMainServerForm(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MyMainServerForm, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Server")
        self.pushButton.clicked.connect(self.openFile)
        '''注释部分，即为 按钮添加 recv 函数 事件'''
        #self.pushButton_2.clicked.connect(self.btn_recv)
    def openFile(self):
        get_directory_path = QFileDialog.getExistingDirectory(self,
                                                              "选取指定文件夹",
                                                              "C:/")
        self.textEdit_3.setText(str(get_directory_path))
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainServerForm()
    myWin.show()
    sys.exit(app.exec_())