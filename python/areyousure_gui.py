# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'areyousure.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_areyousure_window(object):
    def setupUi(self, areyousure_window):
        areyousure_window.setObjectName("areyousure_window")
        areyousure_window.resize(324, 152)
        areyousure_window.setMinimumSize(QtCore.QSize(324, 152))
        areyousure_window.setMaximumSize(QtCore.QSize(324, 152))
        self.centralwidget = QtWidgets.QWidget(areyousure_window)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton_YES = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_YES.setGeometry(QtCore.QRect(70, 60, 84, 25))
        self.pushButton_YES.setCheckable(True)
        self.pushButton_YES.setAutoExclusive(False)
        self.pushButton_YES.setObjectName("pushButton_YES")
        self.pushButton_NO = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_NO.setGeometry(QtCore.QRect(170, 60, 84, 25))
        self.pushButton_NO.setCheckable(True)
        self.pushButton_NO.setAutoExclusive(False)
        self.pushButton_NO.setObjectName("pushButton_NO")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(100, 0, 121, 51))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        areyousure_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(areyousure_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 324, 20))
        self.menubar.setObjectName("menubar")
        areyousure_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(areyousure_window)
        self.statusbar.setObjectName("statusbar")
        areyousure_window.setStatusBar(self.statusbar)

        self.retranslateUi(areyousure_window)
        QtCore.QMetaObject.connectSlotsByName(areyousure_window)

    def retranslateUi(self, areyousure_window):
        _translate = QtCore.QCoreApplication.translate
        areyousure_window.setWindowTitle(_translate("areyousure_window", "Are you sure?"))
        self.pushButton_YES.setText(_translate("areyousure_window", "YES"))
        self.pushButton_NO.setText(_translate("areyousure_window", "NO"))
        self.label_3.setText(_translate("areyousure_window", "are you sure?"))

