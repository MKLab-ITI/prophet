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

# Form implementation generated from reading ui file 'ui\About.ui'
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

class Ui_DialogAbout(object):
    def setupUi(self, DialogAbout):
        DialogAbout.setObjectName(_fromUtf8("DialogAbout"))
        DialogAbout.resize(389, 203)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/about.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogAbout.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(DialogAbout)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btnOK = QtGui.QPushButton(DialogAbout)
        self.btnOK.setEnabled(True)
        self.btnOK.setMinimumSize(QtCore.QSize(75, 0))
        self.btnOK.setMaximumSize(QtCore.QSize(75, 16777215))
        self.btnOK.setObjectName(_fromUtf8("btnOK"))
        self.gridLayout.addWidget(self.btnOK, 3, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblLogo = QtGui.QLabel(DialogAbout)
        self.lblLogo.setMaximumSize(QtCore.QSize(100, 78))
        self.lblLogo.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblLogo.setFrameShadow(QtGui.QFrame.Plain)
        self.lblLogo.setText(_fromUtf8(""))
        self.lblLogo.setPixmap(QtGui.QPixmap(_fromUtf8(":/images/PROPheT Logo.png")))
        self.lblLogo.setScaledContents(True)
        self.lblLogo.setObjectName(_fromUtf8("lblLogo"))
        self.horizontalLayout.addWidget(self.lblLogo)
        self.lblProphet = QtGui.QLabel(DialogAbout)
        self.lblProphet.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblProphet.setOpenExternalLinks(True)
        self.lblProphet.setObjectName(_fromUtf8("lblProphet"))
        self.horizontalLayout.addWidget(self.lblProphet)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.line = QtGui.QFrame(DialogAbout)
        self.line.setFrameShadow(QtGui.QFrame.Raised)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.lblMKLab = QtGui.QLabel(DialogAbout)
        self.lblMKLab.setWordWrap(True)
        self.lblMKLab.setOpenExternalLinks(True)
        self.lblMKLab.setObjectName(_fromUtf8("lblMKLab"))
        self.gridLayout.addWidget(self.lblMKLab, 2, 0, 1, 2)

        self.retranslateUi(DialogAbout)
        QtCore.QMetaObject.connectSlotsByName(DialogAbout)

    def retranslateUi(self, DialogAbout):
        DialogAbout.setWindowTitle(_translate("DialogAbout", "About PROPheT", None))
        self.btnOK.setText(_translate("DialogAbout", "OK", None))
        self.lblProphet.setText(_translate("DialogAbout", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">PROPheT - PeRicles Ontology Population Tool</span></p><p align=\"center\"><span style=\" font-size:10pt;\">version 1.2</span></p></body></html>", None))
        self.lblMKLab.setText(_translate("DialogAbout", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">PROPheT was created by </span><a href=\"http://mklab.iti.gr/\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">MKLab group</span></a></p><p align=\"center\"><span style=\" font-size:10pt;\">under the scope of </span><a href=\"http://pericles-project.eu/\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">PERICLES</span></a><span style=\" font-size:10pt;\"> FP7 research project.</span></p></body></html>", None))

import about_resources_rc
