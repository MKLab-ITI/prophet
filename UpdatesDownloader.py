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

# Form implementation generated from reading ui file 'ui\UpdatesDownloader.ui'
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

class Ui_UpdatesDownloader(object):
    def setupUi(self, UpdatesDownloader):
        UpdatesDownloader.setObjectName(_fromUtf8("UpdatesDownloader"))
        UpdatesDownloader.resize(456, 136)
        self.gridLayout = QtGui.QGridLayout(UpdatesDownloader)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lblMessage = QtGui.QLabel(UpdatesDownloader)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lblMessage.setFont(font)
        self.lblMessage.setObjectName(_fromUtf8("lblMessage"))
        self.verticalLayout.addWidget(self.lblMessage)
        self.lblCurrentJob = QtGui.QLabel(UpdatesDownloader)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lblCurrentJob.setFont(font)
        self.lblCurrentJob.setObjectName(_fromUtf8("lblCurrentJob"))
        self.verticalLayout.addWidget(self.lblCurrentJob)
        self.progressBarUpdate = QtGui.QProgressBar(UpdatesDownloader)
        self.progressBarUpdate.setProperty("value", 24)
        self.progressBarUpdate.setOrientation(QtCore.Qt.Horizontal)
        self.progressBarUpdate.setObjectName(_fromUtf8("progressBarUpdate"))
        self.verticalLayout.addWidget(self.progressBarUpdate)
        spacerItem = QtGui.QSpacerItem(20, 28, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.btnCancel = QtGui.QPushButton(UpdatesDownloader)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 1, 0, 1, 1, QtCore.Qt.AlignRight)

        self.retranslateUi(UpdatesDownloader)
        QtCore.QMetaObject.connectSlotsByName(UpdatesDownloader)

    def retranslateUi(self, UpdatesDownloader):
        UpdatesDownloader.setWindowTitle(_translate("UpdatesDownloader", "Downloading updates...", None))
        self.lblMessage.setText(_translate("UpdatesDownloader", "Performing PROPheT update. Please wait...", None))
        self.lblCurrentJob.setText(_translate("UpdatesDownloader", "Current job", None))
        self.btnCancel.setText(_translate("UpdatesDownloader", "Cancel", None))

