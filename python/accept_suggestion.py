# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'accept_suggestion.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_suggestion_window(object):
    def setupUi(self, suggestion_window):
        suggestion_window.setObjectName("suggestion_window")
        suggestion_window.resize(256, 158)
        self.centralwidget = QtWidgets.QWidget(suggestion_window)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.pushButton_NO = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_NO.setCheckable(True)
        self.pushButton_NO.setAutoExclusive(False)
        self.pushButton_NO.setObjectName("pushButton_NO")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.pushButton_NO)
        self.pushButton_YES = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_YES.setCheckable(True)
        self.pushButton_YES.setAutoExclusive(False)
        self.pushButton_YES.setObjectName("pushButton_YES")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.pushButton_YES)
        suggestion_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(suggestion_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 256, 20))
        self.menubar.setObjectName("menubar")
        suggestion_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(suggestion_window)
        self.statusbar.setObjectName("statusbar")
        suggestion_window.setStatusBar(self.statusbar)

        self.retranslateUi(suggestion_window)
        QtCore.QMetaObject.connectSlotsByName(suggestion_window)

    def retranslateUi(self, suggestion_window):
        _translate = QtCore.QCoreApplication.translate
        suggestion_window.setWindowTitle(_translate("suggestion_window", "Are you sure?"))
        self.label_3.setText(_translate("suggestion_window", "accept suggestion?"))
        self.pushButton_NO.setText(_translate("suggestion_window", "NO"))
        self.pushButton_YES.setText(_translate("suggestion_window", "YES"))

