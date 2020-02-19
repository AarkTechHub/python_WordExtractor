# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Forms\main.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import xlrd, xlwt
from xlwt import Workbook
from PyQt5.QtWidgets import QFileDialog
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import uuid
import urllib.parse
import time

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(651, 447)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.txt_area_debug = QtWidgets.QTextEdit(self.centralwidget)
        self.txt_area_debug.setGeometry(QtCore.QRect(10, 220, 631, 181))
        self.txt_area_debug.setObjectName("txt_area_debug")
        self.txt_filename = QtWidgets.QLineEdit(self.centralwidget)
        self.txt_filename.setGeometry(QtCore.QRect(10, 60, 411, 31))
        self.txt_filename.setObjectName("txt_filename")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 40, 211, 16))
        self.label.setObjectName("label")
        self.btn_file_picker = QtWidgets.QPushButton(self.centralwidget)
        self.btn_file_picker.setGeometry(QtCore.QRect(430, 60, 151, 31))
        self.btn_file_picker.setObjectName("btn_file_picker")
        self.btn_process = QtWidgets.QPushButton(self.centralwidget)
        self.btn_process.setGeometry(QtCore.QRect(10, 120, 131, 41))
        self.btn_process.setObjectName("btn_process")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 651, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AARK TECH HUB Word Extractor"))
        self.label.setText(_translate("MainWindow", "Selected File"))
        self.btn_file_picker.setText(_translate("MainWindow", "Pick File To Process"))
        self.btn_process.setText(_translate("MainWindow", "Process"))
        self.customUi(MainWindow)

    def customUi(self, MainWindow):
        self.mw = MainWindow
        self.btn_file_picker.clicked.connect(lambda : self.filePicker_evt())
        self.btn_process.clicked.connect(lambda : self.fileProcess_evt())
        self.resDict = {}

    def filePicker_evt(self):
        print("picker")
        try:
            filename = QFileDialog.getOpenFileName(self.mw,'Open File')
            print(filename[0])
            self.txt_filename.setText(filename[0])
        except Exception as ex:
            print(ex)

    def fileProcess_evt(self):
        print('process : ' + self.txt_filename.text())
        wb = xlrd.open_workbook(self.txt_filename.text())
        sheet = wb.sheet_by_index(0)
        print(sheet.col_values(0))

        linkList = sheet.col_values(0)
        linkList.pop(0)
        for link in linkList:
            print(link)
            self.getWords(link)
        self.createFile("result_" + str(uuid.uuid4()) + ".xls")

    def getWords(self,link):
        try:
            driver = webdriver.Chrome(executable_path="chromedriver.exe")
            driver.implicitly_wait(10)
            driver.get(link)
            data = driver.page_source
            resList = self.extractWords(data)
            # self.resDict[link] = {'words':resList}
            print(resList)

            button = driver.find_element_by_id('tab_related_items')
            button.click()
            time.sleep(10)
            attachlink = driver.find_element(By.XPATH,"//div[@id='attachments_holder']")
            attachlink_txt = ""
            if(attachlink.text != None):
                print(attachlink.text)
                attachlink_txt = attachlink.text
            else:
                print('None')
            # self.resDict[link]={'attachment':'attach'}#driver.find_element(By.XPATH,"//div[@id='attachments_holder']").text
            self.resDict[link] = {'words': resList,'attachment':attachlink_txt}
            self.txt_area_debug.append("Ran -> " + link + ", Got -> " + str(len(resList)))
            driver.close()
        except Exception as ex:
            print(ex)
            self.txt_area_debug.append("Got Exception in Link ->" + link + ", Exception -> " + str(ex))

    def extractWords(self,data):
        # list1 = re.findall(r'^b0[\w]+', data, re.MULTILINE)
        # list2 = re.findall(r'^B0[\w]+', data, re.MULTILINE)
        data = urllib.parse.unquote(data)
        # print(data)
        list1 = re.findall(r'[\s|,|\"|:]X0[\w]+', data, re.MULTILINE)
        list2 = re.findall(r"[\s|,|\"|:]B0[\w]+", data, re.MULTILINE)
        list3 = re.findall(r"[\s|,|\"|:][\d]+", data, re.MULTILINE)
        li = []
        li2 = []
        li3 = []
        for d in list1:
            data = d[0:11]
            data = data.strip()
            data = data.strip('"')
            data = data.strip(':')
            data = data.strip(',')
            if len(data) == 10:
                li.append(data)

        for d1 in list2:
            data2 = d1[0:11]
            data2 = data2.strip()
            data2 = data2.strip('"')
            data2 = data2.strip(':')
            data2 = data2.strip(',')
            if len(data2) == 10:
                li2.append(data2)

        for d2 in list3:
            data3 = d2[0:11]
            data3 = data3.strip()
            data3 = data3.strip('"')
            data3 = data3.strip(':')
            data3 = data3.strip(',')
            if len(data3) == 10:
                li3.append(data3)

        res_list = li + li2 + li3

        return res_list

    def createFile(self,filename):
        try:
            wb = Workbook()
            sheet1 = wb.add_sheet('Sheet 1')
            links = list(self.resDict.keys())
            print(links)
            for i in range(len(links)):
                sheet1.write(i,0,links[i])
                sheet1.write(i,1,",".join(map(str, self.resDict[links[i]]['words'])))
                sheet1.write(i,2, self.resDict[links[i]]['attachment'])
            wb.save(filename)
            self.txt_area_debug.append("Created Result File at -> " + filename)
        except Exception as ex:
            print(ex)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

