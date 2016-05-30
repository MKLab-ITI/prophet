# -*- coding: utf-8 -*-

"""
This file is part of the PROPheT tool.
Copyright (C) 2016: MKLab <pmitzias@iti.gr; mriga@iti.gr; skontopo@iti.gr>
http://mklab.iti.gr/project/prophet-ontology-populator
https://github.com/MKLab-ITI/prophet
Licensed under the Apache License, Version 2.0 (the "License").
You may use this file in compliance with the License. 
For more details, see LICENCE file. 
"""


# Form implementation generated from reading ui file 'ui\MessageBox.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MessageBox(object):
    def setupUi(self, MessageBox):
        MessageBox.setObjectName(_fromUtf8("MessageBox"))
        MessageBox.resize(417, 139)
        MessageBox.setMinimumSize(QtCore.QSize(380, 0))
        self.gridLayout = QtGui.QGridLayout(MessageBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblMessage = QtGui.QLabel(MessageBox)
        self.lblMessage.setMinimumSize(QtCore.QSize(400, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblMessage.setFont(font)
        self.lblMessage.setAlignment(QtCore.Qt.AlignCenter)
        self.lblMessage.setWordWrap(True)
        self.lblMessage.setObjectName(_fromUtf8("lblMessage"))
        self.gridLayout.addWidget(self.lblMessage, 0, 0, 1, 1)
        self.btnClose = QtGui.QPushButton(MessageBox)
        self.btnClose.setMinimumSize(QtCore.QSize(75, 0))
        self.btnClose.setMaximumSize(QtCore.QSize(75, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.btnClose.setFont(font)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 1, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.retranslateUi(MessageBox)
        QtCore.QMetaObject.connectSlotsByName(MessageBox)

    def retranslateUi(self, MessageBox):
        MessageBox.setWindowTitle(_translate("MessageBox", "Message", None))
        self.lblMessage.setText(_translate("MessageBox", "TextLabel", None))
        self.btnClose.setText(_translate("MessageBox", "Close", None))

