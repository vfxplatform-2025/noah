# -*- coding:utf-8 -*-
'''
Created on Mar 31, 2015

@author: m83
'''

import os, sys, glob, re
import json
from subprocess import *
import shutil
import imp
sys.path.append("/core/TD/pipeline/usd_script")
from cacheExport_module.pyside2_moduleImport import *
from cacheExport_module.assetsExport_moduleImport import *
from cacheExport_module.cacheExport_moduleImport import ABCIMPORTOPT
import os
APPNAME = os.getenv('APPNAME')

# Maya only - reload modules
#imp.reload(uview)
imp.reload(itemScript)
imp.reload(utilScript)
imp.reload(cameraExportScript)
imp.reload(atomScript)
imp.reload(geoCacheScript)
imp.reload(alembicScript)
imp.reload(cameraScript)
imp.reload(dummyScript)
imp.reload(rigScript)
imp.reload(modelScript)
imp.reload(frameRangeScript)
imp.reload(resolutionScript)
imp.reload(lookdevScript)
imp.reload(lightRigScript)
imp.reload(alembicScript_asset)
imp.reload(takeScript)
imp.reload(commentWindow)
imp.reload(instanceScript)

import ucat
#import uview
# from QtTopUiLoader import *
import QtTopUiLoader

class DataStruct(object):
    def __init__(self):

        self.itemClass = {}
        self.itemClass["treeItem"] = {}
        self.itemClass["checkBox"] = {}
        self.itemClass["comboBox1"] = {}
        self.itemClass["comboBox2"] = {}
        self.itemClass["allCheckBoxItemList"] = {}
        self.itemClass["allTreeWidgetItemList"] = {}

        self.itemClass["partTypeCheckBox"] = {}
        self.itemClass["allItemClass"] = {}
        self.itemClass["rootClass"] = {}
        self.itemClass["subClass"] = {}
        self.itemClass["itemClass"] = {}

    def setList(self, itemList):
        for i in itemList:
            if isinstance(i, QtWidgets.QCheckBox):
                self.itemClass["allCheckBoxItemList"].update(itemList)

                if self.itemClass["partTypeCheckBox"].get(itemList[i][0]) == None:
                    self.itemClass["partTypeCheckBox"][itemList[i][0]] = []
                self.itemClass["partTypeCheckBox"][itemList[i][0]].append(i)

            else:
                self.itemClass["allTreeWidgetItemList"].update(itemList)

    def setWidget(self, rootType, itemList):
        if rootType in self.itemClass["allItemClass"]:
            self.itemClass["allItemClass"][rootType].update(itemList)
        else:
            self.itemClass["allItemClass"].update({rootType: None})
            self.itemClass["allItemClass"][rootType] = itemList

    def set(self, itemList, rootType=None):
        for item in itemList:
            font = QtGui.QFont()
            font.setPointSize(9)

            if isinstance(item, QtWidgets.QTreeWidgetItem):
                classType = 'treeItem'
            elif isinstance(item, QtWidgets.QCheckBox):
                classType = 'checkBox'
            elif isinstance(item, QtWidgets.QComboBox):
                classType = 'comboBox'

            #rig", "modelEnv","model", "camera", "frameRange","resolutionSet", "dummy"
            if classType == "comboBox":
                if item.objectName() == "opt1":
                    classType = "comboBox1"
                    if item.count() == 0:
                        if rootType in ["rig", "model", "alembicRig", "alembicModel"]:
                            item.addItems(["None", "PROXY", "LOW", "MID", "HI", "XLOW", "XHi", "MOCAP", "miarmy"])
                        else:
                            item.addItems(["None", "model", "rig"])
                        item.setFont(font)

                else:
                    classType = "comboBox2"
                    if item.count() == 0:
                        if rootType in [ "camera", "frameRange", "resolutionSet", "dummy", "mmDummy","modelDummy" ]:
                            item.addItems([ "import"])
                            item.setFont(font)
                        elif rootType in [ "rig" , "model", "modelLow","modelMid","modelHi","modelXLow","modelXHi", "rigLow","rigMid","rigHi","mocapRig"]:
                            item.addItems([ "reference", "import"])
                            item.setFont(font)

                        elif rootType in ["modelEnv", "rigEnv", "lookdev", "litRig", "digienv"]:
                            item.addItems(["reference"])
                            item.setFont(font)
                        else:
                            item.addItems(["None", "reference", "import"])
                            item.setFont(font)

#             # set Item
            if item not in set(self.itemClass[classType]):
                self.itemClass[classType][item] = []
                 
            if item in set(self.itemClass[classType]):
                # current item
                if itemList[item] not in set(self.itemClass[classType][item]) and itemList[item] is not None:
                    self.itemClass[classType][item].append(itemList[item])

            # if itemList[item] != None:
            if itemList[item] is not None:
                for selRootItem in set(self.itemClass[classType]):
                    if item in set(self.itemClass[classType][selRootItem]):  # allitem
                        if itemList[item] not in set(self.itemClass[classType][selRootItem]):
                            self.itemClass[classType][selRootItem].append(itemList[item])


class updateWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, text=None):
        super(updateWindow, self).__init__(parent)
        self.setStyleSheet("border: None;  font: 15px; color : yellow ; background-color : rgb(57,61,72) ; ")

        self.parent = parent
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.label = QtWidgets.QLabel()
        #### update file name
        self.label.setText("%s" % text)

        self.layout().addWidget(self.label)

        self.moveWindow()

    def moveWindow(self):
        point = self.parent.rect().center()
        globalPoint = self.parent.mapToGlobal(point)

        self.move(globalPoint)


class textpubWindow(QtWidgets.QDialog):
    textpup = QtCore.Signal()

    def __init__(self, parent=None):
        super(textpubWindow, self).__init__(parent)

        self.fileName = ""
        self.dataInfo = {"itemType": None, "itemName": None, "takeDir": None}
        self.setWindowTitle("Comment Window")
        self.resize(300, 200)
        self.setLayout(QtWidgets.QVBoxLayout())

        font = QtGui.QFont()
        font.setPointSize(10)
        fontBold = QtGui.QFont()
        fontBold.setPointSize(10)
        fontBold.setBold(1)

        self.textEdit = QtWidgets.QTextEdit()

        self.commentLabel = QtWidgets.QLabel("Comment")

        cancelButton = QtWidgets.QPushButton("Cancel")
        cancelButton.setFixedSize(80, 28)
        pupButton = QtWidgets.QPushButton("Save")
        pupButton.setFixedSize(80, 28)
        pupButton.setFont(fontBold)

        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(pupButton)
        buttonLayout.setAlignment(QtCore.Qt.AlignRight)
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        buttonLayout.setSpacing(0)

        self.layout().addWidget(self.commentLabel)
        self.layout().addWidget(self.textEdit)
        self.layout().addLayout(buttonLayout)

        self.commentLabel.setFont(fontBold)

        self.textEdit.setFont(font)
        self.textEdit.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

        cancelButton.clicked.connect(self.closeWindow)
        pupButton.clicked.connect(self.textpup2)

        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def textpup2(self):
        """emit"""
        self.textpup.emit()

    def closeWindow(self):
        self.close()


class publishWindow(QtWidgets.QDialog):
    Pub = QtCore.Signal()

    def __init__(self, parent=None):
        super(publishWindow, self).__init__(parent)

        self.fileName = ""
        self.setWindowTitle("publish Window")
        self.resize(300, 200)
        self.setLayout(QtWidgets.QVBoxLayout())

        font = QtGui.QFont()
        font.setPointSize(10)
        fontBold = QtGui.QFont()
        fontBold.setPointSize(10)
        fontBold.setBold(1)

        self.titleLineEdit = QtWidgets.QLineEdit()
        self.textEdit = QtWidgets.QTextEdit()
        pubLabel = QtWidgets.QLabel("Pub File Name")
        commentLabel = QtWidgets.QLabel("Comment")

        # Adding the Check Box
        self.jiho_mmobj_checkBox = QtWidgets.QCheckBox("Export Obj for Matchmove")

        ui_mb_path = cmds.file(sn=1, q=1)
        try:
            path_parts = ui_mb_path.split('/')
            if len(path_parts) > 4:
                check_envsurvey = path_parts[4]
            else:
                check_envsurvey = ''
        except (IndexError, AttributeError):
            check_envsurvey = ''

        if str(check_envsurvey)=='env' or str(check_envsurvey)=='survey':
            self.jiho_mmobj_checkBox.setChecked(True)
        else:
            self.jiho_mmobj_checkBox.setChecked(False)

        cancelButton = QtWidgets.QPushButton("Cancel")
        cancelButton.setFixedSize(80, 28)
        pupButton = QtWidgets.QPushButton("Puplish")
        pupButton.setFixedSize(80, 28)
        pupButton.setFont(fontBold)

        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(pupButton)
        buttonLayout.setAlignment(QtCore.Qt.AlignRight)
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        buttonLayout.setSpacing(0)

        self.layout().addWidget(pubLabel)
        self.layout().addWidget(self.titleLineEdit)
        self.layout().addWidget(commentLabel)
        self.layout().addWidget(self.textEdit)

        # Adding the Check Box to the layout
        self.layout().addWidget(self.jiho_mmobj_checkBox)

        self.layout().addLayout(buttonLayout)

        self.titleLineEdit.setFont(font)
        pubLabel.setFont(fontBold)
        commentLabel.setFont(fontBold)

        self.textEdit.setFont(font)
        self.textEdit.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

        cancelButton.clicked.connect(self.closeWindow)
        pupButton.clicked.connect(self.pup)

        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


    def pup(self):
        """emit"""
        self.Pub.emit()

    def setFileName(self, fileName, subname=""):
        fileName = str(fileName)
        if subname:  # and subname in fileName:
            reEx = re.search(".+(?=_w[0-9]{2}\_?)", fileName)
            if reEx:
                fileName = reEx.group() + "%s" % subname
            else:
                fileName = fileName + subname
            self.titleLineEdit.setText("%s" % fileName)
            return fileName

        # elif subname and subname not in fileName:
        #     fileName =  fileName + subname
        #     self.titleLineEdit.setText("%s" % fileName)
        #     return fileName

        reEx = re.search(".+(?=_w[0-9]{2}$)", fileName)
        if reEx:
            fileName = reEx.group()
        self.titleLineEdit.setText("%s" % fileName)

        return fileName

    def closeWindow(self):
        self.close()


class assetsView(QtWidgets.QWidget):
    refreshed = QtCore.Signal()

    def __init__(self, parent=None):
        super(assetsView, self).__init__(parent)

        self.filepath = os.path.abspath(__file__ + "/../")
        QtTopUiLoader.UiLoader().loadUi(self.filepath + "/cacheExportAsset.ui", self)
        self.setStyleSheet("#topFrame, #optStackedWidget, #optStackedWidget_2 {border: 1px solid rgb(35, 35, 35)}")

        self.parent = parent

        self.setObjectName("assetsView")
        self.resize(1250, 1100)
        
        self.pubWindow = publishWindow()
        self.textpubWindow = textpubWindow()
        
        self.propList = {}
        self.chaList  = {}
        self.envList  = {}
        self.crowdList= {}
        self.litRigList = {}
        self.etcList  = {}
        self.aircraftList = {}
        self.plantList = {}
        self.rockList = {}
        self.setList={}
        self.shipList={}
        self.structureList={}
        self.vehicleList={}
        self.weaponList={}
        self.surveyList = {}
        self.landscapeList = {}

        self.propItem ={}
        self.chaItem ={}
        self.envItem ={}
        self.crowdItem= {}
        self.litRigItem = {}
        self.etcItem ={}
        self.aircraftItem = {}
        self.plantItem = {}
        self.rockItem = {}
        self.setItem = {}
        self.shipItem = {}
        self.structureItem = {}
        self.vehicleItem = {}
        self.weaponItem = {}
        self.surveyItem = {}
        self.landscapeItem = {}

        self.modelLodComboBox.hide()
        self.rigLodComboBox.hide()

        # emit
        self.pubWindow.Pub.connect(self.pupFile)
        # self.connect(self.pubWindow,                     QtCore.SIGNAL("Pub"),                      self.pupFile)
        # self.connect(self.textpubWindow,                 QtCore.SIGNAL("textpup"),                  self.textpup)
        self.textpubWindow.textpup.connect(self.textpup)

        self.checkPushButton.clicked.connect(self.checkSet)
        self.autoSetPushButton.clicked.connect(self.autoSet)
        self.deleteItemPushButton.clicked.connect(self.deleteItem)
        self.typeCheckPushButton.clicked.connect(self.typeCheck)
        self.refreshPushButton.clicked.connect(self.refresh)
        self.refreshPushButton.setIcon(QtGui.QIcon("{}/icon/refresh.png".format(self.filepath)))
        self.usdView_pushButton.clicked.connect(self.usdView)

        self.propTreeWidget.itemSelectionChanged.connect(lambda name=self.propTreeWidget: self.propSelectItems(name))
        self.chaTreeWidget.itemSelectionChanged.connect(lambda name=self.chaTreeWidget: self.chaSelectItems(name))
        self.envTreeWidget.itemSelectionChanged.connect(lambda name=self.envTreeWidget: self.envSelectItems(name))
        self.crowdTreeWidget.itemSelectionChanged.connect(lambda name=self.crowdTreeWidget: self.crowdSelectItems(name))
        self.litRigTreeWidget.itemSelectionChanged.connect(
            lambda name=self.litRigTreeWidget: self.litRigSelectItems(name))
        self.etcTreeWidget.itemSelectionChanged.connect(lambda name=self.etcTreeWidget: self.etcSelectItems(name))
        self.aircraftTreeWidget.itemSelectionChanged.connect(lambda name=self.aircraftTreeWidget: self.aircraftSelectItems(name))
        self.plantTreeWidget.itemSelectionChanged.connect(lambda name=self.plantTreeWidget: self.plantSelectItems(name))
        self.rockTreeWidget.itemSelectionChanged.connect(lambda name=self.rockTreeWidget: self.rockSelectItems(name))
        self.setTreeWidget.itemSelectionChanged.connect(lambda name=self.setTreeWidget: self.setSelectItems(name))
        self.shipTreeWidget.itemSelectionChanged.connect(lambda name=self.shipTreeWidget: self.shipSelectItems(name))
        self.structureTreeWidget.itemSelectionChanged.connect(lambda name=self.structureTreeWidget: self.structureSelectItems(name))
        self.vehicleTreeWidget.itemSelectionChanged.connect(lambda name=self.vehicleTreeWidget: self.vehicleSelectItems(name))
        self.weaponTreeWidget.itemSelectionChanged.connect(lambda name=self.weaponTreeWidget: self.weaponSelectItems(name))
        self.surveyTreeWidget.itemSelectionChanged.connect(lambda name=self.surveyTreeWidget: self.surveySelectItems(name))
        self.landscapeTreeWidget.itemSelectionChanged.connect(lambda name=self.landscapeTreeWidget: self.landscapeSelectItems(name))

        self.propTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.propFc: self.propFc(name, self.propItem[name]))
        self.chaTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.chaFc: self.chaFc(name, self.chaItem[name]))
        self.envTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.envFc: self.envFc(name, self.envItem[name]))
        self.crowdTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.crowdFc: self.crowdFc(name, self.crowdItem[name]))
        self.litRigTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.litRigFc: self.litRigFc(name, self.litRigItem[name]))
        self.etcTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.etcFc: self.etcFc(name, self.etcItem[name]))
        self.aircraftTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.aircraftFc: self.aircraftFc(name, self.aircraftItem[name]))
        self.plantTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.plantFc: self.plantFc(name, self.plantItem[name]))
        self.rockTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.rockFc: self.rockFc(name, self.rockItem[name]))
        self.setTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.setFc: self.setFc(name, self.setItem[name]))
        self.shipTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.shipFc: self.shipFc(name, self.shipItem[name]))
        self.structureTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.structureFc: self.structureFc(name, self.structureItem[name]))
        self.vehicleTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.vehicleFc: self.vehicleFc(name, self.vehicleItem[name]))
        self.weaponTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.weaponFc: self.weaponFc(name, self.weaponItem[name]))
        self.surveyTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.surveyFc: self.surveyFc(name, self.surveyItem[name]))
        self.landscapeTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(
            lambda name=self.landscapeFc: self.landscapeFc(name, self.landscapeItem[name]))

        self.matchmoveCheckBox.stateChanged[int].connect(self.matchmoveCheck)
        self.layoutCheckBox.stateChanged[int].connect(self.layoutCheck)
        self.modelCheckBox.stateChanged[int].connect(self.modelCheck)
        self.rigCheckBox.stateChanged[int].connect(self.rigCheck)
        self.lookdevCheckBox.stateChanged[int].connect(self.lookdevCheck)
        self.litRigSetCheckBox.stateChanged[int].connect(self.litRigSetCheck)

        self.title1CheckBox.stateChanged[int].connect(lambda num, name=self.title1CheckBox: self.titleCheck(num, name))
        self.title2CheckBox.stateChanged[int].connect(lambda num, name=self.title2CheckBox: self.titleCheck(num, name))
        self.title3CheckBox.stateChanged[int].connect(lambda num, name=self.title3CheckBox: self.titleCheck(num, name))

        self.propCheckBox.stateChanged[int].connect(
            lambda num, name=self.propTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.chaCheckBox.stateChanged[int].connect(
            lambda num, name=self.chaTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.envCheckBox.stateChanged[int].connect(
            lambda num, name=self.envTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.crowdCheckBox.stateChanged[int].connect(
            lambda num, name=self.crowdTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.litRigCheckBox.stateChanged[int].connect(
            lambda num, name=self.litRigTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.etcCheckBox.stateChanged[int].connect(
            lambda num, name=self.etcTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.aircraftCheckBox.stateChanged[int].connect(
            lambda num, name=self.aircraftTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.plantCheckBox.stateChanged[int].connect(
            lambda num, name=self.plantTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.rockCheckBox.stateChanged[int].connect(
            lambda num, name=self.rockTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.setCheckBox.stateChanged[int].connect(
            lambda num, name=self.setTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.shipCheckBox.stateChanged[int].connect(
            lambda num, name=self.shipTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.structureCheckBox.stateChanged[int].connect(
            lambda num, name=self.structureTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.vehicleCheckBox.stateChanged[int].connect(
            lambda num, name=self.vehicleTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.weaponCheckBox.stateChanged[int].connect(
            lambda num, name=self.weaponTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.surveyCheckBox.stateChanged[int].connect(
            lambda num, name=self.surveyTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.landscapeCheckBox.stateChanged[int].connect(
            lambda num, name=self.landscapeTreeWidget: name.setHidden(not (num)))  # self.assetWidgetCheck (num, name ))
        self.importItemPushButton.clicked.connect(self.importItem)

        self.etcTreeWidget.hide()
        self.crowdTreeWidget.hide()
        self.aircraftTreeWidget.hide()
        self.plantTreeWidget.hide()
        self.rockTreeWidget.hide()
        self.setTreeWidget.hide()
        self.shipTreeWidget.hide()
        self.structureTreeWidget.hide()
        self.vehicleTreeWidget.hide()
        self.weaponTreeWidget.hide()
        self.surveyTreeWidget.hide()
        self.landscapeTreeWidget.hide()

        # self.connect(self.stretchPushButton,             QtCore.SIGNAL("clicked()"),                 self.setStretch)
        self.stretchPushButton.clicked.connect(self.setStretch)

        self.dataStruct = DataStruct()
        self.dataItemStruct = self.dataStruct.itemClass

        font = QtGui.QFont()
        font.setPointSize(10)
        self.stretchPushButton.setFont(font)

        self.pubModelPushButton.clicked.connect(self.publishFile)
        self.pubRigPushButton.clicked.connect(self.publishFile)

        self.pubLowModelPushButton.clicked.connect(lambda: self.publishFile("_LOW"))
        self.pubLowRigPushButton.clicked.connect(lambda: self.publishFile("_LOW"))
        self.pubLookdevProxyPushButton.clicked.connect(lambda: self.publishFile("_PROXY"))
        self.pubLookdevPushButton.clicked.connect(self.publishFile)
        self.pubDigienvPushButton.clicked.connect(self.publishFile)

        self.clarissePubLookdev_pushButton.clicked.connect(lambda: self.noahExport("clarisse"))
        self.clarissePubDigienv_pushButton.clicked.connect(lambda: self.noahExport("clarisse"))

        self.pubLitRigPushButton.clicked.connect(self.publishFile)

        self.typeCheckBoxFrame.layout().setAlignment(QtCore.Qt.AlignLeft| QtCore.Qt.AlignTop)
        self.stackedPage1.layout().setAlignment(QtCore.Qt.AlignTop)
        self.stackedPage2.layout().setAlignment(QtCore.Qt.AlignTop)
        self.stackedPage3.layout().setAlignment(QtCore.Qt.AlignTop)
        self.stackedPage4.layout().setAlignment(QtCore.Qt.AlignTop)
                
        self.take_ComboBox.setStyleSheet("QComboBox#%s {color: yellow;background-color:transparent;} #%s:hover {background-color: rgb(44,45,51);}" %(self.take_ComboBox.objectName(), self.take_ComboBox.objectName() ))
        self.importItemPushButton.setStyleSheet("QPushButton#importItemPushButton {background-color: rgb(30,100,30);}" )
        self.stretchPushButton.setStyleSheet("#stretchPushButton {background-color: rgba(0,0,0,0%); border-radius:0px;} #stretchPushButton:hover {background-color: rgb(105,114,123);}")
        
        self.treeWidgetType = {"prop":self.propTreeWidget, "cha": self.chaTreeWidget, "env": self.envTreeWidget,"crowd": self.crowdTreeWidget, "litRig": self.litRigTreeWidget, "etc": self.etcTreeWidget,
                               "aircraft": self.aircraftTreeWidget, "plant":self.plantTreeWidget, "rock":self.rockTreeWidget, "set":self.setTreeWidget, "ship":self.shipTreeWidget,
                               "structure": self.structureTreeWidget, "vehicle":self.vehicleTreeWidget, "weapon":self.weaponTreeWidget, "survey":self.surveyTreeWidget, "landscape":self.landscapeTreeWidget,}
        self.take_ComboBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.take_ComboBox.activated[int].connect(self.takeChange)

        self.initUI()
        self.selectItems={"prop": [], "cha": [], "env": [],"crowd": [],"litRig": [], "etc": [],
                          "aircraft": [],"plant": [],"rock": [],"set": [],"ship": [],"structure": [],"vehicle": [],"weapon": [], "survey": [], "landscape": []}
        self.currentSelectItem = {"currentType":None, "name" : None, "class": None, "dir" : None}

        self.matchmoveCheckNum = 2
        self.layoutCheckNum = 2
        self.modelCheckNum = 2
        self.rigCheckNum   = 2
        self.lookdevCheckNum=2
        self.litRigSetCheckNum = 2


    def initUI(self):
        
        font = QtGui.QFont()
        font.setPointSize(10)

        self.title1CheckNum = 2
        self.title2CheckNum = 2
        self.title3CheckNum = 0


    def setPrjName(self, name=None):
        self.proj = name #self.prj_ComboBox.currentText()

        self.init()
        
    def setSeqcName(self, name=None):
        self.seqc=name
        
    def setShotName(self, name=None):
        self.shots = name
        # self.projDir = "/show/%s/seq/%s/%s" %(self.proj, self.seqc, self.shots)

    def setTypeName(self, name=None):
        name = str(name)  #self.type_ComboBox.currentText()
        self.currentPartType = name

        # set QStackedWidget
        type={"model" : 0, "rig": 1, "lookdev":2, "litRig":3, "digienv":4, "dyn": 1,"cloth": 1,"fur": 1, "hair": 1, "clothSim": 1}
        if "%s" %name in type:
            self.optStackedWidget.setCurrentIndex(type[name])
        else:
            self.optStackedWidget.setCurrentIndex(0)

    def init(self):
        # self.rootItemTypes = ["model", "rig", "modelLow","modelMid","modelHi","modelXLow","modelXHi", "rigLow","rigMid","rigHi","rigXLow","rigXHi","mocapRig", "lookdev", "litRig", "alembicRig"

        self.rootItemTypes = ["atom","mmAtom","modelAtom","atomRender","geoCache","dummy","mmDummy","modelDummy","simulGeoCache","furGeoCache" ,
        "clothGeoCache","mmGeoCache" ,"modelGeoCache","geoCacheRender","almelbicAni" ,"alembicModel","alembicRender","alembicFur" ,
        "alembicCloth" ,"alembicSimul" ,"alembicMm", "alembicFx","alembicRig","rig","rigLow" ,"rigMid","rigHi", "rigXLow","rigXHi",
        "mocapRig","camera", "model","modelLow","modelMid","modelHi","modelXLow", "modelXHi","frameRange", "resolutionSet",
        "rigEnv","litRig","modelEnv","lookdev", "digienv"]

        self.propTreeWidget.clear()
        self.chaTreeWidget.clear()
        self.envTreeWidget.clear()
        self.crowdTreeWidget.clear()
        self.litRigTreeWidget.clear()
        self.etcTreeWidget.clear()
        self.aircraftTreeWidget.clear()
        self.plantTreeWidget.clear()
        self.rockTreeWidget.clear()
        self.setTreeWidget.clear()
        self.shipTreeWidget.clear()
        self.structureTreeWidget.clear()
        self.vehicleTreeWidget.clear()
        self.weaponTreeWidget.clear()
        self.surveyTreeWidget.clear()
        self.landscapeTreeWidget.clear()

        self.propDirs =  glob.glob("/show/%s/assets/prop/*/" %self.proj)
        self.chaDirs  =  glob.glob("/show/%s/assets/cha/*/"  %self.proj)
        self.envDirs  =  glob.glob("/show/%s/assets/env/*/"  %self.proj)
        self.crowdDirs=  glob.glob("/show/%s/assets/crowd/*/"%self.proj)
        self.litRigDirs = glob.glob("/show/%s/assets/litRig/*/" % self.proj)
        self.etcDirs  =  glob.glob("/show/%s/assets/ETC/*/"  %self.proj)
        self.aircraftDirs = glob.glob("/show/%s/assets/aircraft/*/" % self.proj)
        self.plantDirs = glob.glob("/show/%s/assets/plant/*/" % self.proj)
        self.rockDirs = glob.glob("/show/%s/assets/rock/*/" % self.proj)
        self.setDirs = glob.glob("/show/%s/assets/set/*/" % self.proj)
        self.shipDirs = glob.glob("/show/%s/assets/ship/*/" % self.proj)
        self.structureDirs = glob.glob("/show/%s/assets/structure/*/" % self.proj)
        self.vehicleDirs = glob.glob("/show/%s/assets/vehicle/*/" % self.proj)
        self.weaponDirs = glob.glob("/show/%s/assets/weapon/*/" % self.proj)
        self.surveyDirs = glob.glob("/show/%s/assets/survey/*/" % self.proj)
        self.landscapeDirs = glob.glob("/show/%s/assets/landscape/*/" % self.proj)

        self.propList = {}
        self.chaList  = {}
        self.envList  = {}
        self.crowdList  = {}
        self.litRigList = {}
        self.etcList  = {}
        self.aircraftList = {}
        self.plantList = {}
        self.rockList = {}
        self.setList = {}
        self.shipList = {}
        self.structureList = {}
        self.vehicleList = {}
        self.weaponList = {}
        self.surveyList = {}
        self.landscapeList = {}

        self.allAssetList = {}
        self.allAssetItems={}

        list(map(lambda x :self.propList.update( {x.split("/")[-2] : x } ) ,  self.propDirs))
        list(map(lambda x :self.chaList.update ( {x.split("/")[-2] : x } ) ,  self.chaDirs))
        list(map(lambda x :self.envList.update ( {x.split("/")[-2] : x } ) ,  self.envDirs))
        list(map(lambda x :self.crowdList.update({x.split("/")[-2] : x } ) ,  self.crowdDirs))
        list(map(lambda x: self.litRigList.update({x.split("/")[-2]:  x})   ,  self.litRigDirs))
        list(map(lambda x :self.etcList.update ( {x.split("/")[-2] : x } ) ,  self.etcDirs))
        list(map(lambda x: self.aircraftList.update({x.split("/")[-2]: x}), self.aircraftDirs))
        list(map(lambda x: self.plantList.update({x.split("/")[-2]: x}), self.plantDirs))
        list(map(lambda x: self.rockList.update({x.split("/")[-2]: x}), self.rockDirs))
        list(map(lambda x: self.setList.update({x.split("/")[-2]: x}), self.setDirs))
        list(map(lambda x: self.shipList.update({x.split("/")[-2]: x}), self.shipDirs))
        list(map(lambda x: self.structureList.update({x.split("/")[-2]: x}), self.structureDirs))
        list(map(lambda x: self.vehicleList.update({x.split("/")[-2]: x}), self.vehicleDirs))
        list(map(lambda x: self.weaponList.update({x.split("/")[-2]: x}), self.weaponDirs))
        list(map(lambda x: self.surveyList.update({x.split("/")[-2]: x}), self.surveyDirs))
        list(map(lambda x: self.landscapeList.update({x.split("/")[-2]: x}), self.landscapeDirs))

        self.allAssetItems.update(self.propList)
        self.allAssetItems.update(self.chaList)
        self.allAssetItems.update(self.envList)
        self.allAssetItems.update(self.crowdList)
        self.allAssetItems.update(self.litRigList)
        self.allAssetItems.update(self.etcList)
        self.allAssetItems.update(self.aircraftList)
        self.allAssetItems.update(self.plantList)
        self.allAssetItems.update(self.rockList)
        self.allAssetItems.update(self.setList)
        self.allAssetItems.update(self.shipList)
        self.allAssetItems.update(self.structureList)
        self.allAssetItems.update(self.vehicleList)
        self.allAssetItems.update(self.weaponList)
        self.allAssetItems.update(self.surveyList)
        self.allAssetItems.update(self.landscapeList)

        self.propItem = {}
        for prop in self.propList:
            propItem = QtWidgets.QTreeWidgetItem(self.propTreeWidget, [prop])
            self.propItem[propItem] = prop
            self.allAssetList.update(self.propItem) 
            
        self.chaItem = {}
        for cha in self.chaList:
            chaItem = QtWidgets.QTreeWidgetItem(self.chaTreeWidget, [cha])
            self.chaItem[chaItem] = cha
            self.allAssetList.update( self.chaItem )
            
        self.envItem = {}
        for env in self.envList:
            envItem = QtWidgets.QTreeWidgetItem(self.envTreeWidget, [env])
            self.envItem[envItem] = env
            self.allAssetList.update( self.envItem )

        self.crowdItem = {}
        for crowd in self.crowdList:
            crowdItem = QtWidgets.QTreeWidgetItem(self.crowdTreeWidget, [crowd])
            self.crowdItem[crowdItem] = crowd
            self.allAssetList.update( self.crowdItem )

        self.litRigItem = {}
        for litRig in self.litRigList:
            litRigItem = QtWidgets.QTreeWidgetItem(self.litRigTreeWidget, [litRig])
            self.litRigItem[litRigItem] = litRig
            self.allAssetList.update( self.litRigItem )

        self.etcItem = {}
        for etc in self.etcList:
            etcItem = QtWidgets.QTreeWidgetItem(self.etcTreeWidget, [etc])
            self.etcItem[etcItem] = etc
            self.allAssetList.update( self.etcItem )

        self.aircraftItem = {}
        for aircraft in self.aircraftList:
            aircraftItem = QtWidgets.QTreeWidgetItem(self.aircraftTreeWidget, [aircraft])
            self.aircraftItem[aircraftItem] = aircraft
            self.allAssetList.update(self.aircraftItem)

        self.plantItem = {}
        for plant in self.plantList:
            plantItem = QtWidgets.QTreeWidgetItem(self.plantTreeWidget, [plant])
            self.plantItem[plantItem] = plant
            self.allAssetList.update(self.plantItem)

        self.rockItem = {}
        for rock in self.rockList:
            rockItem = QtWidgets.QTreeWidgetItem(self.rockTreeWidget, [rock])
            self.rockItem[rockItem] = rock
            self.allAssetList.update(self.rockItem)

        self.setItem = {}
        for set in self.setList:
            setItem = QtWidgets.QTreeWidgetItem(self.setTreeWidget, [set])
            self.setItem[setItem] = set
            self.allAssetList.update(self.setItem)

        self.shipItem = {}
        for ship in self.shipList:
            shipItem = QtWidgets.QTreeWidgetItem(self.shipTreeWidget, [ship])
            self.shipItem[shipItem] = ship
            self.allAssetList.update(self.shipItem)

        self.structureItem = {}
        for structure in self.structureList:
            structureItem = QtWidgets.QTreeWidgetItem(self.structureTreeWidget, [structure])
            self.structureItem[structureItem] = structure
            self.allAssetList.update(self.structureItem)

        self.vehicleItem = {}
        for vehicle in self.vehicleList:
            vehicleItem = QtWidgets.QTreeWidgetItem(self.vehicleTreeWidget, [vehicle])
            self.vehicleItem[vehicleItem] = vehicle
            self.allAssetList.update(self.vehicleItem)

        self.weaponItem = {}
        for weapon in self.weaponList:
            weaponItem = QtWidgets.QTreeWidgetItem(self.weaponTreeWidget, [weapon])
            self.weaponItem[weaponItem] = weapon
            self.allAssetList.update(self.weaponItem)

        self.surveyItem = {}
        for survey in self.surveyList:
            surveyItem = QtWidgets.QTreeWidgetItem(self.surveyTreeWidget, [survey])
            self.surveyItem[surveyItem] = survey
            self.allAssetList.update(self.surveyItem)

        self.landscapeItem = {}
        for landscape in self.landscapeList:
            landscapeItem = QtWidgets.QTreeWidgetItem(self.landscapeTreeWidget, [landscape])
            self.landscapeItem[landscapeItem] = landscape
            self.allAssetList.update(self.landscapeItem)

                ####### select UI Item #####

        if os.path.isfile("/home/m83/maya/cacheExport.json"):
            with open( "/home/m83/maya/cacheExport.json", 'r' ) as f:
                root = json.load(f)
            
            try:
                self.currentSelectItem["currentType"] = root["assetsOpt"]["currentType"]
                self.currentSelectItem["name"] = root["assetsOpt"]["currentName"]
                
                treeWidgetType_item = self.treeWidgetType[ self.currentSelectItem["currentType"] ].findItems(self.currentSelectItem["name"] ,QtCore.Qt.MatchExactly |QtCore.Qt.MatchRecursive,0)[0]
                self.treeWidgetType[ self.currentSelectItem["currentType"] ].setCurrentItem(treeWidgetType_item)
                self.selectAssetItemFC ( treeWidgetType_item )
                self.currentSelectItem["class"] = treeWidgetType_item
                
                self.stretchPushButton.setText("/show/%s/assets/%s/%s/ " %(self.proj,  self.currentSelectItem["currentType"], self.currentSelectItem["name"]))
                
                self.currentSelectItem["dir"] = "/show/%s/assets/%s/%s" %(self.proj,  self.currentSelectItem["currentType"], self.currentSelectItem["name"])
                
            except:
                pass
        try:
            self.matchmoveCheckNum = int("%s" % root["assetsOpt"]["matchmoveCheckNum"])
            self.layoutCheckNum = int("%s" % root["assetsOpt"]["layoutCheckNum"])
            self.modelCheckNum=            int( "%s" %root["assetsOpt"]["modelCheckNum"] )
            self.rigCheckNum=              int( "%s" %root["assetsOpt"]["rigCheckNum"] )
            self.lookdevCheckNum=          int( "%s" %root["assetsOpt"]["lookdevCheckNum"] )
            self.litRigSetCheckNum = int("%s" % root["assetsOpt"]["litRigCheckNum"])
            self.matchmoveCheckBox.setChecked(self.matchmoveCheckNum)
            self.layoutCheckBox.setChecked(self.layoutCheckNum)
            self.modelCheckBox.setChecked  ( self.modelCheckNum)
            self.rigCheckBox.setChecked    ( self.rigCheckNum)
            self.lookdevCheckBox.setChecked( self.lookdevCheckNum)
            self.litRigSetCheckBox.setChecked(self.litRigSetCheckNum)
            
            self.title1CheckNum = int( "%s" %root["assetsOpt"]["title1CheckNum"] )
            self.title2CheckNum = int( "%s" %root["assetsOpt"]["title2CheckNum"] )
            self.title3CheckNum = int( "%s" %root["assetsOpt"]["title3CheckNum"] )
            
            self.title1CheckBox.setChecked(self.title1CheckNum)
            self.title2CheckBox.setChecked(self.title2CheckNum)
            self.title3CheckBox.setChecked(self.title3CheckNum)

            self.showHideItemSet()
            self.titlecheckSet()
        
            self.propCheckBox.setChecked(  root["assetsOpt"]["propCheckBox"] )
            self.chaCheckBox.setChecked(   root["assetsOpt"]["chaCheckBox"] )
            self.envCheckBox.setChecked(   root["assetsOpt"]["envCheckBox"] )
            self.crowdCheckBox.setChecked( root["assetsOpt"]["crowdCheckBox"] )
            self.litRigCheckBox.setChecked(root["assetsOpt"]["litRigCheckBox"])
            self.etcCheckBox.setChecked(   root["assetsOpt"]["etcCheckBox"] )
            self.aircraftCheckBox.setChecked(root["assetsOpt"]["aircraftCheckBox"])
            self.plantCheckBox.setChecked(root["assetsOpt"]["plantCheckBox"])
            self.rockCheckBox.setChecked(root["assetsOpt"]["rockCheckBox"])
            self.setCheckBox.setChecked(root["assetsOpt"]["setCheckBox"])
            self.shipCheckBox.setChecked(root["assetsOpt"]["shipCheckBox"])
            self.structureCheckBox.setChecked(root["assetsOpt"]["structureCheckBox"])
            self.vehicleCheckBox.setChecked(root["assetsOpt"]["vehicleCheckBox"])
            self.weaponCheckBox.setChecked(root["assetsOpt"]["weaponCheckBox"])
            self.surveyCheckBox.setChecked(root["assetsOpt"]["surveyCheckBox"])
            self.landscapeCheckBox.setChecked(root["assetsOpt"]["landscapeCheckBox"])


            if  root["assetsOpt"]["topFrameisHidden"] == True:
                self.topFrame.hide()            
        except:
            pass

        self.commentWindow = commentWindow.stackeStackedWidget( self.currentSelectItem["dir"], self.currentPartType)
        self.stackeStackedWidget.insertWidget ( 1, self.commentWindow )
        self.stackeStackedWidget.setCurrentIndex(1)
        
#         self.ui.myTreeWidget.header().setStretchLastSection(False)
#         self.ui.myTreeWidget.header().setResizeMode(0, QHeaderView.Stretch) 

    # select Item
    def propSelectItems(self, name):
        items = self.propTreeWidget.selectedItems()
        self.selectItems["prop"] = items

    def chaSelectItems(self, name):
        items = self.chaTreeWidget.selectedItems()
        self.selectItems["cha"] = items

    def envSelectItems(self, name):
        items = self.envTreeWidget.selectedItems()
        self.selectItems["env"] = items

    def crowdSelectItems(self, name):
        items = self.crowdTreeWidget.selectedItems()
        self.selectItems["crowd"] = items

    def litRigSelectItems(self, name):
        items = self.litRigTreeWidget.selectedItems()
        self.selectItems["litRig"] = items

    def etcSelectItems(self, name):
        items = self.etcTreeWidget.selectedItems()
        self.selectItems["etc"] = items

    def aircraftSelectItems(self, name):
        items = self.aircraftTreeWidget.selectedItems()
        self.selectItems["aircraft"] = items

    def plantSelectItems(self, name):
        items = self.plantTreeWidget.selectedItems()
        self.selectItems["plant"] = items

    def rockSelectItems(self, name):
        items = self.rockTreeWidget.selectedItems()
        self.selectItems["rock"] = items

    def setSelectItems(self, name):
        items = self.setTreeWidget.selectedItems()
        self.selectItems["set"] = items

    def shipSelectItems(self, name):
        items = self.shipTreeWidget.selectedItems()
        self.selectItems["ship"] = items

    def structureSelectItems(self, name):
        items = self.structureTreeWidget.selectedItems()
        self.selectItems["structure"] = items

    def vehicleSelectItems(self, name):
        items = self.vehicleTreeWidget.selectedItems()
        self.selectItems["vehicle"] = items

    def weaponSelectItems(self, name):
        items = self.weaponTreeWidget.selectedItems()
        self.selectItems["weapon"] = items

    def surveySelectItems(self, name):
        items = self.surveyTreeWidget.selectedItems()
        self.selectItems["survey"] = items

    def landscapeSelectItems(self, name):
        items = self.landscapeTreeWidget.selectedItems()
        self.selectItems["landscape"] = items

    # select Fc
    def propFc(self, className, name):
        self.stretchPushButton.setText(self.propList[name])
        self.currentSelectItem["dir"] = self.propList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "prop"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)
        # print self.propList[name]
        
    def chaFc(self, className, name):
        self.stretchPushButton.setText(self.chaList[name])
        self.currentSelectItem["dir"] = self.chaList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "cha"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)
        # print "<<cha select >>", self.currentSelectItem["class"]

    def envFc(self, className, name):
        self.stretchPushButton.setText(self.envList[name])
        self.currentSelectItem["dir"] = self.envList[name].rsplit("/",1)[0]
        self.currentSelectItem["currentType"] = "env"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)
#         print self.envList[name]

    def crowdFc(self, className, name):
        self.stretchPushButton.setText(self.crowdList[name])
        self.currentSelectItem["dir"] = self.crowdList[name].rsplit("/",1)[0]
        self.currentSelectItem["currentType"] = "crowd"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    def litRigFc(self, className, name):
        self.stretchPushButton.setText(self.litRigList[name])
        self.currentSelectItem["dir"] = self.litRigList[name].rsplit("/",1)[0]
        self.currentSelectItem["currentType"] = "litRig"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    def etcFc(self, className, name):
        self.stretchPushButton.setText(self.etcList[name])
        self.currentSelectItem["dir"] = self.etcList[name].rsplit("/",1)[0]
        self.currentSelectItem["currentType"] = "etc"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)
#         print self.etcList[name]

    def aircraftFc(self, className, name):
        self.stretchPushButton.setText(self.aircraftList[name])
        self.currentSelectItem["dir"] = self.aircraftList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "aircraft"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    def plantFc(self, className, name):
        self.stretchPushButton.setText(self.plantList[name])
        self.currentSelectItem["dir"] = self.plantList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "plant"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    def rockFc(self, className, name):
        self.stretchPushButton.setText(self.rockList[name])
        self.currentSelectItem["dir"] = self.rockList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "rock"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)


    def setFc(self, className, name):
        self.stretchPushButton.setText(self.setList[name])
        self.currentSelectItem["dir"] = self.setList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "set"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    def shipFc(self, className, name):
        self.stretchPushButton.setText(self.shipList[name])
        self.currentSelectItem["dir"] = self.shipList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "ship"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    def structureFc(self, className, name):
        self.stretchPushButton.setText(self.structureList[name])
        self.currentSelectItem["dir"] = self.structureList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "structure"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    def vehicleFc(self, className, name):
        self.stretchPushButton.setText(self.vehicleList[name])
        self.currentSelectItem["dir"] = self.vehicleList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "vehicle"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    def weaponFc(self, className, name):
        self.stretchPushButton.setText(self.weaponList[name])
        self.currentSelectItem["dir"] = self.weaponList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "weapon"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    def surveyFc(self, className, name):
        self.stretchPushButton.setText(self.surveyList[name])
        self.currentSelectItem["dir"] = self.surveyList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "survey"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    def landscapeFc(self, className, name):
        self.stretchPushButton.setText(self.landscapeList[name])
        self.currentSelectItem["dir"] = self.landscapeList[name].rsplit("/", 1)[0]
        self.currentSelectItem["currentType"] = "landscape"
        self.currentSelectItem["name"] = name
        self.currentSelectItem["class"] = className
        self.selectAssetItemFC(className)

    # set Select info
    def selectAssetItemFC(self, item):
        self.commentWindow.setPrjDir(self.currentSelectItem["dir"], self.currentPartType)
        self.assetInfoTreeWidget.clear()
        self.setTake(item)
        self.assetInfoList(item)

    def checkSet(self):
        num = self.checkPushButton.isChecked()

        for i in self.dataItemStruct["checkBox"]:
                i.setChecked(num)    

    def setchangeComboBox1(self, num,name):
        for i in self.dataItemStruct["comboBox1"][name]:
            i.setCurrentIndex(num)
 
    def setchangeComboBox2(self, num,name ):
        for i in self.dataItemStruct["comboBox2"][name]:
            i.setCurrentIndex(num)
                 
    def setchangeCheckBox(self,num,name ):
        for i in self.dataItemStruct["checkBox"][name]:
            if num:
                stateV = QtCore.Qt.Checked
            else:
                stateV = QtCore.Qt.Unchecked

            #i.setCheckState(num)
            i.setCheckState(stateV)

    def setTake(self, name):
        try:
            self.TakeList, self.justTakeList, self.currentTake, TakeName = takeScript.checkTakeName(self.allAssetItems[self.allAssetList[name]][:-1], str(self.currentPartType))  # asset Dir, Type
        except:
            self.currentTake =None
            self.take_ComboBox.clear()
            return

        Takelist = list(self.TakeList.keys())        
        Takelist.sort(reverse=True)
        self.take_ComboBox.clear()
        self.take_ComboBox.addItems(Takelist)

    def changeStackedLayoutMode(self, num):
        self.stackeStackedWidget.setCurrentIndex(not(num))

#------------------Button--------------------------------------
#                 Button
#--------------------------------------------------------------
    def autoSet(self):
        #prj, widgetType, assetName, partType, sceneName, sceneDir = itemScript.getMayaFileList()
        prj, widgetType, assetName, partType, sceneName, sceneDir = utilScript.getMayaFileList()
        widgetTypeList = {"aircraftTreeWidget": self.aircraftFc, "chaTreeWidget": self.chaFc, "envTreeWidget": self.envFc,
                          "crowdTreeWidget": self.crowdFc, "litRigTreeWidget": self.litRigFc, "etcTreeWidget": self.etcFc,
                          "plantTreeWidget": self.plantFc, "rockTreeWidget":self.rockFc, "setTreeWidget":self.setFc,
                          "shipTreeWidget":self.shipFc, "structureTreeWidget":self.structureFc, "vehicleTreeWidget":self.vehicleFc,
                          "weaponTreeWidget":self.weaponFc, "surveyTreeWidget":self.surveyFc, "landscapeTreeWidget":self.landscapeFc}

        try:
            print(("%s" %assetName))
            select_item = self.treeWidgetType[ "%s" %widgetType ].findItems( "%s" %assetName, QtCore.Qt.MatchExactly |QtCore.Qt.MatchRecursive,0)[0]
        except: # KeyError
            return

        self.treeWidgetType["%s" %widgetType ].setCurrentItem(select_item)
        self.selectAssetItemFC( select_item ) # select Item

        try:
            print((">", str(self.treeWidgetType["%s" % widgetType].objectName())))
            widgetTypeList[str(self.treeWidgetType["%s" % widgetType].objectName())](  select_item, str(select_item.text(0)))
        except: # KeyError
            return

        self.focusSet(select_item.treeWidget())

    def deleteItem(self):
        ret = QtWidgets.QMessageBox.question(self, "Question Message", 
              '''Do you want to Delete Item?''', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
         
        if ret == QtWidgets.QMessageBox.Cancel:
            return
         
        globalTake = self.assetinfos
 
        for checkBoxItem in self.dataItemStruct["allCheckBoxItemList"]:
            if checkBoxItem.isChecked():
                rootType = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][0]
                itemName = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][1]
                 
                #item delete
                if globalTake[rootType]["objectList"].get(itemName):
                    del globalTake[rootType]["objectList"][itemName]
                     
                #item List delete
                if not globalTake[rootType].get("objectList"):
                    del globalTake[rootType]

        # Save Item
        TakeName = self.take_ComboBox.currentText()
        #itemScript.deleteAssetSaveInfoList(self.TakeList["%s" %TakeName], globalTake)
        utilScript.deleteAssetSaveInfoList(self.TakeList["%s" % TakeName], globalTake)
        self.assetInfoTreeWidget.clear()                    
#         self.shot(self.shotClass)
        self.refresh()

    def refresh(self):
        self.selectAssetItemFC(self.currentSelectItem["class"])
#         self.shot(self.shotClass)

    def usdView(self):
        for rootType in self.rootItemTypes:
            if  self.dataItemStruct["partTypeCheckBox"].get(rootType) == None:
                continue
            for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:  #check Box List
                if checkBoxItem.isChecked() == True:
                    itemList = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem]
                    objList = {itemList[1]: self.assetinfos[rootType]["objectList"][itemList[1]]}

                    for objName, objPath in list(objList.items()):
                        objUSDpath = objPath.replace(".abc", ".usd")
                        if os.path.exists(objUSDpath):
                            # uview.execute(objUSDpath)
                            print('해당 기능은 지원되지 않습니다.')
                        else:
                            QtWidgets.QMessageBox.information(self, "Message", "usd 파일이 없습니다.", QtWidgets.QMessageBox.Ok)

    def typeCheck(self):
        num = 1- self.typeCheckPushButton.isChecked()

        self.matchmoveCheckBox.setChecked(num)
        self.layoutCheckBox.setChecked(num)
        self.modelCheckBox.setChecked( num)
        self.rigCheckBox.setChecked(num)
        self.lookdevCheckBox.setChecked(num)
        self.litRigSetCheckBox.setChecked(num)

        self.showHideItemSet()
#         self.titlecheckSet()
    def takeChange(self):
        self.assetInfoTreeWidget.clear()
        self.assetInfoList(self.currentSelectItem["class"])
        self.showHideItemSet()
        self.titlecheckSet()

    def showHideItemSet(self):
        self.matchmoveCheck(self.matchmoveCheckNum)
        self.layoutCheck(self.layoutCheckNum)
        self.modelCheck ( self.modelCheckNum)
        self.rigCheck   ( self.rigCheckNum)
        self.lookdevCheck(self.lookdevCheckNum)
        self.litRigSetCheck(self.litRigSetCheckNum)

    def titlecheckSet(self):
        self.titleCheck( self.title1CheckNum, self.title1CheckBox)
        self.titleCheck( self.title2CheckNum, self.title2CheckBox)  
        self.titleCheck( self.title3CheckNum, self.title3CheckBox)

    def matchmoveCheck(self, setNum):
        num = (2 - setNum) /2
        if self.dataItemStruct:
            matchList = ["mm"]
            searchList = ["Mm"]

            keyList = list(self.dataItemStruct["rootClass"].keys())
            for i in keyList:
                checkV = 0
                for matchV in matchList:
                    if re.match(matchV, i):
                        checkV = 1
                for searchV in searchList:
                    if re.search(searchV, i):
                        checkV = 1

                if checkV:
                    rootItem = self.dataItemStruct["rootClass"][i]
                    rootItem.setHidden(num)

            self.matchmoveCheckNum=setNum

    def layoutCheck(self, setNum):
        num = (2 - setNum) /2
        if self.dataItemStruct:
            matchList = ["layout"]
            searchList = ["Layout"]

            keyList = list(self.dataItemStruct["rootClass"].keys())
            for i in keyList:
                checkV = 0
                for matchV in matchList:
                    if re.match(matchV, i):
                        checkV = 1
                for searchV in searchList:
                    if re.search(searchV, i):
                        checkV = 1

                if checkV:
                    rootItem = self.dataItemStruct["rootClass"][i]
                    rootItem.setHidden(num)

            self.layoutCheckNum=setNum

    def modelCheck(self, setNum):
        num = (2 - setNum) /2
        if self.dataItemStruct:
            if self.dataItemStruct["rootClass"].get("model"):
                modelItem  = self.dataItemStruct["rootClass"]["model"]
                modelItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("displayLayerModel"):
                displayLayerModelItem  = self.dataItemStruct["rootClass"]["displayLayerModel"]
                displayLayerModelItem.setHidden(num)
            self.modelCheckNum=setNum

    def rigCheck(self, setNum):
        num = (2 - setNum) /2
        if self.dataItemStruct:
            if self.dataItemStruct["rootClass"].get("rig"):
                rigItem  = self.dataItemStruct["rootClass"]["rig"]
                rigItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("alembicRig"):
                alembicRigItem  = self.dataItemStruct["rootClass"]["alembicRig"]
                alembicRigItem.setHidden(num)
            self.rigCheckNum=setNum

    def lookdevCheck(self, setNum):
        num = (2 - setNum) /2
        if self.dataItemStruct:
            if self.dataItemStruct["rootClass"].get("shader"):
                shaderItem  = self.dataItemStruct["rootClass"]["shader"]
                shaderItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("displayLayerLookdev"):
                displayLayerLookdevItem  = self.dataItemStruct["rootClass"]["displayLayerLookdev"]
                displayLayerLookdevItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("element"):
                elementItem  = self.dataItemStruct["rootClass"]["element"]
                elementItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("properties"):
                propertiesItem  = self.dataItemStruct["rootClass"]["properties"]
                propertiesItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("lookdevSet"):
                lookdevSetItem  = self.dataItemStruct["rootClass"]["lookdevSet"]
                lookdevSetItem.setHidden(num)
            self.lookdevCheckNum=setNum

    def litRigSetCheck(self, setNum):
        num = (2 - setNum) /2
        if self.dataItemStruct:
            if self.dataItemStruct["rootClass"].get("litRig"):
                litRigItem  = self.dataItemStruct["rootClass"]["litRig"]
                litRigItem.setHidden(num)
            self.litRigSetCheckNum=setNum

    def titleCheck(self, num, name):
        if self.title1CheckBox == name:
            for root in self.dataItemStruct["rootClass"]:
                self.dataItemStruct["rootClass"][root].setExpanded(num)
            self.title1CheckNum = num
        
        if self.title2CheckBox == name:
            for sub in self.dataItemStruct["subClass"]:
                sub.setExpanded(num)
                # self.dataItemStruct["subClass"][root].setExpanded(num)
            self.title2CheckNum = num
             
        if self.title3CheckBox == name:
            for item in self.dataItemStruct["itemClass"]:             
                item.setExpanded(num)
                # self.dataItemStruct["itemClass"][root].setExpanded(num)
            self.title3CheckNum = num

    def assetWidgetCheck(self, num, name):
        name.setHidden(num)

    #----------------------------------------------
    #            set info List
    #----------------------------------------------
    def assetInfoList(self,name):

        # get take
        self.assetinfos={}

        if not self.take_ComboBox.currentText():
            self.setTake(name)

        if not self.take_ComboBox.currentText():
            self.dataItemStruct["rootClass"]={}
            self.dataItemStruct["subClass"]   = {}
            self.dataItemStruct["itemClass"]   = {}
            return

        else:
            TakeName = self.take_ComboBox.currentText()
            #self.assetinfos = cameraExportScript.assetInfoList(self.allAssetItems[self.allAssetList[name]][:-1],self.TakeList["%s" % TakeName])
            self.assetinfos = takeScript.assetInfoList(self.allAssetItems[self.allAssetList[name]][:-1], self.TakeList["%s" % TakeName])

        if self.assetinfos == None:
            return

        self.assetInfoItem={}
        #currentPart = itemScript.currentPartType()
        currentPart = utilScript.currentPartType()

        #widget size
        self.assetInfoTreeWidget.setColumnWidth(0, 80)
        self.assetInfoTreeWidget.setColumnWidth(1, 260)
        self.assetInfoTreeWidget.setColumnWidth(2, 250)
        self.assetInfoTreeWidget.setColumnWidth(3, 40)
        self.assetInfoTreeWidget.setColumnWidth(4, 60)
        self.assetInfoTreeWidget.setColumnWidth(8, 80)
        self.assetInfoTreeWidget.setColumnWidth(9, 130)

        self.assetInfoTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        #font
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)

        # ani
        self.dataItemStruct["treeItem"]   = {}
        self.dataItemStruct["checkBox"]   = {}
        self.dataItemStruct["comboBox1"]  = {}
        self.dataItemStruct["comboBox2"]  = {}
        self.dataItemStruct["allCheckBoxItemList"]= {}
        self.dataItemStruct["allTreeWidgetItemList"]= {}
         
        self.dataItemStruct["partTypeCheckBox"]= {}
        self.dataItemStruct["allItemClass"]  = {}
        self.dataItemStruct["rootClass"]  = {}
        self.dataItemStruct["subClass"]   = {}
        self.dataItemStruct["itemClass"]   = {}
         
        for rootItem in self.assetinfos:
            itemList = self.assetinfos[rootItem]
             
            self.assetSceneItem = QtWidgets.QTreeWidgetItem (self.assetInfoTreeWidget)  # create item
            self.assetSceneItem.setExpanded(1)

            # aaaa
            self.assetSceneItem.setText(1, " %s" %rootItem )
            self.assetSceneItem.setText(3, "")

            self.checkBox_root  = QtWidgets.QCheckBox()
            self.comboBox1_root = QtWidgets.QComboBox()
            self.comboBox2_root = QtWidgets.QComboBox()
            self.comboBox1_root.setObjectName("opt1")
            self.comboBox2_root.setObjectName("opt2")
             
             
            self.assetInfoTreeWidget.setItemWidget( self.assetSceneItem, 0, self.checkBox_root)
            self.assetInfoTreeWidget.setItemWidget( self.assetSceneItem, 6, self.comboBox1_root)            
            self.assetInfoTreeWidget.setItemWidget( self.assetSceneItem, 7, self.comboBox2_root)
             
            self.comboBox1_root.setStyleSheet("QComboBox {background-color: transparent;}")
            self.comboBox2_root.setStyleSheet("QComboBox {background-color: transparent;}")
            self.checkBox_root.stateChanged[int].connect(lambda num, name=self.checkBox_root: self.setchangeCheckBox(num, name))
            self.comboBox1_root.activated[int].connect(lambda num, name=self.comboBox1_root: self.setchangeComboBox1(num, name))
            self.comboBox2_root.activated[int].connect(lambda num, name=self.comboBox2_root: self.setchangeComboBox2(num, name))


            # Data
            self.dataStruct.itemClass["rootClass"].update( { rootItem : self.assetSceneItem } )
            self.dataStruct.set( {self.assetSceneItem : None})
            self.dataStruct.set( {self.checkBox_root : None} )
            self.dataStruct.set( {self.comboBox1_root: None}, rootItem )
            self.dataStruct.set( {self.comboBox2_root: None}, rootItem )            

            
            # set objectList
            num = 0
            if not itemList.get("fileName"):
                print((">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> %s erro : PZ ! take edit <<<<<<<<<<<<<<" %rootItem))
                continue

            objectList = utilScript.splitItemName(itemList["objectList"])  # {u'gunShot': [u'gunShot1:ctrl_SET', u'gunShot:ctrl_SET']}

            for infoItem in objectList: # top item
                self.subTreeWidget = QtWidgets.QTreeWidgetItem(self.assetSceneItem)
                self.subTreeWidget.setFont(1, font)
                self.subTreeWidget.setExpanded(1)
                self.subTreeWidget.setText( 1, infoItem)
                self.subTreeWidget.setText( 3, "" )
 
                # middle item set Color
                list(map(lambda x : self.subTreeWidget.setBackground(x, QtGui.QBrush( QtGui.QColor(80, 255 , 0, 10) )), list(range(10))))                

                self.checkBox_midle  = QtWidgets.QCheckBox()
                self.comboBox1_midle = QtWidgets.QComboBox()
                self.comboBox2_midle = QtWidgets.QComboBox()
                self.comboBox1_midle.setObjectName("opt1")
                self.comboBox2_midle.setObjectName("opt2")                
                self.assetInfoTreeWidget.setItemWidget( self.subTreeWidget, 0, self.checkBox_midle)
                self.assetInfoTreeWidget.setItemWidget( self.subTreeWidget, 6, self.comboBox1_midle)
                self.assetInfoTreeWidget.setItemWidget( self.subTreeWidget, 7, self.comboBox2_midle)

                self.comboBox1_midle.setStyleSheet("QComboBox {background-color: transparent;}")
                self.comboBox2_midle.setStyleSheet("QComboBox {background-color: transparent;}")

                self.checkBox_midle.stateChanged[int].connect(lambda num, name=self.checkBox_midle: self.setchangeCheckBox(num, name))
                self.comboBox1_midle.activated[int].connect(lambda num, name=self.comboBox1_midle: self.setchangeComboBox1(num, name))
                self.comboBox2_midle.activated[int].connect(lambda num, name=self.comboBox2_midle: self.setchangeComboBox2(num, name))

                #data
                self.dataStruct.itemClass["subClass"].update( { self.subTreeWidget: infoItem  } )
                self.dataStruct.set( { self.assetSceneItem : self.subTreeWidget  })
                self.dataStruct.set( { self.checkBox_root  : self.checkBox_midle })
                self.dataStruct.set( { self.comboBox1_root : self.comboBox1_midle }, rootItem)
                self.dataStruct.set( { self.comboBox2_root : self.comboBox2_midle }, rootItem)

                #object List
                objList = objectList[infoItem]                      
                for objName in objList:        #sub item
                    #set
                    self.subItemTreeWidget = QtWidgets.QTreeWidgetItem(self.subTreeWidget)
                    self.subItemTreeWidget.setText( 1, "%s" % objName )

                    # Item Point
                    if type(itemList["objectList"][objName]) == type([]):
                        self.subItemTreeWidget.setText( 2, "%s" % re.search( "[\w]+(?=/[\w]+\.)", itemList["objectList"][objName][0]).group() )
                    else:
                        self.subItemTreeWidget.setText( 2, "%s" % re.search( "[\w]+(?=\.)", itemList["objectList"][objName]).group() )

                    # sub item Dir Text
                    #-----------------------
                    self.subItemTreeWidget_PathItem = QtWidgets.QTreeWidgetItem(self.subItemTreeWidget)

                    if type(itemList["objectList"][objName]) == type([]): #camera
                        self.subItemTreeWidget_PathItem.setText(2, "%s" %itemList["objectList"][objName][0])
                    else:
                        self.subItemTreeWidget_PathItem.setText(2, "%s" %itemList["objectList"][objName])
 
                    if type(itemList["objectList"][objName]) == type([]):#imagePlane
                            self.subItemTreeWidget_PathItem.setText( 1, "%s" % itemList["objectList"][objName][1:] )
                            self.subItemTreeWidget_PathItem.setForeground(1 ,QtGui.QBrush( QtGui.QColor(255, 255 , 255, 120) ))
 
                    self.subItemTreeWidget_PathItem.setFlags(  QtCore.Qt.ItemIsEnabled   | QtCore.Qt.ItemIsEditable )
                    self.subItemTreeWidget_PathItem.setForeground(2 ,QtGui.QBrush( QtGui.QColor(255, 255 , 255, 120) ))
 
                    self.subItemTreeWidget.setText( 5, " %s" %itemList["frame"][objName])
                    self.subItemTreeWidget.setText( 8, " %s" %itemList["username"][objName])
                    self.subItemTreeWidget.setText( 9, " %s" %itemList["date"][objName])
 
                    # upDate
                    if currentPart is not None:
                        if itemList["objectCheck"].get(objName).get(currentPart) is not None and itemList["objectCheck"].get(objName).get(currentPart) == 1:
                            updateLabel = QtWidgets.QLabel("UP", self.assetInfoTreeWidget)
                            updateLabel.setMaximumWidth(30)
                            updateLabel.setStyleSheet("border: 2px solid yellow;border-radius: 10px; font:  12px; color :yellow ; background-color : rgb(50, 80 , 100);qproperty-alignment: AlignCenter; ")
                            self.assetInfoTreeWidget.setItemWidget( self.subItemTreeWidget, 4, updateLabel)
                    
                    #-------------------------
                    # Comment Tip
                    #-------------------------
                    if itemList.get("comment") and itemList.get("comment").get(objName):
                        commentText = "%s" %itemList["comment"][objName]
                        self.subItemTreeWidget_PathItem.setText(1, "%s" %commentText)
                        self.itemCommentButton = QtWidgets.QPushButton(self.assetInfoTreeWidget)
                        self.itemCommentButton.setIcon(QtGui.QIcon( "/core/MAYA_2017/shelf/scripts/5.Ani/2.Publish/chacheExport/icon/messages-icon.png"))
                        self.itemCommentButton.setFixedSize(20,20 )
                        self.itemCommentButton.setFlat(1)
                        self.assetInfoTreeWidget.setItemWidget( self.subItemTreeWidget, 5, self.itemCommentButton)
                        UpdateWindow = updateWindow(self.itemCommentButton, commentText)
                        self.itemCommentButton.clicked.connect(lambda i, name=UpdateWindow, button=self.itemCommentButton: self.updatePopWindow(name, button))
                    #-------------------------
                    self.checkBox_item = QtWidgets.QCheckBox()
                    self.comboBox1_item = QtWidgets.QComboBox()
                    self.comboBox2_item = QtWidgets.QComboBox()
                     
                    self.comboBox1_item.setObjectName("opt1")
                    self.comboBox2_item.setObjectName("opt2")                    
                    self.assetInfoTreeWidget.setItemWidget( self.subItemTreeWidget, 0, self.checkBox_item)
                    self.assetInfoTreeWidget.setItemWidget( self.subItemTreeWidget, 6, self.comboBox1_item)                    
                    self.assetInfoTreeWidget.setItemWidget( self.subItemTreeWidget, 7, self.comboBox2_item)
                    self.comboBox1_item.setStyleSheet("QComboBox {background-color: transparent;}")
                    self.comboBox2_item.setStyleSheet("QComboBox {background-color: transparent;}")
 
                    self.checkBox_midle.stateChanged[int].connect(
                        lambda num, name=self.checkBox_midle: self.setchangeCheckBox(num, name))
                    self.comboBox1_midle.activated[int].connect(
                        lambda num, name=self.comboBox1_midle: self.setchangeComboBox1(num, name))
                    self.comboBox2_midle.activated[int].connect(
                        lambda num, name=self.comboBox2_midle: self.setchangeComboBox2(num, name))


                    #data
                    self.dataStruct.itemClass["itemClass"].update( {  self.subItemTreeWidget : objName} )
                     
                    self.dataStruct.set( { self.subTreeWidget   : self.subItemTreeWidget })
                    self.dataStruct.set( { self.checkBox_midle  : self.checkBox_item })
                    self.dataStruct.set( { self.comboBox1_midle : self.comboBox1_item }, rootItem)
                    self.dataStruct.set( { self.comboBox2_midle :self.comboBox2_item }, rootItem)
 
                    self.dataStruct.set( { self.subItemTreeWidget   : self.subItemTreeWidget })
                    self.dataStruct.set( { self.checkBox_item       : self.checkBox_item })
                    self.dataStruct.set( { self.comboBox1_item      : self.comboBox1_item }, rootItem)
                    self.dataStruct.set( { self.comboBox2_item      :self.comboBox2_item }, rootItem)
                    
                    # Spinbox
                    self.spinBox = QtWidgets.QSpinBox()   
                    self.dataStruct.setList  ( { self.subItemTreeWidget : [ rootItem, objName, self.checkBox_item, self.comboBox1_item, self.comboBox2_item, self.spinBox] })
                    self.dataStruct.setList  ( { self.checkBox_item     : [ rootItem, objName, self.subItemTreeWidget, self.comboBox1_item, self.comboBox2_item, self.spinBox] })
                    self.dataStruct.setWidget(  rootItem  , {  objName : [  self.subItemTreeWidget,self.subTreeWidget,self.assetSceneItem  ]  })
                                        
                    # None Item setting
                    if rootItem in [ "modelLow","modelMid","modelHi", "modelXLow", "modelXHi","rigLow","rigMid","rigHi", "rigXLow", "rigXHi", "mocapRig"]: #"rig", "model",
                        self.assetInfoTreeWidget.setItemWidget( self.assetSceneItem, 6, None)
                        self.assetInfoTreeWidget.setItemWidget( self.subTreeWidget, 6, None)
                        self.assetInfoTreeWidget.setItemWidget( self.subItemTreeWidget, 6, None)
                     
                    if rootItem in ["rig", "model","modelLow","modelMid","modelHi","modelXLow", "modelXHi", "rigLow", "rigMid", "rigHi", "rigXLow", "rigXHi", "mocapRig", "lookdev", "digienv"]:
                        self.assetInfoTreeWidget.setItemWidget( self.subItemTreeWidget, 3, self.spinBox)
#                         self.spinBox.setValue(1)
                        self.spinBox.setMinimum (1)
                        self.subItemTreeWidget.setText(  5, "")

                    if rootItem in ["alembicAni", "alembicCrowdSim", "alembicCrowdAni", "alembicModel", "alembicRender","alembicRig",
                                    "alembicFur", "alembicMuscle", "alembicCloth", "alembicSimul", "alembicMm", "alembicFx",
                                    "alembicCurve", "alembicHair", "alembicHairSim", "alembicFurSim", "alembicClothSim", "alembicRig"]:
                        if not rootItem in ["alembicModel", "alembicRig"]:
                            self.assetInfoTreeWidget.setItemWidget(self.assetSceneItem, 6, None)
                            self.assetInfoTreeWidget.setItemWidget(self.subTreeWidget, 6, None)
                            self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 6, None)
                        self.comboBox2_item.clear()
                        self.comboBox2_midle.clear()
                        self.comboBox2_root.clear()
                        self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 3, self.spinBox)
                        self.spinBox.setMinimum (1)
                        self.subItemTreeWidget.setText(  5, "")
                        self.comboBox2_item.addItems(ABCIMPORTOPT)
                        self.comboBox2_midle.addItems(ABCIMPORTOPT)
                        self.comboBox2_root.addItems(ABCIMPORTOPT)
                                            
        self.colorSet()

    def colorSet(self):
        currentType = str(self.currentPartType)
        for root in self.dataItemStruct["rootClass"]:
            font = QtGui.QFont()
            font.setPointSize(13)
            font.setBold(True)
            font.setItalic(True)

            list(map(lambda x : self.dataItemStruct["rootClass"][root].setFont(x, font), list(range(7))))
            list(map(lambda x : self.dataItemStruct["rootClass"][root].setBackground(x, QtGui.QBrush( QtGui.QColor( 80, 100 , 255, 30) )), list(range(10))))

        # setcolor
        globalTake = self.assetinfos
        updateList = {}
        rigItem = []

        for rootType in self.rootItemTypes:
            if globalTake.get(rootType) == None:
                continue
#             if rootType == "model":
            objectList = []
            if not APPNAME == "clarisse":
                objectList = list(set([cmds.getAttr("%s" % x).split(",")[0] for x in cmds.ls("*.%s" % rootType, r=1)]))

            if rootType in self.rootItemTypes: #["model", "modelLow","modelMid","modelHi", "rigLow","rigMid","rigHi","mocapRig",  "modelEnv"]:
                objectList += list(set(rigItem) )

            if objectList:            # is tag
                if "objectList" in globalTake[rootType]:
                    item={}
                    for itemName in globalTake[rootType]["objectList"]:
                        if itemName not in objectList:  # not in itemName

                            item.update( {itemName : globalTake[rootType]["objectList"][itemName]} )
                            updateList.update( {rootType : item} )
                            if rootType in self.dataItemStruct["rootClass"]:
                                list(map(lambda x : self.dataItemStruct["rootClass"][rootType].setBackground(x, QtGui.QBrush( QtGui.QColor( 80, 100 , 255, 130) )), list(range(10))))
                                list(map(lambda x : self.dataItemStruct["allItemClass"][rootType][itemName][0].setForeground(x, QtGui.QBrush( QtGui.QColor( 80, 255 , 0, 160) )), list(range(10))))
                                list(map(lambda x : self.dataItemStruct["allItemClass"][rootType][itemName][1].setBackground(x, QtGui.QBrush( QtGui.QColor( 80, 255 , 0, 70) )), list(range(10))))

                        else:
                            if rootType in ["rig", "rigEnv"]:
                                rigItem.append(itemName)
 
            else:  # not local file/ rootItem   / all item
                if "objectList" in globalTake[rootType]:
                    item={}
                    for itemName in globalTake[rootType]["objectList"]:
                        item.update( {itemName : globalTake[rootType]["objectList"][itemName]} )
                        updateList.update( {rootType : item} )

                        list(map(lambda x : self.dataItemStruct["rootClass"][rootType].setBackground(x, QtGui.QBrush( QtGui.QColor( 80, 100 , 255, 130) )), list(range(10))))
                        list(map(lambda x : self.dataItemStruct["allItemClass"][rootType][itemName][0].setForeground(x, QtGui.QBrush( QtGui.QColor( 80, 255 , 0, 160) )), list(range(10))))
                        list(map(lambda x : self.dataItemStruct["allItemClass"][rootType][itemName][1].setBackground(x, QtGui.QBrush( QtGui.QColor( 80, 255 , 0, 70) )), list(range(10))))


    def colorChecked(self, check=None):
        try:
            TakeName = self.take_ComboBox.currentText()
            self.assetinfos = cameraExportScript.assetInfoList (self.shots[self.shotItem[self.shotClass]] , self.TakeList["%s" %TakeName])
        except:
            return
 
        treewidgetItems = self.assetInfoTreeWidget.selectedItems()
 
        for y in treewidgetItems:
            type = self.Data.treeItems[y]
            for x in self.assetinfos:
                for z in self.assetinfos[x]:
                    if z == type:
                        for i in self.assetinfos[x][type]["objectCheck"]:
                            if self.Data.subItemClassName.get(y) and i == self.Data.subItemClassName[y]:
                                if check == 1:
                                    self.assetinfos[x][type]["objectCheck"][i] = 1
                                     
                                    TakeName = self.take_ComboBox.currentText()
                                    cameraExportScript.assetSaveInfoList(self.TakeList["%s" %TakeName], self.assetinfos)
                                else:
                                    self.assetinfos[x][type]["objectCheck"][i] = 0   

                                    TakeName = self.take_ComboBox.currentText()
                                    cameraExportScript.assetSaveInfoList(self.TakeList["%s" %TakeName], self.assetinfos)                    
    
    def updatePopWindow(self, updateWindowName, button):
        updateWindowName.parent=button
        updateWindowName.moveWindow()
        updateWindowName.show()
        
#-------------------------------------------
#    Export
#-------------------------------------------
    def publishFile(self, opt=""):
        part = { "model" : self.modelExport,"dyn":self.rigExport, "rig":self.rigExport ,"lookdev":self.lookdevExport,  "litRig":self.litRigExport, "digienv":self.digienvExport}
        #partType = itemScript.currentPartType()
        partType = utilScript.currentPartType()

        if not partType:
            cmd = 'DISPLAY=:O notify-send "Noar Message" "Project Setting PZ!" -t 10000'
            Popen(cmd, shell=True, stdout=PIPE)
            return

        if partType == "model":
            opt = self.modelLodComboBox.currentText()
        elif partType == "dyn":
            opt = self.rigLodComboBox.currentText()
        elif partType == "rig":
            opt = self.rigLodComboBox.currentText()

        elif partType == "litRig":
            opt = self.litRigLodComboBox.currentText()
        # if opt == "_LOW":
        #     part[partType]("_LOW")
        # elif opt == "_PROXY":
        #     part[partType]("_PROXY")
        # else:
        #     part[partType]()

        if not opt or opt == "None" :
            part[partType]()
        else:
            part[partType]("_%s" % str(opt).upper())

    def pupFile(self):  ############################################################# publish file
        self.savefileName = str(self.pubWindow.titleLineEdit.text())
        self.savefileText = str(self.pubWindow.textEdit.toPlainText())
        # print ">>>>", self.savefileName, self.pubFileList["pubDir"], self.pubFileList["itemName"]
        self.versionUp = True
        pubDir = self.pubFileList.get("pubDir", "")
        if pubDir and self.savefileName:
            candidates = []
            if "/model/" in pubDir:
                candidates.append("{0}/{1}/{1}.mb".format(pubDir, self.savefileName))
                candidates.append("{0}/{1}".format(pubDir, self.savefileName))
            else:
                candidates.append("{0}/{1}.mb".format(pubDir, self.savefileName))
            candidates.extend(glob.glob("{0}/{1}.*".format(pubDir, self.savefileName)))
            candidates.extend(glob.glob("{0}/{1}_*.*".format(pubDir, self.savefileName)))
            if any([os.path.exists(p) for p in candidates]):
                self.versionUp = False

        # Publish File
        if "/rig/" in self.pubFileList['pubDir'] or "/dyn/" in self.pubFileList['pubDir']:
            print("assetExport.pubFile : rigScript.rigExport")
            opts = {}
            opts["includeProxy"] = self.includeProxy_checkBox.isChecked()

            self.savefileList = self.pubFileList["itemExport"](fileName=self.savefileName, itemdir=self.pubFileList["pubDir"],
                                                               itemName=self.pubFileList["itemName"], opts=opts, comment=self.savefileText)

        elif "/digienv/" in self.pubFileList['pubDir']:
            print("assetExport.pubFile : instanceScript.instanceExport")
            self.savefileList, self.digienvPointInfo, fileDirV, fileTypeV = self.pubFileList["itemExport"](self.savefileName, self.pubFileList["pubDir"], self.pubFileList["itemName"])
            print((fileDirV, fileTypeV))
        else:
            self.savefileList = self.pubFileList["itemExport"](self.savefileName, self.pubFileList["pubDir"],
                                                               self.pubFileList["itemName"])

        # Pub alembic
        if "/rig/" in self.pubFileList['pubDir'] or "/model/" in self.pubFileList['pubDir']:

            # Add Jiho ----------------------------------------------------------------------------------------

            import maya.cmds as cmds

            # self.pubFileList["pubDir"] : /show/ASD2/assets/test/dowooriD/model/pub
            # self.savefileName : dowooriD_model_v01
            # self.pubFileList["itemName"] : dowooriD
            self.mb_path = cmds.file(sn=1, q=1)
            # / show / ASD2 / assets / test / dowooriD / model / wip / scenes / dowooriD_model_v01_w01.mb
            self.mb_name = self.mb_path.split('/')[-1]
            self.base_name = self.mb_name.split('.')[0]
            self.wip_path = self.mb_path.split('/')[0:8]
            self.tex_path = '/'.join(self.wip_path) + '/texture'
            print(('tex_path >>>>>', self.tex_path))
            self.mmobj_path = '/'.join(self.wip_path) + '/data/mmobj'
            self.base_objPath = self.mmobj_path + '/' + self.savefileName
            self.jiho_objPath = self.base_objPath + '/{0}.obj'.format(self.savefileName)
            self.surveyPath = self.mb_path.split('/')[0:5]
            self.mmCollect_path = '/'.join(self.surveyPath) + '/mmGeoCollect'

            self.tex_list = os.listdir(self.tex_path)

            self.all_diff_list = []
            self.diff_fileList = []

            if 'survey' in self.mb_path:

                for i in self.tex_list:
                    if '_diff' in i:
                        self.all_diff_list.append(i)
                    else:
                        pass

                for z in self.all_diff_list:
                    if self.savefileName.split('_')[0] in z:
                        self.diff_fileList.append(z)
                    else:
                        pass

                print(('diff file list >>>>>>>', self.diff_fileList))

                if len(self.diff_fileList) == 1:
                    self.tex_newName = self.savefileName + '_diff.'+self.diff_fileList[0].split('.')[-2]+'.'+self.diff_fileList[0].split('.')[-1]
                    # print self.tex_path + '/' + self.diff_fileList[0]
                    shutil.copy(self.tex_path + '/' + self.diff_fileList[0], self.mmCollect_path+'/'+self.diff_fileList[0])
                    print ('texture file copy Done!!')
                    os.rename(self.mmCollect_path + '/' + self.diff_fileList[0], self.mmCollect_path + '/' +self.tex_newName)
                    print ('texture file rename Done!!')

                elif len(self.diff_fileList) > 1:
                    for i in self.diff_fileList:
                        self.UDIMnum = i.split('.')[-2]
                        if '10' in self.UDIMnum:
                            shutil.copy(self.tex_path + '/' + i, self.mmCollect_path+'/'+i)
                            print ('texture files copy Done!!!')
                            os.rename(self.mmCollect_path+'/'+i, self.mmCollect_path+'/'+self.savefileName+'_diff.'+self.UDIMnum+'.'+i.split('.')[-1])
                            print ('texture files rename Done!!!')

                        else:
                            print ('UDIM number is NOT FOUND!!')
                            pass
                elif len(self.diff_fileList) == 0:
                    print ('No texture matches the modeling version.')
                    pass

                else:
                    print ('diff in file NOT FOUND!!!')
                    pass

            else:
                pass

            # self.jiho_isCheck = self.jiho_mmobj_checkBox.isChecked()
            # self.jiho_isCheck = publishWindow().jiho_mmobj_checkBox
            self.jiho_isCheck = self.pubWindow.jiho_mmobj_checkBox.isChecked()
            print(self.jiho_isCheck, '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

            self.sel_obj = cmds.ls(selection=True)

            if self.jiho_isCheck:
                self.plugin_name = "objExport.so"
                if os.path.isdir(self.base_objPath):
                    pass
                else:
                    try:
                        os.makedirs(self.base_objPath)
                        print (">>>>> mmobj folder make Success <<<<<")
                        cmds.loadPlugin(self.plugin_name)
                    except:
                        pass
                if len(self.sel_obj) != 0:
                    self.serch_obj = cmds.ls(self.mb_path.split('/')[5])
                    cmds.file(self.jiho_objPath, force=True,options="groups=1;ptgroups=0;materials=0;smoothing=1;normals=1",typ="OBJexport", es=True)
                if 'survey' in self.mb_path:
                    shutil.copy(self.jiho_objPath, self.mmCollect_path+'/'+self.savefileName+'.obj')
                else:
                    pass

            # -------------------------------------------------------------------------------------------------

            self.saveAlembicFileList = alembicScript_asset.itemExport(self.savefileName, self.pubFileList["pubDir"],
                                                                      self.pubFileList[
                                                                          "itemName"])  # krExtraA_rig_v02 /show/MR/assets/cha/krExtraA/rig/pub krExtraA
            self.alembicAssetInfoExport()
            # create usd
            try:
                for abcName, abcPath in list(self.saveAlembicFileList.items()):
                    ucat.execute(abcPath)
                    print(("Created usd : {}".format(abcPath.split(".")[0] + ".usd")))
            except:
                print(("Error Created usd : {}".format(abcPath.split(".")[0] + ".usd")))

        # export Take
        self.pubWindow.closeWindow()

        #         if not re.search("_LOW$", self.savefileName):
        self.pubFileList["infoExport"]()  # self.modelAssetInfoExport()

        self.refresh()
        cmd = 'DISPLAY=:O notify-send "Noar Message" "Export Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)


    def modelExport(self, opt=""):
        #modelFileName , modelDir = itemScript.itemPubDirCheck()
        modelFileName, modelDir = utilScript.itemPubDirCheck()

        if modelFileName == None:
            print ("( assetExprot 1261 line ) Erro : Wrong Path !! ")
            return
        
        # rootName Check QMessageBox
        rootName  = modelScript.itemRootAssetNameCheck( modelDir)
        if rootName == None:
            ret = QtWidgets.QMessageBox.information(self, "Change Name !","Asset name does not match. !!", QtWidgets.QMessageBox.Ok)
            if ret == QtWidgets.QMessageBox.Ok:
                return

        # object Name Check
        #assetNameCheck = modelScript.itemAssetNameCheck( modelDir)--------------------------
        assetNameCheck = ""
        if assetNameCheck:
            message = ""
            for i in assetNameCheck:
                message += "%s  == > %s_%s \n" %(i, rootName,i)
            
            ret = QtWidgets.QMessageBox.question(self, "objectName rename ?", "%s" %message, QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            else:
                modelScript.assetNameRename(rootName,  assetNameCheck)

        # shap Name Check
        assetShapeNameCheck = modelScript.itemAssetShapeNameCheck( modelDir)
        if assetShapeNameCheck:
            message = ""
            for i in assetShapeNameCheck:
                if message.count("== >") >= 100: 
                    break
                message += "%s  == > %s \n" %(i, assetShapeNameCheck[i])
            
            ret = QtWidgets.QMessageBox.question(self, "ShapeName rename?", "%s" %message, QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            else:
                modelScript.assetShapeNameRename(assetShapeNameCheck)

        # export
        self.pubFileList = {"pubDir": modelDir, "itemExport": modelScript.modelExport,
                            "infoExport": self.modelAssetInfoExport, "itemName": str(rootName)}

        # open window
        self.pubWindow.setFileName( modelFileName,opt)
        self.pubWindow.show()

    def modelAssetInfoExport(self):
        modelScript.exportTake( self.savefileList, ["globalTake", "localTake"], "model")# takeTypeList = ["globalTake", "localTake"]#
        self.refresh()
        
        if not self.assetinfos.get( "model" ):
            self.assetinfos[ "model" ] ={}
        if not self.assetinfos[ "model" ].get( "comment" ) :
            self.assetinfos[ "model" ].update( { "comment" : {} } )
        
        self.assetinfos[ "model" ]["comment"].update( { self.pubFileList["itemName"] : self.savefileText} )
        
        takeScript.changeSaveTake(self.currentTake, self.assetinfos)



    def rigExport(self, opt=""):
        rigFileName, rigDir = utilScript.itemPubDirCheck()
        if rigFileName == None:
            print ("Error : Wrong Path !! ")
            return
        if "MOCAP" in rigFileName:
            opt = "_MOCAP"

        # rootName Check QMessageBox
        rootName  = rigScript.itemRootAssetNameCheck( rigDir)
        if rootName == None:
            ret = QtWidgets.QMessageBox.information(self, "Change Name !","Asset name does not match. !!", QtWidgets.QMessageBox.Ok)
            if ret == QtWidgets.QMessageBox.Ok:
                return

        # export
        self.pubFileList = {"pubDir": rigDir, "itemExport": rigScript.rigExport,
                            "infoExport": self.rigAssetInfoExport, "itemName": str(rootName)}
        # open window
        self.pubWindow.setFileName(rigFileName, opt)
        self.pubWindow.show()
    
    def rigAssetInfoExport(self):

        rigScript.assetInfoExport( self.savefileList)# takeTypeList = ["globalTake", "localTake"]#

        self.refresh()

        if not self.assetinfos.get( "rig" ):
            self.assetinfos[ "rig" ] ={}

        if not self.assetinfos[ "rig" ].get( "comment" ) :
            self.assetinfos[ "rig" ].update( { "comment" : {} } )

        self.assetinfos[ "rig" ]["comment"].update( { self.pubFileList["itemName"] : self.savefileText} )

        takeScript.changeSaveTake(self.currentTake, self.assetinfos)

    def alembicAssetInfoExport(self):
        alembicScript_asset.assetInfoExport(self.saveAlembicFileList )  # takeTypeList = ["globalTake", "localTake"]#
        self.refresh()

    def noahExport(self, appType="maya", opt=""):

        # select
        deptType = str(self.parent.type_ComboBox.currentText())

        fileName, exportDir = utilScript.itemPubDirCheck(deptType)

        if fileName == None:
            print ("Error : Wrong Path !! ")
            return
        exportDirList = exportDir.split("/")
        entityV = exportDirList[4]
        taskV = exportDirList[5]
        if appType == "clarisse":
            rootNameFunc = {
                "lookdev": mainScriptLinux.setSelItem,
                "digienv": mainScriptLinux.setSelItem
            }
            rootName, rootFullName = rootNameFunc[deptType](deptType, entityV, taskV)
        else:
            # ToDo maya
            return
            '''
            rootNameFunc = {
                "lookdev": lookdevScript.itemRootAssetNameCheck
            }
            rootName = str(rootNameFunc[deptType](exportDir))
            rootFullName = ""
            '''

        if rootName == None:
            ret = QtWidgets.QMessageBox.information(self, "Change Name !","Asset name does not match. !!", QtWidgets.QMessageBox.Ok)
            if ret == QtWidgets.QMessageBox.Ok:
                return

        exportFunc = {
            "clarisse" : mainScriptLinux.exportItem,
            "maya" : utilScript.itemExport,
        }

        self.pubFileList = {
            "pubDir": exportDir,
            "itemExport": exportFunc[appType],
            "infoExport": self.noahAssetInfoExport,
            "itemName": rootName,
            "itemFullName" : rootFullName
        }

        # open window
        self.pubWindow.setFileName(fileName, opt) # go to self.pupFile
        self.pubWindow.show()

    def noahAssetInfoExport(self):
        deptType = str(self.parent.type_ComboBox.currentText())
        takeScript.takeExport(self.savefileList, deptType, versionUp=self.versionUp)

        self.refresh()

        if not self.assetinfos.get(deptType):
            self.assetinfos[deptType] = {}

        if not self.assetinfos[deptType].get("comment"):
            self.assetinfos[deptType].update({"comment": {}})

        if isinstance(self.pubFileList["itemName"], list):
            self.assetinfos[deptType]["comment"].update({self.pubFileList["itemName"][0]: self.savefileText})
        else:
            self.assetinfos[deptType]["comment"].update({self.pubFileList["itemName"]: self.savefileText})

        takeScript.changeSaveTake(self.currentTake, self.assetinfos)

    def lookdevExport(self, opt=""):
        lookdevFileName, lookdevDir = utilScript.itemPubDirCheck()

        if "_PROXY" in lookdevFileName:
            lookdevFileName = lookdevFileName.split("_PROXY")[0]
              
        if lookdevFileName == None:
            print ("( assetExprot 1479 line ) Error : Wrong Path !! ")
            return
        
        # rootName Check QMessageBox
        rootName  = lookdevScript.itemRootAssetNameCheck( lookdevDir)
        if rootName == None:
            ret = QtWidgets.QMessageBox.information(self, "Change Name !","Asset name does not match. !!", QtWidgets.QMessageBox.Ok)
            if ret == QtWidgets.QMessageBox.Ok:
                return

        # export
        self.pubFileList = {"pubDir": lookdevDir, "itemExport": utilScript.itemExport, "infoExport": self.lookdevAssetInfoExport, "itemName": str(rootName)}
        # open window
        self.pubWindow.setFileName( lookdevFileName, opt)
        self.pubWindow.show()

    def lookdevAssetInfoExport(self):
        takeScript.takeExport(self.savefileList, 'lookdev')  # takeTypeList = ["globalTake", "localTake"]#

        self.refresh()
        
        if not self.assetinfos.get( "lookdev" ):
            self.assetinfos[ "lookdev" ] ={}

        if not self.assetinfos[ "lookdev" ].get( "comment" ) :
            self.assetinfos[ "lookdev" ].update( { "comment" : {} } )

        self.assetinfos[ "lookdev" ]["comment"].update( { self.pubFileList["itemName"] : self.savefileText} )

        takeScript.changeSaveTake(self.currentTake, self.assetinfos)

    def litRigExport(self, opt=""):
        litRigFileName, litRigDir = utilScript.itemPubDirCheck()

        if litRigFileName == None:
            print ("( assetExprot 1489 line ) Erro : Wrong Path !! ")
            return

        # rootName Check QMessageBox
        rootName = lightRigScript.itemRootAssetNameCheck(litRigDir)

        if rootName == None:
            ret = QtWidgets.QMessageBox.information(self, "Change Name !", "Asset name does not match. !!",
                                                QtWidgets.QMessageBox.Ok)
            if ret == QtWidgets.QMessageBox.Ok:
                return
        # export
        self.pubFileList = {"pubDir": litRigDir, "itemExport": lightRigScript.itemExport,
                            "infoExport": self.litRigAssetInfoExport, "itemName": str(rootName)}

        # open window
        self.pubWindow.setFileName(litRigFileName, opt)
        self.pubWindow.show()

    def litRigAssetInfoExport(self):
        takeScript.takeExport(self.savefileList, "litRig")  # takeTypeList = ["globalTake", "localTake"]

        self.refresh()

        if not self.assetinfos.get("litRig"):
            self.assetinfos["litRig"] = {}

        if not self.assetinfos["litRig"].get("comment"):
            self.assetinfos["litRig"].update({"comment": {}})

        self.assetinfos["litRig"]["comment"].update({self.pubFileList["itemName"]: self.savefileText})

        takeScript.changeSaveTake(self.currentTake, self.assetinfos)

    def digienvExport(self, opt=""):
        digienvFileName, digienvDir = utilScript.itemPubDirCheck()

        if digienvFileName == None:
            print ("Error : Wrong Path !! ")
            return
        rootName = utilScript.itemRootAssetNameCheck(digienvDir, "digienv")

        if rootName == None:
            ret = QtWidgets.QMessageBox.information(self, "Change Name !", "Asset name does not match. !!",
                                                QtWidgets.QMessageBox.Ok)
            if ret == QtWidgets.QMessageBox.Ok:
                return
        # export
        self.pubFileList = {"pubDir": digienvDir, "itemExport": instanceScript.instanceExport,
                            "infoExport": self.digienvAssetInfoExport, "itemName": str(rootName)}

        # open window
        self.pubWindow.setFileName(digienvFileName, opt)
        self.pubWindow.show()

    def digienvAssetInfoExport(self):
        takeScript.takeExport(self.savefileList, "digienv", instanceInfo=self.digienvPointInfo)  # takeTypeList = ["globalTake", "localTake"]

        self.refresh()

        if not self.assetinfos.get("digienv"):
            self.assetinfos["digienv"] = {}

        if not self.assetinfos["digienv"].get("comment"):
            self.assetinfos["digienv"].update({"comment": {}})

        self.assetinfos["digienv"]["comment"].update({self.pubFileList["itemName"]: self.savefileText})

        takeScript.changeSaveTake(self.currentTake, self.assetinfos)

    #-------------------------------------------
    #    opt menu
    #-------------------------------------------

    def setStretch(self):
        """Stretch"""
        if  self.topFrame.isHidden():
            self.topFrame.show()
            return
        self.topFrame.hide()

    def contextMenuEvent(self, event):
        """contexMenu"""
        pos = event.globalPos()
        item = self.assetInfoTreeWidget.itemAt(event.pos() -self.assetInfoTreeWidget.pos()-QtCore.QPoint(10,28))
        
        if self.dataItemStruct["allTreeWidgetItemList"].get(item) == None:
            # select foucuset out
            treeWidget =  self.focusWidget()
            self.focusSet(treeWidget)
            self.selectItems={"prop": [], "cha": [], "env": [], "crowd": [], "litRig": [],"etc": [],
                              "aircraft": [], "plant": [], "rock": [], "set": [], "ship": [],
                              "structure": [], "vehicle": [], "weapon": [], "survey": []}
            return
        
        menu = QtWidgets.QMenu(self)   
        sepr1 = QtWidgets.QAction(self)
        sepr1.setSeparator(True)
        sepr2 = QtWidgets.QAction(self)
        sepr2.setSeparator(True)
        sepr3 = QtWidgets.QAction(self)
        sepr3.setSeparator(True)
        sepr4 = QtWidgets.QAction(self)
        sepr4.setSeparator(True)
        sepr5 = QtWidgets.QAction(self)
        sepr5.setSeparator(True)
         
        menu.addAction(sepr1)
        menu.addAction("Open Directory", lambda name = item: self.openItemDir(name))
        menu.addAction(sepr2)
        menu.addAction("Change Item", lambda name = item: self.changeItemDir(name))
        menu.addAction(sepr3)
        menu.addAction("Select Object", lambda name = item: self.selectObjectItem(name))
        menu.addAction(sepr4)
        menu.addAction("NameSpace Add", lambda name = item: self.nameSpaceAdd(name))
        menu.addAction("NameSpace Delete", lambda name = item: self.nameSpaceDelete(name))
        menu.addAction("Delete Object (nameSpace)", lambda name = item: self.deleteConnectObj(name))
        menu.addAction(sepr5)            
        menu.addAction("Comment", lambda name = item: self.itemComment(name))
        menu.setStyleSheet( "left: 20px;")
        menu.popup(pos)

    def focusSet(self, name):
        """focus Out"""
        assetViewList = set([self.propTreeWidget, self.chaTreeWidget, self.envTreeWidget, self.crowdTreeWidget,
                             self.litRigTreeWidget, self.etcTreeWidget, self.aircraftTreeWidget, self.plantTreeWidget,
                             self.rockTreeWidget, self.setTreeWidget, self.shipTreeWidget, self.structureTreeWidget,
                             self.vehicleTreeWidget, self.weaponTreeWidget, self.surveyTreeWidget,
                             self.landscapeTreeWidget])
        focusView = list(assetViewList - set([name]))
        
        for i in focusView:
            for item in i.selectedItems():
                item.setSelected(0)

    def itemComment(self, selectWidgetItem):
        widgetItem = [selectWidgetItem]
        
        notObject = []
        selectItme=""
        for item in widgetItem:
            if self.dataItemStruct["allTreeWidgetItemList"].get(item) == None:
                return

            allDate = self.dataItemStruct["allTreeWidgetItemList"][item]
            itemDir = self.assetinfos[allDate[0]]["objectList"][allDate[1]]

            self.textpubWindow.dataInfo = {"itemType": None, "itemName": None, "takeDir": None}
            
            self.textpubWindow.dataInfo["itemType"] = allDate[0]
            self.textpubWindow.dataInfo["itemName"] = allDate[1]
            self.textpubWindow.dataInfo["takeDir"] = self.currentTake

            self.textpubWindow.commentLabel.setText("%s ,  %s " % (allDate[0], allDate[1]))
            aa = self.textpubWindow.exec_()

    def textpup(self):
        itemType = self.textpubWindow.dataInfo["itemType"]
        itemName = self.textpubWindow.dataInfo["itemName"]

        text = str(self.textpubWindow.textEdit.toPlainText())

        if not self.assetinfos[itemType].get("comment"):
            self.assetinfos[itemType].update({"comment": {}})

        self.assetinfos[itemType]["comment"].update({itemName: text})
        
        takeScript.changeSaveTake(self.textpubWindow.dataInfo["takeDir"], self.assetinfos)
        self.textpubWindow.closeWindow()

        self.refresh()
        
    def openItemDir(self, selectWidgetItem):
        #rootItemTypes = ["camera", "model", "modelEnv","rigEnv","dummy", "mmDummy","modelDummy""rig",  "atom", "mmAtom", "geoCache","modelAtom","modelGeoCache","mmGeoCache", "simulGeoCache","frameRange","resolutionSet"]
          
        #isCheck
        widgetItem = []
        for rootType in self.rootItemTypes:
            if self.dataItemStruct["partTypeCheckBox"].get(rootType) == None:
                continue
            for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:  # check Box List
                if checkBoxItem.isChecked() == True:
                    widgetItem.append(self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][2])
                             
        # list
        if not widgetItem:
            widgetItem = [selectWidgetItem]
         
        notObject = []
        selectItme=""
        for item in widgetItem:
            if self.dataItemStruct["allTreeWidgetItemList"].get(item) == None:
                return
             
            allDate = self.dataItemStruct["allTreeWidgetItemList"][item]
            itemDir = self.assetinfos[allDate[0]]["objectList"][allDate[1]]

            if type(itemDir) == type([]):
                itemDir = itemDir[0]

            if "{" in itemDir:
                itemDir = itemDir.split("{")[0]

            if os.path.exists(itemDir):
                itempath = {}
                if not selectItme:  # select Path
                    if os.path.isfile(itemDir):  # "file"
                        cmd = "nautilus %s" % os.path.dirname(itemDir)
                        Popen(cmd, shell=True, stdout=PIPE)
                    else:
                        cmd = "nautilus %s" % itemDir
                        Popen(cmd, shell=True, stdout=PIPE)

    def changeItemDir(self, selectWidgetItem):
        # isCheck
        widgetItem = []
        for rootType in self.rootItemTypes:
            if self.dataItemStruct["partTypeCheckBox"].get(rootType) == None:
                continue

            for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:  # check Box List
                if checkBoxItem.isChecked() == True:
                    widgetItem.append(self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][2])
                             
        # list
        if not widgetItem:
            widgetItem = [selectWidgetItem]

        notObject = []
        selectItme = ""
        for item in widgetItem:
            if self.dataItemStruct["allTreeWidgetItemList"].get(item) == None:
                return

            allDate = self.dataItemStruct["allTreeWidgetItemList"][item]
            itemDir = self.assetinfos[allDate[0]]["objectList"][allDate[1]]

            if type(itemDir) == type([]):
                itemDir = itemDir[0]

            if "{" in itemDir:
                itemDir = itemDir.split("{")[0]

            if os.path.exists(itemDir):
                itempath = {}
                if not selectItme:  # select Path
                    if os.path.isfile(itemDir):  # "file"
                        selectItme = QtWidgets.QFileDialog.getOpenFileName(self, "FileName", os.path.dirname(itemDir), "All Files (*);;Text Files (*.txt)")
                        print (selectItme)

                    else:  # dir
                        options = QtWidgets.QFileDialog.DontResolveSymlinks | QtWidgets.QFileDialog.ShowDirsOnly
                        selectItme = QtWidgets.QFileDialog.getExistingDirectory(self, "Directory", os.path.dirname(itemDir), options)
                         
                if not selectItme : # Not Data
                    return
 
                if allDate[0] == "camera":
                    self.assetinfos[allDate[0]]["objectCheck"][allDate[1]] = {'lit': 1, 'rig': 1, 'fx': 1, 'lookdev': 1} 
                    self.assetinfos[allDate[0]]["updateList"][allDate[1]][0] = "%s" % selectItme
                    self.assetinfos[allDate[0]]["objectList"][allDate[1]][0] = "%s" % selectItme
                else:
                    self.assetinfos[allDate[0]]["objectCheck"][allDate[1]] = {'lit': 1, 'rig': 1, 'fx': 1, 'lookdev': 1}
                    self.assetinfos[allDate[0]]["updateList"][allDate[1]] = "%s" % selectItme
                    self.assetinfos[allDate[0]]["objectList"][allDate[1]] = "%s" % selectItme

            else:
                notObject.append(allDate[1])

        if notObject:
            txt = ""
            for i in notObject:
                txt += "%-30s" % i

            cmds.confirmDialog(title='Please! File Check!', message=txt, button=['ok'])

        globalCurrentTake, globalNewTake, globalNewNum = takeScript.versionUpTakeName("{0}/Take".format(self.shots[self.shotItem[self.shotClass]]), "take")
        takeScript.changeSaveTake(globalNewTake, self.assetinfos)
        self.refresh()
 
    def selectObjectItem(self, selectWidgetItem):
        widgetItem=[]
        # check !!
        for rootType in self.rootItemTypes:
            if self.dataItemStruct["partTypeCheckBox"].get(rootType) == None:
                continue
            for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:  # check Box List
                if checkBoxItem.isChecked() == True:
                    widgetItem.append(self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][2])
 
        # list
        if not widgetItem:
            widgetItem = [selectWidgetItem]

        selectItem = []
        for item in widgetItem:
            if self.dataItemStruct["allTreeWidgetItemList"].get(item) == None:
                return

            allDate = self.dataItemStruct["allTreeWidgetItemList"][item]

            selectItem.append(allDate[1])

        itemList = list(set(selectItem))

        selectItemsList = [x for x in itemList if cmds.ls(x)]
        cmds.select(selectItemsList)

    def nameSpaceAdd(self, selectWidgetItem):
        itemName = selectWidgetItem.text(1)

        if ":" in itemName:
            utilScript.nameSpaceAdd(itemName)

    def nameSpaceDelete(self, selectWidgetItem):
        itemName = selectWidgetItem.text(1)

        if ":" in itemName:
            utilScript.nameSpaceDelete(itemName)

    def deleteConnectObj(self, selectWidgetItem):
        itemName = selectWidgetItem.text(1)
        if ":" in itemName:
            utilScript.deleteConnectObj(itemName)

    def keyPressEvent(self, event):
        pass

    def closeAndSave(self):
        # {'currentType': 'env', 'name': u'mdSnowMt'}
        opt = {}
        opt['currentType'] = self.currentSelectItem['currentType']
        opt['currentName'] = self.currentSelectItem['name']
        # opt['currentClass'] =      self.currentSelectItem["class"]
        opt['topFrameisHidden'] = self.topFrame.isHidden()
        opt['matchmoveCheckNum'] = self.matchmoveCheckNum
        opt['layoutCheckNum'] = self.layoutCheckNum
        opt['modelCheckNum'] = self.modelCheckNum
        opt['rigCheckNum'] = self.rigCheckNum
        opt['lookdevCheckNum'] = self.lookdevCheckNum
        opt['title1CheckNum'] = self.title1CheckNum
        opt['title2CheckNum'] = self.title2CheckNum
        opt['title3CheckNum'] = self.title3CheckNum
        opt['propCheckBox'] = self.propCheckBox.isChecked()
        opt['chaCheckBox'] = self.chaCheckBox.isChecked()
        opt['envCheckBox'] = self.envCheckBox.isChecked()
        opt['crowdCheckBox'] = self.crowdCheckBox.isChecked()
        opt['litRigCheckBox'] = self.litRigCheckBox.isChecked()
        opt['litRigSetCheckBox'] = self.litRigSetCheckBox.isChecked()
        opt['etcCheckBox'] = self.etcCheckBox.isChecked()
        opt['aircraftCheckBox'] = self.aircraftCheckBox.isChecked()
        opt['plantCheckBox'] = self.plantCheckBox.isChecked()
        opt['rockCheckBox'] = self.rockCheckBox.isChecked()
        opt['setCheckBox'] = self.setCheckBox.isChecked()
        opt['shipCheckBox'] = self.shipCheckBox.isChecked()
        opt['structureCheckBox'] = self.structureCheckBox.isChecked()
        opt['vehicleCheckBox'] = self.vehicleCheckBox.isChecked()
        opt['weaponCheckBox'] = self.weaponCheckBox.isChecked()
        opt['surveyCheckBox'] = self.surveyCheckBox.isChecked()
        opt['landscapeCheckBox'] = self.landscapeCheckBox.isChecked()

        return opt 

    def importItem(self):
        TakeName = self.take_ComboBox.currentText()
        
        # get take
        chageItemType = {"atom": atomScript.atomImport,
                             "mmAtom": atomScript.atomImport,
                             "modelAtom": atomScript.atomImport,
                             "atomRender": atomScript.atomImport,
                             "geoCache": geoCacheScript.geoCacheImport,
                             "dummy": dummyScript.dummyImport,
                             "mmDummy": dummyScript.dummyImport,
                             "modelDummy": dummyScript.dummyImport,
                             "simulGeoCache": geoCacheScript.geoCacheImport,
                             "furGeoCache": geoCacheScript.geoCacheImport,
                             "clothGeoCache": geoCacheScript.geoCacheImport,
                             "mmGeoCache": geoCacheScript.geoCacheImport,
                             "modelGeoCache": geoCacheScript.geoCacheImport,
                             "geoCacheRender": geoCacheScript.geoCacheImport,
                             "almelbicAni": alembicScript.alembicImport,
                             "alembicModel": alembicScript.alembicImport,
                             "alembicRender": alembicScript.alembicImport,
                             "alembicFur": alembicScript.alembicImport,
                             "alembicCloth": alembicScript.alembicImport,
                             "alembicSimul": alembicScript.alembicImport,
                             "alembicMm": alembicScript.alembicImport,
                             "alembicLayout": alembicScript.alembicImport,
                             "alembicFx": alembicScript.alembicImport,
                             # "alembicRig"   : alembicScript_asset.alembicImport,
                             "alembicRig": alembicScript.alembicImport,
                             "rig": rigScript.rigImport,
                             "rigLow": rigScript.rigImport,
                             "rigMid": rigScript.rigImport,
                             "rigHi": rigScript.rigImport,
                             "rigXLow": rigScript.rigImport,
                             "rigXHi": rigScript.rigImport,
                             "mocapRig": rigScript.rigImport,
                             "camera": cameraScript.cameraImport,
                             "model": modelScript.modelImport,
                             "modelLow": modelScript.modelImport,
                             "modelMid": modelScript.modelImport,
                             "modelHi": modelScript.modelImport,
                             "modelXLow": modelScript.modelImport,
                             "modelXHi": modelScript.modelImport,
                             "frameRange": frameRangeScript.frameRangeImport,
                             "resolutionSet": resolutionScript.resolutionImport,
                             "rigEnv": rigScript.rigImport,
                             "litRig": lightRigScript.litRigImport,
                             "modelEnv": modelScript.modelImport,
                             "lookdev": lookdevScript.lookdevImport,
                             "digienv": instanceScript.instanceImport
                             }

        prj, widgetType, assetName, partType, sceneName, sceneDir = utilScript.getMayaFileList()
        for rootType in self.rootItemTypes:
            if  self.dataItemStruct["partTypeCheckBox"].get(rootType) == None:
                continue

            for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:  #check Box List
                if checkBoxItem.isChecked() == True:
                    itemList = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem]

                    # objList
                    objList = { itemList[1] : self.assetinfos[rootType]["objectList"][itemList[1]]}  #itemName: item, itemDir: dir 로 정해야 됨.

                    # reference/ import
                    type = itemList[4].currentText()

                    # rig / model type select
                    if itemList[0] in ["rig", "model","modelLow","modelMid","modelHi", "modelXLow","modelXHi",
                                       "rigLow", "rigMid","rigHi","rigXLow","rigXHi","alembicRig","mocapRig",
                                       "lookdev", "modelEnv", "rigEnv","camera","frameRange","resolutionSet",
                                       "dummy", "mmDummy","modelDummy", "almelbicAni", "alembicModel",
                                       "alembicRender", "alembicFur", "alembicCloth", "alembicSimul",
                                       "alembicMm", "alembicFx", "alembicRig"]:
                        subImportItemType = "None"
                    else:
                        subImportItemType = itemList[3].currentText()
                    #import
                    if subImportItemType == "model":
                        print ("model")
                        importItemFn = chageItemType["model"]
                        subObjList = {itemList[1]: self.assetinfos["model"]["objectList"][itemList[1]]}
                        importItemFn(subObjList, type, rootType)

                    elif subImportItemType == "rig":
                        print ("rig")
                        importItemFn = chageItemType["rig"]
                        subObjList = {itemList[1]: self.assetinfos["rig"]["objectList"][itemList[1]]}
                        importItemFn(subObjList, type, rootType)

                    # import Item
                    writeItemName = None

                    itemNum = itemList[5].value()

                    if "rig" == rootType or "model" == rootType:
                        # low/ mid / hi
                        lod = itemList[3].currentText()
                        importItemFn = chageItemType[rootType]
                        writeItemName = importItemFn(objList, type, rootType, lod, itemNum)
                    elif "alembicRig" == rootType or "alembicModel" == rootType:
                        # low/ mid / hi
                        lod = itemList[3].currentText()
                        importItemFn = chageItemType[rootType]
                        writeItemName = importItemFn(objList, type, rootType, itemNum, lod)
                    elif "digienv" == rootType:
                        importItemFn = chageItemType[rootType]
                        # type = import / reference
                        writeItemName = importItemFn(objList, type, rootType, itemNum, TakeName)

                    else:
                        importItemFn = chageItemType[rootType]
                        # type = import / reference
                        writeItemName = importItemFn(objList, type, rootType, itemNum)

                    # update Save
                    newobjList = {}
                    if writeItemName:
                        for i in writeItemName:
                            newobjList.update({i.split(".")[0]: self.assetinfos[rootType]["objectList"][itemList[1]]})
                        takeScript.takeUpdateCheck(newobjList, rootType, self.currentSelectItem["dir"])

                    if sceneDir and sceneDir.split("/")[3] in ["seq"] and rootType in ["model"]:
                        modelScript.exportTakeAssets(newobjList, ["globalTake", "localTake"], "model")
                        self.refreshed.emit()

                        if sceneDir and sceneDir.split("/")[3] in ["seq"] and rootType in ["rig"]:
                            rigData = rigScript.assetInfoExport(newobjList)
                            self.refreshed.emit()

        self.refresh()
