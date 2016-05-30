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

# Form implementation generated from reading ui file 'ui\AddMyModel.ui'
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

class Ui_AddMyModel(object):
    def setupUi(self, AddMyModel):
        AddMyModel.setObjectName(_fromUtf8("AddMyModel"))
        AddMyModel.resize(417, 139)
        self.gridLayout = QtGui.QGridLayout(AddMyModel)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblModelName = QtGui.QLabel(AddMyModel)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblModelName.setFont(font)
        self.lblModelName.setObjectName(_fromUtf8("lblModelName"))
        self.horizontalLayout.addWidget(self.lblModelName)
        self.lineEditModelName = QtGui.QLineEdit(AddMyModel)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditModelName.sizePolicy().hasHeightForWidth())
        self.lineEditModelName.setSizePolicy(sizePolicy)
        self.lineEditModelName.setMinimumSize(QtCore.QSize(300, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEditModelName.setFont(font)
        self.lineEditModelName.setObjectName(_fromUtf8("lineEditModelName"))
        self.horizontalLayout.addWidget(self.lineEditModelName)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 3)
        self.btnOK = QtGui.QPushButton(AddMyModel)
        self.btnOK.setEnabled(True)
        self.btnOK.setMinimumSize(QtCore.QSize(75, 0))
        self.btnOK.setMaximumSize(QtCore.QSize(75, 16777215))
        self.btnOK.setDefault(True)
        self.btnOK.setObjectName(_fromUtf8("btnOK"))
        self.gridLayout.addWidget(self.btnOK, 2, 1, 1, 1)
        self.btnCancel = QtGui.QPushButton(AddMyModel)
        self.btnCancel.setMinimumSize(QtCore.QSize(75, 0))
        self.btnCancel.setMaximumSize(QtCore.QSize(75, 16777215))
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 2, 2, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lblModelURL = QtGui.QLabel(AddMyModel)
        self.lblModelURL.setMinimumSize(QtCore.QSize(38, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblModelURL.setFont(font)
        self.lblModelURL.setObjectName(_fromUtf8("lblModelURL"))
        self.horizontalLayout_3.addWidget(self.lblModelURL)
        self.lineEditModelURL = QtGui.QLineEdit(AddMyModel)
        self.lineEditModelURL.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEditModelURL.setFont(font)
        self.lineEditModelURL.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.lineEditModelURL.setObjectName(_fromUtf8("lineEditModelURL"))
        self.horizontalLayout_3.addWidget(self.lineEditModelURL)
        self.btnOpenFile = QtGui.QPushButton(AddMyModel)
        self.btnOpenFile.setMaximumSize(QtCore.QSize(20, 16777215))
        self.btnOpenFile.setObjectName(_fromUtf8("btnOpenFile"))
        self.horizontalLayout_3.addWidget(self.btnOpenFile)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 3)
        self.btnOK.raise_()
        self.btnCancel.raise_()

        self.retranslateUi(AddMyModel)
        QtCore.QMetaObject.connectSlotsByName(AddMyModel)

    def retranslateUi(self, AddMyModel):
        AddMyModel.setWindowTitle(_translate("AddMyModel", "Add a new model", None))
        self.lblModelName.setText(_translate("AddMyModel", "Name:", None))
        self.lineEditModelName.setToolTip(_translate("AddMyModel", "Type a name for the new model", None))
        self.btnOK.setToolTip(_translate("AddMyModel", "Save new model", None))
        self.btnOK.setText(_translate("AddMyModel", "OK", None))
        self.btnCancel.setText(_translate("AddMyModel", "Cancel", None))
        self.lblModelURL.setToolTip(_translate("AddMyModel", "Type a URL for the new model", None))
        self.lblModelURL.setText(_translate("AddMyModel", "URI:", None))
        self.lineEditModelURL.setToolTip(_translate("AddMyModel", "Type a URL for the new model", None))
        self.btnOpenFile.setToolTip(_translate("AddMyModel", "Open file...", None))
        self.btnOpenFile.setText(_translate("AddMyModel", "...", None))

