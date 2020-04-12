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
#如果导入错误，  请把servergui.py文件复制进 python\Lib\site-packeges\下
import servergui
import client
BUFSIZ = 1024

class MyMainClientForm(QMainWindow, servergui.Ui_Form):
    def __init__(self, parent=None):
        super(MyMainClientForm, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Client")
        self.pushButton.clicked.connect(self.openFile)
        '''注释部分，即为 按钮添加 recv 函数 事件'''
        #self.pushButton_2.clicked.connect(self.btn_send)

        #打开文件目录选择文件
    def openFile(self):
        get_directory_path = QFileDialog.getExistingDirectory(self,
                                                              "选取指定文件夹",
                                                              "C:/")
        self.textEdit_3.setText(str(get_directory_path))
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainClientForm()
    myWin.show()
    sys.exit(app.exec_())