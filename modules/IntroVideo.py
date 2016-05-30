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

# Form implementation generated from reading ui file 'ui\IntroVideo.ui'
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

class Ui_DialogIntroVideo(object):
    def setupUi(self, DialogIntroVideo):
        DialogIntroVideo.setObjectName(_fromUtf8("DialogIntroVideo"))
        DialogIntroVideo.resize(546, 384)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DialogIntroVideo.sizePolicy().hasHeightForWidth())
        DialogIntroVideo.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/PROPheT Logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogIntroVideo.setWindowIcon(icon)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DialogIntroVideo)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.videoPlayerIntro = phonon.Phonon.VideoPlayer(DialogIntroVideo)
        self.videoPlayerIntro.setMinimumSize(QtCore.QSize(0, 0))
        self.videoPlayerIntro.setObjectName(_fromUtf8("videoPlayerIntro"))
        self.verticalLayout_2.addWidget(self.videoPlayerIntro)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnPlayPause = QtGui.QPushButton(DialogIntroVideo)
        self.btnPlayPause.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/play.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnPlayPause.setIcon(icon1)
        self.btnPlayPause.setFlat(True)
        self.btnPlayPause.setObjectName(_fromUtf8("btnPlayPause"))
        self.horizontalLayout.addWidget(self.btnPlayPause)
        self.seekSlider = phonon.Phonon.SeekSlider(DialogIntroVideo)
        self.seekSlider.setObjectName(_fromUtf8("seekSlider"))
        self.horizontalLayout.addWidget(self.seekSlider)
        self.volumeSlider = phonon.Phonon.VolumeSlider(DialogIntroVideo)
        self.volumeSlider.setMinimumSize(QtCore.QSize(100, 0))
        self.volumeSlider.setMaximumSize(QtCore.QSize(100, 16777215))
        self.volumeSlider.setObjectName(_fromUtf8("volumeSlider"))
        self.horizontalLayout.addWidget(self.volumeSlider)
        self.btnFullScreen = QtGui.QPushButton(DialogIntroVideo)
        self.btnFullScreen.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/fullscreen.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnFullScreen.setIcon(icon2)
        self.btnFullScreen.setFlat(True)
        self.btnFullScreen.setObjectName(_fromUtf8("btnFullScreen"))
        self.horizontalLayout.addWidget(self.btnFullScreen)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtGui.QFrame(DialogIntroVideo)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.checkBoxDontShowAgain = QtGui.QCheckBox(DialogIntroVideo)
        self.checkBoxDontShowAgain.setChecked(True)
        self.checkBoxDontShowAgain.setObjectName(_fromUtf8("checkBoxDontShowAgain"))
        self.horizontalLayout_2.addWidget(self.checkBoxDontShowAgain)
        self.btnExit = QtGui.QPushButton(DialogIntroVideo)
        self.btnExit.setMaximumSize(QtCore.QSize(70, 16777215))
        self.btnExit.setObjectName(_fromUtf8("btnExit"))
        self.horizontalLayout_2.addWidget(self.btnExit, QtCore.Qt.AlignRight)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.videoPlayerIntro.raise_()
        self.btnExit.raise_()
        self.checkBoxDontShowAgain.raise_()
        self.line.raise_()
        self.seekSlider.raise_()
        self.btnPlayPause.raise_()
        self.volumeSlider.raise_()
        self.btnFullScreen.raise_()

        self.retranslateUi(DialogIntroVideo)
        QtCore.QMetaObject.connectSlotsByName(DialogIntroVideo)

    def retranslateUi(self, DialogIntroVideo):
        DialogIntroVideo.setWindowTitle(_translate("DialogIntroVideo", "Welcome to PROPheT!", None))
        self.checkBoxDontShowAgain.setText(_translate("DialogIntroVideo", "Don\'t show again", None))
        self.btnExit.setText(_translate("DialogIntroVideo", "Skip", None))

from PyQt4 import phonon
import intro_video_resources_rc
