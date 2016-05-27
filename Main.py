"""
This file is part of the PROPheT tool.

Copyright (C) 2016: MKLab <pmitzias@iti.gr; mriga@iti.gr; skontopo@iti.gr>

http://mklab.iti.gr/project/prophet-ontology-populator
https://github.com/MKLab-ITI/prophet

Licensed under the Apache License, Version 2.0 (the "License").
You may use this file in compliance with the License. 
For more details, see LICENCE file. 

"""

__authors__ = 'Panagiotis Mitzias (pmitzias@iti.gr), Marina Riga (mriga@iti.gr)'

import sys, time

# This line disables the creation of a log file from py2exe
sys.stderr = sys.stdout

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
import Functions
from PyQt4.QtGui import QTreeWidgetItem, QWizard

from rdflib import Graph, util
from rdflib.namespace import NamespaceManager
from shutil import copyfile
from subprocess import Popen
from os import remove, path

from MainWindow import Ui_MainWindow
from AddEndpoint import Ui_AddEndpoint
from AddNamespace import Ui_AddNamespace
from AddMyModel import Ui_AddMyModel
from Preferences import Ui_Preferences
from SearchByClassWizard import Ui_WizardSearchByClassName
from SearchByInstanceWizard import Ui_WizardSearchByInstanceName
from EnrichInstanceWizard import Ui_WizardEnrichInstance
from SearchByInstanceLabelWizard import Ui_WizardSearchByInstanceLabel
from About import Ui_DialogAbout
from UpdatesDownloader import Ui_UpdatesDownloader

import main_window_resources_rc
import preferences_resources_rc
import search_by_class_wizard_resources_rc
import search_by_existing_instance_wizard_resources_rc
import search_by_instance_label_wizard_resources_rc
import enrich_instance_wizard_resources_rc
import messagebox_resources_rc


class Main(QtGui.QMainWindow):
    graph = Graph()
    myModelName = ''
    changesMadeToModel = False

    # Main window constructor
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # MAKE CONNECTIONS
        self.ui.actionSelect_endpoint.triggered.connect(self.showEndpointPreferences)
        self.ui.actionToolBarSelect_endpoint.triggered.connect(self.showEndpointPreferences)

        self.ui.actionView_Log.triggered.connect(self.showLog)
        self.ui.actionToolBarLog.triggered.connect(self.showLog)

        self.ui.actionPreferences.triggered.connect(self.showDialogPreferences)
        self.ui.actionPreferencesToolBar.triggered.connect(self.showDialogPreferences)

        self.ui.actionEdit_namespaces.triggered.connect(self.showNamespacesPreferences)
        self.ui.actionToolBarNamespaces.triggered.connect(self.showNamespacesPreferences)

        self.ui.actionLoad_model.triggered.connect(self.showMyModelsPreferences)
        self.ui.actionToolBarLoad_my_model.triggered.connect(self.showMyModelsPreferences)

        self.ui.actionEdit_mapping.triggered.connect(self.showMappingPreferences)
        self.ui.actionToolBarMapping.triggered.connect(self.showMappingPreferences)

        self.ui.actionExit.triggered.connect(self.close)

        self.ui.actionSearch_by_class_name.triggered.connect(self.showSearchByClassWizard)
        self.ui.actionSearch_endpoint_by_class_name.triggered.connect(self.showSearchByClassWizard)

        self.ui.actionSearch_by_existing_instance.triggered.connect(self.showSearchByInstanceWizard)
        self.ui.actionSearch_endpoint_by_existing_instance.triggered.connect(self.showSearchByInstanceWizard)

        self.ui.actionSearch_by_instance_label.triggered.connect(self.showSearchByInstanceLabelWizard)
        self.ui.actionSearch_endpoint_by_instance_label.triggered.connect(self.showSearchByInstanceLabelWizard)

        self.ui.actionEnrich_instance.triggered.connect(self.showEnrichInstanceWizard)
        self.ui.actionEnrich_Instance_2.triggered.connect(self.showEnrichInstanceWizard)

        self.ui.actionExport_to_file.triggered.connect(self.showFileDialogSaveGraph)
        self.ui.actionExport_to_file_2.triggered.connect(self.showFileDialogSaveGraph)

        self.ui.actionDatabase_actions.triggered.connect(self.showDatabasePreferences)
        self.ui.actionDatabase_actions_2.triggered.connect(self.showDatabasePreferences)

        self.ui.actionAbout.triggered.connect(self.showAboutDialog)

        self.ui.actionOnline_documentation.triggered.connect(lambda: Functions.openLinkToBrowser('http://mklab.iti.gr/project/prophet-ontology-populator'))
        self.ui.actionQuick_presentation.triggered.connect(lambda: Functions.openLinkToBrowser('https://www.youtube.com/embed/9oLBwkR-GOc'))

        self.ui.actionCheck_for_updates.triggered.connect(self.checkForUpdates)

        self.ui.lineEditSearchMyModel.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchMyModel, self.ui.treeWidgetMyModel))
        self.ui.lineEditSearchMyModel.returnPressed.connect(lambda: Functions.searchAndGiveFocusToTree(self.ui.lineEditSearchMyModel, self.ui.treeWidgetMyModel))

        self.ui.btnExpandAll.clicked.connect(self.ui.treeWidgetMyModel.expandAll)
        self.ui.btnCollapseAll.clicked.connect(self.ui.treeWidgetMyModel.collapseAll)

        # Context Menu connections
        self.ui.treeWidgetMyModel.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetMyModel, self, self.getGraph()))

        # Key shortcuts
        QtGui.QShortcut(QtGui.QKeySequence('Ctrl+F'), self).activated.connect(self.ui.lineEditSearchMyModel.setFocus)

        # Threads
        self.checkInternetConnectionThread = CheckInternetConnectionThread(self)
        QtCore.QObject.connect(self.checkInternetConnectionThread, QtCore.SIGNAL("checkIfInternetConnectionIsOn"), self.checkIfInternetConnectionIsOn)
        self.checkInternetConnectionThread.start()

        # If check for updates is enabled
        if Functions.getSettingFromDB('auto_update') == 1:
            self.checkForUpdates()

        # CONSTRUCT UI ELEMENTS
        itemEndpoint = QtGui.QTableWidgetItem(Functions.getEndpointName())
        itemEndpoint.setTextAlignment(QtCore.Qt.AlignHCenter)
        itemEndpoint.setTextColor(QtGui.QColor(55, 122, 151)) #rgb numbers of hex #377a97 color
        boldFont = QFont(); boldFont.setBold(True)
        itemEndpoint.setFont(boldFont)
        self.ui.tableWidgetMyModelStats.setItem(0, 0, itemEndpoint)

        # Icons
        self.class_icon = QtGui.QIcon(':/images/class.png')
        self.instance_icon = QtGui.QIcon(':/images/instance.png')
        self.property_icon = QtGui.QIcon(':/images/property.png')
        self.value_icon = QtGui.QIcon(':/images/value.png')
        self.annotation_icon = QtGui.QIcon(':/images/annotation.png')

    def getGraph(self):
        return self.graph

    def setGraph(self, newGraph):
        self.graph = newGraph

    def getMyModelName(self):
        return self.myModelName

    def setMyModelName(self, newName):
        self.myModelName = newName

    def getChangesMadeToModel(self):
        return self.changesMadeToModel

    def setChangesMadeToModel(self, bool_to_set):
        self.changesMadeToModel = bool_to_set

    def showSearchByClassWizard(self):
        # Check if user has loaded a my_model yet
        if self.getMyModelName() == '':
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please load a model first.", QtGui.QMessageBox.Close)

            self.showMyModelsPreferences()

            return

        wizard = SearchByClassWizard()
        wizard.exec_()

        # Reload main graph tree and stats
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())
        self.loadMyModelStatsToTable(self.getGraph(), self.getMyModelName())

    def showSearchByInstanceWizard(self):
        # Check if user has loaded a my_model yet
        if self.getMyModelName() == '':
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please load a model first.", QtGui.QMessageBox.Close)

            self.showMyModelsPreferences()

            return

        # If there are no instances in the graph, stop
        if len(Functions.getAllInstancesFromGraph(self.getGraph())) == 0:
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + self.getMyModelName() + "</span> does not have any instances.", QtGui.QMessageBox.Close)

            return

        wizard = SearchByInstanceName()
        wizard.exec_()

        # Reload main graph tree and stats
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())
        self.loadMyModelStatsToTable(self.getGraph(), self.getMyModelName())

    def showSearchByInstanceLabelWizard(self):
        # Check if user has loaded a my_model yet
        if self.getMyModelName() == '':
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please load a model first.", QtGui.QMessageBox.Close)

            self.showMyModelsPreferences()

            return

        wizard = SearchByInstanceLabel()
        wizard.exec_()

        # Reload main graph tree and stats
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())
        self.loadMyModelStatsToTable(self.getGraph(), self.getMyModelName())


    def showEnrichInstanceWizard(self):
        # Check if user has loaded a my_model yet
        if self.getMyModelName() == '':
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please load a model first.", QtGui.QMessageBox.Close)

            self.showMyModelsPreferences()

            return

        # If there are no instances in the graph, stop
        if len(Functions.getAllInstancesFromGraph(self.getGraph())) == 0:
            # Show message box with error)
            QtGui.QMessageBox.critical(self, 'Error', "Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + self.getMyModelName() + "</span> does not have any instances.", QtGui.QMessageBox.Close)
            return

        wizard = EnrichInstance()
        wizard.exec_()

        # Reload main graph tree and stats
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())
        self.loadMyModelStatsToTable(self.getGraph(), self.getMyModelName())

    def showMyModelsPreferences(self):
        dialog = PreferencesDialog(1)

        dialog.exec_()

        del dialog

        # Reload Graph area
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())

    def showEndpointPreferences(self):
        dialog = PreferencesDialog(2)

        dialog.exec_()

        del dialog

        # Reload Graph area
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())

    def showLog(self):
        dialog = PreferencesDialog(5)

        dialog.exec_()

        del dialog

        # Reload Graph area
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())

    def showNamespacesPreferences(self):
        dialog = PreferencesDialog(3)

        dialog.exec_()

        del dialog

        # Reload Graph area
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())

    def showMappingPreferences(self):
        dialog = PreferencesDialog(4)

        dialog.exec_()

        del dialog

        # Reload Graph area
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())

    def showDialogPreferences(self):

        dialog = PreferencesDialog(0)

        dialog.exec_()

        del dialog

        # Reload Graph area
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())

    def showDatabasePreferences(self):
        dialog = PreferencesDialog(6)

        dialog.exec_()

        del dialog

        # Reload Graph area
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())

    def showAboutDialog(self):
        dialog = AboutDialog()

        dialog.exec_()

        del dialog

    def loadMyModelToTree(self, my_graph, myModelName):

        # Clear Tree
        self.ui.treeWidgetMyModel.clear()

        # Clear search lineedit
        self.ui.lineEditSearchMyModel.clear()

        # Get list of classes for this graph
        classes = Functions.getAllClassesFromGraph(my_graph)

        # Fill the tree with my graph
        # For each class
        for clas in classes:

            # Initialize new parent for QTree
            class_level = QTreeWidgetItem()
            clas_x = Functions.getPhraseWithPrefix(clas)
            class_level.setText(0, clas_x)
            class_level.setToolTip(0, "<b>Class:</b><br> " + clas_x)
            # Set icon
            class_level.setIcon(0, self.class_icon)

            # Get all instances of class
            class_instances = Functions.getInstancesOfClassFromGraph(my_graph, clas)

            # For each instance
            for instance in class_instances:

                # Initialize new parent for QTree
                instance_level = QTreeWidgetItem()
                instance_x = Functions.getPhraseWithPrefix(instance)
                instance_level.setText(0, instance_x)
                instance_level.setToolTip(0, "<b>Instance:</b><br> " + instance_x)

                # Set icon
                instance_level.setIcon(0, self.instance_icon)

                class_level.addChild(instance_level)

                instance_properties = Functions.getDataPropertiesOfInstanceFromGraph(my_graph, instance)

                for instance_property in instance_properties:
                    property_level = QTreeWidgetItem()

                    property_x = Functions.getPhraseWithPrefix(instance_property[0])
                    value_x = instance_property[1].toPython()
                    #property_level.setText(0, "Property: " + property_x + " Value: " + value_x)
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.property_icon)
                    property_level.setIcon(1, self.value_icon)

                    instance_level.addChild(property_level)

                # Get sameAs values and add them to tree
                allSameAsValues = Functions.getSameAsValueForInstanceFromGraph(my_graph, instance)

                for sameAsValue in allSameAsValues:
                    property_level = QTreeWidgetItem()
                    property_x = Functions.getPhraseWithPrefix('http://www.w3.org/2002/07/owl#sameAs')
                    value_x = Functions.getPhraseWithPrefix(sameAsValue)
                    #property_level.setText(0, "Property: " + property_x + " Value: " + value_x)
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.annotation_icon)
                    property_level.setIcon(1, self.value_icon)

                    instance_level.addChild(property_level)

                # Get rdfs:label values and add them to tree
                allLabelValues = Functions.getLabelsOfInstanceFromGraph(my_graph, instance)

                for labelValue in allLabelValues:
                    property_level = QTreeWidgetItem()
                    property_x = Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label')
                    value_x = labelValue
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.annotation_icon)
                    property_level.setIcon(1, self.value_icon)

                    instance_level.addChild(property_level)

            self.ui.treeWidgetMyModel.insertTopLevelItem(0, class_level)

        self.ui.treeWidgetMyModel.sortItems(0, 0)   # sortItems(column, Qt.AscendingOrder)

        self.ui.treeWidgetMyModel.expandAll()

        # Make column 0 wide enough to fit contents
        self.ui.treeWidgetMyModel.resizeColumnToContents(0)

    def loadMyModelStatsToTable(self, my_graph, myModelName):

        # Clear stats table
        self.ui.tableWidgetMyModelStats.clearContents()

        # Get list of classes for this graph
        classes = Functions.getAllClassesFromGraph(my_graph)

        # Get list of instances from graph
        instances = Functions.getAllInstancesFromGraph(my_graph)

        # Get all object properties from graph
        dataProperties = Functions.getAllDataPropertiesFromGraph(my_graph)

        # Complete stats table
        itemEndpoint = QtGui.QTableWidgetItem(Functions.getEndpointName())
        itemEndpoint.setTextAlignment(QtCore.Qt.AlignHCenter)
        itemEndpoint.setTextColor(QtGui.QColor(55, 122, 151)) #rgb numbers of hex #377a97 color
        boldFont = QFont(); boldFont.setBold(True)
        itemEndpoint.setFont(boldFont)
        self.ui.tableWidgetMyModelStats.setItem(0, 0, itemEndpoint)

        itemMyModel = QtGui.QTableWidgetItem(myModelName)
        itemMyModel.setTextAlignment(QtCore.Qt.AlignHCenter)
        itemMyModel.setTextColor(QtGui.QColor(88, 174, 130)) #rgb numbers of hex #58ae82 color
        itemMyModel.setFont(boldFont)
        self.ui.tableWidgetMyModelStats.setItem(0, 1, itemMyModel)

        itemClasses = QtGui.QTableWidgetItem(str(len(classes)))
        itemClasses.setTextAlignment(QtCore.Qt.AlignHCenter)
        self.ui.tableWidgetMyModelStats.setItem(0, 2, itemClasses)

        itemInstances = QtGui.QTableWidgetItem(str(len(instances)))
        itemInstances.setTextAlignment(QtCore.Qt.AlignHCenter)
        self.ui.tableWidgetMyModelStats.setItem(0, 3, itemInstances)

        itemDataProperties = QtGui.QTableWidgetItem(str(len(dataProperties)))
        itemDataProperties.setTextAlignment(QtCore.Qt.AlignHCenter)
        self.ui.tableWidgetMyModelStats.setItem(0, 4, itemDataProperties)

    def toggleAllFunctionsButtons(self, status):
        self.ui.actionExport_to_file.setEnabled(status)
        self.ui.actionExport_to_file_2.setEnabled(status)

        self.ui.actionEnrich_instance.setEnabled(status)
        self.ui.actionEnrich_Instance_2.setEnabled(status)

        self.ui.actionSearch_by_class_name.setEnabled(status)
        self.ui.actionSearch_endpoint_by_class_name.setEnabled(status)

        self.ui.actionSearch_by_existing_instance.setEnabled(status)
        self.ui.actionSearch_endpoint_by_existing_instance.setEnabled(status)

        self.ui.actionSearch_by_instance_label.setEnabled(status)
        self.ui.actionSearch_endpoint_by_instance_label.setEnabled(status)

        self.ui.lineEditSearchMyModel.setEnabled(status)

        self.ui.btnExpandAll.setEnabled(status)
        self.ui.btnCollapseAll.setEnabled(status)

    def toggleEndpointRelatedFunctionsButtons(self, status):
        self.ui.actionEnrich_instance.setEnabled(status)
        self.ui.actionEnrich_Instance_2.setEnabled(status)

        self.ui.actionSearch_by_class_name.setEnabled(status)
        self.ui.actionSearch_endpoint_by_class_name.setEnabled(status)

        self.ui.actionSearch_by_existing_instance.setEnabled(status)
        self.ui.actionSearch_endpoint_by_existing_instance.setEnabled(status)

        self.ui.actionSearch_by_instance_label.setEnabled(status)
        self.ui.actionSearch_endpoint_by_instance_label.setEnabled(status)

    def showFileDialogSaveGraph(self):

        # if there is no graph to save
        if (self.getGraph()).__len__() == 0:
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "There is no model to export.", QtGui.QMessageBox.Close)

        else:
            fileDialog = QtGui.QFileDialog()
            fileNameAndPath = fileDialog.getSaveFileName(self, "Export Graph to file", "", '*.owl;;*.rdf;;*.ttl;;*.nt;;*.n3')

            try:
                str(fileNameAndPath)
            except UnicodeEncodeError:
                QtGui.QMessageBox.critical(self, 'Error', "Export Graph to file failed.\nPlease select a filename and path with latin characters.", QtGui.QMessageBox.Close)
                return

            # If user selected a file
            if fileNameAndPath != "":
                # Define a file inside our directory to export
                tempLocalFile = str('temp_export_file.' + fileNameAndPath.split('.')[-1])
                tempLocalFileAbsolutePath = path.abspath(tempLocalFile)

                # Serialize graph to temp file
                (window.getGraph()).serialize(tempLocalFileAbsolutePath, util.guess_format(tempLocalFileAbsolutePath))

                # Copy temp file to selected fileNameAndPath
                copyfile(tempLocalFile, str(fileNameAndPath))

                # Delete temp file
                remove(tempLocalFile)

                # Prepare strings for message
                fileName = str(fileNameAndPath).split("/")[-1]
                filePath = '/'.join(str(fileNameAndPath).split('/')[:-1])

                QtGui.QMessageBox.information(self, 'Success', "File " + fileName + "\n was successfully saved in\n " + filePath + ".", QtGui.QMessageBox.Close)

                # Log
                Functions.addEntryToLog("Model " + self.getMyModelName() + " was exported to " + fileNameAndPath)

                # Change changesMadeToModel boolean to false, since all changes are considered saved
                self.setChangesMadeToModel(False)

    def checkIfInternetConnectionIsOn(self):
        if Functions.checkIfInternetConnectionIsOn() == False:
            self.ui.statusbar.showMessage("No Internet connection. Please check your network settings.")
            self.toggleEndpointRelatedFunctionsButtons(status=False)
        else:
            self.ui.statusbar.showMessage("", 1)

            # If a my model has been loaded earlier
            if self.getMyModelName() != '':
                self.toggleEndpointRelatedFunctionsButtons(status=True)

    def closeEvent(self, event):
        # If previous model not saved, prompt for export
        if self.getChangesMadeToModel() == True:
            # Show message box with prompt
            reply = QtGui.QMessageBox.question(self, 'Are you sure?', "Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + window.getMyModelName() +
                                               "</span> was changed but not saved. <br>\n Do you want to export it now?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No, QMessageBox.Cancel)

            if reply == QMessageBox.Yes:
                window.showFileDialogSaveGraph()
                event.ignore()
            elif reply == QMessageBox.No:
                self.close()
            elif reply == QMessageBox.Cancel:
                event.ignore()

    def checkForUpdates(self):
        self.checkForUpdatesThread = CheckForUpdates(self)
        QtCore.QObject.connect(self.checkForUpdatesThread, QtCore.SIGNAL("updateFound"), self.runUpdate)
        self.checkForUpdatesThread.start()

    def runUpdate(self):
        # Show message box with prompt
        reply = QtGui.QMessageBox.information(self, 'Update available', "A newer version of PROPheT was found.\nWould you like to "
                                                                        "update now?\n(PROPheT will restart automatically)", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        # If user declines update
        if reply == QMessageBox.No:
            return

        # If user accepts update
        elif reply == QMessageBox.Yes:

            # TODO: Get this code and put to wizards exec_ so that they do not block main window
            # setWindowModality(QtCore.Qt.NonModal)

            # Show UpdateDownloader
            dialog = UpdateDownloader()
            # dialog.exec_()
            # dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            dialog.setModal(True)
            dialog.show()

            dialog.downloadFilesToUpdate()

            # If download succeeded
            if dialog.downloadSucceeded == True:

                # Run Updater.exe
                DETACHED_PROCESS = 0x00000008
                p = Popen("Updater.exe", shell=False, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=DETACHED_PROCESS)

                # Close PROPheT
                self.close()

class CheckInternetConnectionThread(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        while True:
            self.emit(QtCore.SIGNAL("checkIfInternetConnectionIsOn"))
            time.sleep(5)

# About dialog
class AboutDialog(QtGui.QDialog):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_DialogAbout()
        self.ui.setupUi(self)

        self.ui.btnOK.clicked.connect(self.close)

# Preferences implementation
class PreferencesDialog(QtGui.QDialog):

    def __init__(self, tabIndex):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)

        # MAKE CONNECTIONS
        self.ui.btnSelectEndpoint.clicked.connect(self.btnSelectEndpoint_clicked)
        self.ui.tableWidgetKnownEndpoints.itemDoubleClicked.connect(self.endpointDoubleClicked)
        self.ui.tableWidgetKnownEndpoints.itemSelectionChanged.connect(self.endpointSelectionChanged)
        self.ui.btnAddEndpoint.clicked.connect(self.showDialogAddEndpoint)
        self.ui.btnDeleteEndpoint.clicked.connect(self.deleteEndpoint)
        self.ui.btnClearLog.clicked.connect(self.clearLogEntries)
        self.ui.btnAddNamespace.clicked.connect(self.showDialogAddNamespaces)
        self.ui.btnDeleteNamespace.clicked.connect(self.deleteNamespace)
        self.ui.btnRestoreDefaultNamespaces.clicked.connect(self.restoreDefaultNamespaces)
        self.ui.btnAddMyModel.clicked.connect(self.showDialogAddMyModel)
        self.ui.btnDeleteMyModel.clicked.connect(self.deleteMyModel)
        self.ui.btnLoadMyModel.clicked.connect(self.loadMyModel)
        self.ui.tableWidgetMyModels.itemDoubleClicked.connect(lambda: self.ui.tableWidgetMyModels.editItem(self.ui.tableWidgetMyModels.currentItem()))
        self.ui.tableWidgetKnownNamespaces.itemDoubleClicked.connect(lambda: self.ui.tableWidgetKnownNamespaces.editItem(self.ui.tableWidgetKnownNamespaces.currentItem()))
        self.ui.btnDeleteMapping.clicked.connect(self.deleteMapping)
        self.ui.btnDeleteAllMappings.clicked.connect(self.deleteAllMappings)
        self.ui.btnSaveChangesInGeneralTab.clicked.connect(self.saveSettingsFromGeneralTab)
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnExportDatabase.clicked.connect(self.exportDatabase)
        self.ui.btnImportDatabase.clicked.connect(self.importDatabase)
        self.ui.btnResetToDefaultDatabase.clicked.connect(self.restoreDatabaseToDefault)

        self.ui.tableWidgetKnownNamespaces.cellChanged.connect(self.editNamespaceInDB)
        self.ui.tableWidgetKnownEndpoints.cellChanged.connect(self.editEndpointInDB)
        self.ui.tableWidgetMyModels.cellChanged.connect(self.editMyModelInDB)

        # Show the requested tab
        self.tabIndex = tabIndex
        self.ui.tabWidgetPreferences.setCurrentIndex(self.tabIndex)

        # Context Menu connections
        self.ui.tableWidgetKnownNamespaces.customContextMenuRequested.connect(self.openContextMenuNamespacesTable)
        self.ui.tableWidgetKnownEndpoints.customContextMenuRequested.connect(self.openContextMenuEndpointsTable)
        self.ui.tableWidgetMyModels.customContextMenuRequested.connect(self.openContextMenuMyModelsTable)
        self.ui.tableWidgetKnownMappings.customContextMenuRequested.connect(self.openContextMenuMappingsTable)

        # Load tables
        self.loadAllTablesInPreferences()

    def loadAllTablesInPreferences(self):

        # Load EM instances limit from DB
        self.loadEMInstancesLimit()

        # Load sameAs option from DB
        self.loadSameAsOptionSetting()

        # Load owl:equivalentProperty option from DB
        self.loadEquivalentPropertyOptionSetting()

        # Load rdfs:label option from DB
        self.loadLabelOptionSetting()

        # Load Check for updates option from DB
        self.loadCheckForUpdatesOptionSetting()

        # Load endpoint list from DB to table
        self.loadEndpointsToTable()

        # Load log entries from DB to table
        self.loadLogEntriesToTable()

        # Load namespaces from DB to table
        self.loadNamespacesToTable()

        # Load my models from DB to table
        self.loadMyModelsToTable()

        # Load mappings from DB to table
        self.loadMappingsToTable()

        # Load database stats from DB to table
        self.loadDatabaseStatisticsToTable()

        # Make my model progressbar invisible
        self.ui.progressBarLoad.setVisible(False)

    # GENERAL TAB FUNCTIONS
    def loadEMInstancesLimit(self):

        self.ui.spinBoxEMInstancesLimit.setValue(int(Functions.getSettingFromDB('em_instances_limit')))

    def saveSettingsFromGeneralTab(self):

        # Set instances limit setting to DB
        Functions.setSettingToDB('em_instances_limit', self.ui.spinBoxEMInstancesLimit.value())

        # Set sameAs option to DB
        Functions.setSettingToDB('sameas_option', str(self.ui.comboBoxSameAsOption.currentText()))

        # Set owl:equivalentProperty option to DB
        if self.ui.checkBoxPropertyEquivalentToOption.isChecked():
            Functions.setSettingToDB('equivalent_property_option', 1)
        else:
            Functions.setSettingToDB('equivalent_property_option', 0)

        # Set rdfs:label option to DB
        if self.ui.checkBoxLabelOption.isChecked():
            Functions.setSettingToDB('label_option', 1)
        else:
            Functions.setSettingToDB('label_option', 0)

        # Set Check for updates option to DB
        if self.ui.checkBoxCheckForUpdatesAtStartupOption.isChecked():
            Functions.setSettingToDB('auto_update', 1)
        else:
            Functions.setSettingToDB('auto_update', 0)

        # Show message box with success
        QtGui.QMessageBox.information(self, 'Success', "Settings were saved successfully.", QtGui.QMessageBox.Close)

        #Log
        Functions.addEntryToLog("General settings were saved successfully")
        # Load log entries to table
        self.loadLogEntriesToTable()

    def loadSameAsOptionSetting(self):

        self.ui.comboBoxSameAsOption.setCurrentIndex(self.ui.comboBoxSameAsOption.findText(Functions.getSettingFromDB('sameas_option')))

    def loadEquivalentPropertyOptionSetting(self):
        if Functions.getSettingFromDB('equivalent_property_option') == 1:
            self.ui.checkBoxPropertyEquivalentToOption.setChecked(True)
        else:
            self.ui.checkBoxPropertyEquivalentToOption.setChecked(False)

    def loadLabelOptionSetting(self):
        if Functions.getSettingFromDB('label_option') == 1:
            self.ui.checkBoxLabelOption.setChecked(True)
        else:
            self.ui.checkBoxLabelOption.setChecked(False)

    def loadCheckForUpdatesOptionSetting(self):
        if Functions.getSettingFromDB('auto_update') == 1:
            self.ui.checkBoxCheckForUpdatesAtStartupOption.setChecked(True)
        else:
            self.ui.checkBoxCheckForUpdatesAtStartupOption.setChecked(False)

    # ENDPOINTS TAB FUNCTIONS
    def showDialogAddEndpoint(self):
        dialog = AddEndpointDialog()

        dialog.exec_()

        del dialog

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

    def loadEndpointsToTable(self):
        # Clear table
        self.ui.tableWidgetKnownEndpoints.setRowCount(0)

        # Load known endpoints from DB
        endpoints = Functions.getListOfEndpointsFromDB()

        # Get the currently selected endpoint
        currentEndpointName = Functions.getEndpointName()

        # Put the to table
        for endpoint in endpoints:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetKnownEndpoints.rowCount()
            self.ui.tableWidgetKnownEndpoints.insertRow(rowPosition)

            name_item = QtGui.QTableWidgetItem(endpoint[0])
            uri_item = QtGui.QTableWidgetItem(endpoint[1])

            if endpoint[0] == currentEndpointName:
                name_item.setToolTip('Currently selected')
                uri_item.setToolTip('Currently selected')
                name_item.setIcon(QtGui.QIcon(':/images/on.png'))

            # Insert the endpoint
            self.ui.tableWidgetKnownEndpoints.setItem(rowPosition, 0, name_item)
            self.ui.tableWidgetKnownEndpoints.setItem(rowPosition, 1, uri_item)

        # Highlight the currently selected endpoint
        for i in range(self.ui.tableWidgetKnownEndpoints.rowCount()):
            if self.ui.tableWidgetKnownEndpoints.item(i, 0).text() == currentEndpointName:
                self.ui.tableWidgetKnownEndpoints.selectRow(i)

    def deleteEndpoint(self):
        # If no selection has been made
        if self.ui.tableWidgetKnownEndpoints.currentRow() == -1:
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please select an endpoint from the list.", QtGui.QMessageBox.Close)

            return

        # Take the endpoint selected from table
        endpointName = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 0).text()
        endpointUrl = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 1).text()

        # If the desired endpoint is the current in settings
        if endpointName == Functions.getCurrentEndpointName():
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "This endpoint is currently in use.\nCould not be deleted.", QtGui.QMessageBox.Close)
            return
        # Or is DBPedia
        elif endpointUrl == 'http://dbpedia.org/sparql':
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "This endpoint cannot be deleted.", QtGui.QMessageBox.Close)
            return

        Functions.deleteEndpointFromDatabase(endpointName)

        # Log
        Functions.addEntryToLog("Endpoint " + endpointName + " was deleted")

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

    def endpointDoubleClicked(self):
        selected_name = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 0).text()

        # If the right-clicked name is the current name, editing should not be allowed
        if selected_name == Functions.getEndpointName() or selected_name == 'DBPedia':
            return

        self.ui.tableWidgetKnownEndpoints.editItem(self.ui.tableWidgetKnownEndpoints.currentItem())

    def endpointSelectionChanged(self):
        try:
            selected_name = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 0).text()
            current_endpoint = Functions.getEndpointName()

            if selected_name == 'DBPedia' or selected_name == current_endpoint:
                self.ui.btnDeleteEndpoint.setEnabled(False)
            else:
                self.ui.btnDeleteEndpoint.setEnabled(True)

            if selected_name == current_endpoint:
                self.ui.btnSelectEndpoint.setEnabled(False)
            else:
                self.ui.btnSelectEndpoint.setEnabled(True)

        except:
            pass

    def btnSelectEndpoint_clicked(self):
        # If no selection has been made
        if self.ui.tableWidgetKnownEndpoints.currentRow() == -1:
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please select an endpoint from the list.", QtGui.QMessageBox.Close)

            return

        # TODO: Log if this is True
        self.setSelectedEndpointURLAsSetting()

        # Update table of stats in main window
        itemEndpoint = QtGui.QTableWidgetItem(Functions.getEndpointName())
        itemEndpoint.setTextAlignment(QtCore.Qt.AlignHCenter)
        itemEndpoint.setTextColor(QtGui.QColor(55, 122, 151)) #rgb numbers of hex #377a97 color
        boldFont = QFont(); boldFont.setBold(True)
        itemEndpoint.setFont(boldFont)
        window.ui.tableWidgetMyModelStats.setItem(0, 0, itemEndpoint)

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

    def setSelectedEndpointURLAsSetting(self):

        # Get the old URL from settings
        oldEndpointURL = Functions.getEndpointURL()

        # Take the endpoint selected from table
        newEndpointName = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 0).text()
        newEndpointURL = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 1).text()

        # Set the new URL to DB
        # If it is set successfully
        if Functions.setEndpointURL(oldEndpointURL, newEndpointURL):
            # Log
            Functions.addEntryToLog("Endpoint " + newEndpointName + " was selected")

            # Show message box with success
            QtGui.QMessageBox.information(self, 'Success', "Endpoint <span style='font-size:9pt; font-weight:550; color:#377a97;'>" + newEndpointName + "</span> was selected as External Model.", QtGui.QMessageBox.Close)

        # If it fails
        else:
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Could not reach the requested endpoint.", QtGui.QMessageBox.Close)

    # LOG TAB FUNCTIONS
    def loadLogEntriesToTable(self):
        # Clear table
        self.ui.tableWidgetLogEntries.setRowCount(0)

        # Load log entries from DB
        entries = Functions.getListOfLogEntries()

        # Put the entry to table
        for entry in entries:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetLogEntries.rowCount()
            self.ui.tableWidgetLogEntries.insertRow(rowPosition)

            # Insert the endpoint
            self.ui.tableWidgetLogEntries.setItem(rowPosition, 0, QtGui.QTableWidgetItem(entry[0]))
            self.ui.tableWidgetLogEntries.setItem(rowPosition, 1, QtGui.QTableWidgetItem(entry[1]))

        # Highlight the first entry
        self.ui.tableWidgetLogEntries.selectRow(self.ui.tableWidgetLogEntries.rowCount() - 1)

         # Sort table
        self.ui.tableWidgetLogEntries.sortItems(0, QtCore.Qt.DescendingOrder) # latest entry will appear as first

    def clearLogEntries(self):
        # Clear table
        self.ui.tableWidgetLogEntries.setRowCount(0)

        # Delete entries from DB table
        Functions.clearLog()

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

    # NAMESPACES TAB FUNCTIONS
    def showDialogAddNamespaces(self):
        dialog = AddNamespaceDialog()

        dialog.exec_()

        del dialog

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

        # Reload Graph area
        window.loadMyModelToTree(window.getGraph(), window.getMyModelName())

    def loadNamespacesToTable(self):
        # Clear table
        self.ui.tableWidgetKnownNamespaces.setRowCount(0)

        # Load known namespaces from DB
        namespaces = Functions.getListOfNamespaces()

        # Put the to table
        for namespace in namespaces:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetKnownNamespaces.rowCount()
            self.ui.tableWidgetKnownNamespaces.insertRow(rowPosition)

            # Insert the namespace
            self.ui.tableWidgetKnownNamespaces.setItem(rowPosition, 0, QtGui.QTableWidgetItem(str(namespace[0])))
            self.ui.tableWidgetKnownNamespaces.setItem(rowPosition, 1, QtGui.QTableWidgetItem(str(namespace[1])))

    def restoreDefaultNamespaces(self):

        # Delete all namespaces from db
        query = 'DELETE FROM namespaces'
        Functions.executeSQLSubmit(query)

        # Copy backup
        query = 'INSERT INTO namespaces SELECT * FROM namespaces_backup'

        Functions.executeSQLSubmit(query)

        # Log
        Functions.addEntryToLog("Default namespaces were restored")

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

        # window.loadMyModelToTree(window.getGraph(), window.getMyModelName())

    def deleteNamespace(self):
        # If no selection has been made
        if self.ui.tableWidgetKnownNamespaces.currentRow() == -1:
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please select a namespace from the list.", QtGui.QMessageBox.Close)

            return

        # Take the namespace selected from table
        prefix = self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 0).text()

        Functions.deleteNamespaceFromDatabase(prefix)

        # Log
        Functions.addEntryToLog("Namespace " + prefix + " was deleted")

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

        # Reset namespaces in my graph's namespace manager, so it can be populated again with the correct DB values
        window.graph.namespace_manager = NamespaceManager(Graph())

        # MY MODELS TAB FUNCTIONS
    def showDialogAddMyModel(self):
        dialog = AddMyModelDialog()

        dialog.exec_()

        del dialog

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

    def loadMyModelsToTable(self):
        # Clear table
        self.ui.tableWidgetMyModels.setRowCount(0)

        # Load my models from DB
        my_models = Functions.getListOfMyModelsFromDB()

        # Put the model to table
        for model in my_models:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetMyModels.rowCount()
            self.ui.tableWidgetMyModels.insertRow(rowPosition)

            # Insert the model
            self.ui.tableWidgetMyModels.setItem(rowPosition, 0, QtGui.QTableWidgetItem(model[0]))
            self.ui.tableWidgetMyModels.setItem(rowPosition, 1, QtGui.QTableWidgetItem(model[1]))

    def deleteMyModel(self):
        # If no selection has been made
        if self.ui.tableWidgetMyModels.currentRow() == -1:
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please select a Model from the list.", QtGui.QMessageBox.Close)

            return

        # Take the model selected from table
        myModelName = self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 0).text()

        Functions.deleteMyModelFromDatabase(myModelName)

        # Log
        Functions.addEntryToLog("My Model " + myModelName + " was deleted")

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

    def loadMyModel(self):
        # If no selection has been made
        if self.ui.tableWidgetMyModels.currentRow() == -1:
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please select a Model from the list.", QtGui.QMessageBox.Close)
            return

        # If previous model not saved, prompt for export
        if window.getChangesMadeToModel() == True:
            # Show message box with prompt
            reply = QtGui.QMessageBox.question(self, 'Are you sure?', "Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + window.getMyModelName() +
                                               "</span> was changed but not saved.<br>\nDo you want to export it now?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No, QMessageBox.Cancel)

            if reply == QMessageBox.Yes:
                window.showFileDialogSaveGraph()
                return
            elif reply == QMessageBox.Cancel:
                return

        # Make progressBar visible
        self.ui.progressBarLoad.setVisible(True)

        # Take the model selected from table
        myModelName = self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 0).text()
        myModelURL = str(self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 1).text())

        # ProgressBar
        self.ui.progressBarLoad.setValue(10)

        # Create a new graph
        my_graph = Graph()

        # ProgressBar
        self.ui.progressBarLoad.setValue(20)

        try:
            # Load the requested ontology to graph
            my_graph.parse(myModelURL, model=util.guess_format(myModelURL))

        except Exception as e:
            # Make progressBar invisible
            self.ui.progressBarLoad.setVisible(False)

            # Show message box with error
            print e.message
            error_message = "Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + myModelName + "</span> could not be parsed."
            if len(e.message) != 0:
                error_message = error_message + "\n\nError:" + str(e.message)
            QtGui.QMessageBox.critical(self, 'Error', error_message, QtGui.QMessageBox.Close)

            return

        # ProgressBar
        self.ui.progressBarLoad.setValue(80)

        # Replace the main graph
        window.setGraph(my_graph)

        # Set the new My Model name
        window.setMyModelName(myModelName)

        # Call main window's function to load model and stats
        window.loadMyModelToTree(my_graph, myModelName)
        window.loadMyModelStatsToTable(my_graph, myModelName)

        # ProgressBar
        self.ui.progressBarLoad.setValue(100)

        # Log
        Functions.addEntryToLog("Model " + myModelName + " was loaded")

        # Make changesMadeToModel boolean false because a fresh model was loaded
        window.setChangesMadeToModel(False)

        # Make progressBar invisible
        self.ui.progressBarLoad.setVisible(False)

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

        # Show messagebox of success
        # QtGui.QMessageBox.information(self, 'Success', "Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + myModelName + "</span> was loaded successfully.", QtGui.QMessageBox.Close)

        # Enable Functions
        window.toggleAllFunctionsButtons(status=True)

        # Close preferences dialog
        self.accept()

    # MAPPINGS TAB FUNCTIONS
    def loadMappingsToTable(self):
        # Clear table
        self.ui.tableWidgetKnownMappings.setRowCount(0)

        # Load mappings from DB
        mappings = Functions.getListOfMappingsFromDB()

        # Put the mappings to table
        for mapping in mappings:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetKnownMappings.rowCount()
            self.ui.tableWidgetKnownMappings.insertRow(rowPosition)

            # Insert the mapping
            self.ui.tableWidgetKnownMappings.setItem(rowPosition, 0, QtGui.QTableWidgetItem(mapping[0]))
            self.ui.tableWidgetKnownMappings.item(rowPosition, 0).setToolTip(mapping[0])

            self.ui.tableWidgetKnownMappings.setItem(rowPosition, 1, QtGui.QTableWidgetItem(mapping[1]))
            self.ui.tableWidgetKnownMappings.item(rowPosition, 1).setToolTip(mapping[1])

            self.ui.tableWidgetKnownMappings.setItem(rowPosition, 2, QtGui.QTableWidgetItem(mapping[2]))
            self.ui.tableWidgetKnownMappings.item(rowPosition, 2).setToolTip(mapping[2])

            self.ui.tableWidgetKnownMappings.setItem(rowPosition, 3, QtGui.QTableWidgetItem(mapping[3]))
            self.ui.tableWidgetKnownMappings.item(rowPosition, 3).setToolTip(mapping[3])

    def deleteMapping(self):
        # If no selection has been made
        if self.ui.tableWidgetKnownMappings.currentRow() == -1:
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please select a mapping from the list.", QtGui.QMessageBox.Close)

            return

        # Take the model selected from table
        my_model = self.ui.tableWidgetKnownMappings.item(self.ui.tableWidgetKnownMappings.currentRow(), 0).text()
        my_property = self.ui.tableWidgetKnownMappings.item(self.ui.tableWidgetKnownMappings.currentRow(), 1).text()
        external_property = self.ui.tableWidgetKnownMappings.item(self.ui.tableWidgetKnownMappings.currentRow(), 2).text()
        external_model = self.ui.tableWidgetKnownMappings.item(self.ui.tableWidgetKnownMappings.currentRow(), 3).text()

        Functions.deleteMappingFromDB(my_model, my_property, external_property, external_model)

        # Log
        Functions.addEntryToLog("Mapping " + my_property + " (My Model: " + my_model + ") --> " +
                                            external_property + " (External Model: " + external_model + ") was deleted")

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

    def deleteAllMappings(self):
        if self.ui.tableWidgetKnownMappings.rowCount() == 0:
            return

        for i in range (self.ui.tableWidgetKnownMappings.rowCount()):
            self.ui.tableWidgetKnownMappings.setCurrentItem(self.ui.tableWidgetKnownMappings.item(0,0))

            self.deleteMapping()

    # DATABASE TAB FUNCTIONS

    def loadDatabaseStatisticsToTable(self):
        self.ui.tableWidgetDatabaseStats.setItem(0, 0, QtGui.QTableWidgetItem(str(len(Functions.getListOfMyModelsFromDB()))))
        self.ui.tableWidgetDatabaseStats.setItem(0, 1, QtGui.QTableWidgetItem(str(len(Functions.getListOfEndpointsFromDB()))))
        self.ui.tableWidgetDatabaseStats.setItem(0, 2, QtGui.QTableWidgetItem(str(len(Functions.getListOfNamespaces()))))
        self.ui.tableWidgetDatabaseStats.setItem(0, 3, QtGui.QTableWidgetItem(str(len(Functions.getListOfMappingsFromDB()))))
        self.ui.tableWidgetDatabaseStats.setItem(0, 4, QtGui.QTableWidgetItem(str(len(Functions.getListOfDistinctPairsMMEMInMappingsFromDB()))))
        self.ui.tableWidgetDatabaseStats.setItem(0, 5, QtGui.QTableWidgetItem(str(len(Functions.getListOfLogEntries()))))

    def exportDatabase(self):
        fileNameAndPath = QtGui.QFileDialog().getSaveFileName(self, "Export database to file", "", '*.sqlite')

        try:
            filePath = '/'.join(str(fileNameAndPath).split('/')[:-1])
        except UnicodeEncodeError:
            QtGui.QMessageBox.critical(self, 'Error', "Export failed.\nPlease select a filename and path with latin characters.", QtGui.QMessageBox.Close)
            return

        if fileNameAndPath != "":

            # Copy database to directory
            copyfile('database/myDB.sqlite', fileNameAndPath)

            QtGui.QMessageBox.information(self, 'Success', "Current database was successfully saved in\n " + filePath + ".", QtGui.QMessageBox.Close)

        #Log
        Functions.addEntryToLog("Current database was exported in " + filePath)
        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

    def importDatabase(self):
        # Select database file to import
        fileNameAndPath = QtGui.QFileDialog().getOpenFileName(self, "Select a database to import", "", '*.sqlite')

        if fileNameAndPath != "":

            try:
                test = str(fileNameAndPath)
            except UnicodeEncodeError:
                QtGui.QMessageBox.critical(self, 'Error', "Import failed.\nPlease select a filename and path with latin characters.", QtGui.QMessageBox.Close)
                return

            # Check if database is valid (with queries)
            if Functions.checkIfProphetDatabase(str(fileNameAndPath)) == False:
                QtGui.QMessageBox.critical(self, 'Error', "Not a PROPheT database file.\nOperation cancelled.", QtGui.QMessageBox.Close)
                return

            # Copy new database
            copyfile(fileNameAndPath, 'database/myDB.sqlite')
            QtGui.QMessageBox.information(self, 'Success', "Selected database was successfully imported.", QtGui.QMessageBox.Close)

            # Set selected endpoint DBPedia
            Functions.setSettingToDB('endpoint_url', 'http://dbpedia.org/sparql')

            #Log
            Functions.addEntryToLog("Selected database was imported in PROPheT")

            # Reload all tables in preferences
            self.loadAllTablesInPreferences()

    def restoreDatabaseToDefault(self):
        # Ask user first if they are sure
        reply = QtGui.QMessageBox.question(self, 'Restore default database', "Are you sure you want to reset the database?\nAll changes will be lost.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:

            # Set selected endpoint DBPedia
            Functions.setSettingToDB('endpoint_url', 'http://dbpedia.org/sparql')

            # Copy default database
            copyfile('database/myDB_default.sqlite', 'database/myDB.sqlite')

            QtGui.QMessageBox.information(self, 'Success', "Default database was successfully restored.", QtGui.QMessageBox.Close)

            # Reload all tables in preferences
            self.loadAllTablesInPreferences()

    def openContextMenuNamespacesTable(self):

        if self.ui.tableWidgetKnownNamespaces.rowCount() == 0:
            return

        selected_prefix = self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 0).text()
        selected_url = self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 1).text()

        menu = QtGui.QMenu()

        # Add general Namespace functions to menu

        # Add an Add namespace action
        menu.addAction("Add namespace...").triggered.connect(self.showDialogAddNamespaces)

        # Add a Delete namespace action
        menu.addAction("Delete namespace").triggered.connect(self.deleteNamespace)

        # Add a Restore default namespaces action
        menu.addAction("Restore default namespaces").triggered.connect(self.restoreDefaultNamespaces)

        # Add a separator
        menu.addSeparator()

        # If a namespace prefix is selected
        if self.ui.tableWidgetKnownNamespaces.currentColumn() == 0:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit prefix")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetKnownNamespaces.editItem(self.ui.tableWidgetKnownNamespaces.currentItem()))
            edit_action.setFont(QtGui.QFont("Segoe UI", -1, QtGui.QFont.Bold, False))

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy prefix to clipboard").triggered.connect(lambda: Functions.copyTextToClipBoard(selected_prefix))

        # If a namespace url is selected
        elif self.ui.tableWidgetKnownNamespaces.currentColumn() == 1:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit URI")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetKnownNamespaces.editItem(self.ui.tableWidgetKnownNamespaces.currentItem()))
            edit_action.setFont(QtGui.QFont("Segoe UI", -1, QtGui.QFont.Bold, False))

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy namespace to clipboard").triggered.connect(lambda: Functions.copyTextToClipBoard(selected_url))

            # Add an action and connect it with the appropriate function when triggered
            menu.addAction("View namespace in browser").triggered.connect(lambda: Functions.openLinkToBrowser(selected_url))

        position = QtGui.QCursor.pos()

        menu.exec_(position)

    def openContextMenuEndpointsTable(self):

        if self.ui.tableWidgetKnownEndpoints.rowCount() == 0:
            return

        selected_name = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 0).text()
        selected_url = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 1).text()

        menu = QtGui.QMenu()

        # Add general Namespace functions to menu
        # Add an Add endpoint action
        menu.addAction("Add endpoint...").triggered.connect(self.showDialogAddEndpoint)

        # Add a Delete endpoint action
        delete_action = menu.addAction("Delete endpoint")
        delete_action.triggered.connect(self.deleteEndpoint)
        #currentEndpointName = Functions.getEndpointName()

        # Add a Select endpoint action with bold font
        select_action = menu.addAction("Select endpoint")
        select_action.triggered.connect(self.btnSelectEndpoint_clicked)

        # Add a separator
        menu.addSeparator()

        # If an endpoint name is selected
        if self.ui.tableWidgetKnownEndpoints.currentColumn() == 0:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit name")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetKnownEndpoints.editItem(self.ui.tableWidgetKnownEndpoints.currentItem()))
            edit_action.setFont(QtGui.QFont("Segoe UI", -1, QtGui.QFont.Bold, False))

            # If the right-clicked name is the current name, editing should not be allowed
            if selected_name == Functions.getEndpointName() or selected_name == 'DBPedia':
                edit_action.setEnabled(False)

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy name to clipboard").triggered.connect(lambda: Functions.copyTextToClipBoard(selected_name))

        # If a endpoint url is selected
        elif self.ui.tableWidgetKnownEndpoints.currentColumn() == 1:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit URI")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetKnownEndpoints.editItem(self.ui.tableWidgetKnownEndpoints.currentItem()))
            edit_action.setFont(QtGui.QFont("Segoe UI", -1, QtGui.QFont.Bold, False))

            # If the right-clicked name is the current name, editing should not be allowed
            if selected_url == Functions.getEndpointURL() or selected_name == 'DBPedia':
                edit_action.setEnabled(False)
                delete_action.setEnabled(False)

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy URI to clipboard").triggered.connect(lambda: Functions.copyTextToClipBoard(selected_url))

            # Add an action and connect it with the appropriate function when triggered
            menu.addAction("View endpoint in browser").triggered.connect(lambda: Functions.openLinkToBrowser(selected_url))

        position = QtGui.QCursor.pos()

        menu.exec_(position)

    def openContextMenuMyModelsTable(self):

        if self.ui.tableWidgetMyModels.rowCount() == 0:
            return

        selected_name = self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 0).text()
        selected_url = self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 1).text()

        menu = QtGui.QMenu()

        # Add general Namespace functions to menu
        # Add an Add model action
        menu.addAction("Add model...").triggered.connect(self.showDialogAddMyModel)

        # Add a Delete endpoint action
        menu.addAction("Delete model").triggered.connect(self.deleteMyModel)

        # Add a Select my model action with bold font
        select_action = menu.addAction("Load model")
        select_action.triggered.connect(self.loadMyModel)

        # Add a separator
        menu.addSeparator()

        # If a My model name is selected
        if self.ui.tableWidgetMyModels.currentColumn() == 0:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit name")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetMyModels.editItem(self.ui.tableWidgetMyModels.currentItem()))
            edit_action.setFont(QtGui.QFont("Segoe UI", -1, QtGui.QFont.Bold, False))

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy name to clipboard").triggered.connect(lambda: Functions.copyTextToClipBoard(selected_name))

        # If a My model url is selected
        elif self.ui.tableWidgetMyModels.currentColumn() == 1:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit URI")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetMyModels.editItem(self.ui.tableWidgetMyModels.currentItem()))
            edit_action.setFont(QtGui.QFont("Segoe UI", -1, QtGui.QFont.Bold, False))

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy URI to clipboard").triggered.connect(lambda: Functions.copyTextToClipBoard(selected_url))

            # Add an action to open model in browser and connect it with the appropriate function when triggered
            view_in_browser_action = menu.addAction("View model in browser")
            view_in_browser_action.triggered.connect(lambda: Functions.openLinkToBrowser(selected_url))

            if 'http' not in selected_url:
                view_in_browser_action.setEnabled(False)

        position = QtGui.QCursor.pos()

        menu.exec_(position)

    def openContextMenuMappingsTable(self):

        if self.ui.tableWidgetKnownMappings.rowCount() == 0:
            return

        menu = QtGui.QMenu()

        # Add delete mapping function to menu
        menu.addAction("Delete mapping").triggered.connect(self.deleteMapping)

        # Add delete all mappings function to menu
        menu.addAction("Delete all mappings").triggered.connect(self.deleteAllMappings)

        position = QtGui.QCursor.pos()

        menu.exec_(position)

    def editNamespaceInDB(self):

        if self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 0) is None or self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 1) is None:
            return

        current_prefix = self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 0).text()
        current_url = self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 1).text()

        try:
            str(current_prefix)
            str(current_url)
        except UnicodeEncodeError:
            # Show error
            QtGui.QMessageBox.critical(self, 'Error', "Please use only latin characters.", QtGui.QMessageBox.Close)

            # Reload table
            self.loadNamespacesToTable()
            return

        # If a namespace prefix is changed
        if self.ui.tableWidgetKnownNamespaces.currentColumn() == 0:

            # If the whole text was deleted from prefix
            if len(current_prefix) == 0:

                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "Prefix cannot be empty", QtGui.QMessageBox.Close)

                # Reload table
                self.loadNamespacesToTable()

                return

            # If new prefix already exists in DB
            if current_prefix in Functions.getListOfNamespacePrefixesFromDB():
                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "Prefix already exists in the list", QtGui.QMessageBox.Close)

                # Reload table
                self.loadNamespacesToTable()

                return

            Functions.updatePrefixOfNamespaceInDatabase(current_prefix, current_url)

        # If a namespace url is changed
        elif self.ui.tableWidgetKnownNamespaces.currentColumn() == 1:

            # If the whole text was deleted from url
            if len(current_url) == 0:
                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "URL cannot be empty", QtGui.QMessageBox.Close)

                # Reload table
                self.loadNamespacesToTable()

                return

            # If new url already exists in DB
            if current_url in Functions.getListOfNamespaceUrlsFromDB():
                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "URL already exists in the list", QtGui.QMessageBox.Close)

                # Reload table
                self.loadNamespacesToTable()

                return

            Functions.updateUrlOfNamespaceInDatabase(current_prefix, current_url)

    def editEndpointInDB(self):

        if self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 0) is None or self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 1) is None:
            return

        current_name = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 0).text()
        current_url = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 1).text()

        try:
            str(current_name)
            str(current_url)
        except UnicodeEncodeError:
            # Show error
            QtGui.QMessageBox.critical(self, 'Error', "Please use only latin characters.", QtGui.QMessageBox.Close)

            # Reload table
            self.loadEndpointsToTable()
            return

        # If the endpoint name is changed
        if self.ui.tableWidgetKnownEndpoints.currentColumn() == 0:

            # If the whole text was deleted from name
            if len(current_name) == 0:

                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "Name cannot be empty", QtGui.QMessageBox.Close)

                # Reload table
                self.loadEndpointsToTable()

                return

            # If new name already exists in DB
            if current_name in Functions.getListOfEndpointNamesFromDB():
                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "Name already exists in the list", QtGui.QMessageBox.Close)

                # Reload table
                self.loadEndpointsToTable()

                return

            Functions.updateNameOfEndpointInDatabase(current_name, current_url)

        # If the endpoint url is changed
        elif self.ui.tableWidgetKnownEndpoints.currentColumn() == 1:

            # If the whole text was deleted from url
            if len(current_url) == 0:
                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "Endpoint URL cannot be empty", QtGui.QMessageBox.Close)

                # Reload table
                self.loadEndpointsToTable()

                return

            # If new url already exists in DB
            if current_url in Functions.getListOfEndpointUrlsFromDB():
                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "URL already exists in the list", QtGui.QMessageBox.Close)

                # Reload table
                self.loadEndpointsToTable()

                return

            Functions.updateUrlOfEndpointInDatabase(current_name, current_url)

    def editMyModelInDB(self):

        if self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 0) is None or self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 1) is None:
            return

        current_name = self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 0).text()
        current_url = self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 1).text()

        try:
            str(current_name)
            str(current_url)
        except UnicodeEncodeError:
            # Show error
            QtGui.QMessageBox.critical(self, 'Error', "Please use only latin characters.", QtGui.QMessageBox.Close)

            # Reload table
            self.loadMyModelsToTable()
            return

        # If a model name is changed
        if self.ui.tableWidgetMyModels.currentColumn() == 0:

            # If the whole text was deleted from prefix
            if len(current_name) == 0:

                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "Name cannot be empty", QtGui.QMessageBox.Close)

                # Reload table
                self.loadMyModelsToTable()

                return

            # If new name already exists in DB
            if current_name in Functions.getListOfMyModelNamesFromDB():
                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "Name already exists in the list", QtGui.QMessageBox.Close)

                # Reload table
                self.loadMyModelsToTable()

                return

            Functions.updateNameOfMyModelInDatabase(current_name, current_url)

        # If my model url is changed
        elif self.ui.tableWidgetMyModels.currentColumn() == 1:

            # If the whole text was deleted from url
            if len(current_url) == 0:
                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "URL cannot be empty", QtGui.QMessageBox.Close)

                # Reload table
                self.loadMyModelsToTable()

                return

            # If new url already exists in DB
            if current_url in Functions.getListOfMyModelUrlsFromDB():
                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "URL already exists in the list", QtGui.QMessageBox.Close)

                # Reload table
                self.loadMyModelsToTable()

                return

            Functions.updateUrlOfMyModelInDatabase(current_name, current_url)

class AddEndpointDialog(QtGui.QDialog):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_AddEndpoint()
        self.ui.setupUi(self)

        # MAKE CONNECTIONS
        self.ui.btnCancel.clicked.connect(self.close)
        self.ui.btnOK.clicked.connect(self.btnOK_clicked)

    def btnOK_clicked(self):
        name = self.ui.lineEditEndpointName.text()
        url = self.ui.lineEditEndpointURL.text()

        # If the name field is empty
        if name == '':
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please type a name for the new endpoint.", QtGui.QMessageBox.Close)
            return

        # If the URL field is empty
        if url == "":
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please type a URL for the new endpoint.", QtGui.QMessageBox.Close)
            return

        # Check if latin characters
        try:
            str(name)
            str(url)
        except UnicodeEncodeError:
            # Show error
            QtGui.QMessageBox.critical(self, 'Error', "Please use only latin characters.", QtGui.QMessageBox.Close)
            return

        # If the given name exists in the DB.
        if name in Functions.getListOfEndpointNamesFromDB():
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "An endpoint with the name <span style='font-size:9pt; font-weight:550; color:#377a97;'>" + name +
                                       "</span> already exists in the list.", QtGui.QMessageBox.Close)
            return

        #If given url exists in the DB
        if url in Functions.getListOfEndpointUrlsFromDB():
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "An endpoint with the url <span style='font-size:9pt; font-weight:550; color:#377a97;'>" + url +
                                       "</span> already exists in the list.", QtGui.QMessageBox.Close)
            return

        # Since everything is ok, we add the new endpoint to the DB
        Functions.addEndpointToDatabase(name, url)

        #Log
        Functions.addEntryToLog("New endpoint " + name + " was inserted")

        # Close the dialog
        self.close()

class AddNamespaceDialog(QtGui.QDialog):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_AddNamespace()
        self.ui.setupUi(self)

        # MAKE CONNECTIONS
        self.ui.btnCancel.clicked.connect(self.close)
        self.ui.btnOK.clicked.connect(self.btnOK_clicked)

    def btnOK_clicked(self):
        prefix = self.ui.lineEditNamespacePrefix.text().toLower()
        url = self.ui.lineEditNamespaceURL.text()

        # If the prefix field is empty
        if prefix == '':
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please type a prefix for the new namespace.", QtGui.QMessageBox.Close)
            return

        # If the URL field is empty
        if url == "":
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please type a URL for the new namespace.", QtGui.QMessageBox.Close)
            return

        # Check if latin characters
        try:
            str(prefix)
            str(url)
        except UnicodeEncodeError:
            # Show error
            QtGui.QMessageBox.critical(self, 'Error', "Please use only latin characters.", QtGui.QMessageBox.Close)
            return

        # If the given prefix exists in the DB.
        if prefix in Functions.getListOfNamespacePrefixesFromDB():
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "A namespace with the prefix <span style='font-size:9pt; font-weight:550; color:#000000;'>" + prefix +
                                       "</span> already exists in the list.", QtGui.QMessageBox.Close)
            return

        # If given url exists in the DB
        if url in Functions.getListOfNamespaceUrlsFromDB():
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "A namespace with the url <span style='font-size:9pt; font-weight:550; color:#000000;'>" + url +
                                       "</span> already exists in the list.", QtGui.QMessageBox.Close)
            return

        # Since everything is ok, we add the new namespace to the DB
        Functions.addNamespaceToDatabase(prefix, url)

        #Log
        Functions.addEntryToLog("New namespace " + prefix + " was inserted")

        # Close the dialog
        self.close()

class AddMyModelDialog(QtGui.QDialog):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_AddMyModel()
        self.ui.setupUi(self)

        # MAKE CONNECTIONS
        self.ui.btnCancel.clicked.connect(self.close)
        self.ui.btnOK.clicked.connect(self.btnOK_clicked)
        self.ui.btnOpenFile.clicked.connect(self.btnOpenFile_clicked)

    def btnOpenFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Select a file to open', "", '*.owl;;*.rdf;;*.ttl;;All files (*.*)')
        if fileName:
            self.ui.lineEditModelURL.setText(fileName)

    def btnOK_clicked(self):
        name = self.ui.lineEditModelName.text()
        url = self.ui.lineEditModelURL.text()

        # If the name field is empty
        if name == '':
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please type a name for the <span style='font-size:9pt; font-weight:550; color:#58ae82;'>new Model</span>.", QtGui.QMessageBox.Close)
            return

        # If the URL field is empty
        if url == "":
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "Please type a URL for the <span style='font-size:9pt; font-weight:550; color:#58ae82;'>new Model</span>.", QtGui.QMessageBox.Close)
            return

        # Check if latin characters
        try:
            str(name)
            str(url)
        except UnicodeEncodeError:
            # Show error
            QtGui.QMessageBox.critical(self, 'Error', "Please use only latin characters.", QtGui.QMessageBox.Close)
            return

        # If the given name exists in the DB.
        if name in Functions.getListOfMyModelNamesFromDB():
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "A model with the name <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + name +
                                       "</span> already exists in the list.", QtGui.QMessageBox.Close)
            return

        # If the given url exists in the DB.
        if url in Functions.getListOfMyModelUrlsFromDB():
            # Show message box with error
            QtGui.QMessageBox.critical(self, 'Error', "A model with the url <span style='font-size:9pt; font-weight:550; color:#000000;'>" + url +
                                       "</span> already exists in the list.", QtGui.QMessageBox.Close)
            return

        # Since everything is ok, we add the new my model to the DB
        Functions.addMyModelToDatabase(name, url)

        #Log
        Functions.addEntryToLog("New model " + name + " was inserted")

        # Close the dialog
        self.close()


class SearchByInstanceName(QtGui.QWizard):

    def __init__(self):
        QtGui.QWizard.__init__(self)
        self.ui = Ui_WizardSearchByInstanceName()
        self.ui.setupUi(self)

        # Icons
        self.class_icon = QtGui.QIcon(':/images/class.png')
        self.instance_icon = QtGui.QIcon(':/images/instance.png')
        self.property_icon = QtGui.QIcon(':/images/property.png')
        self.value_icon = QtGui.QIcon(':/images/value.png')
        self.annotation_icon = QtGui.QIcon(':/images/annotation.png')

        # MAKE CONNECTIONS
        self.button(QtGui.QWizard.NextButton).clicked.connect(lambda: self.nextButton_clicked())
        self.button(QtGui.QWizard.BackButton).clicked.connect(lambda: self.backButton_clicked())
        self.button(QtGui.QWizard.FinishButton).clicked.connect(lambda: self.accept())
        self.ui.treeWidgetSelectInstanceToSearchFor.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSelectInstanceToSearchFor, self))
        self.ui.treeWidgetSelectClasses.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSelectClasses, self))
        self.ui.treeWidgetSelectInstancesToImport.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSelectInstancesToImport, self))
        self.ui.treeWidgetSummary.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSummary, self))
        self.ui.btnAllPage2.clicked.connect(self.allButtonPage2Clicked)
        self.ui.btnNonePage2.clicked.connect(self.ui.treeWidgetSelectClasses.clearSelection)
        self.ui.btnAllPage3.clicked.connect(self.allButtonPage3Clicked)
        self.ui.btnNonePage3.clicked.connect(self.ui.treeWidgetSelectInstancesToImport.clearSelection)

        self.ui.lineEditSearchTreePage1.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreePage1, self.ui.treeWidgetSelectInstanceToSearchFor))
        self.ui.lineEditSearchTreePage2.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreePage2, self.ui.treeWidgetSelectClasses))
        self.ui.lineEditSearchTreePage3.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreePage3, self.ui.treeWidgetSelectInstancesToImport))
        self.ui.lineEditSearchTreeSummary.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreeSummary, self.ui.treeWidgetSummary))

        self.ui.btnExpandAll_page1.clicked.connect(self.ui.treeWidgetSelectInstanceToSearchFor.expandAll)
        self.ui.btnCollapseAll_page1.clicked.connect(self.ui.treeWidgetSelectInstanceToSearchFor.collapseAll)
        self.ui.btnExpandAll_page3.clicked.connect(self.ui.treeWidgetSelectInstancesToImport.expandAll)
        self.ui.btnCollapseAll_page3.clicked.connect(self.ui.treeWidgetSelectInstancesToImport.collapseAll)
        self.ui.btnExpandAll_Summary.clicked.connect(self.ui.treeWidgetSummary.expandAll)
        self.ui.btnCollapseAll_Summary.clicked.connect(self.ui.treeWidgetSummary.collapseAll)

        #CONSTRUCT UI ELEMENTS
        self.ui.lblSearchInstanceInEM.setText("Select an instance of My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'> " + window.getMyModelName() +
                                              "</span> to search for similar instances in the External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'> " + Functions.getCurrentEndpointName() + "</span>:")
        self.ui.lblShowPropertiesOfBothModels.setText("Match properties of External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" +
                                                      Functions.getCurrentEndpointName() + "</span> to equivalent properties of My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" +
                                                      window.getMyModelName() + "</span>:")
        self.loadMyModelToTreeAndClassesComboBox(window.getGraph())

    def loadMyModelToTreeAndClassesComboBox(self, my_graph):
        # Clear Tree
        self.ui.treeWidgetSelectInstanceToSearchFor.clear()

        # Get list of classes for this graph
        classes = Functions.getAllClassesFromGraph(my_graph)
        classes.sort()

        # Fill the tree with my graph

        # For each class
        for clas in classes:

            # Initialize new parent for QTree
            class_level = QTreeWidgetItem()
            clas_x = Functions.getPhraseWithPrefix(clas)
            class_level.setText(0, clas_x)
            class_level.setFlags(QtCore.Qt.ItemFlags(0))
            class_level.setFlags(QtCore.Qt.ItemIsEnabled)
            class_level.setToolTip(0, "<b>Class:</b><br> " + clas_x)
            # Set icon
            class_level.setIcon(0, self.class_icon)

            # Add class to combobox of page 3
            self.ui.comboBoxMyModelClasses.addItem(Functions.getPhraseWithPrefix(clas))

            # Get all instances of class
            class_instances = Functions.getInstancesOfClassFromGraph(my_graph, clas)

            # For each instance
            for instance in class_instances:

                # Initialize new parent for QTree
                instance_level = QTreeWidgetItem()
                instance_x = Functions.getPhraseWithPrefix(instance)
                instance_level.setText(0, instance_x)
                instance_level.setToolTip(0, "<b>Instance:</b><br> " + instance_x)

                # Set icon
                instance_level.setIcon(0, self.instance_icon)

                class_level.addChild(instance_level)

                instance_properties = Functions.getDataPropertiesOfInstanceFromGraph(my_graph, instance)

                for instance_property in instance_properties:
                    property_level = QTreeWidgetItem()

                    property_x = Functions.getPhraseWithPrefix(instance_property[0])
                    value_x = instance_property[1].toPython()
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setFlags(QtCore.Qt.ItemFlags(0))
                    property_level.setFlags(QtCore.Qt.ItemIsEnabled)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.property_icon)
                    property_level.setIcon(1, self.value_icon)

                    instance_level.addChild(property_level)

                allSameAsValues = Functions.getSameAsValueForInstanceFromGraph(my_graph, instance)

                for sameAsValue in allSameAsValues:

                    property_level = QTreeWidgetItem()
                    property_x = Functions.getPhraseWithPrefix('http://www.w3.org/2002/07/owl#sameAs')
                    value_x = Functions.getPhraseWithPrefix(sameAsValue)
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setFlags(QtCore.Qt.ItemFlags(0))
                    property_level.setFlags(QtCore.Qt.ItemIsEnabled)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.annotation_icon)
                    property_level.setIcon(1, self.value_icon)

                    # If it is an annotation property
                    if property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2002/07/owl#sameAs') or property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#seeAlso') or property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label'):
                        property_level.setIcon(0, self.annotation_icon)

                    instance_level.addChild(property_level)

                labels_of_instance = Functions.getLabelsOfInstanceFromGraph(window.getGraph(), instance)

                for label in labels_of_instance:
                    property_level = QTreeWidgetItem()
                    property_x = Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label')
                    value_x = label
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setFlags(QtCore.Qt.ItemFlags(0))
                    property_level.setFlags(QtCore.Qt.ItemIsEnabled)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.annotation_icon)
                    property_level.setIcon(1, self.value_icon)

                    instance_level.addChild(property_level)

            self.ui.treeWidgetSelectInstanceToSearchFor.insertTopLevelItem(0, class_level)

            class_level.setExpanded(True)

        self.ui.treeWidgetSelectInstanceToSearchFor.sortItems(0, 0)

        # Make column 0 wide enough to fit contents (needs to expand all tree and re-collapse as wanted)
        self.ui.treeWidgetSelectInstanceToSearchFor.expandAll()
        self.ui.treeWidgetSelectInstanceToSearchFor.resizeColumnToContents(0)

        self.ui.treeWidgetSelectInstanceToSearchFor.collapseAll()
        for i in range(self.ui.treeWidgetSelectInstanceToSearchFor.topLevelItemCount()):
            self.ui.treeWidgetSelectInstanceToSearchFor.topLevelItem(i).setExpanded(True)

        # Put class icon to classes in combobox of page 3
        for i in range(self.ui.comboBoxMyModelClasses.count()):
            self.ui.comboBoxMyModelClasses.setItemIcon(i, self.class_icon)

    def loadClassesFromEMToTree(self, classes):
        # Clear tree
        self.ui.treeWidgetSelectInstancesToImport.clear()

        if len(classes) == 0:
            self.ui.lineEditSearchTreePage2.setEnabled(False)
            return

        else:
            self.ui.lineEditSearchTreePage2.setEnabled(True)

            # Sort classes list
            classes.sort()

            # For each class
            for clas in classes:

                # Initialize new parent for QTree
                class_level = QTreeWidgetItem()
                clas_x = Functions.getPhraseWithPrefix(clas)
                class_level.setText(0, clas_x)
                class_level.setToolTip(0, "<b>Class:</b><br> " + clas_x)
                # Set icon
                class_level.setIcon(0, self.class_icon)

                # Insert class to tree
                self.ui.treeWidgetSelectClasses.insertTopLevelItem(0, class_level)

            self.ui.treeWidgetSelectClasses.sortItems(0, 0)

    def loadSelectedClassesAndInstancesFromEMToTree(self, selectedClasses):
        # Clear tree
        self.ui.treeWidgetSelectInstancesToImport.clear()

        # Sort classes list
        selectedClasses.sort()

        # For each class
        for clas in selectedClasses:

            # Initialize new parent for QTree
            class_level = QTreeWidgetItem()
            clas_x = Functions.getPhraseWithPrefix(clas)
            class_level.setText(0, clas_x)
            class_level.setFlags(QtCore.Qt.ItemFlags(0))
            class_level.setFlags(QtCore.Qt.ItemIsEnabled)
            class_level.setToolTip(0, "<b>Class:</b><br> " + clas_x)
            # Set icon
            class_level.setIcon(0, self.class_icon)

            ## Search for instances of each class and add to tree
            instancesOfClass = Functions.queryEndpointForInstancesOfClass(Functions.getPhraseWithURL(clas))

            # Add each instance under the "Instances:"
            for instance in instancesOfClass:

                # Initialize new parent for QTree
                instance_level = QTreeWidgetItem()
                instance_x = Functions.getPhraseWithPrefix(instance)
                instance_level.setText(0, instance_x)
                instance_level.setToolTip(0, "<b>Instance:</b><br> " + instance_x)

                # Set icon
                instance_level.setIcon(0, self.instance_icon)

                ## Search for data properties of each instance and add to tree
                properties = Functions.queryEndpointForDataPropertiesOfInstance(instance)

                # Add each property under the "Properties:"
                for property in properties:

                    property_level = QTreeWidgetItem()

                    property_x = Functions.getPhraseWithPrefix(property[0])
                    value_x = property[1]
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setFlags(QtCore.Qt.ItemFlags(0))
                    property_level.setFlags(QtCore.Qt.ItemIsEnabled)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.property_icon)
                    property_level.setIcon(1, self.value_icon)

                    # If it is an annotation property
                    if property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2002/07/owl#sameAs') or property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#seeAlso') or property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label'):
                        property_level.setIcon(0, self.annotation_icon)

                    instance_level.addChild(property_level)

                labels_of_instance = Functions.queryEndpointForLabelsOfInstance(instance)

                for label in labels_of_instance:

                    property_level = QTreeWidgetItem()
                    property_x = Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label')
                    value_x = label
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setFlags(QtCore.Qt.ItemFlags(0))
                    property_level.setFlags(QtCore.Qt.ItemIsEnabled)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.annotation_icon)
                    property_level.setIcon(1, self.value_icon)

                    instance_level.addChild(property_level)

                class_level.addChild(instance_level)

            # Insert class to tree
            self.ui.treeWidgetSelectInstancesToImport.insertTopLevelItem(0, class_level)
            class_level.setExpanded(True)

        # Make column 0 wide enough to fit contents (needs to expand all tree and re-collapse as wanted)
        self.ui.treeWidgetSelectInstancesToImport.expandAll()
        self.ui.treeWidgetSelectInstancesToImport.resizeColumnToContents(0)

        self.ui.treeWidgetSelectInstancesToImport.collapseAll()
        for i in range(self.ui.treeWidgetSelectInstancesToImport.topLevelItemCount()):
            self.ui.treeWidgetSelectInstancesToImport.topLevelItem(i).setExpanded(True)

        self.ui.treeWidgetSelectInstancesToImport.sortItems(0, 0)

    def nextButton_clicked(self):

        # If it is page 2
        if self.currentId() == 1:
            # If no selection has been made
            if len(self.ui.treeWidgetSelectInstanceToSearchFor.selectedItems()) == 0:
                # Go back to page 1
                self.back()

                # Show message box with error
                QtGui.QMessageBox.critical(self, 'Error', "Please select an instance from the list.", QtGui.QMessageBox.Close)
                return

            # Change label in page 2
            self.ui.lblSearchForInstanceClassesFound.setText("Classes found in External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" + Functions.getCurrentEndpointName() +
                                                             "</span>. Please select a class (or more) to show instances in the next step.")

            # Get selected instance of my model as URL phrase
            selectedInstanceToSearch = self.getSelectedMyModelInstanceFromTree()

            # Set instance to search variable
            #self.setInstanceToSearch(selectedInstanceToSearch)

            # Get labels of instance
            labelsOfInstanceToSearch = Functions.getLabelsOfInstanceFromGraph(window.getGraph(), selectedInstanceToSearch)

            # If no label found
            if len(labelsOfInstanceToSearch) == 0:
                # Go back to page 1
                self.back()

                # Show message box with warning
                QtGui.QMessageBox.warning(self, 'Warning', "This instance does not have an rdfs:label to search for.", QtGui.QMessageBox.Close)
                return

            # Query endpoint for instances with the same label
            instancesFromEM = []

            # For each label found in MM for this instance
            for label in labelsOfInstanceToSearch:
                try:
                    # Query endpoint for instances with this label and put results in instancesFromEM
                    instancesFromEM.extend(Functions.queryEndpointForInstancesWithLabel(label, searchType='Exact match'))
                except:
                    #print "label not unicode"
                    pass

            # Query endpoint for each instance to get it's classes
            classesFromInstancesFromEM = []

            for EMInstance in instancesFromEM:
                classesFromInstancesFromEM.extend(Functions.queryEndpointForClassesOfInstance(EMInstance))

            # Load classes to tree
            self.loadClassesFromEMToTree(classesFromInstancesFromEM)

        # If it is page 3
        if self.currentId() == 2:
            # If no selection has been made
            if len(self.ui.treeWidgetSelectClasses.selectedItems()) == 0:
                # Go back to page 2
                self.back()

                # Show message box with error
                QtGui.QMessageBox.critical(self, 'Error', "Please select a class (or more) from the list to search for instances.", QtGui.QMessageBox.Close)

                return

            classesToSearchForInstancesInEM = []

            for clas in (self.ui.treeWidgetSelectClasses.selectedItems()):
                classesToSearchForInstancesInEM.append(clas.text(0))

            # Change label in page 2
            self.ui.lblSearchForInstanceInstancesFound.setText("Instances found in External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" + Functions.getCurrentEndpointName() +
                                                               "</span>. Please select an instance (or more) to import.")

            # Load tree
            self.loadSelectedClassesAndInstancesFromEMToTree(classesToSearchForInstancesInEM)

        # If it is page 4
        if self.currentId() == 3:
            # If no selection has been made
            if len(self.ui.treeWidgetSelectInstancesToImport.selectedItems()) == 0:
                # Go back to page 3
                self.back()

                # Show message box with error
                QtGui.QMessageBox.critical(self, 'Error', "Please select an instance (or more) from the list to import to My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + window.getMyModelName()+ "</span>.", QtGui.QMessageBox.Close)

                return

            # set message in corresponding label of next page
            self.ui.lblSelectMyModelClassToImportInstances.setText("Select a class from My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + window.getMyModelName() + "</span> to import instances:")

            # Select index -1 in the combobox
            self.ui.comboBoxMyModelClasses.setCurrentIndex(-1)

        # If it is page 5
        if self.currentId() == 4:
            # If no selection has been made
            if self.ui.comboBoxMyModelClasses.currentIndex() == -1:
                # Go back to page 4
                self.back()

                # Show message box with error
                QtGui.QMessageBox.critical(self, 'Error', "Please select a class from My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + window.getMyModelName() + "</span> to import instances.", QtGui.QMessageBox.Close)

                return

            # Alter properties of specific buttons in wizard pages
            self.ui.wizardPage5.setButtonText(QWizard.NextButton, 'Populate')

            self.loadDataToTableWidgetViewPropertiesOfBothModels()

        # If it is page 6 (Populate button has been pressed)
        if self.currentId() == 5:
            # Create a list with the desired properties
            desired_em_properties = []

            # Handle mapping table
            for row in range(self.ui.tableWidgetViewPropertiesOfBothModels.rowCount()):
                # If it is not <empty>
                if self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText() != '<empty>':
                    # Add to desired properties
                    desired_em_properties.append(Functions.getPhraseWithURL(self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text()))

                    # Update mapping if it exists
                    Functions.updateMappingToDB(window.getMyModelName(), self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText(), self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(), Functions.getEndpointName())

                    # Insert mapping if it does not exist
                    Functions.addMappingToDB(window.getMyModelName(), self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText(), self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(), Functions.getEndpointName())

                # If it is <empty> delete if from DB (if it exists)
                else:
                    Functions.deleteMappingOfExternalPropertyFromBD(window.getMyModelName(), self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(), Functions.getEndpointName())

            # Clear summary tree
            self.ui.treeWidgetSummary.clear()

            # Insert selected instances from EM to MyModel
            self.insertInstancesFromEMToMyModel()

            # Insert selected data properties to graph
            self.insertDataPropertiesForSelectedInstancesFromEMToMyModel(desired_em_properties)

            # Add text to label
            self.ui.lblPopulatedInstances.setText("Instances added to class " + self.ui.comboBoxMyModelClasses.currentText() + ".")

            # Sort and arrange summary tree widget
            # Sort items of summary tree widget
            self.ui.treeWidgetSummary.sortItems(0, 0)

            # Make column 0 of summary tree widget wide enough to fit contents (needs to expand all tree and re-collapse as wanted)
            self.ui.treeWidgetSummary.expandAll()
            self.ui.treeWidgetSummary.resizeColumnToContents(0)

            # Log
            Functions.addEntryToLog("Instances added to class " + self.ui.comboBoxMyModelClasses.currentText() + " with Search by Existing Instance method")

            # Change changesMadeToModel boolean to use for exit prompt message
            window.setChangesMadeToModel(True)

        # set window title according to wizard page
        self.button_clicked_setWindowTitle(QWizard.currentId(self))

    def backButton_clicked(self):
        # set window title according to wizard page
        self.button_clicked_setWindowTitle(QWizard.currentId(self))

    def button_clicked_setWindowTitle(self, qwizard_pageId):
        if (qwizard_pageId == 0):
            self.setWindowTitle(QtCore.QString("Search by Existing Instance - Step 1"))
        elif (qwizard_pageId == 1):
            self.setWindowTitle(QtCore.QString("Search by Existing Instance - Step 2"))
        elif (qwizard_pageId == 2):
            self.setWindowTitle(QtCore.QString("Search by Existing Instance - Step 3"))
        elif (qwizard_pageId == 3):
            self.setWindowTitle(QtCore.QString("Search by Existing Instance - Step 4"))
        elif (qwizard_pageId == 4):
            self.setWindowTitle(QtCore.QString("Search by Existing Instance - Step 5"))
        elif (qwizard_pageId == 5):
            self.setWindowTitle(QtCore.QString("Search by Existing Instance - Summary"))

    def insertInstancesFromEMToMyModel(self):

        selected_instances =[]
        for instance in self.ui.treeWidgetSelectInstancesToImport.selectedItems():
            selected_instances.append(Functions.getPhraseWithURL(instance.text(0)))

        window.setGraph(Functions.addNewInstancesToGraph(window.getGraph(), selected_instances, Functions.getPhraseWithURL(self.ui.comboBoxMyModelClasses.currentText()), self))

    def insertDataPropertiesForSelectedInstancesFromEMToMyModel(self, desired_em_properties):
        # Get class name
        my_class = Functions.getPhraseWithURL(self.ui.comboBoxMyModelClasses.currentText())

        # For each selected instance (which has already been imported to My Model's graph)
        for selected_instance in self.ui.treeWidgetSelectInstancesToImport.selectedItems():
            em_instance = Functions.getPhraseWithURL(selected_instance.text(0))

            # For each desired property, query the value(s) from EM
            for em_property in desired_em_properties:
                # Find my model property from DB
                my_model_property = Functions.searchForMyPropertyInMappings(window.getMyModelName(), Functions.getEndpointName(), em_property)

                # Query EM for values of property
                em_values = Functions.queryEndpointForSpecificDataPropertyValue(em_instance, em_property)

                # For each value of this property (in case of multiple values found)
                for em_value in em_values:

                    # Add property and value to my model's graph
                    window.setGraph(Functions.addNewDataPropertyWithValueToGraph(window.getGraph(), my_class, em_instance, my_model_property, em_value.encode('utf8', 'replace'), self))

                #check if owl:equivalentProperty is enabled
                if Functions.getSettingFromDB('equivalent_property_option') == 1:
                    window.setGraph(
                        Functions.addEquivalentPropertyMatchingToGraph(
                            window.getGraph(), my_model_property, em_property
                        )
                    )

    def getSelectedMyModelInstanceFromTree(self):

        return Functions.getPhraseWithURL(self.ui.treeWidgetSelectInstanceToSearchFor.selectedItems()[0].text(0))

    def loadDataToTableWidgetViewPropertiesOfBothModels(self):

        # Clear table
        self.ui.tableWidgetViewPropertiesOfBothModels.setRowCount(0)

        # Get selection of User from QTreeWidget
        selected_instances = []
        for instance in self.ui.treeWidgetSelectInstancesToImport.selectedItems():
            selected_instances.append(Functions.getPhraseWithURL(instance.text(0)))

        unique_em_properties = []

        # Find unique property list for selected instances
        for instance in selected_instances:
            instance_properties_and_values = Functions.queryEndpointForDataPropertiesOfInstance(unicode(instance))

            for property in instance_properties_and_values:
                if property[0] not in unique_em_properties:
                    unique_em_properties.append(property[0])

        # If no properties have been found
        if unique_em_properties == []:
            self.ui.lblShowPropertiesOfBothModels.setText("No properties were found for the selected instance(s).")
            return

        unique_em_properties.sort()

        # Get all my model properties
        my_model_properties = Functions.getAllDataPropertiesFromGraph(window.getGraph())
        my_model_properties.sort()

        # Load properties to Table
        for external_property in unique_em_properties:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetViewPropertiesOfBothModels.rowCount()
            self.ui.tableWidgetViewPropertiesOfBothModels.insertRow(rowPosition)

            # Insert external property to column 0
            self.ui.tableWidgetViewPropertiesOfBothModels.setItem(rowPosition, 0, QtGui.QTableWidgetItem(Functions.getPhraseWithPrefix(external_property)))

            # Create new combo box to list all properties with prefix if possible
            comboBoxMyModelProperties = QtGui.QComboBox()

            comboBoxMyModelProperties.addItem("<empty>")
            for my_model_property in my_model_properties:
                comboBoxMyModelProperties.addItem(Functions.getPhraseWithPrefix(my_model_property))
            comboBoxMyModelProperties.setCurrentIndex(0)

            existing_mapping = Functions.searchForMyPropertyInMappings(window.getMyModelName(), Functions.getEndpointName(), external_property)

            if existing_mapping != False:
                index_of_existing_property_in_combobox = comboBoxMyModelProperties.findText(Functions.getPhraseWithPrefix(existing_mapping))
                # If my model property is found in combobox
                if index_of_existing_property_in_combobox != -1:
                    comboBoxMyModelProperties.setCurrentIndex(index_of_existing_property_in_combobox)

            self.ui.tableWidgetViewPropertiesOfBothModels.setCellWidget(rowPosition, 1, comboBoxMyModelProperties)

    def allButtonPage2Clicked(self):
        self.ui.treeWidgetSelectClasses.selectAll()
        self.ui.treeWidgetSelectClasses.setFocus()

    def allButtonPage3Clicked(self):
        self.ui.treeWidgetSelectInstancesToImport.selectAll()
        self.ui.treeWidgetSelectInstancesToImport.setFocus()

class SearchByInstanceLabel(QtGui.QWizard):
    def __init__(self):
        QtGui.QWizard.__init__(self)
        self.ui = Ui_WizardSearchByInstanceLabel()
        self.ui.setupUi(self)

        # Icons
        self.class_icon = QtGui.QIcon(':/images/class.png')
        self.instance_icon = QtGui.QIcon(':/images/instance.png')
        self.property_icon = QtGui.QIcon(':/images/property.png')
        self.value_icon = QtGui.QIcon(':/images/value.png')
        self.annotation_icon = QtGui.QIcon(':/images/annotation.png')

        # MAKE CONNECTIONS
        self.ui.lineEditSearchInstanceLabelInEMClassName.textChanged.connect(self.lineEditSearchInstanceLabelInEMClassName_textChanged)
        self.button(QtGui.QWizard.NextButton).clicked.connect(lambda: self.nextButton_clicked())
        self.button(QtGui.QWizard.BackButton).clicked.connect(lambda: self.backButton_clicked())
        self.ui.btnSearchInstanceLabelInEM.clicked.connect(self.btnSearchInstanceLabelInEM_clicked)
        self.ui.btnAllPage1.clicked.connect(self.allButtonPage1Clicked)
        self.ui.btnNonePage1.clicked.connect(self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.clearSelection)
        self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults, self))
        self.ui.treeWidgetSummary.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSummary, self))
        self.ui.radioButtonExactMatch.toggled.connect(self.radioButtonExactMatch_toggled)

        self.ui.lineEditSearchTreePage1.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreePage1, self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults))
        self.ui.lineEditSearchTreeSummary.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreeSummary, self.ui.treeWidgetSummary))

        self.ui.btnExpandAll.clicked.connect(self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.expandAll)
        self.ui.btnCollapseAll.clicked.connect(self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.collapseAll)
        self.ui.btnExpandAll_Summary.clicked.connect(self.ui.treeWidgetSummary.expandAll)
        self.ui.btnCollapseAll_Summary.clicked.connect(self.ui.treeWidgetSummary.collapseAll)

        #CONSTRUCT UI ELEMENTS
        self.loadMyModelClassesToCombobox(window.getGraph())
        self.loadLanguagesToComboBox()
        self.ui.lblSearching.setVisible(False)
        self.ui.lblSearchInstanceLabelInEM.setText("Search for instances with label in External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" +
                                                   Functions.getCurrentEndpointName() + "</span>:")
        self.ui.lblSelectMyModelClassToImportInstances.setText("Select a class from My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" +
                                                               window.getMyModelName() + "</span> to import instances:")
        self.ui.lblShowPropertiesOfBothModels.setText("Match properties of External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" +
                                                      Functions.getCurrentEndpointName() + "</span> to equivalent properties of My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" +
                                                      window.getMyModelName() + "</span>:")

    def loadLanguagesToComboBox(self):
        languages_list = Functions.getListOfLanguagesFromDB()

        self.ui.comboBoxSearchLanguage.insertSeparator(self.ui.comboBoxSearchLanguage.count() + 1)

        for language in languages_list:
            self.ui.comboBoxSearchLanguage.addItem(language[0] + ', ' + language[1])

    def radioButtonExactMatch_toggled(self):
        if self.ui.radioButtonExactMatch.isChecked():
            self.ui.checkBoxCaseSensitive.setEnabled(False)
        else:
            self.ui.checkBoxCaseSensitive.setEnabled(True)

    def lineEditSearchInstanceLabelInEMClassName_textChanged(self):
        if self.ui.lineEditSearchInstanceLabelInEMClassName.text() == '':
            self.ui.btnSearchInstanceLabelInEM.setEnabled(False)
        else:
            self.ui.btnSearchInstanceLabelInEM.setEnabled(True)
            self.ui.btnSearchInstanceLabelInEM.setDefault(True)

    def loadMyModelClassesToCombobox(self, my_graph):
        # Get list of classes for this graph
        classes = Functions.getAllClassesFromGraph(my_graph)
        classes.sort()

        # Add classes to combobox of page 2
        for clas in classes:
            self.ui.comboBoxMyModelClasses.addItem(Functions.getPhraseWithPrefix(clas))

        # Put class icon to classes in combobox
        for i in range(self.ui.comboBoxMyModelClasses.count()):
            self.ui.comboBoxMyModelClasses.setItemIcon(i, self.class_icon)

        self.ui.comboBoxMyModelClasses.setCurrentIndex(-1)

    def loadFoundInstancesFromEMToTree(self, foundInstances):
        # Clear tree
        self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.clear()

        # For each found instance
        for instance in foundInstances:

            # Initialize new parent for QTree
            instance_level = QTreeWidgetItem()

            instance_x = Functions.getPhraseWithPrefix(instance)
            instance_level.setText(0, instance_x)
            instance_level.setToolTip(0, "<b>Instance:</b><br> " + instance_x)

            # Set icon
            instance_level.setIcon(0, self.instance_icon)

            ## Search for classes of this instance and add to tree
            classesOfInstance = Functions.queryEndpointForClassesOfInstance(Functions.getPhraseWithURL(instance))

            # Add a "Type of class" child to tree
            class_level = QTreeWidgetItem()
            class_level.setText(0, "Type of:")
            class_level.setIcon(0, self.class_icon)
            class_level.setFlags(QtCore.Qt.ItemFlags(0))
            class_level.setFlags(QtCore.Qt.ItemIsEnabled)
            instance_level.addChild(class_level)

            # Add each class under the "Instances:"
            for clas in classesOfInstance:
                class_sublevel = QTreeWidgetItem()

                clas_x = Functions.getPhraseWithPrefix(clas)
                class_sublevel.setText(0, clas_x)
                class_sublevel.setToolTip(0, "<b>Class:</b><br> " + clas_x)
                # Set icon
                class_sublevel.setIcon(0, self.class_icon)

                class_sublevel.setFlags(QtCore.Qt.ItemFlags(0))
                class_sublevel.setFlags(QtCore.Qt.ItemIsEnabled)
                class_level.addChild(class_sublevel)

            ## Search for data properties of each instance and add to tree
            propertiesOfInstance = Functions.queryEndpointForDataPropertiesOfInstance(instance)

            # Add a "Property" child to tree
            property_level = QTreeWidgetItem()
            property_level.setText(0, "Properties:")
            property_level.setFlags(QtCore.Qt.ItemFlags(0))
            property_level.setFlags(QtCore.Qt.ItemIsEnabled)
            property_level.setIcon(0, self.property_icon)
            instance_level.addChild(property_level)

            # Add each property under the "Properties:"
            for property in propertiesOfInstance:
                property_sublevel = QTreeWidgetItem()

                property_x = Functions.getPhraseWithPrefix(property[0])
                value_x = property[1]
                property_sublevel.setText(0, property_x)
                property_sublevel.setText(1, value_x)
                property_sublevel.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                property_sublevel.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                # Set icons
                property_sublevel.setIcon(0, self.property_icon)
                property_sublevel.setIcon(1, self.value_icon)

                # If it is an annotation property owl:sameAs
                if property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2002/07/owl#sameAs') or property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#seeAlso') or property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label'):
                    property_sublevel.setIcon(0, self.annotation_icon)

                property_sublevel.setFlags(QtCore.Qt.ItemFlags(0))
                property_sublevel.setFlags(QtCore.Qt.ItemIsEnabled)
                property_level.addChild(property_sublevel)

            labels_of_instance = Functions.queryEndpointForLabelsOfInstance(instance)

            for label in labels_of_instance:
                property_sublevel = QTreeWidgetItem()

                property_x = Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label')
                value_x = Functions.getPhraseWithPrefix(Functions.getPhraseWithPrefix(label))
                property_sublevel.setText(0, property_x)
                property_sublevel.setText(1, value_x)
                property_sublevel.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                property_sublevel.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                # Set icons
                property_sublevel.setIcon(0, self.annotation_icon)
                property_sublevel.setIcon(1, self.value_icon)

                property_sublevel.setFlags(QtCore.Qt.ItemFlags(0))
                property_sublevel.setFlags(QtCore.Qt.ItemIsEnabled)
                property_level.addChild(property_sublevel)

            # Insert instance to tree
            self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.insertTopLevelItem(0, instance_level)
            instance_level.setExpanded(True)

        # Sort items
        self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.sortItems(0, 0)

        # Make column 0 wide enough to fit contents (needs to expand all tree and re-collapse as wanted)
        self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.expandAll()
        self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.resizeColumnToContents(0)

        self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.collapseAll()
        for i in range(self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.topLevelItemCount()):
            self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.topLevelItem(i).setExpanded(True)

    def btnSearchInstanceLabelInEM_clicked(self):

        self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.setEnabled(False)
        self.ui.lblSearching.setVisible(True)

        # Clear results tree
        self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.clear()

        QApplication.processEvents()

        instances = []

        if self.ui.radioButtonExactMatch.isChecked():
            searchType = 'Exact match'
        elif self.ui.radioButtonContainsTerm.isChecked() and self.ui.checkBoxCaseSensitive.isChecked():
            searchType = 'Contains + Case sensitive'
        elif self.ui.radioButtonContainsTerm.isChecked() and not self.ui.checkBoxCaseSensitive.isChecked():
            searchType = 'Contains'

        if self.ui.comboBoxSearchLanguage.currentText() == 'None':
            language_code = 'None'
        else:
            language_code = str(self.ui.comboBoxSearchLanguage.currentText()).split(', ')[-1]

        try:
            instances = Functions.queryEndpointForInstancesWithLabel(self.ui.lineEditSearchInstanceLabelInEMClassName.text(), searchType, language_code)
        except:
            # print "label not unicode"
            pass

        # instances = Functions.queryEndpointForInstancesWithLabel(self.ui.lineEditSearchInstanceLabelInEMClassName.text(), searchType, language_code)

        if len(instances) == 0:
            self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.setEnabled(True)
            self.ui.lblSearching.setVisible(False)
            self.ui.lineEditSearchTreePage1.setEnabled(False)
            self.ui.btnExpandAll.setEnabled(False)
            self.ui.btnCollapseAll.setEnabled(False)
            self.ui.btnAllPage1.setEnabled(False)
            self.ui.btnNonePage1.setEnabled(False)

            # Show message box with error
            QtGui.QMessageBox.warning(self, 'Warning', "No instances with label " + self.ui.lineEditSearchInstanceLabelInEMClassName.text() + " were found. \n"
                                                   "Please perform a different search.", QtGui.QMessageBox.Close)

        else:
            # Load instances to tree
            self.loadFoundInstancesFromEMToTree(instances)

            self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.setEnabled(True)
            self.ui.lblSearching.setVisible(False)
            self.ui.lineEditSearchTreePage1.setEnabled(True)
            self.ui.btnExpandAll.setEnabled(True)
            self.ui.btnCollapseAll.setEnabled(True)
            self.ui.btnAllPage1.setEnabled(True)
            self.ui.btnNonePage1.setEnabled(True)

    def loadDataToTableWidgetViewPropertiesOfBothModels(self):

        # Clear table
        self.ui.tableWidgetViewPropertiesOfBothModels.setRowCount(0)

        # Get selection of User from QTreeWidget
        selected_instances = []
        for instance in self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.selectedItems():
            selected_instances.append(Functions.getPhraseWithURL(instance.text(0)))

        unique_em_properties = []

        # Find unique property list for selected instances
        for instance in selected_instances:
            instance_properties_and_values = Functions.queryEndpointForDataPropertiesOfInstance(instance)

            for property in instance_properties_and_values:
                if property[0] not in unique_em_properties:
                    unique_em_properties.append(property[0])

        # If no properties have been found
        if unique_em_properties == []:
            self.ui.lblShowPropertiesOfBothModels.setText("No properties were found for the selected instance(s).")
            return

        unique_em_properties.sort()

        # Get all my model properties
        my_model_properties = Functions.getAllDataPropertiesFromGraph(window.getGraph())
        my_model_properties.sort()

        # Load properties to Table
        for external_property in unique_em_properties:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetViewPropertiesOfBothModels.rowCount()
            self.ui.tableWidgetViewPropertiesOfBothModels.insertRow(rowPosition)

            # Insert external property to column 0
            self.ui.tableWidgetViewPropertiesOfBothModels.setItem(rowPosition, 0, QtGui.QTableWidgetItem(Functions.getPhraseWithPrefix(external_property)))

            # Create new combo box to list all properties with prefix if possible
            comboBoxMyModelProperties = QtGui.QComboBox()
            comboBoxMyModelProperties.addItem("<empty>")
            for my_model_property in my_model_properties:
                comboBoxMyModelProperties.addItem(Functions.getPhraseWithPrefix(my_model_property))
            comboBoxMyModelProperties.setCurrentIndex(0)

            existing_mapping = Functions.searchForMyPropertyInMappings(window.getMyModelName(), Functions.getEndpointName(), external_property)

            if existing_mapping != False:
                index_of_existing_property_in_combobox = comboBoxMyModelProperties.findText(Functions.getPhraseWithPrefix(existing_mapping))
                # If my model property is found in combobox
                if index_of_existing_property_in_combobox != -1:
                    comboBoxMyModelProperties.setCurrentIndex(index_of_existing_property_in_combobox)

            self.ui.tableWidgetViewPropertiesOfBothModels.setCellWidget(rowPosition, 1, comboBoxMyModelProperties)

    def insertInstancesFromEMToMyModel(self):

        selected_instances =[]
        for instance in self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.selectedItems():
            selected_instances.append(Functions.getPhraseWithURL(instance.text(0)))

        window.setGraph(Functions.addNewInstancesToGraph(window.getGraph(), selected_instances, Functions.getPhraseWithURL(self.ui.comboBoxMyModelClasses.currentText()), self))

    def insertDataPropertiesForSelectedInstancesFromEMToMyModel(self, desired_em_properties):
        # Get class name
        my_class = Functions.getPhraseWithURL(self.ui.comboBoxMyModelClasses.currentText())

        # For each selected instance (which has already been imported to My Model's graph)
        for selected_instance in self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.selectedItems():
            em_instance = Functions.getPhraseWithURL(selected_instance.text(0))

            # For each desired property, query the value(s) from EM
            for em_property in desired_em_properties:
                # Find my model property from DB
                my_model_property = Functions.searchForMyPropertyInMappings(window.getMyModelName(), Functions.getEndpointName(), em_property)

                # Query EM for values of property
                em_values = Functions.queryEndpointForSpecificDataPropertyValue(em_instance, em_property)

                # For each value of this property (in case of multiple values found)
                for em_value in em_values:

                    # Add property and value to my model's graph
                    window.setGraph(Functions.addNewDataPropertyWithValueToGraph(window.getGraph(), my_class, em_instance, my_model_property, em_value.encode('utf8', 'replace'), self))

                # Check if owl:equivalentProperty is enabled
                if Functions.getSettingFromDB('equivalent_property_option') == 1:
                    window.setGraph(
                        Functions.addEquivalentPropertyMatchingToGraph(
                            window.getGraph(), my_model_property, em_property
                        )
                    )

    def loadSelectedInstancesWithMyClassURLToResults(self):
        # Clear table
        self.ui.listWidgetAddedInstances.clear()

        my_namespace = Functions.getURLOfPhrase(Functions.getPhraseWithURL(self.ui.comboBoxMyModelClasses.currentText()))

        for instance in self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.selectedItems():
            instance_name = Functions.URLAndNameToPrefixAndName(Functions.getPhraseWithURL(instance.text(0)))['name']

            instance_full = Functions.getPhraseWithPrefix(Functions.createInstaceURIFromNamespaceAndInstanceName(my_namespace, instance_name))

            self.ui.listWidgetAddedInstances.addItem(instance_full)

    def allButtonPage1Clicked(self):
        self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.selectAll()
        self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.setFocus()

    def nextButton_clicked(self):

        # If it is page 2
        if self.currentId() == 1:
            # If no selection has been made
            if len(self.ui.treeWidgetSearchInstanceLabelInEMInstancesResults.selectedItems()) == 0:
                # Go back to page 1
                self.back()

                # Show message box with error
                QtGui.QMessageBox.critical(self, 'Error', "Please select an instance (or more) from the list  to import to My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" +
                    window.getMyModelName() + "</span>.", QtGui.QMessageBox.Close)
                return

        # If it is page 3
        if self.currentId() == 2:
            # If no selection has been made
            if self.ui.comboBoxMyModelClasses.currentIndex() == -1:
                # Go back to page 2
                self.back()

                # Show message box with error
                QtGui.QMessageBox.critical(self, 'Error', "Please select a class from My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'> " + window.getMyModelName() +
                                           "</span> to import instances.", QtGui.QMessageBox.Close)

                return

            # Alter properties of specific buttons in wizard pages
            self.ui.wizardPage3.setButtonText(QWizard.NextButton, 'Populate')

            self.loadDataToTableWidgetViewPropertiesOfBothModels()

        # If it is page 4 (Populate button has been pressed)
        if self.currentId() == 3:
            # Clear summary tree
            self.ui.treeWidgetSummary.clear()

            # Create a list with the desired properties
            desired_em_properties = []

            # Handle mapping table
            for row in range(self.ui.tableWidgetViewPropertiesOfBothModels.rowCount()):
                # If it is not <empty>
                if self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText() != '<empty>':
                    # Add to desired properties
                    desired_em_properties.append(Functions.getPhraseWithURL(self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text()))

                    # Update mapping if it exists
                    Functions.updateMappingToDB(window.getMyModelName(), self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText(), self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(), Functions.getEndpointName())

                    # Insert mapping if it does not exist
                    Functions.addMappingToDB(window.getMyModelName(), self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText(), self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(), Functions.getEndpointName())

                # If it is <empty> delete if from DB (if it exists)
                else:
                    Functions.deleteMappingOfExternalPropertyFromBD(window.getMyModelName(), self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(), Functions.getEndpointName())

            # Insert selected instances from EM to MyModel
            self.insertInstancesFromEMToMyModel()

            # Insert selected data properties to graph and put the inserted triples to summary tree widget
            self.insertDataPropertiesForSelectedInstancesFromEMToMyModel(desired_em_properties)

            # Add text to result list and label
            self.ui.lblPopulatedInstances.setText("Instances added to class " + self.ui.comboBoxMyModelClasses.currentText() + ".")
            #self.loadSelectedInstancesWithMyClassURLToResults()

            # Sort and arrange summary tree widget
            # Sort items of summary tree widget
            self.ui.treeWidgetSummary.sortItems(0, 0)

            # Make column 0 of summary tree widget wide enough to fit contents (needs to expand all tree and re-collapse as wanted)
            self.ui.treeWidgetSummary.expandAll()
            self.ui.treeWidgetSummary.resizeColumnToContents(0)

            # Log
            Functions.addEntryToLog("Instances added to class " + self.ui.comboBoxMyModelClasses.currentText() + " with Search by Instance Label method")

            # Change changesMadeToModel to use for exit prompt message
            window.setChangesMadeToModel(True)

        # set window title according to wizard page
        self.button_clicked_setWindowTitle(QWizard.currentId(self))

    def backButton_clicked(self):
        # set window title according to wizard page
        self.button_clicked_setWindowTitle(QWizard.currentId(self))

    def button_clicked_setWindowTitle(self, qwizard_pageId):
        if (qwizard_pageId == 0):
            self.setWindowTitle(QtCore.QString("Search by Instance Label - Step 1"))
        elif (qwizard_pageId == 1):
            self.setWindowTitle(QtCore.QString("Search by Instance Label - Step 2"))
        elif (qwizard_pageId == 2):
            self.setWindowTitle(QtCore.QString("Search by Instance Label - Step 3"))
        elif (qwizard_pageId == 3):
            self.setWindowTitle(QtCore.QString("Search by Instance Label - Summary"))

class EnrichInstance(QtGui.QWizard):

    def __init__(self):
        QtGui.QWizard.__init__(self)
        self.ui = Ui_WizardEnrichInstance()
        self.ui.setupUi(self)

        # MAKE CONNECTIONS
        self.button(QtGui.QWizard.NextButton).clicked.connect(lambda: self.nextButton_clicked())
        self.button(QtGui.QWizard.BackButton).clicked.connect(lambda: self.backButton_clicked())
        self.ui.treeWidgetSelectInstanceToSearchFor.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSelectInstanceToSearchFor, self))
        self.ui.treeWidgetSelectPropertiesToImport.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSelectPropertiesToImport, self))
        self.ui.treeWidgetSummary.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSummary, self))
        self.ui.btnAllPage2.clicked.connect(self.allButtonClicked)
        self.ui.btnNonePage2.clicked.connect(self.ui.treeWidgetSelectPropertiesToImport.clearSelection)

        self.ui.lineEditSearchTreePage1.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreePage1, self.ui.treeWidgetSelectInstanceToSearchFor))
        self.ui.lineEditSearchTreePage2.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreePage2, self.ui.treeWidgetSelectPropertiesToImport))
        self.ui.lineEditSearchTreeSummary.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreeSummary, self.ui.treeWidgetSummary))

        self.ui.btnExpandAllPage1.clicked.connect(self.ui.treeWidgetSelectInstanceToSearchFor.expandAll)
        self.ui.btnCollapseAllPage1.clicked.connect(self.ui.treeWidgetSelectInstanceToSearchFor.collapseAll)
        self.ui.btnExpandAllPage2.clicked.connect(self.ui.treeWidgetSelectPropertiesToImport.expandAll)
        self.ui.btnCollapseAllPage2.clicked.connect(self.ui.treeWidgetSelectPropertiesToImport.collapseAll)
        self.ui.btnExpandAll_Summary.clicked.connect(self.ui.treeWidgetSummary.expandAll)
        self.ui.btnCollapseAll_Summary.clicked.connect(self.ui.treeWidgetSummary.collapseAll)

        # Icons
        self.class_icon = QtGui.QIcon(':/images/class.png')
        self.instance_icon = QtGui.QIcon(':/images/instance.png')
        self.property_icon = QtGui.QIcon(':/images/property.png')
        self.value_icon = QtGui.QIcon(':/images/value.png')
        self.annotation_icon = QtGui.QIcon(':/images/annotation.png')

        #CONSTRUCT UI ELEMENTS
        self.ui.lblSearchInstanceInEM.setText("Select an instance of My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + window.getMyModelName() +
                                              "</span> to search for similar instances in the External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" + Functions.getCurrentEndpointName() + "</span>:")
        self.ui.lblShowPropertiesOfBothModels.setText("Match properties of External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" +
                                                      Functions.getCurrentEndpointName() + "</span> to equivalent properties of My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" +
                                                      window.getMyModelName() + "</span>:")
        self.loadMyModelToTree(window.getGraph())

    def loadMyModelToTree(self, my_graph):
        # Clear Tree
        self.ui.treeWidgetSelectInstanceToSearchFor.clear()

        # Get list of classes for this graph
        classes = Functions.getAllClassesFromGraph(my_graph)

        # For each class
        for clas in classes:

            # Initialize new parent for QTree
            class_level = QTreeWidgetItem()
            clas_x = Functions.getPhraseWithPrefix(clas)
            class_level.setText(0, clas_x)
            class_level.setFlags(QtCore.Qt.ItemFlags(0))
            class_level.setFlags(QtCore.Qt.ItemIsEnabled)
            class_level.setToolTip(0, "<b>Class:</b><br> " + clas_x)
            # Set icon
            class_level.setIcon(0, self.class_icon)

            # Get all instances of class
            class_instances = Functions.getInstancesOfClassFromGraph(my_graph, clas)

            # For each instance
            for instance in class_instances:

                # Initialize new parent for QTree
                instance_level = QTreeWidgetItem()
                instance_x = Functions.getPhraseWithPrefix(instance)
                instance_level.setText(0, instance_x)
                instance_level.setToolTip(0, "<b>Instance:</b><br> " + instance_x)

                # Set icon
                instance_level.setIcon(0, self.instance_icon)

                class_level.addChild(instance_level)

                instance_properties = Functions.getDataPropertiesOfInstanceFromGraph(my_graph, instance)

                for instance_property in instance_properties:
                    property_level = QTreeWidgetItem()

                    property_x = Functions.getPhraseWithPrefix(instance_property[0])
                    value_x = instance_property[1].toPython()
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setFlags(QtCore.Qt.ItemFlags(0))
                    property_level.setFlags(QtCore.Qt.ItemIsEnabled)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.property_icon)
                    property_level.setIcon(1, self.value_icon)

                    instance_level.addChild(property_level)

                allSameAsValues = Functions.getSameAsValueForInstanceFromGraph(my_graph, instance)

                for sameAsValue in allSameAsValues:

                    property_level = QTreeWidgetItem()
                    property_x = Functions.getPhraseWithPrefix('http://www.w3.org/2002/07/owl#sameAs')
                    value_x = Functions.getPhraseWithPrefix(sameAsValue)
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setFlags(QtCore.Qt.ItemFlags(0))
                    property_level.setFlags(QtCore.Qt.ItemIsEnabled)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.annotation_icon)
                    property_level.setIcon(1, self.value_icon)

                    instance_level.addChild(property_level)

                labels_of_instance = Functions.getLabelsOfInstanceFromGraph(window.getGraph(), instance)

                for label in labels_of_instance:

                    property_level = QTreeWidgetItem()
                    property_x = Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label')
                    value_x = label
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setFlags(QtCore.Qt.ItemFlags(0))
                    property_level.setFlags(QtCore.Qt.ItemIsEnabled)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.annotation_icon)
                    property_level.setIcon(1, self.value_icon)

                    instance_level.addChild(property_level)

            self.ui.treeWidgetSelectInstanceToSearchFor.insertTopLevelItem(0, class_level)

        self.ui.treeWidgetSelectInstanceToSearchFor.sortItems(0, 0)

        self.ui.treeWidgetSelectInstanceToSearchFor.expandAll()

        # Make column 0 wide enough to fit contents
        self.ui.treeWidgetSelectInstanceToSearchFor.resizeColumnToContents(0)

    def loadInstancesFromEMToTree(self, instances):
        # Clear tree
        self.ui.treeWidgetSelectPropertiesToImport.clear()

        # For each class
        for instance in instances:

            # Initialize new parent for QTree
            instance_level = QTreeWidgetItem()
            instance_x = Functions.getPhraseWithPrefix(instance)
            instance_level.setText(0, instance_x)
            instance_level.setFlags(QtCore.Qt.ItemFlags(0))
            instance_level.setFlags(QtCore.Qt.ItemIsEnabled)
            instance_level.setToolTip(0, "<b>Instance:</b><br> " + instance_x)

            # Set icon
            instance_level.setIcon(0, self.instance_icon)

            ## Search for parent classes of each instance and add to tree
            classes = Functions.queryEndpointForClassesOfInstance(instance)

            # Add a "Type of class" child to tree
            class_level = QTreeWidgetItem()
            class_level.setText(0, "Type of:")
            class_level.setFlags(QtCore.Qt.ItemFlags(0))
            class_level.setFlags(QtCore.Qt.ItemIsEnabled)
            class_level.setIcon(0, self.class_icon)
            instance_level.addChild(class_level)

            # Add each class under the "Type of class"
            for clas in classes:
                class_sublevel = QTreeWidgetItem()
                clas_x = Functions.getPhraseWithPrefix(clas)
                class_sublevel.setText(0, clas_x)
                class_sublevel.setToolTip(0, "<b>Class:</b><br> " + clas_x)
                # Set icon
                class_sublevel.setIcon(0, self.class_icon)

                class_sublevel.setFlags(QtCore.Qt.ItemFlags(0))
                class_sublevel.setFlags(QtCore.Qt.ItemIsEnabled)
                class_level.addChild(class_sublevel)

                class_level.addChild(class_sublevel)

            ## Search for data properties of each instance and add to tree
            properties = Functions.queryEndpointForDataPropertiesOfInstance(instance)

            # Add a "Property" child to tree
            property_level = QTreeWidgetItem()
            property_level.setText(0, "Properties:")
            property_level.setFlags(QtCore.Qt.ItemFlags(0))
            property_level.setFlags(QtCore.Qt.ItemIsEnabled)
            property_level.setIcon(0, self.property_icon)
            instance_level.addChild(property_level)

            # Add each property under the "Property"
            for property in properties:
                property_sublevel = QTreeWidgetItem()
                property_x = Functions.getPhraseWithPrefix(property[0])
                value_x = property[1]
                property_sublevel.setText(0, property_x)
                property_sublevel.setText(1, value_x)
                property_sublevel.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                property_sublevel.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                # Set icons
                property_sublevel.setIcon(0, self.property_icon)
                property_sublevel.setIcon(1, self.value_icon)

                # If it is an annotation property owl:sameAs
                if property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2002/07/owl#sameAs') or property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#seeAlso') or property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label'):
                    property_sublevel.setIcon(0, self.annotation_icon)

                property_level.addChild(property_sublevel)

            self.ui.treeWidgetSelectPropertiesToImport.insertTopLevelItem(0, instance_level)
            instance_level.setExpanded(True)
            property_level.setExpanded(True)
            class_level.setExpanded(True)
            self.ui.treeWidgetSelectPropertiesToImport.resizeColumnToContents(0)
            class_level.setExpanded(False)


        self.ui.treeWidgetSelectPropertiesToImport.sortItems(0, 0)

        # Make column 0 wide enough to fit contents
        # self.ui.treeWidgetSelectPropertiesToImport.resizeColumnToContents(0)

    def nextButton_clicked(self):

        # If it is page 2
        if self.currentId() == 1:
            # If no selection has been made
            if len(self.ui.treeWidgetSelectInstanceToSearchFor.selectedItems()) == 0:
                # Go back to page 1
                self.back()

                # Show message box with error
                QtGui.QMessageBox.critical(self, 'Error', "Please select an instance from the list.", QtGui.QMessageBox.Close)
                return


            # Get selected instance of my model as URL phrase
            selectedInstanceToSearch = self.getSelectedMyModelInstanceFromTree()

            # Get label of instance
            labelsOfInstanceToSearch = Functions.getLabelsOfInstanceFromGraph(window.getGraph(), selectedInstanceToSearch)

            # If no label found
            if len(labelsOfInstanceToSearch) == 0:
                self.back()

                # Show message box with warning
                QtGui.QMessageBox.warning(self, 'Warning', "This instance does not have an rdfs:label to search for.", QtGui.QMessageBox.Close)
                return

            # Query endpoint for instances with the same label
            instancesFromEM = []

            # For each label found in MM for this instance
            for label in labelsOfInstanceToSearch:
                try:
                    # Query endpoint for instances with this label and put results in instancesFromEM
                    instancesFromEM.extend(Functions.queryEndpointForInstancesWithLabel(label, searchType= 'Exact match'))
                except:
                    #print "label not unicode"
                    pass

            if instancesFromEM != []:
                # Change label in page 2
                self.ui.lblSearchForInstanceSimilarInstancesFound.setText("Instances found in <span style='font-size:9pt; font-weight:550; color:#377a97;'>" + Functions.getCurrentEndpointName() +
                                                                        "</span>. Please select properties to import to the instance of My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" +
                                                                          window.getMyModelName() + "</span>.")
            else:
                self.ui.lblSearchForInstanceSimilarInstancesFound.setText("No similar instances found in <span style='font-size:9pt; font-weight:550; color:#377a97;'>" + Functions.getCurrentEndpointName() +
                                                                        "</span>. Please go back and select a different instance to enrich. ")

            # Load instances to tree
            self.loadInstancesFromEMToTree(instancesFromEM)

        # If it is page 3
        if self.currentId() == 2:
            # If no selection has been made
            if len(self.ui.treeWidgetSelectPropertiesToImport.selectedItems()) == 0:
                # Go back to page 2
                self.back()

                # Show message box with error
                QtGui.QMessageBox.critical(self, 'Error', "Please select a property (or more) from the list to import to My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" +
                                           window.getMyModelName() + "</span>.", QtGui.QMessageBox.Close)

                return

            # Alter properties of specific buttons in wizard pages
            self.ui.wizardPage3.setButtonText(QWizard.NextButton, 'Populate')

            self.loadDataToTableWidgetViewPropertiesOfBothModels()

        # If it is page 5 (Populate button has been pressed)
        if self.currentId() == 3:
            # Handle mapping table
            for row in range(self.ui.tableWidgetViewPropertiesOfBothModels.rowCount()):
                if self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText() != '<empty>':
                    # Update mapping if it exists
                    Functions.updateMappingToDB(window.getMyModelName(), self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText(), self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(), Functions.getEndpointName())

                    # Insert mapping if it does not exist
                    Functions.addMappingToDB(window.getMyModelName(), self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText(), self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(), Functions.getEndpointName())

                # If it is <empty> delete if from DB (if it exists)
                else:
                    Functions.deleteMappingOfExternalPropertyFromBD(window.getMyModelName(), self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(), Functions.getEndpointName())

            # Insert selected instances from EM to MyModel
            inserted_properties = self.insertPropertiesAndValuesFromEMToMyModelInstance()

            # Load to results list and label
            self.ui.lblPopulatedInstances.setText("Instance " + Functions.getPhraseWithPrefix(self.getSelectedMyModelInstanceFromTree()) + " was enriched with properties:")

            # self.loadSelectedPropertiesToResultsList(inserted_properties)
            self.loadSelectedPropertiesToSummaryTree(Functions.getPhraseWithPrefix(self.getSelectedMyModelInstanceFromTree()), inserted_properties)

            # Log
            Functions.addEntryToLog("Instance " + Functions.getPhraseWithPrefix(self.getSelectedMyModelInstanceFromTree()) + " was enriched with properties")

            # Change changesMadeToModel to use for exit prompt message
            window.setChangesMadeToModel(True)

        # set window title according to wizard page
        self.button_clicked_setWindowTitle(QWizard.currentId(self))

    def backButton_clicked(self):
        # set window title according to wizard page
        self.button_clicked_setWindowTitle(QWizard.currentId(self))

    def button_clicked_setWindowTitle(self, qwizard_pageId):
        if (qwizard_pageId == 0):
            self.setWindowTitle(QtCore.QString("Enrich Instance with Properties - Step 1"))
        elif (qwizard_pageId == 1):
            self.setWindowTitle(QtCore.QString("Enrich Instance with Properties - Step 2"))
        elif (qwizard_pageId == 2):
            self.setWindowTitle(QtCore.QString("Enrich Instance with Properties - Step 3"))
        elif (qwizard_pageId == 3):
            self.setWindowTitle(QtCore.QString("Enrich Instance with Properties - Summary"))

    def loadSelectedPropertiesToSummaryTree(self, enriched_instance, inserted_properties):

        # Clear tree
        self.ui.treeWidgetSummary.clear()

        instance_level = QTreeWidgetItem()
        instance_level.setText(0, enriched_instance)
        instance_level.setIcon(0, self.instance_icon)

        # Add items
        for property in inserted_properties:

            property_level = QTreeWidgetItem()
            property_x = Functions.getPhraseWithPrefix(property[0])
            value_x = property[1]
            property_level.setText(0, property_x)
            property_level.setText(1, value_x)
            property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
            property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

            # Set icons
            property_level.setIcon(0, self.property_icon)
            property_level.setIcon(1, self.value_icon)

            # If it is an annotation property owl:sameAs
            if property_x == 'owl:sameAs' or property_x == Functions.getPhraseWithPrefix('owl:sameAs'):
                property_level.setIcon(0, self.annotation_icon)

            instance_level.addChild(property_level)

        self.ui.treeWidgetSummary.insertTopLevelItem(0, instance_level)
        self.ui.treeWidgetSummary.expandAll()

        # Make column 0 wide enough to fit contents
        self.ui.treeWidgetSummary.resizeColumnToContents(0)

    def insertPropertiesAndValuesFromEMToMyModelInstance(self):

        selected_instance_to_enrich = self.getSelectedMyModelInstanceFromTree()
        selected_properties_and_values = self.getSelectedPropertiesAndValuesFromTree()
        inserted_properties = []

        for property in selected_properties_and_values:
            # Correspond EM property with my model property from DB
            my_model_property = Functions.searchForMyPropertyInMappings(window.getMyModelName(), Functions.getEndpointName(), property[0])

            # If mapping was found
            if my_model_property != False:
                # Enrich instance with properties
                window.setGraph(Functions.enrichInstanceWithDataPropertyInGraph(window.getGraph(), selected_instance_to_enrich, my_model_property, property[1]))

                #check if owl:equivalentProperty is enabled
                if Functions.getSettingFromDB('equivalent_property_option') == 1:
                    window.setGraph(
                        Functions.addEquivalentPropertyMatchingToGraph(
                            window.getGraph(), my_model_property, property[0]
                        )
                    )

                # Add to list
                inserted_properties.append([my_model_property, property[1]])

        return inserted_properties

    def getSelectedMyModelInstanceFromTree(self):
        selectedItem = self.ui.treeWidgetSelectInstanceToSearchFor.selectedItems()[0].text(0)

        return Functions.getPhraseWithURL(selectedItem)

    def getSelectedPropertiesAndValuesFromTree(self):
        # Get selection of User from QTreeWidget
        selected_properties_and_values = []
        for property_line in self.ui.treeWidgetSelectPropertiesToImport.selectedItems():
            property = property_line.text(0)

            value = property_line.text(1)

            selected_properties_and_values.append([Functions.getPhraseWithURL(property), value])

        return selected_properties_and_values

    def loadDataToTableWidgetViewPropertiesOfBothModels(self):

        # Clear table
        self.ui.tableWidgetViewPropertiesOfBothModels.setRowCount(0)

        selected_properties_and_values = self.getSelectedPropertiesAndValuesFromTree()

        unique_em_properties = []

        # Find unique property list for selected instances
        for property in selected_properties_and_values:
            if property[0] not in unique_em_properties:
                unique_em_properties.append(property[0])

        # If no properties have been found
        if unique_em_properties == []:
            self.ui.lblShowPropertiesOfBothModels.setText("No properties were found for the selected instance(s).")
            return

        unique_em_properties.sort()

        # Get all my model properties
        my_model_properties = Functions.getAllDataPropertiesFromGraph(window.getGraph())
        my_model_properties.sort()

        # Load properties to Table
        for external_property in unique_em_properties:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetViewPropertiesOfBothModels.rowCount()
            self.ui.tableWidgetViewPropertiesOfBothModels.insertRow(rowPosition)

            # Insert external property to column 0
            self.ui.tableWidgetViewPropertiesOfBothModels.setItem(rowPosition, 0, QtGui.QTableWidgetItem(Functions.getPhraseWithPrefix(external_property)))

            # Create new combo box to list all properties with prefix if possible
            comboBoxMyModelProperties = QtGui.QComboBox()
            comboBoxMyModelProperties.addItem("<empty>")
            for my_model_property in my_model_properties:
                comboBoxMyModelProperties.addItem(Functions.getPhraseWithPrefix(my_model_property))
            comboBoxMyModelProperties.setCurrentIndex(0)

            existing_mapping = Functions.searchForMyPropertyInMappings(window.getMyModelName(), Functions.getEndpointName(), external_property)

            if existing_mapping != False:
                index_of_existing_property_in_combobox = comboBoxMyModelProperties.findText(Functions.getPhraseWithPrefix(existing_mapping))
                # If my model property is found in combobox
                if index_of_existing_property_in_combobox != -1:
                    comboBoxMyModelProperties.setCurrentIndex(index_of_existing_property_in_combobox)

            self.ui.tableWidgetViewPropertiesOfBothModels.setCellWidget(rowPosition, 1, comboBoxMyModelProperties)

    def allButtonClicked(self):
        self.ui.treeWidgetSelectPropertiesToImport.selectAll()
        self.ui.treeWidgetSelectPropertiesToImport.setFocus()

class SearchByClassWizard(QtGui.QWizard):

    current_selected_instances_with_properties_and_values = []

    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self)
        super(SearchByClassWizard, self).__init__(parent)
        self.ui = Ui_WizardSearchByClassName()
        self.ui.setupUi(self)

        # Icons
        self.class_icon = QtGui.QIcon(':/images/class.png')
        self.instance_icon = QtGui.QIcon(':/images/instance.png')
        self.property_icon = QtGui.QIcon(':/images/property.png')
        self.value_icon = QtGui.QIcon(':/images/value.png')
        self.annotation_icon = QtGui.QIcon(':/images/annotation.png')

        # MAKE CONNECTIONS
        self.ui.btnSearchClassInEM.clicked.connect(self.btnSearchClassInEM_clicked)
        self.ui.lineEditSearchClassInEMClassName.textChanged.connect(self.lineEditSearchClassInEMClassName_textChanged)
        self.button(QWizard.NextButton).clicked.connect(lambda: self.nextButton_clicked())
        self.button(QWizard.BackButton).clicked.connect(lambda: self.backButton_clicked())
        self.ui.btnAllPage1.clicked.connect(self.allButtonClicked)
        self.ui.btnNonePage1.clicked.connect(self.ui.treeWidgetSearchClassInEMInstancesResults.clearSelection)

        self.ui.treeWidgetSearchClassInEMInstancesResults.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSearchClassInEMInstancesResults, self))
        self.ui.treeWidgetSummary.customContextMenuRequested.connect(lambda: Functions.openContextMenuInTree(self.ui.treeWidgetSummary, self))

        self.ui.lineEditSearchTreePage1.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreePage1, self.ui.treeWidgetSearchClassInEMInstancesResults))
        self.ui.lineEditSearchTreeSummary.textChanged.connect(lambda: Functions.searchTree(self.ui.lineEditSearchTreeSummary, self.ui.treeWidgetSummary))

        self.ui.btnExpandAll.clicked.connect(self.ui.treeWidgetSearchClassInEMInstancesResults.expandAll)
        self.ui.btnCollapseAll.clicked.connect(self.ui.treeWidgetSearchClassInEMInstancesResults.collapseAll)
        self.ui.btnExpandAll_Summary.clicked.connect(self.ui.treeWidgetSummary.expandAll)
        self.ui.btnCollapseAll_Summary.clicked.connect(self.ui.treeWidgetSummary.collapseAll)

        # CONSTRUCT UI ELEMENTS
        self.loadListOfPrefixesOfNamespacesToComboBox()
        self.loadAvailableClassesOfMMInComboBox()
        self.ui.lblSearching.setVisible(False)
        self.ui.lblSearchClassInEM.setText("Search for class in External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'> " + Functions.getCurrentEndpointName() +
                                           "</span>:")

        # Alter properties of specific buttons in wizard pages
        self.ui.wizardPage3.setButtonText(QWizard.NextButton, 'Populate')

    def getSelectedInstacesWithPropertiesAndValues(self):
        return self.current_selected_instances_with_properties_and_values

    def setSelectedInstancesWithPropertiesAndValues(self, newSelectedInstancesWithPropertiesAndValues):
        self.current_selected_instances_with_properties_and_values = newSelectedInstancesWithPropertiesAndValues

    def getSelectedInstancesToPopulate(self):
        # To get only instances to populate from current selection kept in list with properties and values
        instances_to_populate = []
        for instance_row in self.getSelectedInstacesWithPropertiesAndValues(): #self.getSelectedInstacesWithPropertiesAndValues() are already with https
            if instance_row[0] not in instances_to_populate: # instance_row[0] is instance URI
                instances_to_populate.append(instance_row[0])

        return instances_to_populate


    def loadAvailableClassesOfMMInComboBox(self):

        self.ui.comboBoxAvailableClassesInMM.clear()

        all_classes_in_MM = Functions.getAllClassesFromGraph(window.getGraph())
        all_classes_in_MM.sort()

        for tmp_class in all_classes_in_MM:
            self.ui.comboBoxAvailableClassesInMM.addItem(Functions.getPhraseWithPrefix(tmp_class))

        # Put class icon to classes in combobox
        for i in range(self.ui.comboBoxAvailableClassesInMM.count()):
            self.ui.comboBoxAvailableClassesInMM.setItemIcon(i, self.class_icon)

        self.ui.comboBoxAvailableClassesInMM.setCurrentIndex(-1)

    def loadListOfPrefixesOfNamespacesToComboBox(self):
        prefixes = Functions.getListOfNamespacePrefixesFromDB()

        # Put each result in comboBoxNamespaces
        for prefix in prefixes:
            self.ui.comboBoxNamespaces.addItem((prefix))

    def lineEditSearchClassInEMClassName_textChanged(self):
        if self.ui.lineEditSearchClassInEMClassName.text() == '':
            self.ui.btnSearchClassInEM.setEnabled(False)
        else:
            self.ui.btnSearchClassInEM.setEnabled(True)
            self.ui.btnSearchClassInEM.setDefault(True)

    def btnSearchClassInEM_clicked(self):

        # clear if anything is imported in QTreeWidget from previous btnSearchClassInEM_clicked
        self.ui.treeWidgetSearchClassInEMInstancesResults.clear()

        # Show searching label
        self.ui.lblSearching.setVisible(True)
        # Disable treewidget
        self.ui.treeWidgetSearchClassInEMInstancesResults.setEnabled(False)

        QApplication.processEvents()

        # Get values from components
        prefixToSearch = self.ui.comboBoxNamespaces.currentText()
        classNameToSearch = self.ui.lineEditSearchClassInEMClassName.text()

        instances_of_class = []

        try:
            # Fetch all instances and their properties of Class defined by user (with limit)
            instances_of_class = Functions.queryEndpointForInstancesOfClassWithPrefix(prefixToSearch + ":" + classNameToSearch)
        except:
            # print "class name not unicode"
            pass

        if instances_of_class.__len__() == 0:
            self.ui.lblSearching.setVisible(False)
            self.ui.treeWidgetSearchClassInEMInstancesResults.setEnabled(True)

            self.ui.lineEditSearchTreePage1.setEnabled(False)
            self.ui.btnAllPage1.setEnabled(False)
            self.ui.btnNonePage1.setEnabled(False)
            self.ui.btnExpandAll.setEnabled(False)
            self.ui.btnCollapseAll.setEnabled(False)

            # Show message box with error
            QtGui.QMessageBox.warning(self, 'Warning', "No such class or instances found for class "
                                                      "<span style='font-size:9pt; font-weight:550; color:#000000;'>" + prefixToSearch + ":" + classNameToSearch + "</span>. <br>\n"
                                                   "Please perform a different search.", QtGui.QMessageBox.Close)


        else:
            # For each instance, get all properties from EM
            for instance in instances_of_class:
                # Initialize new parent for QTree
                instance_level = QTreeWidgetItem()
                instance_x = Functions.getPhraseWithPrefix(instance)
                instance_level.setText(0, instance_x)
                instance_level.setToolTip(0, "<b>Instance:</b><br> " + instance_x)

                # Set icon
                instance_level.setIcon(0, self.instance_icon)

                # instance_properties = self.getAllPropertiesWithValuesFromEMForAnInstanceWithURI(instance)
                instance_properties = Functions.queryEndpointForDataPropertiesOfInstance(instance)

                for instance_property_row in instance_properties:
                    property_level = QTreeWidgetItem()
                    property_x = Functions.getPhraseWithPrefix(instance_property_row[0])
                    value_x = instance_property_row[1]

                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    # child.setText(0, tmp_text)
                    property_level.setFlags(QtCore.Qt.ItemFlags(0)) #NoItemFlags
                    property_level.setFlags(QtCore.Qt.ItemIsEnabled) #Only enabled, not selectable or clickable, etc.

                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.property_icon)
                    property_level.setIcon(1, self.value_icon)

                    # If it is an annotation property owl:sameAs
                    if property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2002/07/owl#sameAs') or property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#seeAlso') or property_x == Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label'):
                        property_level.setIcon(0, self.annotation_icon)

                    instance_level.addChild(property_level)

                # add rdfs:label values of instance in qtreewidget
                labels_of_instance = Functions.queryEndpointForLabelsOfInstance(instance)

                for label in labels_of_instance:
                    property_level = QTreeWidgetItem()
                    property_x = Functions.getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label')
                    value_x = label
                    property_level.setText(0, property_x)
                    property_level.setText(1, value_x)
                    property_level.setFlags(QtCore.Qt.ItemFlags(0))
                    property_level.setFlags(QtCore.Qt.ItemIsEnabled)
                    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
                    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

                    # Set icons
                    property_level.setIcon(0, self.annotation_icon)
                    property_level.setIcon(1, self.value_icon)

                    instance_level.addChild(property_level)

                self.ui.treeWidgetSearchClassInEMInstancesResults.insertTopLevelItem(0, instance_level)

            self.ui.treeWidgetSearchClassInEMInstancesResults.sortItems(0, 0)

            self.ui.treeWidgetSearchClassInEMInstancesResults.expandAll()
            self.ui.treeWidgetSearchClassInEMInstancesResults.resizeColumnToContents(0)
            self.ui.treeWidgetSearchClassInEMInstancesResults.collapseAll()

            self.ui.lineEditSearchTreePage1.setEnabled(True)
            self.ui.btnAllPage1.setEnabled(True)
            self.ui.btnNonePage1.setEnabled(True)
            self.ui.btnExpandAll.setEnabled(True)
            self.ui.btnCollapseAll.setEnabled(True)

            self.ui.lblSearching.setVisible(False)
            self.ui.treeWidgetSearchClassInEMInstancesResults.setEnabled(True)

    def nextButton_clicked(self):

        # Get selection of User in QTreeWidget
        selected_items = self.ui.treeWidgetSearchClassInEMInstancesResults.selectedItems()

        if (QWizard.currentId(self)==1):

            # set message in corresponding label of next page
            self.ui.lblPromptMessageInSearchClassInMM.setText("Select a class from My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + window.getMyModelName() +
                                                              "</span> to import instances:")

            if self.ui.lineEditSearchClassInEMClassName.text() =='':
                # Go to previous wizard page
                QWizard.back(self)

                QtGui.QMessageBox.critical(self, 'Error', "Please add a class name in corresponding field to Search in External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" +
                                           Functions.getCurrentEndpointName() + "</span>.", QtGui.QMessageBox.Close)

            # Display Message Box to inform user if no selection was made
            elif not selected_items:
                # Go to previous wizard page
                QWizard.back(self)

                # Show message box with error
                QtGui.QMessageBox.critical(self, 'Error', "Please select one or more instances from previous results \n" +
                                                   "to display their properties in next step.", QtGui.QMessageBox.Close)

        elif (QWizard.currentId(self)==2):
            # check if any selection was made in wizard page 2
            if self.ui.comboBoxAvailableClassesInMM.currentIndex() == -1: # selection in combobox is empty
                # Go to previous wizard page
                QWizard.back(self)

                # Show message box with error
                QtGui.QMessageBox.critical(self, 'Error', "Please select a class from My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" +
                                           window.getMyModelName() + "</span> that matches to defined class of External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" +
                                           Functions.getCurrentEndpointName() + "</span>", QtGui.QMessageBox.Close)
            else:
                self.loadDataToTableWidgetViewPropertiesOfBothModels()

        elif (QWizard.currentId(self)==3):
            self.loadMatchingPropertiesOverviewToWidgetListUpdateDBAndCreateGraph()

            # Log
            Functions.addEntryToLog("Instances added to class " + self.ui.comboBoxAvailableClassesInMM.currentText() + " with Search by class method")

            # Change changesMadeToModel to use for exit prompt message
            window.setChangesMadeToModel(True)

        # set window title according to wizard page
        self.button_clicked_setWindowTitle(QWizard.currentId(self))

    def backButton_clicked(self):
        # set window title according to wizard page
        self.button_clicked_setWindowTitle(QWizard.currentId(self))

    def button_clicked_setWindowTitle(self, qwizard_pageId):
        if (qwizard_pageId == 0):
            self.setWindowTitle(QtCore.QString("Search by Class - Step 1"))
        elif (qwizard_pageId == 1):
            self.setWindowTitle(QtCore.QString("Search by Class - Step 2"))
        elif (qwizard_pageId == 2):
            self.setWindowTitle(QtCore.QString("Search by Class - Step 3"))
        elif (qwizard_pageId == 3):
            self.setWindowTitle(QtCore.QString("Search by Class - Summary"))

    def loadDataToTableWidgetViewPropertiesOfBothModels(self):

        # Clear table
        self.ui.tableWidgetViewPropertiesOfBothModels.setRowCount(0)

        # Set label above table. Label will be changed accordingly if unique_properties_list is empty
        self.ui.lblShowPropertiesOfBothModels.setText("Match properties of External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" +
                                                      Functions.getCurrentEndpointName() + "</span> to equivalent properties of My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" +
                                                      window.getMyModelName() + "</span>:")

        my_model_properties_list = Functions.getAllDataPropertiesFromGraph(window.getGraph())
        my_model_properties_list.sort()

        # Get selection of User in QTreeWidget
        selected_items = self.ui.treeWidgetSearchClassInEMInstancesResults.selectedItems()

        selected_instances = []
        unique_properties_list = []

        # Keep instances and values in one variable
        all_data = []

        # For every selected item (if parent in QTreeWidget) find its items (children) and get their name (text)
        # This name stands for the property of the selected item
        # Place every retrieved property in a list of unique_properties in order to fill in the Table afterwards

        for item in selected_items:
            #item is an instance, and we get all corresponding properties from current parent in tree
            current_parent = Functions.getPhraseWithURL(item.text(0))
            selected_instances.append(current_parent)

            for i in range(0, item.childCount()):
                #Get text from child
                tmp_text_child = item.child(i).text(0)
                text_child = Functions.getPhraseWithURL(tmp_text_child)
                tmp_value = item.child(i).text(1)

                tmp_instance_data = []
                tmp_instance_data.append(current_parent) # first record: URI instance
                tmp_instance_data.append(text_child) #second record: property_name
                tmp_instance_data.append(tmp_value) # third record: property_value
                # ready to apply to all data
                all_data.append(tmp_instance_data)

                if (text_child not in unique_properties_list) and (text_child != "rdfs:label") and (text_child != "https://www.w3.org/2000/01/rdf-schema#label") and (text_child != "http://www.w3.org/2000/01/rdf-schema#label"):
                    unique_properties_list.append(text_child)

        # Set all data to current selected instances
        self.setSelectedInstancesWithPropertiesAndValues(all_data)
        # Sort list
        unique_properties_list.sort()

        if unique_properties_list == []:
            # Change message to label in wizardPage3
            self.ui.lblShowPropertiesOfBothModels.setText("There are no properties in selected instances of External Model <span style='font-size:9pt; font-weight:550; color:#377a97;'>" +
                                                          Functions.getCurrentEndpointName() + "</span> to match with properties of My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" +
                                                          window.getMyModelName() + "</span>.")

        # Load properties to Table
        for external_property in unique_properties_list:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetViewPropertiesOfBothModels.rowCount()
            self.ui.tableWidgetViewPropertiesOfBothModels.insertRow(rowPosition)

            # Insert the value
            self.ui.tableWidgetViewPropertiesOfBothModels.setItem(rowPosition, 0, QtGui.QTableWidgetItem(Functions.getPhraseWithPrefix(external_property)))

            # Create new combo box to list all properties
            comboBoxMyModelProperties = QtGui.QComboBox()
            comboBoxMyModelProperties.addItem("<empty>")
            for my_model_property in my_model_properties_list:
                comboBoxMyModelProperties.addItem(Functions.getPhraseWithPrefix(my_model_property))

            existing_mapping = Functions.searchForMyPropertyInMappings(window.getMyModelName(), Functions.getEndpointName(), external_property)

            if existing_mapping == False:
                comboBoxMyModelProperties.setCurrentIndex(0)
            else:
                index_of_existing_property_in_combobox = comboBoxMyModelProperties.findText(Functions.getPhraseWithPrefix(existing_mapping))
                if index_of_existing_property_in_combobox != -1: # means that external model is found in combobox
                    comboBoxMyModelProperties.setCurrentIndex(index_of_existing_property_in_combobox)

            self.ui.tableWidgetViewPropertiesOfBothModels.setCellWidget(rowPosition, 1, comboBoxMyModelProperties)

    def loadMatchingPropertiesOverviewToWidgetListUpdateDBAndCreateGraph(self):

        # Clear components
        self.ui.lblPopulatedInstances.clear()
        self.ui.treeWidgetSummary.clear()

        # Initializations of variables for graph
        instances_to_populate = self.getSelectedInstancesToPopulate()
        selected_class_in_MM = Functions.getPhraseWithURL(self.ui.comboBoxAvailableClassesInMM.currentText())

        #Insert instances to graph
        self.insertInstancesFromEMToMM(instances_to_populate, selected_class_in_MM)

        # Display text to Populated instances label
        self.ui.lblPopulatedInstances.setText(self.getTextForlblPopulatedInstances(instances_to_populate))

        # Handle mapping table
        for row in range(self.ui.tableWidgetViewPropertiesOfBothModels.rowCount()):

            # If it is not <empty>
            if self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText() != '<empty>': #meaning my_property !=<empty>

                # Update mapping if it exists with another match of my_property - external_property
                Functions.updateMappingToDB(window.getMyModelName(),
                                            self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText(),
                                            self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(),
                                            Functions.getEndpointName())


                # Insert mapping if it does not exist at all
                Functions.addMappingToDB(window.getMyModelName(),
                                         self.ui.tableWidgetViewPropertiesOfBothModels.cellWidget(row, 1).currentText(),
                                         self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(),
                                         Functions.getEndpointName())


            # If it is <empty> delete if from DB (if it exists)
            else:
                Functions.deleteMappingOfExternalPropertyFromBD(window.getMyModelName(),
                                                                self.ui.tableWidgetViewPropertiesOfBothModels.item(row, 0).text(),
                                                                Functions.getEndpointName())

        # Insert selected data properties to graph
        self.insertDataPropertiesForSelectedInstancesFromEMToMM(instances_to_populate, selected_class_in_MM)

    def insertInstancesFromEMToMM(self, instances_to_populate, selected_class_in_MM):
        # Add new instances to Graph of Main
        window.setGraph(Functions.addNewInstancesToGraph(window.getGraph(), instances_to_populate, selected_class_in_MM, self))

    def insertDataPropertiesForSelectedInstancesFromEMToMM(self, instances_to_populate, selected_class_in_MM):

        # For existing mapping in DB, add corresponding values to matching properties
        # variables needed:
        # my_model, external_model, mappings, instances_to_populate and their corresponding properties/values, selected_class_in_MM

        listMappingsInDB = Functions.getListOfMappingPropertiesFromDB(window.getMyModelName(), Functions.getEndpointName())

        if listMappingsInDB != False:
            # Mappings returned from DB is a 2Dlist with one row for each pair of properties: [my_property, external_property]
            for instance_to_populate in instances_to_populate:

                for instance_row in self.getSelectedInstacesWithPropertiesAndValues():
                    if instance_to_populate == instance_row[0]: # instance_row[0] is instance URI
                        # then we need to get its properties and values
                        current_EM_property = instance_row[1]
                        current_EM_value = instance_row[2]
                        # Look for current_EM_property in mappings
                        for current_mapping_in_DB in listMappingsInDB:

                            if current_mapping_in_DB[1] == current_EM_property:

                                #then get the corresponding property in my_model
                                current_MM_property = current_mapping_in_DB[0]
                                # Create triple of data property in graph
                                window.setGraph(
                                    Functions.addNewDataPropertyWithValueToGraph(
                                        window.getGraph(), str(selected_class_in_MM), instance_to_populate, current_MM_property, current_EM_value, self
                                    )
                                )

                                #check if owl:equivalentProperty is enabled
                                if Functions.getSettingFromDB('equivalent_property_option') == 1:
                                    window.setGraph(
                                        Functions.addEquivalentPropertyMatchingToGraph(
                                            window.getGraph(), current_MM_property, current_EM_property
                                        )
                                    )

        # sort, expand and resize tree widget item
        self.ui.treeWidgetSummary.sortItems(0,0)
        self.ui.treeWidgetSummary.expandAll()
        self.ui.treeWidgetSummary.resizeColumnToContents(0)

    def getTextForlblPopulatedInstances(self, instances_to_populate):
         # Instances label
        if instances_to_populate !=[]:
            return "The following instances and values were successfully populated in My Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + window.getMyModelName() + "</span>."
        else:
            return "No instances were populated in the current process."

    def allButtonClicked(self):
        self.ui.treeWidgetSearchClassInEMInstancesResults.selectAll()
        self.ui.treeWidgetSearchClassInEMInstancesResults.setFocus()


class UpdateDownloader(QtGui.QDialog):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_UpdatesDownloader()
        self.ui.setupUi(self)

        self.downloadCancelled = False
        self.downloadSucceeded = False

        # MAKE CONNECTIONS
        self.ui.btnCancel.clicked.connect(self.btnCancel_clicked)

        # CONSTRUCT UI ELEMENTS
        self.ui.progressBarUpdate.setValue(0)
        self.ui.lblCurrentJob.setText("Connecting to server...")

    def btnCancel_clicked(self):
        self.downloadCancelled = True

        # Delete downloaded files
        Functions.deleteUpdateFolder()

        self.close()

    def downloadFilesToUpdate(self):
        # Get list of files that need to be downloaded and placed in the PROPheT folder
        self.ui.lblCurrentJob.setText("Getting list of files...")
        files_to_update = Functions.getListOfFilesToUpdate()

        print "Files to update", files_to_update

        self.ui.progressBarUpdate.setValue(3)

        # If no file needs to be downloaded
        if files_to_update == []:
            print "No files to update"
            self.ui.progressBarUpdate.setValue(100)
            return

        # Calculate progressBar increment
        step = ((100 - self.ui.progressBarUpdate.value())/len(files_to_update))

        # For each file in the list
        for filename in files_to_update:
            # If user cancelled download
            if self.downloadCancelled == True:
                return

            self.ui.lblCurrentJob.setText("Downloading file " + filename + "...")
            self.ui.progressBarUpdate.setValue(self.ui.progressBarUpdate.value() + step)

            # Download file inside folder updates
            # If it fails to download some file show message and delete all files downloaded
            if Functions.downloadFileFromLatestVersionFolder(filename) == False:
                # Show error message
                QtGui.QMessageBox.critical(self, 'Error', "File " + filename +
                                           " could not be downloaded.\nInstallation failed.", QtGui.QMessageBox.Close)

                self.close()
                return

            # Process events in case Cancel has been pressed and waits for GIL
            QApplication.processEvents()

        # Fill progressBar and change message
        self.ui.lblCurrentJob.setText("Preparing for installation...")
        self.ui.progressBarUpdate.setValue(100)

        self.downloadSucceeded = True
        self.close()

## SPLASH SCREEN START
class MovieSplashScreen(QSplashScreen):
    def __init__(self, movie, parent = None):
        movie.jumpToFrame(0)
        pixmap = QPixmap(movie.frameRect().size())

        QSplashScreen.__init__(self, pixmap)
        self.movie = movie
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):
        self.movie.start()

    def hideEvent(self, event):
        self.movie.stop()

    def paintEvent(self, event):

        painter = QPainter(self)
        pixmap = self.movie.currentPixmap()
        self.setMask(pixmap.mask())
        painter.drawPixmap(0, 0, pixmap)

    def sizeHint(self):
        return self.movie.scaledSize()
## END

## CHECK FOR UPDATES THREAD
class CheckForUpdates(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        if Functions.checkIfInternetConnectionIsOn():

            # If there is an available update
            if Functions.checkForUpdatedProphetVersion():

                # Signal main window that an update was found
                self.emit(QtCore.SIGNAL("updateFound"))
## END


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    ## Animated splash screen code
    movie = QMovie("images/Logo_Animation.gif")
    splash = MovieSplashScreen(movie)
    splash.show()

    start = time.time()

    while movie.state() == QMovie.Running and time.time() < start + 5:
        app.processEvents()

    window = Main()
    window.show()

    splash.finish(window)

    sys.exit(app.exec_())
