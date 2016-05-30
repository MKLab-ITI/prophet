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

# Form implementation generated from reading ui file 'ui\AddNamespace.ui'
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

class Ui_AddNamespace(object):
    def setupUi(self, AddNamespace):
        AddNamespace.setObjectName(_fromUtf8("AddNamespace"))
        AddNamespace.resize(417, 139)
        self.gridLayout = QtGui.QGridLayout(AddNamespace)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblNamespacePrefix = QtGui.QLabel(AddNamespace)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblNamespacePrefix.setFont(font)
        self.lblNamespacePrefix.setObjectName(_fromUtf8("lblNamespacePrefix"))
        self.horizontalLayout.addWidget(self.lblNamespacePrefix)
        self.lineEditNamespacePrefix = QtGui.QLineEdit(AddNamespace)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditNamespacePrefix.sizePolicy().hasHeightForWidth())
        self.lineEditNamespacePrefix.setSizePolicy(sizePolicy)
        self.lineEditNamespacePrefix.setMinimumSize(QtCore.QSize(300, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEditNamespacePrefix.setFont(font)
        self.lineEditNamespacePrefix.setObjectName(_fromUtf8("lineEditNamespacePrefix"))
        self.horizontalLayout.addWidget(self.lineEditNamespacePrefix)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lblNamespaceURL = QtGui.QLabel(AddNamespace)
        self.lblNamespaceURL.setMinimumSize(QtCore.QSize(37, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblNamespaceURL.setFont(font)
        self.lblNamespaceURL.setObjectName(_fromUtf8("lblNamespaceURL"))
        self.horizontalLayout_2.addWidget(self.lblNamespaceURL)
        self.lineEditNamespaceURL = QtGui.QLineEdit(AddNamespace)
        self.lineEditNamespaceURL.setMinimumSize(QtCore.QSize(300, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEditNamespaceURL.setFont(font)
        self.lineEditNamespaceURL.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.lineEditNamespaceURL.setObjectName(_fromUtf8("lineEditNamespaceURL"))
        self.horizontalLayout_2.addWidget(self.lineEditNamespaceURL)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 3)
        self.btnCancel = QtGui.QPushButton(AddNamespace)
        self.btnCancel.setMinimumSize(QtCore.QSize(75, 0))
        self.btnCancel.setMaximumSize(QtCore.QSize(75, 16777215))
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 2, 2, 1, 1)
        self.btnOK = QtGui.QPushButton(AddNamespace)
        self.btnOK.setEnabled(True)
        self.btnOK.setMinimumSize(QtCore.QSize(75, 0))
        self.btnOK.setMaximumSize(QtCore.QSize(75, 16777215))
        self.btnOK.setDefault(True)
        self.btnOK.setObjectName(_fromUtf8("btnOK"))
        self.gridLayout.addWidget(self.btnOK, 2, 1, 1, 1)

        self.retranslateUi(AddNamespace)
        QtCore.QMetaObject.connectSlotsByName(AddNamespace)

    def retranslateUi(self, AddNamespace):
        AddNamespace.setWindowTitle(_translate("AddNamespace", "Add a new namespace", None))
        self.lblNamespacePrefix.setToolTip(_translate("AddNamespace", "Type a prefix for the new namespace", None))
        self.lblNamespacePrefix.setText(_translate("AddNamespace", "Prefix:", None))
        self.lineEditNamespacePrefix.setToolTip(_translate("AddNamespace", "Type a prefix for the new namespace", None))
        self.lblNamespaceURL.setToolTip(_translate("AddNamespace", "Type a URL for the new namespace", None))
        self.lblNamespaceURL.setText(_translate("AddNamespace", "URI:", None))
        self.lineEditNamespaceURL.setToolTip(_translate("AddNamespace", "Type a URL for the new namespace", None))
        self.lineEditNamespaceURL.setText(_translate("AddNamespace", "http://", None))
        self.btnCancel.setText(_translate("AddNamespace", "Cancel", None))
        self.btnOK.setText(_translate("AddNamespace", "OK", None))

