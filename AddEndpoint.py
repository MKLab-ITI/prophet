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

# Form implementation generated from reading ui file 'ui\AddEndpoint.ui'
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

class Ui_AddEndpoint(object):
    def setupUi(self, AddEndpoint):
        AddEndpoint.setObjectName(_fromUtf8("AddEndpoint"))
        AddEndpoint.resize(417, 139)
        self.gridLayout = QtGui.QGridLayout(AddEndpoint)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lblEndpointName = QtGui.QLabel(AddEndpoint)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblEndpointName.setFont(font)
        self.lblEndpointName.setObjectName(_fromUtf8("lblEndpointName"))
        self.horizontalLayout_2.addWidget(self.lblEndpointName)
        self.lineEditEndpointName = QtGui.QLineEdit(AddEndpoint)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditEndpointName.sizePolicy().hasHeightForWidth())
        self.lineEditEndpointName.setSizePolicy(sizePolicy)
        self.lineEditEndpointName.setMinimumSize(QtCore.QSize(300, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEditEndpointName.setFont(font)
        self.lineEditEndpointName.setObjectName(_fromUtf8("lineEditEndpointName"))
        self.horizontalLayout_2.addWidget(self.lineEditEndpointName)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 3)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lblEndpointURL = QtGui.QLabel(AddEndpoint)
        self.lblEndpointURL.setMinimumSize(QtCore.QSize(90, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblEndpointURL.setFont(font)
        self.lblEndpointURL.setObjectName(_fromUtf8("lblEndpointURL"))
        self.horizontalLayout_3.addWidget(self.lblEndpointURL)
        self.lineEditEndpointURL = QtGui.QLineEdit(AddEndpoint)
        self.lineEditEndpointURL.setMinimumSize(QtCore.QSize(300, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEditEndpointURL.setFont(font)
        self.lineEditEndpointURL.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.lineEditEndpointURL.setObjectName(_fromUtf8("lineEditEndpointURL"))
        self.horizontalLayout_3.addWidget(self.lineEditEndpointURL)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 3)
        self.btnCancel = QtGui.QPushButton(AddEndpoint)
        self.btnCancel.setMinimumSize(QtCore.QSize(75, 0))
        self.btnCancel.setMaximumSize(QtCore.QSize(75, 16777215))
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 2, 2, 1, 1)
        self.btnOK = QtGui.QPushButton(AddEndpoint)
        self.btnOK.setEnabled(True)
        self.btnOK.setMinimumSize(QtCore.QSize(75, 0))
        self.btnOK.setMaximumSize(QtCore.QSize(75, 16777215))
        self.btnOK.setDefault(True)
        self.btnOK.setObjectName(_fromUtf8("btnOK"))
        self.gridLayout.addWidget(self.btnOK, 2, 1, 1, 1)

        self.retranslateUi(AddEndpoint)
        QtCore.QMetaObject.connectSlotsByName(AddEndpoint)

    def retranslateUi(self, AddEndpoint):
        AddEndpoint.setWindowTitle(_translate("AddEndpoint", "Add a new endpoint", None))
        self.lblEndpointName.setToolTip(_translate("AddEndpoint", "Type a name for the new endpoint", None))
        self.lblEndpointName.setText(_translate("AddEndpoint", "Endpoint name:", None))
        self.lineEditEndpointName.setToolTip(_translate("AddEndpoint", "Type a name for the new endpoint", None))
        self.lblEndpointURL.setToolTip(_translate("AddEndpoint", "Type a URL for the new endpoint", None))
        self.lblEndpointURL.setText(_translate("AddEndpoint", "Endpoint URI:", None))
        self.lineEditEndpointURL.setToolTip(_translate("AddEndpoint", "Type a URL for the new endpoint", None))
        self.lineEditEndpointURL.setText(_translate("AddEndpoint", "http://", None))
        self.btnCancel.setText(_translate("AddEndpoint", "Cancel", None))
        self.btnOK.setToolTip(_translate("AddEndpoint", "Save new endpoint", None))
        self.btnOK.setText(_translate("AddEndpoint", "OK", None))

