# -*- coding:utf-8 -*-
'''
Created on Mar 31, 2015

@author: m83
'''

import os, glob, re, shutil, time
import configparser
import json
from subprocess import *

# from .cacheExport_module.pyside2_moduleImport import *
# from .cacheExport_module.cacheExport_moduleImport import *
# from .cacheExport_module.cacheExport_moduleImport import APPNAME
# from .cacheExport_module.cacheExport_moduleImport import ABCIMPORTOPT

print("="*50)
print("DEBUG: CACHEEXPORT LOADING STARTED")
print("="*50)
import os
print("DEBUG: Starting cacheExport module imports...")
print(f"DEBUG: NOAH_ROOT environment variable: '{os.environ.get('NOAH_ROOT', 'NOT SET')}'")
print(f"DEBUG: Current working directory: {os.getcwd()}")
print(f"DEBUG: cacheExport.py file location: {__file__}")
print("="*50)
from cacheExport_module.pyside2_moduleImport import *
from cacheExport_module.cacheExport_moduleImport import *
print("DEBUG: cacheExport module imports completed")
from cacheExport_module.cacheExport_moduleImport import ABCIMPORTOPT
from script import usdScript
from script import mayaHairScript
import importlib
from functools import partial
from script import convert_byte_to_string
from script import multi_camExport

try:
    importlib.reload(atomScript)
    importlib.reload(geoCacheScript)
    importlib.reload(usdScript)
    importlib.reload(yetiCacheScript)
    importlib.reload(alembicScript)
    importlib.reload(assScript)
    importlib.reload(cameraScript)
    importlib.reload(dummyScript)
    importlib.reload(mayaScript)
    importlib.reload(mayaHairScript)
    importlib.reload(renderLayerScript)
    importlib.reload(rigScript)
    importlib.reload(modelScript)
    importlib.reload(frameRangeScript)
    importlib.reload(resolutionScript)
    importlib.reload(modelEnvScript)
    importlib.reload(vrayProxyScript)
    importlib.reload(lookdevScript)
    importlib.reload(fxScript)
    importlib.reload(tractorJobScript)
    importlib.reload(convert_byte_to_string)
    importlib.reload(shotgunScript)
    importlib.reload(utilScript)
    importlib.reload(dataScript)
    importlib.reload(referenceSettings)
    importlib.reload(takeScript)
    importlib.reload(asstesExport)
    importlib.reload(commentWindow)
    importlib.reload(instanceScript)
except:
    pass

# from QtTopUiLoader import *
# from modal_widget import *
import QtTopUiLoader
import modal_widget

importlib.reload(modal_widget)

#from . import cacheExport_style.qtmodern.styles as qm_styles
#from . import cacheExport_style.qtmodern.windows as qm_windows
import cacheExport_style.qtmodern.styles as qm_styles
import cacheExport_style.qtmodern.windows as qm_windows



class DataStruct(object):  # TreeWidget Data
    def __init__(self, parent=None):
        self.itemClass = {}
        self.itemClass["treeItem"] = {}
        self.itemClass["checkBox"] = {}
        self.itemClass["comboBox1"] = {}
        self.itemClass["comboBox2"] = {}

        self.itemClass["allCheckBoxItemList"] = {}
        self.itemClass["allTreeWidgetItemList"] = {}
        self.itemClass["partTypeCheckBox"] = {}
        self.itemClass["allItemClass"] = {}
        self.itemClass["rootClass"] = {}  # { name : qobject name, ..}
        self.itemClass["subClass"] = {}
        self.itemClass["itemClass"] = {}

    @property
    def rootClass(self):
        return self.itemClass["rootClass"]

    @rootClass.setter
    def rootClass(self, data):
        self.itemClass["rootClass"].update(data)

    def setList(self, itemList):
        for i in itemList:
            # if str(type(i) ) == "<class 'PyQt5.QtWidgets.QCheckBox'>":
            # if str(type(i)) == "<type 'PySide2.QtWidgets.QCheckBox'>":
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
                classType = "treeItem"
            elif isinstance(item, QtWidgets.QCheckBox):
                classType = 'checkBox'
            elif isinstance(item, QtWidgets.QComboBox):
                classType = 'comboBox'

            if classType == 'comboBox':
                if item.objectName() == "opt1":
                    classType = "comboBox1"
                    if item.count() == 0:
                        if rootType in ["rig", "model", "alembicRig", "alembicModel"]:
                            # item.addItems(["None", "Low", "Mid","Hi","XLow","XHi", "Mocap", "PROXY", "miarmy"])
                            item.addItems(["None", "PROXY", "LOW", "MID", "HI", "XLOW", "XHI", "MOCAP", "miarmy"])
                        else:
                            item.addItems(["None", "model", "rig"])
                        item.setFont(font)
                else:
                    classType = "comboBox2"
                    if item.count() == 0:
                        if rootType in ["resolutionSet", "lightRig"]:
                            item.addItems(["import"])
                            item.setFont(font)
                        elif rootType in ["camera"]:
                            item.addItems(["import", "alembic"])
                            item.setFont(font)
                        elif rootType in ["frameRange"]:
                            item.addItems(["JustFrame", "FullFrame"])
                            item.setFont(font)
                        elif rootType in ["model", "modelEnv", "dummy", "mmDummy", "layoutDummy", "modelDummy",
                                          "mayaLayoutDummy", "lookdev", "digienv"]:
                            item.addItems(["reference", "import"])
                            item.setFont(font)
                        elif re.match("maya", rootType):
                            item.addItems(["reference", "import"])
                            item.setFont(font)
                        elif rootType == "mayaHair":
                            item.addItems(["reference", "import"])
                            item.setFont(font)
                        elif rootType in ["rig", "rigEnv"]:
                            # item.addItems(["reference", "import", "lookdevproxy", "instance"])
                            item.addItems(["reference", "import", "instance"])
                            item.setFont(font)
                        elif rootType in ["ass", "vdbFx"]:
                            item.addItems(["import"])
                            item.setFont(font)
                        else:
                            item.addItems(["None", "reference", "import"])
                            item.setFont(font)
            # set Item
            if item not in set(self.itemClass[classType]):
                self.itemClass[classType][item] = []

            if item in set(self.itemClass[classType]):
                if itemList[item] not in set(self.itemClass[classType][item]) and itemList[
                    item] is not None:  # current item
                    self.itemClass[classType][item].append(itemList[item])

            if itemList[item] is not None:
                for selRootItem in set(self.itemClass[classType]):
                    # if item in self.itemClass[classType][selRootItem]: # allitem
                    if item in set(self.itemClass[classType][selRootItem]):  # allitem
                        if itemList[item] not in set(self.itemClass[classType][selRootItem]):
                            self.itemClass[classType][selRootItem].append(itemList[item])


# class updateWindow(QtWidgets.QWidget):
class noteWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, text=None):
        super(noteWindow, self).__init__(parent)
        self.parent = parent
        self.setStyleSheet("border: None;  font: 15px; color : yellow ; background-color : rgb(57,61,72) ; ")

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.label = QtWidgets.QLabel()
        self.label.setText("%s" % text)  # update file name

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
        self.setWindowTitle("Note Window")
        self.resize(300, 200)

        self.setLayout(QtWidgets.QVBoxLayout())

        font = QtGui.QFont()
        font.setPointSize(10)
        fontBold = QtGui.QFont()
        fontBold.setPointSize(10)
        fontBold.setBold(1)

        self.textEdit = QtWidgets.QTextEdit()

        self.commentLabel = QtWidgets.QLabel("Note")

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
        size   = self.geometry()
        self.move((screen.width()  - size.width())  / 2,
                  (screen.height() - size.height()) / 2)
    # emit
    def textpup2(self):
        self.textpup.emit()

    def closeWindow(self):
        self.close()

class MainWindow(QtWidgets.QMainWindow):
    # def __init__(self, parent = getMayaWindow()):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        # load ui
        self.filepath = os.path.abspath(__file__ + "/../")
        if self.filepath.startswith('/home/m83/dev4th'):
            self.filepath = self.filepath.replace('/home/m83/dev4th', '/core/TD/hyunil_dev/dev4th')
        QtTopUiLoader.UiLoader().loadUi(self.filepath + "/cacheExportUI.ui", self)

        # get config
        typeConfig = configparser.ConfigParser()
        typeConfig.read(self.filepath + "/config/typeConfig.ini")
        self.ASSETS_TYPE = typeConfig.options("assets")

        self.setObjectName("Cache Export")
        self.resize(1300, 1200)
        self.textpubWindow = textpubWindow()

        # emit
        self.textpubWindow.textpup.connect(self.textpup)

        self.prj_ComboBox.activated[int].connect(self.prjSet)
        self.type_ComboBox.activated[int].connect(self.type)

        # Use only currentItemChanged to avoid double execution on mouse click
        self.sqc_TreeWidget.currentItemChanged.connect(lambda current, previous: self.sqc(current) if current and hasattr(self, 'commentWindow') else None)

        # Use only currentItemChanged to avoid double execution on mouse click  
        self.shot_TreeWidget.currentItemChanged.connect(lambda current, previous: self.shot(current) if current and hasattr(self, 'commentWindow') else None)
        # self.shot_TreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(lambda: self.shot(self.shot))


        self.take_ComboBox.activated[int].connect(self.takeChange)
        
        # Add click event for copying item name to clipboard
        self.assetInfoTreeWidget.itemClicked.connect(self.copyItemNameToClipboard)

        # self.shotTabClearSelection_pushButton.clicked.connect(lambda type="selection": self.shotTabClear(type))
        self.shotTabClearSelection_pushButton.clicked.connect(lambda: self.shotTabClear("selection"))

        # self.shotTabClearAll_pushButton.clicked.connect(lambda type="all": self.shotTabClear(type))
        self.shotTabClearAll_pushButton.clicked.connect(lambda: self.shotTabClear("all"))

        # tractor
        self.openTractorBtn.clicked.connect(self.openTractor)

        # atom
        self.atomSetAllLoad_PushButton.clicked.connect(
            # lambda name=self.atomSetAllLoad_PushButton: self.atomLoadSet(name))
            lambda: self.atomLoadSet(self.atomSetAllLoad_PushButton))

        self.atomMocapSetLoad_PushButton.clicked.connect(
            # lambda name=self.atomMocapSetLoad_PushButton: self.atomLoadSet(name))
            lambda: self.atomLoadSet(self.atomMocapSetLoad_PushButton))

        self.atomSetSelectLoad_PushButton.clicked.connect(
            # lambda name=self.atomSetSelectLoad_PushButton: self.atomLoadSet(name))
            lambda: self.atomLoadSet(self.atomSetSelectLoad_PushButton))

        self.atomExport_PushButton.clicked.connect(self.atomExport)
        self.atomExportFarm_PushButton.clicked.connect(lambda: self.noahExport("atom", "farm", self.atom_TreeWidget))

        # GeoCache
        self.geoCacheSetAllLoad_PushButton.clicked.connect(
            # lambda name=self.geoCacheSetAllLoad_PushButton: self.geoCacheLoadSet(name))
            lambda: self.geoCacheLoadSet(self.geoCacheSetAllLoad_PushButton))

        self.geoCacheSetLoad_PushButton.clicked.connect(
            # lambda name=self.geoCacheSetLoad_PushButton: self.geoCacheLoadSet(name))
            lambda: self.geoCacheLoadSet(self.geoCacheSetLoad_PushButton))

        self.geoCacheExport_Pushbutton.clicked.connect(self.geoCacheExport)
        self.loadMeshPushButton.clicked.connect(self.loadMesh)

        self.renderFarm2PushButtom.clicked.connect(self.renderFarmGeoCache)
        self.renderFarm2PushButtom.hide()

        # alembic
        self.alembic_step_label.hide()
        self.alembic_opt_lineEdit.hide()
        self.alembic_TreeWidget.setColumnWidth(0, 347)
        self.alembicGeoSetLoad_PushButton.clicked.connect(
            # lambda name=self.alembicGeoSetLoad_PushButton: self.alembicLoadMesh(name))
            lambda: self.alembicLoadMesh(self.alembicGeoSetLoad_PushButton))

        self.alembicCurveSetLoad_PushButton.clicked.connect(
            # lambda name=self.alembicCurveSetLoad_PushButton: self.alembicLoadMesh(name))
            lambda: self.alembicLoadMesh(self.alembicCurveSetLoad_PushButton))

        self.alembicLoadMeshPushButton.clicked.connect(
            # lambda name=self.alembicLoadMeshPushButton: self.alembicLoadMesh(name))
            lambda: self.alembicLoadMesh(self.alembicLoadMeshPushButton))

        self.alembicSceneSetLoad_pushButton.clicked.connect(
            # lambda name=self.alembicSceneSetLoad_pushButton: self.alembicLoadMesh(name))
            lambda: self.alembicLoadMesh(self.alembicSceneSetLoad_pushButton))

        self.alembicExport_PushButton1.clicked.connect(self.alembicExport)
        self.renderFarm3PushButtom.clicked.connect(self.renderFarmAbc)

        # Yeti
        self.yetiExportLocal_dev_PushButton.clicked.connect(
            lambda: self.noahExport("yetiCache", "local", self.yeti_TreeWidget))

        self.yetiCacheSetAllLoad_PushButton.clicked.connect(
            # lambda name=self.yetiCacheSetAllLoad_PushButton: self.yetiCacheLoadSet(name))
            lambda: self.yetiCacheLoadSet(self.yetiCacheSetAllLoad_PushButton))

        self.yetiExport_PushButton.clicked.connect(self.yetiCacheExport)
        self.label_13.hide()
        self.comboBox.hide()
        self.yetiCacheFrameRange_combo.hide()
        self.yetiExportLocal_dev_PushButton.hide()
        self.renderFarm4PushButtom.hide()

        self.renderFarm4PushButtom.clicked.connect(self.renderFarmYeti)

        # Ass
        self.assLoadMeshPushButton.clicked.connect(lambda: self.setLoadMesh("ass"))
        self.assExportLocal_PushButton.clicked.connect(lambda: self.noahExport("ass", "local", self.ass_TreeWidget))
        self.assExportFarm_PushButton.clicked.connect(lambda: self.noahExport("ass", "farm", self.ass_TreeWidget))

        # Maya
        self.mayaLoadMesh_pushButton.clicked.connect(lambda: self.setLoadMesh("maya"))
        self.mayaExportFarm_pushButton.hide()
        self.mayaUse_label.hide()
        self.mayaUse_comboBox.hide()
        self.mayaAlembic_checkBox.hide()
        self.mayaFrameRange_combo.hide()
        # self.mayaExportFarm_pushButton.clicked.connect(lambda :self.assExport("maya", "farm", self.maya_TreeWidget))
        # self.mayaExportLocal_pushButton.clicked.connect(lambda: self.noahExport("maya", "local", self.maya_TreeWidget))
        self.mayaExportLocal_pushButton.clicked.connect(lambda: self.noahExport("maya", "local", self.maya_TreeWidget))
        self.mayaExportHair_pushButton.clicked.connect(lambda: self.exportHair())
        self.clarisseExportLocal_pushButton.clicked.connect(
            lambda: self.noahExport("clarisse", "local", self.clarisse_TreeWidget))

        # Instance
        self.instance_TreeWidget.setColumnWidth(0, 347)

        self.instanceSetLoad_PushButton.clicked.connect(
            # lambda name=self.instanceSetLoad_PushButton: self.setLoadInstance(name))
            lambda: self.setLoadInstance(self.instanceSetLoad_PushButton))

        self.instanceExport_PushButton.clicked.connect(
            lambda: self.noahExport("instance", "local", self.instance_TreeWidget))

        # RenderLayer
        self.renderLayerLoad_pushButton.clicked.connect(self.setLoadRenderLayer)
        self.renderLayerExportFarm_pushButton.clicked.connect(
            lambda: self.noahExport("renderlayer", "farm", self.renderLayer_TreeWidget))
        self.renderLayerExportLocal_pushButton.hide()

        # Clarisse
        self.clarisse_TreeWidget.setColumnWidth(0, 347)
        self.clarisseLoadItem_pushButton.clicked.connect(lambda: self.setLoadClarisse("sel"))
        self.clarisseEnvItem_pushButton.clicked.connect(lambda: self.setLoadClarisse("ENV"))

        # Camera
        self.camExport_PushButton.clicked.connect(self.camExport)
        self.frameRangePushButton.clicked.connect(self.frameRangeExport)
        self.resolutionPushButton.clicked.connect(self.resolutionExport)
        self.dummyExportPushButton.clicked.connect(self.dummyExport)
        self.dummyExportPushButton.hide()
        self.label_3.hide()
        self.modelEnvPushButton.clicked.connect(self.modelEnvExport)
        self.lookdevEnvPushButton.clicked.connect(self.lookdevEnvExport)
        self.proxyAutoConnectShaderPushButton.clicked.connect(self.proxyAutoConnectShader)

        # Import option
        self.importItemPushButton.clicked.connect(self.importItem)
        self.checkPushButton.clicked.connect(self.checkSet)

        self.autoSetPushButton.clicked.connect(self.autoSet)
        self.deleteItemPushButton.clicked.connect(self.deleteItem)

        # self.envCheckBox.stateChanged[int].connect(self.envCheck)
        # self.assetsCheckBox.stateChanged[int].connect(self.assetsCheck)
        # self.matchMoveCacheCheckBox.stateChanged[int].connect(self.matchMoveCacheCheck)
        # self.layoutCacheCheckBox.stateChanged[int].connect(self.layoutCacheCheck)
        # self.modelCacheCheckBox.stateChanged[int].connect(self.modelCacheCheck)
        #
        # self.aniCacheCheckBox.stateChanged[int].connect(self.aniCacheCheck)
        # self.simulCacheCheckBox.stateChanged[int].connect(self.simulCacheCheck)
        # self.renderCacheCheckBox.stateChanged[int].connect(self.renderCacheCheck)
        # self.fxCacheCheckBox.stateChanged[int].connect(self.fxCacheCheck)
        self.envCheckBox.stateChanged[int].connect(self.envCheck)
        self.assetsCheckBox.stateChanged[int].connect(self.assetsCheck)
        self.matchMoveCacheCheckBox.stateChanged[int].connect(self.matchMoveCacheCheck)
        self.layoutCacheCheckBox.stateChanged[int].connect(self.layoutCacheCheck)
        self.modelCacheCheckBox.stateChanged[int].connect(self.modelCacheCheck)
        self.aniCacheCheckBox.stateChanged[int].connect(self.aniCacheCheck)
        self.simulCacheCheckBox.stateChanged[int].connect(self.simulCacheCheck)
        self.renderCacheCheckBox.stateChanged[int].connect(self.renderCacheCheck)
        self.fxCacheCheckBox.stateChanged[int].connect(self.fxCacheCheck)

        self.stretchPushButton.clicked.connect(self.setStretch)
        self.totalTake_checkBox.stateChanged[int].connect(self.takeChange)

        # self.title1CheckBox.stateChanged[int].connect(lambda num, name=self.title1CheckBox: self.titleCheck(num, name))
        self.title1CheckBox.stateChanged[int].connect(lambda num: self.titleCheck(num, self.title1CheckBox))

        # self.title2CheckBox.stateChanged[int].connect(lambda num, name=self.title2CheckBox: self.titleCheck(num, name))
        self.title2CheckBox.stateChanged[int].connect(lambda num: self.titleCheck(num, self.title2CheckBox))

        # self.title3CheckBox.stateChanged[int].connect(lambda num, name=self.title3CheckBox: self.titleCheck(num, name))
        self.title3CheckBox.stateChanged[int].connect(lambda num: self.titleCheck(num, self.title3CheckBox))

        self.typeCheckPushButton.clicked.connect(self.typeCheck)
        self.refreshPushButton.setIcon(QtGui.QIcon("{}/icon/refresh.png".format(self.filepath)))
        self.refreshPushButton.clicked.connect(self.refresh)
        self.meshReplace.clicked.connect(self.meshreplaceOpen)

        self.shotPushButton.pressed.connect(lambda: self.setShot())
        self.assetsPushButton.pressed.connect(lambda: self.setAsset())

        self.commentPushButton.pressed.connect(
            # lambda name=self.commentPushButton: self.changeStackedCommentLayout(name))
            lambda: self.changeStackedCommentLayout(self.commentPushButton))

        # self.exportPushButton.pressed.connect(lambda name=self.exportPushButton: self.changeStackedExportLayout(name))
        self.exportPushButton.pressed.connect(lambda: self.changeStackedExportLayout(self.exportPushButton))

        self.dataStruct = DataStruct(self)
        self.dataItemStruct = self.dataStruct.itemClass

        # 0=unchecked , 1=pariallychecked, 2=checked - Change default to checked
        self.envCheckNum = 0  # Changed to checked (0 means checked in this context)
        self.assetsCheckNum = 0  # Changed to checked
        self.matchMoveCacheCheckNum = 0  # Changed to checked
        self.layoutCacheCheckNum = 0  # Changed to checked
        self.modelCacheCheckNum = 0  # Changed to checked
        self.aniCacheCheckNum = 0  # Changed to checked
        # self.postvizCacheCheckNum = 2
        self.simulCacheCheckNum = 0  # Changed to checked
        self.renderCacheCheckNum = 0  # Changed to checked
        self.fxCacheCheckNum = 0  # Changed to checked

        self.title1CheckNum = 0  # Changed to checked
        self.title2CheckNum = 0  # Changed to checked
        self.title3CheckNum = 0  # Already checked

        # assetsView
        self.assetsView = asstesExport.assetsView(self)
        self.frame.widget(1).setLayout(QtWidgets.QHBoxLayout())
        self.frame.widget(1).layout().addWidget(self.assetsView)

        self.appStackedWidget_1.setCurrentIndex(0)
        self.assetsView.appStackedWidget_1.setCurrentIndex(0)

        # self.assetsView.setParent(self)
        self.assetsView.refreshed.connect(self.refresh)

        self.init()
        self.currentPrj = ""
        self.commentWindow = commentWindow.stackeStackedWidget(self.currentPrj, str(self.type_ComboBox.currentText()))
        self.stackeStackedWidget.insertWidget(0, self.commentWindow)
        self.assetsView.changeStackedLayoutMode(0)

        self.sqc_TreeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        self.shot_TreeWidget.sortItems(0, QtCore.Qt.AscendingOrder)

        font = QtGui.QFont()
        font.setPointSize(10)
        self.stretchPushButton.setFont(font)

        self.stackeStackedWidget.setCurrentIndex(1)

        self.take_ComboBox.setStyleSheet(
            "QComboBox#%s {color: yellow;background-color:transparent;} #%s:hover {background-color: rgb(44,45,51);}" % (
            self.take_ComboBox.objectName(), self.take_ComboBox.objectName()))
        self.importItemPushButton.setStyleSheet("QPushButton#importItemPushButton {background-color: rgb(30,100,30);}")
        self.optFrame.layout().setAlignment(QtCore.Qt.AlignLeft)
        self.stretchPushButton.setStyleSheet(
            "#stretchPushButton {background-color: rgba(0,0,0,0%); border-radius:0px;} #stretchPushButton:hover {background-color: rgb(105,114,123);}")
        # self.shotTabWidget.setStyleSheet  ( "#shotTabWidget{ background-color: rgba(0,0,0,0%); } ")
        self.shotTabWidget.setStyleSheet(
            "#shotTabWidget::pane { background: transparent; border:0; } QTabWidget::tab-bar { width:30000px;} QTabBar { background: #383838; font-size:11pt;}")

        self.frame.layout().setSpacing(0)
        self.topMenuFrame.setStyleSheet("background-color:rgb(57,61,72)")
        self.shotPushButton.setStyleSheet("background-color:rgb(44,45,51)")
        self.assetsPushButton.setStyleSheet("background-color:rgb(37,41,52)")

        self.exportFrame.layout().setAlignment(QtCore.Qt.AlignTop)

        self.lod_ComboBox.setStyleSheet("#lod_ComboBox{color:orange;}")

        self.prj_ComboBox.setStyleSheet(
            "#prj_ComboBox {border: 2px solid orange; border-radius: 10px; padding: 1px -20px 1px 40px; min-width: 1em;}::down-arrow { background-color:transparent;border: 1px solid orange;}")
        self.prj_ComboBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.type_ComboBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.take_ComboBox.setFocusPolicy(QtCore.Qt.NoFocus)

        self.setStyleSheet(
            "QMainWindow {border-image: url(%s/icon/background-blur.png)} QToolTip { font-size:15px; font: italic; }" % self.filepath)

        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
        
        # Add USD Tab
        self.add_usd_tab()

    def init(self):
        self.setWindowIcon(QtGui.QIcon("{}/icon/noah.png".format(self.filepath)))
        # set project
        self.proj = {}
        self.shotClass = ''
        # self.proj = cameraExportScript.projectList()
        self.proj = utilScript.projectList()
        prj = list(self.proj.keys())
        prj.sort()
        self.prj_ComboBox.addItems(prj)

        # set part
        noahData = dataScript.NoahData()
        # self.partType = ["matchmove", "model", "layout", "ani", "postviz", "lookdev", "lit", "litRig", "fx", "rig", "dyn", "finalize", "cloth", "fur", "hair", "hairSim", "furSim", "clothSim", "comp"]
        self.partType = noahData.partType
        self.type_ComboBox.addItems(self.partType)

        self.rootItemTypes = noahData.rootItem()

        self.prjSet()

        if os.path.isfile("/home/m83/maya/cacheExport.json"):
            with open("/home/m83/maya/cacheExport.json", 'r') as f:
                jsonOpt = json.load(f)

            prj_num = self.prj_ComboBox.findText(jsonOpt["cacheOpt"]["prj"])
            self.prj_ComboBox.setCurrentIndex(prj_num)

            currentSceneFile = cmds.file(q=True, sn=True)

            checkPartName = 0
            for partName in self.partType:
                if "/{}/".format(partName) in currentSceneFile:
                    type_num = self.type_ComboBox.findText(partName)
                    checkPartName = 1
            if not checkPartName:
                type_num = self.type_ComboBox.findText(jsonOpt["cacheOpt"]["type"])

            self.type_ComboBox.setCurrentIndex(type_num)
            self.prjSet()

            # set seq
            try:
                sqc_item = self.sqc_TreeWidget.findItems(jsonOpt["cacheOpt"]["seqc"],
                                                         QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)[0]
                self.sqc_TreeWidget.setCurrentItem(sqc_item)
                self.sqc(sqc_item)
            except:
                pass

            # set shot
            try:
                shot_item = self.shot_TreeWidget.findItems(jsonOpt["cacheOpt"]["shot"],
                                                           QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)[0]
                self.shot_TreeWidget.setCurrentItem(shot_item)
                self.shot(shot_item)
            except:
                pass

            # set cache check option
            try:
                self.envCheckNum = jsonOpt["cacheOpt"]["envCheckNum"]
                self.assetsCheckNum = jsonOpt["cacheOpt"]["assetsCheckNum"]
                self.matchMoveCacheCheckNum = jsonOpt["cacheOpt"]["matchMoveCacheCheckNum"]
                self.layoutCacheCheckNum = jsonOpt["cacheOpt"]["layoutCacheCheckNum"]
                self.modelCacheCheckNum = jsonOpt["cacheOpt"]["modelCacheCheckNum"]
                self.aniCacheCheckNum = jsonOpt["cacheOpt"]["aniCacheCheckNum"]
                # self.postvizCacheCheckNum =     int(str(jsonOpt["cacheOpt"]["postvizCacheCheckNum"]))
                self.simulCacheCheckNum = jsonOpt["cacheOpt"]["simulCacheCheckNum"]
                self.renderCacheCheckNum = jsonOpt["cacheOpt"]["renderCacheCheckNum"]
                self.fxCacheCheckNum = jsonOpt["cacheOpt"]["fxCacheCheckNum"]

                self.envCheckBox.setChecked(self.envCheckNum)
                self.assetsCheckBox.setChecked(self.assetsCheckNum)
                self.matchMoveCacheCheckBox.setChecked(self.matchMoveCacheCheckNum)
                self.layoutCacheCheckBox.setChecked(self.layoutCacheCheckNum)
                self.modelCacheCheckBox.setChecked(self.modelCacheCheckNum)
                self.aniCacheCheckBox.setChecked(self.aniCacheCheckNum)
                # self.postvizCacheCheckBox.setChecked(self.postvizCacheCheckNum)
                self.simulCacheCheckBox.setChecked(self.simulCacheCheckNum)
                self.renderCacheCheckBox.setChecked(self.renderCacheCheckNum)
                self.fxCacheCheckBox.setChecked(self.fxCacheCheckNum)

                self.title1CheckNum = jsonOpt["cacheOpt"]["title1CheckNum"]
                self.title2CheckNum = jsonOpt["cacheOpt"]["title2CheckNum"]
                self.title3CheckNum = jsonOpt["cacheOpt"]["title3CheckNum"]

                self.title1CheckBox.setChecked(self.title1CheckNum)
                self.title2CheckBox.setChecked(self.title2CheckNum)
                self.title3CheckBox.setChecked(self.title3CheckNum)

                self.showHideItemSet()
                self.titlecheckSet()
            except:
                pass

    def setShot(self):
        self.frame.setCurrentIndex(0)
        # self.shotgunLoad = ShotgunLoad(cacheExportWin)
        # self.shotgunLoad.setShotgun()

        # setShotgun(self)

    def setAsset(self):
        self.frame.setCurrentIndex(1)
        # self.shotgunListWidget.clear()

    # prj_ComboBox
    def prjSet(self):
        self.shot_TreeWidget.clear()
        self.assetsView.setTypeName(self.type_ComboBox.currentText())

        # self.sqcSet()
        # sqc
        # def sqcSet(self):
        self.assetInfoTreeWidget.clear()
        self.sqc_TreeWidget.clear()

        if not self.prj_ComboBox.currentText():
            return

        self.seqc = utilScript.sequence(self.proj[str(self.prj_ComboBox.currentText())])
        seqc = list(self.seqc.keys())
        self.seqcItem = {}
        for item in seqc:
            seqcItem = QtWidgets.QTreeWidgetItem(self.sqc_TreeWidget, [item])
            self.seqcItem[seqcItem] = item

        # assetsView
        self.assetsView.setPrjName(self.prj_ComboBox.currentText())

    # type_ComboBox
    def type(self):
        # set asset QStackedWidget
        self.assetsView.setTypeName(self.type_ComboBox.currentText())

        # set shot QStackedWidget
        name = self.type_ComboBox.currentText()
        type = {"model": 0, "rig": 0, "lit": 1, "lookdev": 1, "dyn": 0, "finalize": 0, "cloth": 0, "fur": 0, "hair": 0,
                "clothSim": 0}
        if "%s" % str(name) in type:
            self.subExportStackedWidget.setCurrentIndex(type[str(name)])
        else:
            self.subExportStackedWidget.setCurrentIndex(0)

    # sqc_TreeWidget
    def sqc(self, name):
        self.assetInfoTreeWidget.clear()
        self.shot_TreeWidget.clear()

        self.shots = utilScript.shotList(self.seqc[self.seqcItem[name]])

        shot = list(self.shots.keys())  # self.prj_ComboBox.currentIndex()

        self.shotItem = {}
        for item in shot:
            shotItem = QtWidgets.QTreeWidgetItem(self.shot_TreeWidget, [item])
            self.shotItem[shotItem] = item

        # assetsView
        self.assetsView.setSeqcName(self.seqcItem[name])
        # self.setWindowTitle(self.seqc[self.seqcItem[name]])
        self.setWindowTitle("Ark - %s" % self.seqc[self.seqcItem[name]])
        self.stretchPushButton.setText(self.seqc[self.seqcItem[name]])

    # shot_TreeWidget
    def shot(self, name, takeIndex=0):

        self.currentPrj = self.shots[self.shotItem[name]]
        self.shotClass = name

        self.assetInfoTreeWidget.clear()
        self.take_ComboBox.clear()
        self.atom_TreeWidget.clear()
        self.geoCache_TreeWidget.clear()
        # Folder check
        # self.camList(name)
        # self.dummyList(name)

        # take
        self.setTake(name)
        if not takeIndex == 0:
            self.take_ComboBox.setCurrentIndex(takeIndex)
        self.assetInfoList(name)

        self.showHideItemSet()
        self.titlecheckSet()

        # assetsView
        self.assetsView.setShotName(self.shotItem[name])

        # commentWindow
        self.commentWindow.setPrjDir(self.shots[self.shotItem[name]], self.type_ComboBox.currentText())
        try:
            self.setWindowTitle("Ark - %s/%s" % (self.shots[self.shotItem[name]], self.type_ComboBox.currentText()))
            self.stretchPushButton.setText(self.shots[self.shotItem[name]])
        except:
            return

        # shotgun List
        # self.shotgunLoad = ShotgunLoad(cacheExportWin)
        # self.shotgunLoad.setShotgun()

        # setShotgun(self)

    def shotTabClear(self, type):
        tabObj = self.shotTabWidget
        index = tabObj.currentIndex()
        tabName = str(tabObj.tabText(index))
        treeWidgetName = tabName[0].lower() + tabName[1:] + "_TreeWidget"
        treeWidget = self.findChild(QtWidgets.QTreeWidget, treeWidgetName)
        if type == "all":
            treeWidget.clear()
        if type == "selection":
            root = treeWidget.invisibleRootItem()
            itemList = treeWidget.selectedItems()
            for i in itemList:
                root.removeChild(i)

    def setTake(self, name):
        self.TakeList = {}
        self.currentTake = ""
        currentType = ""
        TakeName = ""

        try:
            currentType = str(self.type_ComboBox.currentText())
            self.TakeList, self.justTakeList, self.currentTake, TakeName = takeScript.checkTakeName(
                self.shots[self.shotItem[name]], currentType)

        except:
            self.take_ComboBox.clear()
            return

        Takelist = list(self.TakeList.keys())
        Takelist.sort(reverse=True)
        self.take_ComboBox.clear()
        self.take_ComboBox.addItems(Takelist)

    def autoSet(self):
        # prj, sqc, shot, partType, sceneName, sceneDir = itemScript.getMayaFileList()
        prj, sqc, shot, partType, sceneName, sceneDir = utilScript.getMayaFileList()

        prj_num = self.prj_ComboBox.findText("%s" % prj)
        self.prj_ComboBox.setCurrentIndex(prj_num)

        type_num = self.type_ComboBox.findText("%s" % partType)
        self.type_ComboBox.setCurrentIndex(type_num)
        self.prjSet()

        try:
            print((">>> %s" % sqc))
            sqc_item = self.sqc_TreeWidget.findItems("%s" % sqc, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)[
                0]
        except IndexError:
            return
        self.sqc_TreeWidget.setCurrentItem(sqc_item)
        self.sqc(sqc_item)

        shot_item = self.shot_TreeWidget.findItems("%s" % shot, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)[0]
        self.shot_TreeWidget.setCurrentItem(shot_item)
        self.shot(shot_item)

    def deleteItem(self):
        ret = QtWidgets.QMessageBox.question(self, "Question Message",
                                             '''Do you want to Delete Item?''', QtWidgets.QMessageBox.Ok,
                                             QtWidgets.QMessageBox.Cancel)

        if ret == QtWidgets.QMessageBox.Cancel:
            return
        globalTake = self.assetinfos

        for checkBoxItem in self.dataItemStruct["allCheckBoxItemList"]:
            if checkBoxItem.isChecked():
                rootType = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][0]
                itemName = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][1]

                # item delete
                if globalTake[rootType]["objectList"].get(itemName):
                    del globalTake[rootType]["objectList"][itemName]

                # item List delete
                if not globalTake[rootType].get("objectList"):
                    del globalTake[rootType]
        # Save Item
        TakeName = self.take_ComboBox.currentText()
        # itemScript.deleteAssetSaveInfoList(self.TakeList["%s" %TakeName], globalTake)
        utilScript.deleteAssetSaveInfoList(self.TakeList["%s" % TakeName], globalTake)
        self.assetInfoTreeWidget.clear()
        self.shot(self.shotClass)

    def envCheck(self, setNum):
        num = (2 - setNum) // 2

        if self.dataItemStruct:
            if self.dataItemStruct["rootClass"].get("resolutionSet"):
                resolutionSetItem = self.dataItemStruct["rootClass"]["resolutionSet"]
                resolutionSetItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("lightRig"):
                lightRigItem = self.dataItemStruct["rootClass"]["lightRig"]
                lightRigItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("frameRange"):
                frameRangeItem = self.dataItemStruct["rootClass"]["frameRange"]
                frameRangeItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("camera"):
                cameraItem = self.dataItemStruct["rootClass"]["camera"]
                cameraItem.setHidden(num)
            self.envCheckNum = setNum


    def assetsCheck(self, setNum):
        num = (2 - setNum) // 2

        if self.dataItemStruct:
            if self.dataItemStruct["rootClass"].get("rig"):
                rigItem = self.dataItemStruct["rootClass"]["rig"]
                rigItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("model"):
                modelItem = self.dataItemStruct["rootClass"]["model"]
                modelItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("rigEnv"):
                rigENVItem = self.dataItemStruct["rootClass"]["rigEnv"]
                rigENVItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("modelEnv"):
                modelENVItem = self.dataItemStruct["rootClass"]["modelEnv"]
                modelENVItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("lookdev"):
                lookdevItem = self.dataItemStruct["rootClass"]["lookdev"]
                lookdevItem.setHidden(num)
            self.assetsCheckNum = setNum

    def matchMoveCacheCheck(self, setNum):
        num = (2 - setNum) // 2

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

            self.matchMoveCacheCheckNum = setNum

    def layoutCacheCheck(self, setNum):
        num = (2 - setNum) // 2

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

            self.layoutCacheCheckNum = setNum

    def aniCacheCheck(self, setNum):
        num = (2 - setNum) // 2

        if self.dataItemStruct:
            if self.dataItemStruct["rootClass"].get("dummy"):
                dummyItem = self.dataItemStruct["rootClass"]["dummy"]
                dummyItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("atom"):
                atomItem = self.dataItemStruct["rootClass"]["atom"]
                atomItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("atomCrowdAni"):
                alembicCrowdSimItem = self.dataItemStruct["rootClass"]["atomCrowdAni"]
                alembicCrowdSimItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("geoCache"):
                geoCacheItem = self.dataItemStruct["rootClass"]["geoCache"]
                geoCacheItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicAni"):
                alembicAniItem = self.dataItemStruct["rootClass"]["alembicAni"]
                alembicAniItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("usdAni"):
                usdAniItem = self.dataItemStruct["rootClass"]["usdAni"]
                usdAniItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("alembicCrowdSim"):
                alembicCrowdSimItem = self.dataItemStruct["rootClass"]["alembicCrowdSim"]
                alembicCrowdSimItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("alembicCrowdAni"):
                alembicCrowdAniItem = self.dataItemStruct["rootClass"]["alembicCrowdAni"]
                alembicCrowdAniItem.setHidden(num)
            self.aniCacheCheckNum = setNum

    def simulCacheCheck(self, setNum):
        num = (2 - setNum) // 2

        if self.dataItemStruct:
            if self.dataItemStruct["rootClass"].get("simulGeoCache"):
                simulGeoCacheItem = self.dataItemStruct["rootClass"]["simulGeoCache"]
                simulGeoCacheItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("yetiCache"):
                yetiCacheItem = self.dataItemStruct["rootClass"]["yetiCache"]
                yetiCacheItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("furGeoCache"):
                furGeoCacheItem = self.dataItemStruct["rootClass"]["furGeoCache"]
                furGeoCacheItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("clothGeoCache"):
                clothGeoCacheItem = self.dataItemStruct["rootClass"]["clothGeoCache"]
                clothGeoCacheItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicCfxCrowd"):
                alembicCfxCrowdItem = self.dataItemStruct["rootClass"]["alembicCfxCrowd"]
                alembicCfxCrowdItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicSimul"):
                alembicSimulItem = self.dataItemStruct["rootClass"]["alembicSimul"]
                alembicSimulItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicFur"):
                alembicFurItem = self.dataItemStruct["rootClass"]["alembicFur"]
                alembicFurItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicMuscle"):
                alembicMuscleItem = self.dataItemStruct["rootClass"]["alembicMuscle"]
                alembicMuscleItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicCloth"):
                alembicClothItem = self.dataItemStruct["rootClass"]["alembicCloth"]
                alembicClothItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicCurve"):
                alembicCurveItem = self.dataItemStruct["rootClass"]["alembicCurve"]
                alembicCurveItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("clothSimGeoCache"):
                clothSimGeoCacheItem = self.dataItemStruct["rootClass"]["clothSimGeoCache"]
                clothSimGeoCacheItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("hairGeoCache"):
                hairGeoCacheItem = self.dataItemStruct["rootClass"]["hairGeoCache"]
                hairGeoCacheItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("hairSimGeoCache"):
                hairSimGeoCacheItem = self.dataItemStruct["rootClass"]["hairSimGeoCache"]
                hairSimGeoCacheItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("furSimGeoCache"):
                furSimGeoCacheItem = self.dataItemStruct["rootClass"]["furSimGeoCache"]
                furSimGeoCacheItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicFur"):
                alembicFurItem = self.dataItemStruct["rootClass"]["alembicFur"]
                alembicFurItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicFurSim"):
                alembicFurSimItem = self.dataItemStruct["rootClass"]["alembicFurSim"]
                alembicFurSimItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicHair"):
                alembicHairItem = self.dataItemStruct["rootClass"]["alembicHair"]
                alembicHairItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicHairSim"):
                alembicHairSimItem = self.dataItemStruct["rootClass"]["alembicHairSim"]
                alembicHairSimItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicClothSim"):
                alembicClothSimItem = self.dataItemStruct["rootClass"]["alembicClothSim"]
                alembicClothSimItem.setHidden(num)
            self.simulCacheCheckNum = setNum

    def renderCacheCheck(self, setNum):
        num = (2 - setNum) // 2

        if self.dataItemStruct:
            if self.dataItemStruct["rootClass"].get("geoCacheRender"):
                geoCacheRenderItem = self.dataItemStruct["rootClass"]["geoCacheRender"]
                geoCacheRenderItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("atomRender"):
                atomRenderItem = self.dataItemStruct["rootClass"]["atomRender"]
                atomRenderItem.setHidden(num)

            if self.dataItemStruct["rootClass"].get("alembicRender"):
                alembicRenderItem = self.dataItemStruct["rootClass"]["alembicRender"]
                alembicRenderItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("ass"):
                assItem = self.dataItemStruct["rootClass"]["ass"]
                assItem.setHidden(num)
            self.renderCacheCheckNum = setNum

    def fxCacheCheck(self, setNum):
        num = (2 - setNum) // 2

        if self.dataItemStruct:
            if self.dataItemStruct["rootClass"].get("alembicFx"):
                alembicFxItem = self.dataItemStruct["rootClass"]["alembicFx"]
                alembicFxItem.setHidden(num)
            if self.dataItemStruct["rootClass"].get("vdbFx"):
                vdbFxItem = self.dataItemStruct["rootClass"]["vdbFx"]
                vdbFxItem.setHidden(num)
        self.fxCacheCheckNum = setNum

    def modelCacheCheck(self, setNum):
        num = (2 - setNum) // 2

        if self.dataItemStruct:

            matchList = ["model", "muscle"]
            searchList = ["Model", "Muscle", "Finalize"]

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

            self.modelCacheCheckNum = setNum

    def assetInfoList(self, name):
        self.treeLoad_progressBar.setValue(0)
        # get take
        self.assetinfos = {}

        if not self.take_ComboBox.currentText():
            self.setTake(name)

        if not self.take_ComboBox.currentText():
            self.dataItemStruct["rootClass"] = {}
            self.dataItemStruct["subClass"] = {}
            self.dataItemStruct["itemClass"] = {}
            return
        else:
            TakeName = self.take_ComboBox.currentText()
            if not self.totalTake_checkBox.isChecked():
                TakeName = TakeName.replace("take.", "take_just.")
                self.assetinfos = takeScript.takeInfoList(self.shots[self.shotItem[name]],
                                                          self.justTakeList["%s" % TakeName])
            else:
                TakeName = TakeName.replace("take_just.", "take.")
                self.assetinfos = takeScript.takeInfoList(self.shots[self.shotItem[name]],
                                                          self.TakeList["%s" % TakeName])

        if self.assetinfos == None:
            return

        self.assetInfoItem = {}
        currentPart = utilScript.currentPartType()

        # widget size
        self.assetInfoTreeWidget.setColumnWidth(0, 80)
        self.assetInfoTreeWidget.setColumnWidth(1, 260)
        self.assetInfoTreeWidget.setColumnWidth(2, 250)
        self.assetInfoTreeWidget.setColumnWidth(3, 40)
        self.assetInfoTreeWidget.setColumnWidth(4, 60)
        self.assetInfoTreeWidget.setColumnWidth(8, 80)
        self.assetInfoTreeWidget.setColumnWidth(9, 130)

        self.assetInfoTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        # font
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)

        #  refresh datastruct
        self.dataItemStruct["treeItem"] = {}
        self.dataItemStruct["checkBox"] = {}
        self.dataItemStruct["comboBox1"] = {}
        self.dataItemStruct["comboBox2"] = {}

        self.dataItemStruct["allCheckBoxItemList"] = {}
        self.dataItemStruct["allTreeWidgetItemList"] = {}
        self.dataItemStruct["partTypeCheckBox"] = {}
        self.dataItemStruct["allItemClass"] = {}
        self.dataItemStruct["rootClass"] = {}
        self.dataItemStruct["subClass"] = {}
        self.dataItemStruct["itemClass"] = {}

        # set Version column Name
        rootItemList1 = ["frameRange", "resolutionSet", "lightRig", "dummy", "mmDummy", "layoutDummy", "postvizDummy",
                         "modelDummy", "atom", "mayaLayoutDummy", "maya",
                         "postvizAtom", "mmAtom", "modelAtom", "atomRender", "alembicCrowdSim",
                         "alembicCrowdAni"]  # Asset and shot

        rootItemList2 = ["geoCache", "simulGeoCache", "furGeoCache", "clothGeoCache", "mmGeoCache", "muscleGeoCache",
                         "modelGeoCache",
                         "geoCacheRender", "hairGeoCache", "hairSimGeoCache", "furSimGeoCache", "clothSimGeoCache",
                         "clarisseLit", "clarisseDigienv"
                         ]  # Asset and shot

        rootItemList3 = ["fxCache", "yetiCache",
                         "alembicModel", "alembicAni", "alembicCfxCrowd", "alembicRender", "alembicRig", "alembicFur",
                         "alembicFinalize", "alembicMuscle", "alembicCloth", "alembicSimul", "alembicMm",
                         "alembicLayout", "alembicFx", "alembicCurve", "alembicHair", "alembicHairSim",
                         "alembicFurSim", "alembicClothSim",
                         "usdAni"  # Add USD Animation support
                         ]  # Asset and shot

        abcRootItemList = ["alembicAni", "alembicCrowdSim", "alembicCrowdAni", "alembicModel", "alembicRender",
                           "alembicRig", "alembicCfxCrowd",
                           "alembicFur", "alembicFinalize", "alembicMuscle", "alembicCloth", "alembicSimul",
                           "alembicMm", "alembicLayout",
                           "alembicFx", "alembicCurve", "alembicHair", "alembicHairSim", "alembicFurSim",
                           "alembicClothSim",
                           "clarisseLit", "clarisseDigienv"
                           ]
        usdRootItemList = ["usdAni"]  # USD items - hide Opt1, use Opt2 for stage/import
        instanceItemList = ["instanceAni", "instanceDigienv", "instanceModel", "instanceLayout"]

        # root class
        progressValueSum = 0
        progressValue = 100.0 / len(self.assetinfos)
        self.treeLoad_progressBar.setValue(10)
        for rootItem in self.assetinfos:

            itemList = self.assetinfos[rootItem]

            self.assetSceneItem = QtWidgets.QTreeWidgetItem(self.assetInfoTreeWidget)  # create item
            self.assetSceneItem.setExpanded(1)

            self.assetSceneItem.setText(1, " %s" % rootItem)  # Name column
            self.assetSceneItem.setText(3, " %d" % len(itemList["objectList"]))  # Num column

            self.checkBox_root = QtWidgets.QCheckBox()

            self.comboBox1_root = QtWidgets.QComboBox()
            self.comboBox2_root = QtWidgets.QComboBox()
            self.comboBox1_root.setObjectName("opt1")
            self.comboBox2_root.setObjectName("opt2")

            self.assetInfoTreeWidget.setItemWidget(self.assetSceneItem, 0, self.checkBox_root)  # Check column
            self.assetInfoTreeWidget.setItemWidget(self.assetSceneItem, 6, self.comboBox1_root)  # Opt1 column
            self.assetInfoTreeWidget.setItemWidget(self.assetSceneItem, 7, self.comboBox2_root)  # Opt2 column

            self.comboBox1_root.setStyleSheet("QComboBox {background-color: transparent;}")
            self.comboBox2_root.setStyleSheet("QComboBox {background-color: transparent;}")

            self.checkBox_root.stateChanged[int].connect(
                lambda num, checkbox=self.checkBox_root: self.setchangeCheckBox(num, checkbox))
            self.comboBox1_root.activated[int].connect(
                lambda num: self.setchangeComboBox1(num, self.comboBox1_root))
            self.comboBox2_root.activated[int].connect(
                lambda num: self.setchangeComboBox2(num, self.comboBox2_root))

            # Data
            # self.dataItemStruct.itemClass["rootClass"].update( { rootItem : self.assetSceneItem } )
            self.dataStruct.rootClass = {rootItem: self.assetSceneItem}
            self.dataStruct.set({self.assetSceneItem: None})
            self.dataStruct.set({self.checkBox_root: None})
            self.dataStruct.set({self.comboBox1_root: None}, rootItem)
            self.dataStruct.set({self.comboBox2_root: None}, rootItem)

            # set objectList
            num = 0
            # fileName = itemList["fileName"].keys()[0]

            # sub class
            objectList = utilScript.splitItemName(
                itemList["objectList"])  # {u'gunShot': [u'gunShot1:ctrl_SET', u'gunShot:ctrl_SET']}
            for infoItem in objectList:  # top item
                self.subTreeWidget = QtWidgets.QTreeWidgetItem(self.assetSceneItem)
                self.subTreeWidget.setFont(1, font)
                self.subTreeWidget.setExpanded(1)
                self.subTreeWidget.setText(1, infoItem)
                self.subTreeWidget.setText(3, "%d" % len(objectList[infoItem]))

                # item row color : green
                list(map(lambda x: self.subTreeWidget.setBackground(x, QtGui.QBrush(QtGui.QColor(80, 255, 0, 10))),
                    list(range(10))))

                self.checkBox_midle = QtWidgets.QCheckBox()
                self.comboBox1_midle = QtWidgets.QComboBox()
                self.comboBox2_midle = QtWidgets.QComboBox()
                self.comboBox1_midle.setObjectName("opt1")
                self.comboBox2_midle.setObjectName("opt2")
                self.assetInfoTreeWidget.setItemWidget(self.subTreeWidget, 0, self.checkBox_midle)  # Check column
                self.assetInfoTreeWidget.setItemWidget(self.subTreeWidget, 6, self.comboBox1_midle)  # Opt1 column
                self.assetInfoTreeWidget.setItemWidget(self.subTreeWidget, 7, self.comboBox2_midle)  # Opt2 column

                self.comboBox1_midle.setStyleSheet("QComboBox {background-color: transparent;}")
                self.comboBox2_midle.setStyleSheet("QComboBox {background-color: transparent;}")

                self.checkBox_midle.stateChanged[int].connect(
                    lambda num, checkbox=self.checkBox_midle: self.setchangeCheckBox(num, checkbox))
                self.comboBox1_midle.activated[int].connect(
                    lambda num: self.setchangeComboBox1(num, self.comboBox1_midle))
                self.comboBox2_midle.activated[int].connect(
                    lambda num: self.setchangeComboBox2(num, self.comboBox2_midle))

                # data
                self.dataStruct.itemClass["subClass"].update({self.subTreeWidget: infoItem})
                self.dataStruct.set({self.assetSceneItem: self.subTreeWidget})
                self.dataStruct.set({self.checkBox_root: self.checkBox_midle})
                self.dataStruct.set({self.comboBox1_root: self.comboBox1_midle}, rootItem)
                self.dataStruct.set({self.comboBox2_root: self.comboBox2_midle}, rootItem)

                # item class : object List
                objList = objectList[infoItem]
                objList.sort()
                for objName in objList:
                    # set
                    self.subItemTreeWidget = QtWidgets.QTreeWidgetItem(self.subTreeWidget)
                    self.subItemTreeWidget.setText(1, "%s" % objName)  # Name column

                    if rootItem in rootItemList1:
                        self.subItemTreeWidget.setText(2, "%s" % re.search("[\w]+(?=/[\w|]+\.)",
                                                                           itemList["objectList"][objName]).group())
                    elif re.match("maya", rootItem) or re.match("atom", rootItem):
                        self.subItemTreeWidget.setText(2, "%s" % re.search("[\w]+(?=/[\w|]+\.)",
                                                                           itemList["objectList"][objName]).group())
                    elif rootItem in rootItemList2:
                        self.subItemTreeWidget.setText(2, "%s" % itemList["objectList"][objName].split("/")[-2])
                    elif rootItem in rootItemList3:
                        if rootItem in ["alembicFx", "fxCache", "yetiCache"]:
                            self.subItemTreeWidget.setText(2, "%s" % itemList["fileName"][objName].split("/")[-1])
                        else:
                            self.subItemTreeWidget.setText(2, "%s" % itemList["objectList"][objName].split("/")[-3])
                    else:
                        if type(itemList["objectList"][objName]) == type([]):
                            if re.search("[\w]+(?=/[\w]+\.)", itemList["objectList"][objName][0]):
                                self.subItemTreeWidget.setText(2, "%s" % re.search("[\w]+(?=/[\w]+\.)",
                                                                                   itemList["objectList"][objName][
                                                                                       0]).group())
                        else:
                            self.subItemTreeWidget.setText(2, "%s" % re.search("[\w]+(?=\.)",
                                                                               itemList["objectList"][objName]).group())

                    # item child class : version path ( Version column )
                    self.subItemTreeWidget_PathItem = QtWidgets.QTreeWidgetItem(self.subItemTreeWidget)

                    if type(itemList["objectList"][objName]) == type([]):
                        self.subItemTreeWidget_PathItem.setText(1, "%s" % itemList["objectList"][objName][1:])
                        self.subItemTreeWidget_PathItem.setText(2, "%s" % itemList["objectList"][objName][0])
                        self.subItemTreeWidget_PathItem.setForeground(1, QtGui.QBrush(QtGui.QColor(255, 255, 255, 120)))
                    else:
                        self.subItemTreeWidget_PathItem.setText(2, "%s" % itemList["objectList"][
                            objName])  # Version column path

                    self.subItemTreeWidget_PathItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                    self.subItemTreeWidget_PathItem.setForeground(2, QtGui.QBrush(QtGui.QColor(255, 255, 255, 120)))

                    self.subItemTreeWidget.setText(5, " %s" % itemList["frame"][objName])  # Frame column
                    self.subItemTreeWidget.setText(8, " %s" % itemList["username"][objName])  # Artist column
                    self.subItemTreeWidget.setText(9, " %s" % itemList["date"][objName])  # Date column

                    # -------------------------
                    # upDate
                    # -------------------------
                    if currentPart is not None:
                        if itemList["objectCheck"].get(objName).get(currentPart) is not None and itemList[
                            "objectCheck"].get(objName).get(currentPart) == 1:
                            self.updateLabel = QtWidgets.QPushButton("UP", self.assetInfoTreeWidget)
                            # self.updateLabel.setText("UP")
                            self.updateLabel.setMaximumWidth(30)
                            self.updateLabel.setStyleSheet(
                                "border:2px solid yellow; border-radius:10px; font:11px; color:yellow; background-color:rgb(120, 80, 100);")

                            self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 4, self.updateLabel)

                    # -------------------------
                    # Comment Tip
                    # -------------------------
                    if itemList.get("comment") and itemList.get("comment").get(objName):
                        commentText = "%s" % itemList["comment"][objName]
                        # self.subItemTreeWidget_PathItem.setText(1, "%s" %commentText) # Name column
                        self.itemCommentButton = QtWidgets.QPushButton(self.assetInfoTreeWidget)
                        self.itemCommentButton.setIcon(QtGui.QIcon("{}/icon/messages-icon.png".format(self.filepath)))
                        self.itemCommentButton.setFixedSize(20, 20)
                        self.itemCommentButton.setFlat(1)
                        self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 3, self.itemCommentButton)
                        noteWin = noteWindow(self.itemCommentButton, commentText)
                        self.itemCommentButton.clicked.connect(
                            lambda: self.commentPopWindow(noteWin, self.itemCommentButton))

                    # -------------------------
                    self.checkBox_item = QtWidgets.QCheckBox()
                    self.comboBox1_item = QtWidgets.QComboBox()
                    self.comboBox2_item = QtWidgets.QComboBox()

                    self.comboBox1_item.setObjectName("opt1")
                    self.comboBox2_item.setObjectName("opt2")
                    self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 0, self.checkBox_item)
                    self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 6, self.comboBox1_item)
                    self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 7, self.comboBox2_item)
                    self.comboBox1_item.setStyleSheet("QComboBox {background-color: transparent;}")
                    self.comboBox2_item.setStyleSheet("QComboBox {background-color: transparent;}")

                    self.checkBox_midle.stateChanged[int].connect(
                        lambda num, checkbox=self.checkBox_midle: self.setchangeCheckBox(num, checkbox))
                    self.comboBox1_midle.activated[int].connect(
                        lambda num: self.setchangeComboBox1(num, self.comboBox1_midle))
                    self.comboBox2_midle.activated[int].connect(
                        lambda num: self.setchangeComboBox2(num, self.comboBox2_midle))

                    # data
                    self.dataStruct.itemClass["itemClass"].update({self.subItemTreeWidget: objName})

                    self.dataStruct.set({self.subTreeWidget: self.subItemTreeWidget})
                    self.dataStruct.set({self.checkBox_midle: self.checkBox_item})
                    self.dataStruct.set({self.comboBox1_midle: self.comboBox1_item}, rootItem)
                    self.dataStruct.set({self.comboBox2_midle: self.comboBox2_item}, rootItem)

                    self.dataStruct.set({self.subItemTreeWidget: self.subItemTreeWidget})
                    self.dataStruct.set({self.checkBox_item: self.checkBox_item})
                    self.dataStruct.set({self.comboBox1_item: self.comboBox1_item}, rootItem)
                    self.dataStruct.set({self.comboBox2_item: self.comboBox2_item}, rootItem)

                    self.dataStruct.setList({self.subItemTreeWidget: [rootItem, objName, self.checkBox_item,
                                                                      self.comboBox1_item, self.comboBox2_item]})
                    self.dataStruct.setList({self.checkBox_item: [rootItem, objName, self.subItemTreeWidget,
                                                                  self.comboBox1_item, self.comboBox2_item]})
                    self.dataStruct.setWidget(rootItem, {
                        objName: [self.subItemTreeWidget, self.subTreeWidget, self.assetSceneItem]})

                    if rootItem in ["modelEnv", "lookdev", "rigEnv", "camera", "frameRange", "resolutionSet",
                                    "lightRig", "dummy", "mmDummy", "layoutDummy", "modelDummy", "mayaLayoutDummy",
                                    "vdbFx", "ass"]:  # "rig", "model",
                        self.assetInfoTreeWidget.setItemWidget(self.assetSceneItem, 6, None)
                        self.assetInfoTreeWidget.setItemWidget(self.subTreeWidget, 6, None)
                        self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 6, None)

                    if re.match("maya", rootItem) or re.match("atom", rootItem):
                        self.assetInfoTreeWidget.setItemWidget(self.assetSceneItem, 6, None)
                        self.assetInfoTreeWidget.setItemWidget(self.subTreeWidget, 6, None)
                        self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 6, None)

                    if rootItem in abcRootItemList:
                        if not rootItem in ["alembicModel", "alembicRig"]:
                            self.assetInfoTreeWidget.setItemWidget(self.assetSceneItem, 6, None)
                            self.assetInfoTreeWidget.setItemWidget(self.subTreeWidget, 6, None)
                            self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 6, None)
                        self.comboBox2_item.clear()
                        self.comboBox2_midle.clear()
                        self.comboBox2_root.clear()
                        # self.comboBox2_item.addItems(["alembic", "gpu", "proxy", "import"])
                        # self.comboBox2_midle.addItems(["alembic", "gpu", "proxy","import" ])
                        # self.comboBox2_root.addItems(["alembic", "gpu", "proxy", "import"])
                        self.comboBox2_item.addItems(ABCIMPORTOPT)
                        self.comboBox2_midle.addItems(ABCIMPORTOPT)
                        self.comboBox2_root.addItems(ABCIMPORTOPT)

                    if rootItem in usdRootItemList:
                        # Hide Opt1 for USD items
                        self.assetInfoTreeWidget.setItemWidget(self.assetSceneItem, 6, None)
                        self.assetInfoTreeWidget.setItemWidget(self.subTreeWidget, 6, None)
                        self.assetInfoTreeWidget.setItemWidget(self.subItemTreeWidget, 6, None)
                        # Set Opt2 options for USD: stage (default) and import
                        self.comboBox2_item.clear()
                        self.comboBox2_midle.clear()
                        self.comboBox2_root.clear()
                        self.comboBox2_item.addItems(["import", "stage"])
                        self.comboBox2_midle.addItems(["import", "stage"])
                        self.comboBox2_root.addItems(["import", "stage"])

                    if rootItem in ["rig", "model"]:
                        self.subItemTreeWidget.setText(5, "")

                    if rootItem in instanceItemList:
                        self.comboBox2_item.clear()
                        self.comboBox2_midle.clear()
                        self.comboBox2_root.clear()
                        instanceImportOpt = ["reference"]
                        self.comboBox2_item.addItems(instanceImportOpt)
                        self.comboBox2_midle.addItems(instanceImportOpt)
                        self.comboBox2_root.addItems(instanceImportOpt)

            progressValueSum += progressValue
            self.treeLoad_progressBar.setValue(progressValueSum)

        self.treeLoad_progressBar.setValue(100)
        self.colorSet()

    def showHideItemSet(self):
        self.envCheck(self.envCheckNum)
        self.assetsCheck(self.assetsCheckNum)
        self.matchMoveCacheCheck(self.matchMoveCacheCheckNum)
        self.layoutCacheCheck(self.layoutCacheCheckNum)
        self.aniCacheCheck(self.aniCacheCheckNum)
        self.modelCacheCheck(self.modelCacheCheckNum)
        self.simulCacheCheck(self.simulCacheCheckNum)
        self.renderCacheCheck(self.renderCacheCheckNum)
        self.fxCacheCheck(self.fxCacheCheckNum)

    def titlecheckSet(self):
        self.titleCheck(self.title1CheckNum, self.title1CheckBox)
        self.titleCheck(self.title2CheckNum, self.title2CheckBox)
        self.titleCheck(self.title3CheckNum, self.title3CheckBox)

    def typeCheck(self):
        num = 1 - self.typeCheckPushButton.isChecked()

        self.envCheckBox.setChecked(num)
        self.assetsCheckBox.setChecked(num)
        self.matchMoveCacheCheckBox.setChecked(num)
        self.layoutCacheCheckBox.setChecked(num)
        # self.layoutCacheCheckBox.setChecked(num)
        self.modelCacheCheckBox.setChecked(num)
        self.aniCacheCheckBox.setChecked(num)
        self.simulCacheCheckBox.setChecked(num)
        self.renderCacheCheckBox.setChecked(num)
        self.fxCacheCheckBox.setChecked(num)

        self.showHideItemSet()
        self.titlecheckSet()

    def takeChange(self):
        self.assetInfoTreeWidget.clear()
        self.assetInfoList(self.shotClass)
        self.showHideItemSet()
        self.titlecheckSet()

    def colorSet(self):
        currentType = str(self.type_ComboBox.currentText())
        for root in self.dataItemStruct["rootClass"]:
            font = QtGui.QFont()
            font.setPointSize(13)
            font.setBold(True)
            font.setItalic(True)

            list(map(lambda x: self.dataItemStruct["rootClass"][root].setFont(x, font), list(range(7))))
            list(map(lambda x: self.dataItemStruct["rootClass"][root].setBackground(x, QtGui.QBrush(
                QtGui.QColor(80, 100, 255, 30))), list(range(10))))

        # setcolor
        globalTake = self.assetinfos
        updateList = {}
        rigItem = []

        for rootType in self.rootItemTypes:

            if globalTake.get(rootType) == None:
                continue

            try:
                objectList = list(set([(type(cmds.getAttr("%s" % x)) != int and type(
                    cmds.getAttr("%s" % x)) != float and "," in cmds.getAttr("%s" % x)) and
                                                    cmds.getAttr("%s" % x).split(",")[0] for x in cmds.ls("*.%s" % rootType, r=1)]))
            except:
                objectList = [False]

            if objectList == [False]:
                objectList = []
                if rootType in ["rig"]:
                    rigItem = objectList

                if rootType in ["model", "modelEnv"]:
                    objectList += rigItem

            if objectList:  # is tag
                item = {}

                for itemName in globalTake[rootType]["objectList"]:
                    itemName2 = ""
                    if rootType == "ass":
                        itemName2 = itemName + "_ass"
                    if rootType == "vdbFx":
                        itemName2 = itemName + "_vdbFx"

                    checkItem = 1
                    if itemName2 != "":
                        if itemName2 not in objectList:
                            checkItem = 0
                    else:
                        if itemName not in objectList:
                            checkItem = 0

                    # if itemName not in objectList:  # not in itemName
                    if not checkItem:
                        item.update({itemName: globalTake[rootType]["objectList"][itemName]})
                        updateList.update({rootType: item})

                        if rootType in self.dataItemStruct["rootClass"]:
                            list(map(lambda x: self.dataItemStruct["rootClass"][rootType].setBackground(x, QtGui.QBrush(
                                QtGui.QColor(80, 100, 255, 130))), list(range(10))))
                            list(map(lambda x: self.dataItemStruct["allItemClass"][rootType][itemName][0].setForeground(x,
                                                                                                                   QtGui.QBrush(
                                                                                                                       QtGui.QColor(
                                                                                                                           80,
                                                                                                                           255,
                                                                                                                           0,
                                                                                                                           160))),
                                list(range(10))))
                            list(map(lambda x: self.dataItemStruct["allItemClass"][rootType][itemName][1].setBackground(x,
                                                                                                                   QtGui.QBrush(
                                                                                                                       QtGui.QColor(
                                                                                                                           80,
                                                                                                                           255,
                                                                                                                           0,
                                                                                                                           70))),
                                list(range(10))))
                    else:
                        if rootType in ["rig", "rigEnv"]:
                            rigItem.append(itemName)

            else:  # not local file/ rootItem   / all item
                item = {}

                for itemName in globalTake[rootType]["objectList"]:
                    item.update({itemName: globalTake[rootType]["objectList"][itemName]})
                    updateList.update({rootType: item})
                    try:
                        if rootType in self.dataItemStruct["rootClass"]:
                            list(map(lambda x: self.dataItemStruct["rootClass"][rootType].setBackground(x, QtGui.QBrush(
                                QtGui.QColor(80, 100, 255, 130))), list(range(10))))
                            list(map(lambda x: self.dataItemStruct["allItemClass"][rootType][itemName][0].setForeground(x,
                                                                                                                   QtGui.QBrush(
                                                                                                                       QtGui.QColor(
                                                                                                                           80,
                                                                                                                           255,
                                                                                                                           0,
                                                                                                                           160))),
                                list(range(10))))
                            list(map(lambda x: self.dataItemStruct["allItemClass"][rootType][itemName][1].setBackground(x,
                                                                                                                   QtGui.QBrush(
                                                                                                                       QtGui.QColor(
                                                                                                                           80,
                                                                                                                           255,
                                                                                                                           0,
                                                                                                                           70))),
                                list(range(10))))
                    except Exception as why:
                        info = 'Exception: {}\n{}\n{}\n'.format(rootType, list(self.dataItemStruct["rootClass"].keys()), why)
                        self.testprint(info)

    # hyunil comments #02 ->>>> 디버깅이 안되니 파일에 error 보기위한 function
    def testprint(self, info):
        path = "/home/m83/tmp"
        if os.path.exists(path):
            writetype = 'a'
        else:
            os.mkdir(path)
            writetype = 'w'

        with open("/home/m83/tmp/errorinfo.txt", writetype) as f:
            f.write(info)
            f.write('--' * 50 + '\n')

    # hyunil comments #02 <end>

    # All check button
    def checkSet(self):
        num = self.checkPushButton.isChecked()
        for i in self.dataItemStruct["checkBox"]:
            i.setChecked(num)

    # refresh icon
    def refresh(self):
        self.shot(self.shotClass)

    # assetInfoTreeWidget Check column
    def setchangeCheckBox(self, num, name):
        for i in self.dataItemStruct["checkBox"][name]:
            if num:
                stateV = QtCore.Qt.Checked
            else:
                stateV = QtCore.Qt.Unchecked
            i.setCheckState(stateV)

    # assetInfoTreeWidget Opt1 column
    def setchangeComboBox1(self, num, name):
        for i in self.dataItemStruct["comboBox1"][name]:
            i.setCurrentIndex(num)

    # assetInfoTreeWidget Opt2 column
    def setchangeComboBox2(self, num, name):
        for i in self.dataItemStruct["comboBox2"][name]:
            i.setCurrentIndex(num)

    # Export ----------------------------------------------------------------------------------------------------------
    def camExport(self):
        partType = self.type_ComboBox.currentText()
        cameraFileName, cameraDir = utilScript.itemDircheck("camera")

        # file Dir check
        fileCheck = utilScript.itemFilecheck(cameraDir, cameraFileName, "camera")
        versionUp = True

        # overwrite
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        # stereo check
        stereoCamCheck = cameraScript.stereoCamCheck()
        if stereoCamCheck != None and stereoCamCheck == "noStereo":
            messageBox = QtWidgets.QMessageBox()
            font = QtGui.QFont()
            font.setPointSize(10)
            messageBox.setFont(font)

            reply = messageBox.question(self, "Question Message", "Is it stereo?", QtWidgets.QMessageBox.Yes,
                                        QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                messageBox.information(self, "Message", "PZ !! Stereo Rename !!", QtWidgets.QMessageBox.Ok)
                return

        # fileList
        # cameraItemList = cameraScript.itemListSelect()
        cameraItemList = utilScript.itemListSelect("camera")

        # get handle check
        num = self.handle_LineEdit.text()

        # fileList = {}
        # if cameraItemList is not None:
        #     userOrigRO = self.cameraUseOrigRO_checkBox.isChecked()
        #     for i in cameraItemList:
        #         # print atomFileName, atomDir, i, int(num)  #EO_055_ani_v01_w02_test /show/JM/seq/EO/EO_055/ani/wip/data/ani/EO_055_ani_v01_w02_test gunShot1:ctrl_SET 10
        #         if len(cameraItemList) == 1:
        #             cameraFile = cameraScript.cameraExport(cameraFileName, cameraDir, i, int(num),
        #                                                    userOrigRO)  # int(num)) -> itemNum
        #         else:
        #             cameraFile = cameraScript.cameraExport(cameraFileName, cameraDir, i, int(num), userOrigRO,
        #                                                    cameraItemList.index(i))  # int(num)) -> itemNum
        #
        #         fileList.update(cameraFile)  # atomItemList           #카메라 한개씩 익스포트 셋팅

        fileList = {}
        if cameraItemList is not None:
            userOrigRO = self.cameraUseOrigRO_checkBox.isChecked()

            if len(cameraItemList) == 1:
                item = cameraItemList[0]
                cameraFile = cameraScript.cameraExport(cameraFileName, cameraDir, item, int(num), userOrigRO)
                fileList.update(cameraFile)
            else:
                subName_list = multi_camExport.ListEditor(cameraItemList)
                if subName_list.exec_():
                    editedItems = subName_list.getEditedItems()

                    for i, item in enumerate(cameraItemList):
                        cameraFile = cameraScript.cameraExport(cameraFileName, cameraDir, item, int(num), userOrigRO, i, editedItems[i])
                        fileList.update(cameraFile)
                else:
                    return

            # cameraScript.assetInfoExport(fileList)
            takeScript.takeExport(fileList, "camera", versionUp=versionUp)
            # self.shots[self.shotItem[self.shotClass]], fileList , "Ani", "atom"
            self.shot(self.shotClass)  # refresh treewidget
            # cmds.confirmDialog ( title ='complete' , message ='Export complete', button=[ 'ok' ])
            cmd = 'DISPLAY=:O notify-send "Noar Message" "Export Complete" -t 10000'
            Popen(cmd, shell=True, stdout=PIPE)
        else:
            ret = QtWidgets.QMessageBox.question(self, "Message", "Please selecet camera", QtWidgets.QMessageBox.Ok)
            if ret == QtWidgets.QMessageBox.Ok:
                return

    def renderFarmAtom(self):
        print ("AtomExport")

    def renderFarmGeoCache(self):
        print ("GeoCacheExport")

    def renderFarmYeti(self):
        print ("YetiExport")

    def renderFarmAbc(self):
        abcType = "abc"
        tractorEngineV = str(self.tractorEngine_comboBox.currentText())

        # cache scene save
        saveSceneName = cmds.file(save=True)
        saveSceneDir = os.path.dirname(saveSceneName)
        saveSceneFile, saveSceneExt = os.path.splitext(saveSceneName)
        if not os.path.isdir("%s/tmp" % saveSceneDir):
            os.makedirs("%s/tmp" % saveSceneDir)
        suffixName = time.strftime("%Y%m%d_%H%M%S_noha_abc")

        newSaveSceneName = "%s/tmp/%s.%s" % (saveSceneDir, saveSceneFile.split("/")[-1], suffixName)
        shutil.copy2(saveSceneName, newSaveSceneName)

        # key Bake
        handleNum = int(self.handle_LineEdit.text())

        print ("AbcExport")
        partType = self.type_ComboBox.currentText()
        objectName = self.alembic_TreeWidget.objectName()
        frameType = str(self.abcFrameRange_combo.currentText())

        if partType in self.partType:
            dirName = "alembic"

        else:
            print ("Part Type Select ! \n cache Export.py")
            return

        # alembicFileName, alembicDir = utilScript.itemDircheck(objectName, dirName)
        alembicFileName, alembicDir = utilScript.itemDircheck(dirName)
        fileCheck = utilScript.itemFilecheck(alembicDir)
        versionUp = True

        # select
        root = self.alembic_TreeWidget.invisibleRootItem()  # treewidget List find name
        child_count = root.childCount()

        item = {}
        hiddenList = []
        for x in range(child_count):
            checkType = str(root.child(x).text(2))
            grpName = str(root.child(x).text(0))
            if checkType == "merge":
                item["{}_{}".format(grpName, "mergeObjectSpace")] = {"step": str(root.child(x).text(1)),
                                                                     "type": "mergeObjectSpace", "hidden": []}
                item["{}_{}".format(grpName, "mergeWorldSpace")] = {"step": str(root.child(x).text(1)),
                                                                    "type": "mergeWorldSpace", "hidden": []}
                if not grpName in hiddenList:
                    hiddenList.append(grpName)
            elif "scene," in checkType:
                abcType = "abc_scene"
                if self.createSceneSetFile_checkBox.isChecked():
                    abcType = "abc_sceneCreate"

                item[grpName] = {"step": str(root.child(x).text(1)), "type": str(root.child(x).text(2)), "hidden": []}
                handleNum = 0
            else:
                item[grpName] = {"step": str(root.child(x).text(1)), "type": str(root.child(x).text(2)), "hidden": []}

        # item = map(lambda x: str(root.child(x).text(0)), range(child_count))
        print (item)
        if not item:
            return

        # overwrite
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        alembicItemList = item  # selecting
        if hiddenList:
            for itemV, itemAttr in list(alembicItemList.items()):
                if itemAttr["type"] == "base":
                    alembicItemList[itemV]["hidden"] = hiddenList

        # alembic export
        if partType in self.partType:

            fileList = {}
            cmds.refresh(su=1)

            mayaVersion = cmds.about(v=True)
            cacheFile = tractorJobScript.itemExport(alembicFileName, alembicDir, alembicItemList, int(handleNum),
                                                    frameType, newSaveSceneName, 1, abcType, mayaVersion, self.filepath,
                                                    tractorEngineV)
            if cacheFile:
                fileList.update(cacheFile)

            cmds.refresh(su=0)

            if not fileList:  # not cachefile
                return

            # info export
            # alembicScript.assetInfoExport(fileList, "farm", frameType)
            takeScript.takeExport(fileList, "alembic", {}, "farm", frameType, versionUp=versionUp)

    def openTractor(self):
        tractorV = str(self.tractorEngine_comboBox.currentText())

        cmd = 'firefox http://{}.m83.co.kr/tractor/tv &'.format(tractorV)
        Popen(cmd, shell=True, stdout=PIPE)

    def frameRangeExport(self):
        partType = self.type_ComboBox.currentText()
        rangeFileName, rangeDir = utilScript.itemDircheck("frameRange")
        fileCheck = utilScript.itemFilecheck(rangeDir)
        versionUp = True

        # overwrite
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        # frameRange Export .py
        fileList = {}
        rangeFile = frameRangeScript.frameRangeExport(rangeFileName, rangeDir, "frameRange")
        fileList.update(rangeFile)

        # info export
        takeScript.takeExport(fileList, "frameRange", versionUp=versionUp)

        self.shot(self.shotClass)
        cmd = 'DISPLAY=:O notify-send "Noah Message" "Export Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)

    def resolutionExport(self):
        partType = self.type_ComboBox.currentText()
        # rangeFileName , rangeDir = resolutionScript.itemDircheck()
        # fileCheck = resolutionScript.itemFilecheck( rangeDir)
        rangeFileName, rangeDir = utilScript.itemDircheck("resolution")
        fileCheck = utilScript.itemFilecheck(rangeDir)
        versionUp = True

        # overwrite
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        fileList = {}
        # rangeFile = resolutionScript.itemExport( rangeFileName , rangeDir, "resolutionSet" )
        rangeFile = resolutionScript.resolutionExport(rangeFileName, rangeDir, "resolutionSet")
        fileList.update(rangeFile)

        # info export
        # resolutionScript.assetInfoExport( fileList )
        takeScript.takeExport(fileList, "resolutionSet", versionUp=versionUp)
        self.shot(self.shotClass)
        cmd = 'DISPLAY=:O notify-send "Noar Message" "Export Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)

    def dummyExport(self):
        partType = self.type_ComboBox.currentText()
        # dummyFileName, dummyDir = dummyScript.itemDircheck()
        # fileCheck = dummyScript.itemFilecheck( dummyDir)
        dummyFileName, dummyDir = utilScript.itemDircheck("dummy")
        fileCheck = utilScript.itemFilecheck(dummyDir)
        versionUp = True

        # overwrite
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        # dummyItemList = dummyScript.itemListSelect()  # selecting
        dummyItemList = utilScript.itemListSelect()  # selecting

        fileList = {}
        for i in dummyItemList:
            # dummyFile = dummyScript.itemExport( dummyFileName, dummyDir, i)
            dummyFile = dummyScript.dummyExport(dummyFileName, dummyDir, i)
            fileList.update(dummyFile)  # atomItemList

        # info export
        # dummyScript.assetInfoExport( fileList )
        takeScript.takeExport(fileList, "dummy", versionUp=versionUp)
        self.shot(self.shotClass)
        cmd = 'DISPLAY=:O notify-send "Noar Message" "Export Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)

    def modelEnvExport(self):
        partType = self.type_ComboBox.currentText()
        # modelEnvFileName , modelEnvDir = modelEnvScript.itemDircheck()
        # fileCheck = modelEnvScript.itemFilecheck( modelEnvDir)
        modelEnvFileName, modelEnvDir = utilScript.itemDircheck("modelEnv")
        fileCheck = utilScript.itemFilecheck(modelEnvDir)
        versionUp = True

        # overwrite
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        # modelEnvItemName = modelEnvScript.itemListSelect()  # selecting
        modelEnvItemName = utilScript.itemListSelect("modelEnv")  # selecting
        modelEnvItem = modelEnvScript.findModelEnvData(str(self.prj_ComboBox.currentText()), modelEnvItemName)

        # file Export
        fileList = {}
        # modelEnvFile = modelEnvScript.itemExport( modelEnvFileName , modelEnvDir, "modelEnv" )
        modelEnvFile = modelEnvScript.modelEnvExport(modelEnvFileName, modelEnvDir, "modelEnv")

        fileList.update(modelEnvFile)

        # info export
        # modelEnvScript.assetInfoExport( fileList )
        takeScript.takeExport(fileList, "modelEnv", versionUp=versionUp)

        self.shot(self.shotClass)
        cmd = 'DISPLAY=:O notify-send "Noar Message" "Export Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)

    def lookdevEnvExport(self):
        partType = self.type_ComboBox.currentText()
        # lookdevFileName , lookdevDir = lookdevScript.itemDircheck()
        # fileCheck = lookdevScript.itemFilecheck(lookdevDir)
        lookdevFileName, lookdevDir = utilScript.itemDircheck("lookdev")
        fileCheck = utilScript.itemFilecheck(lookdevDir)
        versionUp = True

        # overwrite
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        # assetName = lookdevDir.split("/")[5]
        assetName = lookdevDir.split("/show/")[1].split("/")[3]

        fileList = {}

        # lookdevFile = lookdevScript.itemExport( lookdevFileName, lookdevDir, assetName)
        lookdevFile = lookdevScript.lookdevExport(lookdevFileName, lookdevDir, assetName)
        fileList.update(lookdevFile)  # atomItemList

        # info export
        # lookdevScript.assetInfoExport(fileList)
        takeScript.takeExport(fileList, "lookdev", versionUp=versionUp)
        self.shot(self.shotClass)
        cmd = 'DISPLAY=:O notify-send "Noar Message" "Export Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)

    # proxyAutoConnectShaderPushButton
    def proxyAutoConnectShader(self):
        # itemScript.proxyAutoConnectShader()
        vrayProxyScript.proxyAutoConnectShader()
        self.shot(self.shotClass)  # refresh assetInfoTreeWidget
        # cmds.confirmDialog ( title ='complete' , message ='Connect complete', button=[ 'ok' ])
        cmd = 'DISPLAY=:O notify-send "Noar Message" "Connect Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)

    # atomSetAllLoad_PushButton
    def atomLoadSet(self, name):
        self.atom_TreeWidget.clear()
        loadName = name.objectName().split("_")[0]
        selectList = atomScript.atomAllLoadSet(str(loadName))

        if not selectList:
            print('>>>>>> Please selection "set" <<<<<<<')
            return
        for item in selectList:
            atomItem = QtWidgets.QTreeWidgetItem(self.atom_TreeWidget, [item])

    # loadMeshPushButton
    def loadMesh(self):
        self.geoCache_TreeWidget.clear()

        self.cacheTmp = {}
        itemList = []
        selectMeshList = cmds.ls(sl=1)

        for selectMesh in selectMeshList:

            if not cmds.ls(selectMesh, dag=1, type="mesh"):
                continue
            #             print selectMesh, cmds.ls( sl=1, dag=1, type="mesh" )
            for rootType in self.rootItemTypes:
                if self.dataItemStruct["partTypeCheckBox"].get(rootType) == None:
                    continue

                for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:  # check Box List
                    if checkBoxItem.isChecked() == True:
                        itemList = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem]
                        cachePath = self.assetinfos[itemList[0]]["objectList"][itemList[1]]

                        # select !!
                        shapName = cmds.ls(selectMesh, dag=1, type="mesh")[0]
                        if ":" in shapName:
                            shapName = shapName.split(":")[1]
                        cacheList = glob.glob("%s/*" % cachePath)

                        if "%s/%s_%s.mc" % (cachePath, itemList[1].split(":")[0], shapName) in cacheList:
                            # set Item
                            geoCacheItem = QtWidgets.QTreeWidgetItem(self.geoCache_TreeWidget, [selectMesh])
                            self.cacheTmp[selectMesh] = itemList[1]  # .split(":")[0]
                        else:
                            print(("Not match object Name!! - %s" % selectMesh))
                            print((" => %s_%s.mc" % (itemList[1].split(":")[0], shapName)))
        if not itemList:
            print ("GeoCache not Check !!")

        else:
            self.cacheTmp[selectMesh] = itemList[1]

    # geoCacheSetAllLoad_PushButton
    # geoCacheSetLoad_PushButton
    def geoCacheLoadSet(self, name):
        self.geoCache_TreeWidget.clear()

        loadName = name.objectName().split("_")[0]
        selectList = geoCacheScript.geoCacheAllLoadSet(str(loadName))
        print(("Select Set Num : %s " % len(selectList)))

        # ----------num -----????
        # geoCacheItemList = geoCacheScript.itemListSelect(selectList )  # selecting
        geoCacheItemList = utilScript.itemListSelect("geoCache", selectList)  # selecting

        geoCacheScript.checkCacheNum(geoCacheItemList)
        # ------------------------------

        for item in selectList:
            geoCacheItem = QtWidgets.QTreeWidgetItem(self.geoCache_TreeWidget, [item])

    # yetiCacheSetAllLoad_PushButton
    def yetiCacheLoadSet(self, name):
        self.yeti_TreeWidget.clear()
        loadName = name.objectName().split("_")[0]

        selectList = yetiCacheScript.yetiCacheAllLoadSet(str(loadName))

        for item in selectList:
            yetiCacheItem = QtWidgets.QTreeWidgetItem(self.yeti_TreeWidget, [item])
            yetiCacheItem.setBackground(1, QtGui.QBrush(QtGui.QColor(60, 60, 60)))
            yetiCacheItem.setFlags(yetiCacheItem.flags() | QtCore.Qt.ItemIsEditable)

    # assLoadMeshPushButton
    def setLoadMesh(self, typeV):
        if typeV == "ass":
            self.ass_TreeWidget.clear()
            treeWidget = self.ass_TreeWidget
        if typeV == "maya":
            self.maya_TreeWidget.clear()
            treeWidget = self.maya_TreeWidget
        selectList = cmds.ls(sl=1)
        for item in selectList:
            # treeItem = QtWidgets.QTreeWidgetItem(self.ass_TreeWidget,[item])
            treeItem = QtWidgets.QTreeWidgetItem(treeWidget, [item])

    # alembicGeoSetLoad_PushButton
    # alembicCurveSetLoad_PushButton
    # alembicLoadMeshPushButton
    def alembicLoadMesh(self, name):
        if not self.multiBtn_checkBox.isChecked():
            self.alembic_TreeWidget.clear()

        if name.objectName() == "alembicGeoSetLoad_PushButton":
            lodType = self.lod_ComboBox.currentText()
            print('lodType >>>>>>>>>>>>>>>>', lodType)
            selectList = alembicScript.alembicAllLoadSet(lodType)
        elif name.objectName() == "alembicCurveSetLoad_PushButton":
            selectList = alembicScript.alembicCurveLoadSet()
        elif name.objectName() == "alembicSceneSetLoad_pushButton":
            selectList = alembicScript.alembicSceneSetLoad()
        else:
            selectList = alembicScript.alembicLoadMesh()

        if not selectList:
            return

        for item, attrDic in list(selectList.items()):
            alembicItem = QtWidgets.QTreeWidgetItem(self.alembic_TreeWidget, [item, attrDic["step"], attrDic["type"]])
            alembicItem.setFlags(alembicItem.flags() | QtCore.Qt.ItemIsEditable)
            alembicItem.setTextAlignment(1, QtCore.Qt.AlignCenter)

    # renderLayerLoad_pushButton
    def setLoadRenderLayer(self):

        self.renderLayer_TreeWidget.clear()

        renderLayerList = cmds.ls(type="renderLayer")
        renderLayerDic = {}
        for renderLayerName in renderLayerList:
            if len(renderLayerName.split(":")) == 1:  # referenc render layer  check
                if re.search("defaultRenderLayer", renderLayerName):
                    if renderLayerName != "defaultRenderLayer":
                        continue
                renderableV = cmds.getAttr("%s.renderable" % renderLayerName)
                if renderableV:
                    renderableID = cmds.getAttr("%s.identification" % renderLayerName)
                    renderLayerDic[renderableID] = renderLayerName

        sceneName = cmds.file(q=True, sn=True)
        sceneList = sceneName.split("/show/")[1].split("/")
        for idV, item in list(renderLayerDic.items()):
            layerNum = item.split("_")[-1]
            takePath = "/show/{}/{}/{}/{}_{}/Take".format(sceneList[0], sceneList[1], sceneList[2], sceneList[2],
                                                          layerNum)
            print (takePath)
            if os.path.exists(takePath):
                takeList = glob.glob("{}/take.*.json".format(takePath))
                takeList.sort(reverse=True)
                if takeList:
                    with open(takeList[0]) as f:
                        takeData = json.load(f)
                    if 'frameRange' in list(takeData.keys()):
                        frameRange = list(takeData['frameRange']["frame"].keys())[0]
                        item = item + ",{}".format(frameRange)

            treeItem = QtWidgets.QTreeWidgetItem(self.renderLayer_TreeWidget, [item])

    # Instance
    def setLoadInstance(self, name):
        self.instance_TreeWidget.clear()

        exportSeqToAsset = self.exportSeqToAsset_checkBox.isChecked()
        if name.objectName() == "instanceSetLoad_PushButton":
            selectList = instanceScript.instanceSetLoad(exportSeqToAsset)

        if not selectList:
            return

        for item, attrDic in list(selectList.items()):
            instanceItem = QtWidgets.QTreeWidgetItem(self.instance_TreeWidget, [item, attrDic["type"]])
            instanceItem.setFlags(instanceItem.flags() | QtCore.Qt.ItemIsEditable)
            instanceItem.setTextAlignment(1, QtCore.Qt.AlignCenter)

    # Clarisse (disabled for Maya-only mode)
    def setLoadClarisse(self, typeV):
        print("Clarisse functionality disabled in Maya-only mode")
        return

    # Export -----------------------------------------------------------------------------------------------------------

    # atomExport_PushButton
    def atomExport(self):
        partType = utilScript.currentPartType()
        objectName = self.atom_TreeWidget.objectName()

        # atomFileName , atomDir = atomScript.itemDircheck(objectName)
        # fileCheck = atomScript.itemFilecheck( atomDir)
        atomFileName, atomDir = utilScript.itemDircheck("atom", objectName)
        fileCheck = utilScript.itemFilecheck(atomDir)
        versionUp = True

        # select
        root = self.atom_TreeWidget.invisibleRootItem()  # find name
        child_count = root.childCount()
        item = [str(root.child(x).text(0)) for x in range(child_count)]

        if not item:  # Not all teturn
            return

        # overwrite
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        # atomItemList = atomScript.itemListSelect(item)  # selecting

        atomItemList = utilScript.itemListSelect("atom", item)  # selecting

        # key Bake
        num = self.handle_LineEdit.text()
        if self.keyBake_CheckBox.isChecked():
            # atomScript.itemKeyBake(int(num))
            atomScript.atomKeyBake(int(num))

        #         # atom Export
        fileList = {}
        for i in atomItemList:
            # atomFile = atomScript.itemExport( atomFileName, atomDir, i, int(num))
            atomFile = atomScript.atomExport(atomFileName, atomDir, i, int(num))
            fileList.update(atomFile)  # atomItemList

        # info export
        # atomScript.assetInfoExport( fileList )
        takeScript.takeExport(fileList, "atom", versionUp=versionUp)

        # rig Info
        rigData = rigScript.findRigData(fileList, self.ASSETS_TYPE)
        # rigScript.subAssetInfoExport( fileList, rigData )
        # takeScript.takeExport(fileList, "rig", "", rigData)
        takeScript.takeExport(fileList, "rig", rigData, versionUp=versionUp)

        # model Info
        modelData = modelScript.exportTake(fileList, ["globalTake", "localTake"],
                                           "model")

        # asset write
        shot_item = self.shot_TreeWidget.currentItem()
        shotNumber = str(shot_item.text(0))
        shotDir = self.shots[str(shot_item.text(0))]

        shotDirItem = {}
        shotDirItem[shotNumber] = shotDir  # 여기서 부터 넣고 기록하는 것
        # rigScript.rigListInfoWrite(shotDirItem,   rigData)
        takeScript.takeAddExport(shotDirItem, rigData, "rig")
        takeScript.takeAddExport(shotDirItem, modelData, "model")

        self.shot(self.shotClass)  # refresh assetInfoTreeWidget

        cmd = 'DISPLAY=:O notify-send "Noar Message" "Export Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)

    # yetiExport_PushButton
    def yetiCacheExport(self):
        # select
        root = self.yeti_TreeWidget.invisibleRootItem()  # treewidget List find name
        child_count = root.childCount()

        fileList = {}
        list(map(lambda x: fileList.update({str(root.child(x).text(0)): str(root.child(x).text(1))}), list(range(child_count))))
        versionUp = True
        if fileList:
            has_existing = any([os.path.exists(p) for p in fileList.values() if p])
            if has_existing:
                ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                     QtWidgets.QMessageBox.Cancel)
                if ret == QtWidgets.QMessageBox.Cancel:
                    return
                versionUp = False

        # # info export
        # yetiCacheScript.assetInfoExport(fileList)
        takeScript.takeExport(fileList, "yetiCache", versionUp=versionUp)
        self.shot(self.shotClass)  # refresh assetInfoTreeWidget

        cmd = 'DISPLAY=:O notify-send "Noar Message" "Export Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)

    def geoCacheExport(self):
        # partType = itemScript.currentPartType()
        partType = utilScript.currentPartType()
        #         partType = self.type_ComboBox.currentText()
        objectName = self.geoCache_TreeWidget.objectName()

        if partType in ["ani", "model", "matchmove", "layout", "dyn", "finalize", "fur", "cloth", "clothSim", "hair",
                        "lit"]:
            dirName = "geoCache"

        else:
            print ("Part Type Select ! \n cache Export.py  1723")
            return

        # geoCacheFileName, geoCacheDir = geoCacheScript.itemDircheck(objectName, dirName)
        # fileCheck = geoCacheScript.itemFilecheck(geoCacheDir)
        geoCacheFileName, geoCacheDir = utilScript.itemDircheck(dirName)
        fileCheck = utilScript.itemFilecheck(geoCacheDir)
        versionUp = True

        # select
        root = self.geoCache_TreeWidget.invisibleRootItem()  # treewidget List find name
        child_count = root.childCount()
        item = [str(root.child(x).text(0)) for x in range(child_count)]

        if not item:
            return

        # overwrite
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        # geoCacheItemList = geoCacheScript.itemListSelect(item)  # selecting
        geoCacheItemList = utilScript.itemListSelect("geoCache", item)  # selecting

        # key Bake
        num = self.handle_LineEdit.text()

        # info export
        if partType in ["ani", "layout", "matchmove", "model", "lit"]:
            # geocache Export
            fileList = {}
            for i in geoCacheItemList:
                cacheFile = geoCacheScript.geoCacheExportSet(geoCacheFileName, geoCacheDir, i)
                if not cacheFile:
                    continue
                fileList.update(cacheFile)

            if not fileList:  # not cachefile
                return

            # geoCacheScript.itemExport(fileList, geoCacheDir, int(num))
            geoCacheScript.geoCacheExport(fileList, geoCacheDir, int(num))

            # info export
            # geoCacheScript.assetInfoExport(fileList)
            takeScript.takeExport(fileList, "geoCache", versionUp=versionUp)

            # rig Info
            rigData = rigScript.findRigData(fileList)
            # rigScript.subAssetInfoExport(fileList, rigData)  # 캐쉬 데이타/ 리깅 데이타
            # takeScript.takeExport(fileList, "rig", "", rigData)
            takeScript.takeExport(fileList, "rig", rigData, versionUp=versionUp)
            modelData = modelScript.exportTake(fileList, ["globalTake", "localTake"],
                                               "model")  # takeTypeList = ["globalTake", "localTake"]

            # asset write
            shot_item = self.shot_TreeWidget.currentItem()
            shotNumber = str(shot_item.text(0))
            shotDir = self.shots[str(shot_item.text(0))]

            shotDirItem = {}
            shotDirItem[shotNumber] = shotDir  # 여기서 부터 넣고 기록하는 것
            # rigScript.rigListInfoWrite(shotDirItem, rigData)
            takeScript.takeAddExport(shotDirItem, rigData, "rig")
            # modelScript.modelListInfoWrite(shotDirItem, modelData)
            takeScript.takeAddExport(shotDirItem, modelData, "model")

        elif partType in ["dyn", "finalize", "fur", "cloth", "clothSim", "hair"]:
            # filter
            filterItem = []
            for i in self.cacheTmp:  # load mesh
                if i in geoCacheItemList:
                    filterItem.append(i)

            fileList = {}
            for i in filterItem:
                cacheFile = geoCacheScript.geoCacheExportSet(geoCacheFileName, geoCacheDir, i)
                if not cacheFile:
                    continue
                fileList.update(cacheFile)

            if not fileList:  # not cachefile
                return

            # cacheFile = geoCacheScript.itemExport(filterItem, geoCacheDir, int(num), i)
            geoCacheScript.geoCacheExport(filterItem, geoCacheDir, int(num), 1)

            # info export
            # geoCacheScript.assetInfoExport(fileList)
            takeScript.takeExport(fileList, "geoCache", versionUp=versionUp)

        self.shot(self.shotClass)  # refresh assetInfoTreeWidget
        cmd = 'DISPLAY=:O notify-send "Noar Message" "Export Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)

    def alembicExport(self):
        partType = self.type_ComboBox.currentText()
        objectName = self.alembic_TreeWidget.objectName()

        if partType in self.partType:
            dirName = "alembic"

        else:
            print ("Part Type Select ! \n cache Export.py")
            return

        # alembicFileName , alembicDir = alembicScript.itemDircheck(objectName, dirName)
        # fileCheck = alembicScript.itemFilecheck( alembicDir)
        alembicFileName, alembicDir = utilScript.itemDircheck(dirName)
        fileCheck = utilScript.itemFilecheck(alembicDir)
        versionUp = True

        # select
        root = self.alembic_TreeWidget.invisibleRootItem()  # treewidget List find name
        child_count = root.childCount()
        item = {}
        hiddenList = []
        for x in range(child_count):
            checkType = str(root.child(x).text(2))
            grpName = str(root.child(x).text(0))
            if checkType == "merge":
                item["{}_{}".format(grpName, "mergeObjectSpace")] = {"step": str(root.child(x).text(1)),
                                                                     "type": "mergeObjectSpace", "hidden": []}
                item["{}_{}".format(grpName, "mergeWorldSpace")] = {"step": str(root.child(x).text(1)),
                                                                    "type": "mergeWorldSpace", "hidden": []}
                if not grpName in hiddenList:
                    hiddenList.append(grpName)
            elif "scene," in checkType:
                QtWidgets.QMessageBox.information(self, "메세지", "scene_SET 타입은 렌더팜으로만 export가 가능합니다.")
                return
            else:
                item[grpName] = {"step": str(root.child(x).text(1)), "type": str(root.child(x).text(2)), "hidden": []}

        # item = map(lambda x: str(root.child(x).text(0) ), range(child_count) )
        print (item)
        if not item:
            return

        # overwrite
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        alembicItemList = item  # selecting
        if hiddenList:
            for itemV, itemAttr in list(alembicItemList.items()):
                if itemAttr["type"] == "base":
                    alembicItemList[itemV]["hidden"] = hiddenList

        # key Bake
        num = self.handle_LineEdit.text()

        # alembic step Num
        # step_num = self.alembic_opt_lineEdit.text()

        # info export
        if partType in self.partType:

            fileList = {}
            cmds.refresh(su=1)
            frameType = str(self.abcFrameRange_combo.currentText())

            # for i in alembicItemList:
            for i, attrDic in list(alembicItemList.items()):
                # cacheFile = alembicScript.itemExport( alembicFileName, alembicDir, i,int(num), step_num, frameType)  #( atomFileName, atomDir, i, int(num))
                # cacheFile = alembicScript.alembicExport(alembicFileName, alembicDir, i, int(num), step_num, frameType)
                cacheFile = alembicScript.alembicExport(alembicFileName, alembicDir, i, int(num), attrDic["step"],
                                                        frameType, attrDic["type"], attrDic["hidden"])
                if not cacheFile:
                    continue
                fileList.update(cacheFile)

            cmds.refresh(su=0)

            if not fileList:  # not cachefile
                return

            # info export
            # alembicScript.assetInfoExport( fileList, "local", frameType )
            takeScript.takeExport(fileList, "alembic", {}, "local", frameType, versionUp=versionUp)

            self.shot(self.shotClass)  # refresh assetInfoTreeWidget
            cmd = 'DISPLAY=:O notify-send "Noar Message" "Export Complete" -t 10000'
            Popen(cmd, shell=True, stdout=PIPE)

    def exportHair(self):
        """Export Hair functionality for Maya tab"""
        import os
        print("Export Hair button clicked")
        
        # Get selected items from maya tree widget
        root = self.maya_TreeWidget.invisibleRootItem()
        child_count = root.childCount()
        itemList = [str(root.child(x).text(0)) for x in range(child_count)]
        
        if not itemList:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select items to export hair")
            return
            
        # Get export directory - for hair, use direct path without filename subfolder
        current_scene = cmds.file(query=True, sceneName=True)
        if current_scene:
            scene_dir = os.path.dirname(current_scene)
            if '/wip/' in scene_dir:
                base_path = scene_dir.split('/wip/')[0]
                exportDir = os.path.join(base_path, 'wip', 'data', 'hair')
            else:
                exportDir = os.path.join(scene_dir, 'data', 'hair')
        else:
            exportDir = os.path.join(os.getcwd(), 'data', 'hair')
        
        # Create directory if it doesn't exist
        if not os.path.exists(exportDir):
            os.makedirs(exportDir)
        
        # Get current scene name for file info
        fileData = utilScript.getFileName()
        currentSceneName = fileData[0] if fileData else "hair_export"
        
        # Check if directory exists
        fileCheck = utilScript.itemFilecheck(exportDir)
        versionUp = True
        if fileCheck:
            ret = QtWidgets.QMessageBox.question(self, "Question Message", "File overwrite?", 
                                               QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False
        
        try:
            cmds.refresh(su=1)
            
            # Get export settings
            mayaExt = "mb"  # Default to Maya Binary for hair (smaller file size, faster loading)
            mayaAlembic = True  # Also export as alembic
            frameType = "FrameRange"
            
            # Call mayaHairExport function
            fileList = mayaHairScript.mayaHairExport(currentSceneName, exportDir, itemList, 
                                                    "mayaHair", mayaExt, mayaAlembic, frameType)
            
            cmds.refresh(su=0)
            
            if fileList:
                # Export take information
                takeScript.takeExport(fileList, "mayaHair", {}, "local", frameType, versionUp=versionUp)
                
                # Refresh UI
                self.shot(self.shotClass)
                
                # Show success message
                QtWidgets.QMessageBox.information(self, "Export Hair", 
                    "Hair export completed successfully!\nExported %d items" % len(fileList))
                
                # System notification
                cmd = 'DISPLAY=:O notify-send "Noah Message" "Hair Export Complete" -t 10000'
                Popen(cmd, shell=True, stdout=PIPE)
            else:
                QtWidgets.QMessageBox.warning(self, "Export Hair", "No files were exported")
                
        except Exception as e:
            cmds.refresh(su=0)
            QtWidgets.QMessageBox.critical(self, "Export Hair Error", 
                "Error during hair export:\n%s" % str(e))
            print("Hair export error:", str(e))

    def noahExport(self, fileType, exportType, treeObj):
        print(("%s Export" % fileType))
        tractorEngineV = str(self.tractorEngine_comboBox.currentText())

        farmSceneName = ""
        if exportType == "farm":
            # cache scene save
            saveSceneName = cmds.file(save=True)
            saveSceneDir = os.path.dirname(saveSceneName)
            saveSceneFile, saveSceneExt = os.path.splitext(saveSceneName)
            if not os.path.isdir("%s/tmp" % saveSceneDir):
                os.makedirs("%s/tmp" % saveSceneDir)
            suffixName = time.strftime("%Y%m%d_%H%M%S_noha") + "_{}".format(fileType)

            farmSceneName = "%s/tmp/%s.%s" % (saveSceneDir, saveSceneFile.split("/")[-1], suffixName)
            shutil.copy2(saveSceneName, farmSceneName)

        partType = self.type_ComboBox.currentText()

        if partType in self.partType:
            # if fileType == "maya":
            # dirName = self.mayaUse_comboBox.currentText()
            #    dirName = "maya"
            # else:
            dirName = fileType
        else:
            print(("Not Exists : %s" % partType))
            return

        currentSceneName, exportDir = utilScript.itemDircheck(dirName)  # exportFileName == currentSceneName
        fileCheck = utilScript.itemFilecheck(exportDir)
        versionUp = True

        # select
        root = treeObj.invisibleRootItem()  # treewidget List find name
        child_count = root.childCount()
        itemList = [str(root.child(x).text(0)) for x in range(child_count)]
        print (itemList)

        if not itemList:
            return

        # overwrite
        if fileCheck:
            print (exportDir)
            ret = QtWidgets.QMessageBox.question(self, "Quesstion Message", "File ovewrite ?", QtWidgets.QMessageBox.Ok,
                                                 QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            versionUp = False

        # key Bake
        num = self.handle_LineEdit.text()

        # alembic step Num
        step_num = 1

        # info export
        if partType in self.partType:

            fileList = {}
            cmds.refresh(su=1)

            frameType = "FrameRange"
            handleNum = int(self.handle_LineEdit.text())
            keybake = self.keyBake_CheckBox.isChecked()

            if fileType == "atom":
                mayaVersion = cmds.about(v=True)
                cacheFile = atomScript.atomExport2(currentSceneName, exportDir, itemList, int(num), step_num,
                                                   frameType, farmSceneName, 1, fileType, mayaVersion, self.filepath,
                                                   exportType, keybake, handleNum, tractorEngineV)
                if cacheFile:
                    fileList.update(cacheFile)

            if fileType == "yetiCache":
                frameType = str(self.yetiCacheFrameRange_combo.currentText())

                if exportType == "local":
                    for i in itemList:
                        # TODO
                        print (i)
                        # cacheFile = yetiCacheScript.yetiCacheExport(exportFileName, exportDir, i, int(num), step_num, frameType)
                        # if not cacheFile:
                        #    continue
                        # fileList.update(cacheFile)

                elif exportType == "farm":
                    mayaVersion = cmds.about(v=True)
                    cacheFile = tractorJobScript.itemExport(currentSceneName, exportDir, itemList, int(num),
                                                            step_num, frameType, farmSceneName, 1, fileType,
                                                            mayaVersion, self.filepath, tractorEngineV)
                    if cacheFile:
                        fileList.update(cacheFile)
                else:
                    print ("Error : unknwon exportType")
                    return 1

            if fileType == "ass":
                frameType = str(self.assFrameRange_combo.currentText())
                step_num = self.ass_opt_lineEdit.text()

                if exportType == "local":
                    for i in itemList:
                        cacheFile = assScript.assExport(currentSceneName, exportDir, i, int(num), step_num, frameType)
                        if not cacheFile:
                            continue
                        fileList.update(cacheFile)
                elif exportType == "farm":
                    mayaVersion = cmds.about(v=True)
                    cacheFile = tractorJobScript.itemExport(currentSceneName, exportDir, itemList, int(num),
                                                            step_num, frameType, farmSceneName, 1, fileType,
                                                            mayaVersion, self.filepath, tractorEngineV)
                    if cacheFile:
                        fileList.update(cacheFile)
                else:
                    print ("Error : unknwon exportType")
                    return 1

            if fileType == "usd":
                try:
                    from script import usdScript
                    importlib.reload(usdScript)
                    step_num = self.usd_opt_lineEdit.text()
                    frameType = str(self.usdFrameRange_combo.currentText())  # Use USD frame range

                    if exportType == "local":
                        for i in itemList:
                            cacheFile = usdScript.usdExport(currentSceneName, exportDir, i, int(num), step_num, frameType)
                            if not cacheFile:
                                continue
                            fileList.update(cacheFile)
                    elif exportType == "farm":
                        # Create dictionary structure like Alembic for farm export
                        item = {}
                        for grpName in itemList:
                            item[grpName] = {"step": step_num, "type": "base", "hidden": []}
                        
                        
                        mayaVersion = cmds.about(v=True)
                        cacheFile = tractorJobScript.itemExport({}, exportDir, item, int(num),
                                                                frameType, farmSceneName, 1, fileType,
                                                                mayaVersion, self.filepath, tractorEngineV)
                        if cacheFile:
                            fileList.update(cacheFile)
                    else:
                        print ("Error : unknown exportType")
                        return 1
                except ImportError:
                    print("USD export not available - usdScript not found")
                    return 1

            if fileType == "maya":
                # mayaUse = self.mayaUse_comboBox.currentText()
                mayaUse = ""
                fileType = "maya" + mayaUse.capitalize()

                mayaExt = self.mayaExt_comboBox.currentText()
                mayaAlembic = self.mayaAlembic_checkBox.isChecked()
                frameType = self.mayaFrameRange_combo.currentText()
                cacheFile = mayaScript.mayaExport(currentSceneName, exportDir, itemList, fileType, mayaExt, mayaAlembic,
                                                  frameType)

                if cacheFile:
                    fileList.update(cacheFile)

            if fileType == "instance":
                exportSeqToAsset = self.exportSeqToAsset_checkBox.isChecked()
                cacheFile, pointInfo, instanceFileDir, instanceFileType = instanceScript.instanceExport(
                    currentSceneName, exportDir, itemList=itemList, exportSeqToAsset=exportSeqToAsset,
                    fileTypeV=fileType)
                if cacheFile:
                    fileList.update(cacheFile)

            if fileType == "renderlayer":
                mayaVersion = cmds.about(v=True)
                cacheFile = renderLayerScript.renderLayerExport(currentSceneName, exportDir, itemList, int(num),
                                                                step_num, frameType, farmSceneName, 1, "abc",
                                                                mayaVersion, self.filepath, exportType, keybake,
                                                                handleNum)
                if cacheFile:
                    fileList.update(cacheFile)

            if fileType == "clarisse":
                print("Clarisse export disabled in Maya-only mode")
                return

            cmds.refresh(su=0)

            if not fileList:  # not cachefile
                return

            # info export
            if fileType != "renderlayer":
                if fileType == "instance":
                    takeScript.takeExport(fileList, instanceFileType, frameType="CurrentFrame", instanceInfo=pointInfo,
                                          fileDirV=instanceFileDir, versionUp=versionUp)
                else:
                    takeScript.takeExport(fileList, fileType, {}, exportType, frameType, versionUp=versionUp)
                if fileType == "atom":
                    rigData = rigScript.findRigData(fileList, self.ASSETS_TYPE)
                    takeScript.takeExport(fileList, "rig", rigData, exportType, versionUp=versionUp)

                self.shot(self.shotClass)  # refresh assetInfoTreeWidget

            cmd = 'DISPLAY=:O notify-send "Noah Message" "Export Complete" -t 10000'
            Popen(cmd, shell=True, stdout=PIPE)

    def contextMenuEvent(self, event):
        pos = event.globalPos()
        item = self.assetInfoTreeWidget.itemAt(event.pos() - self.assetInfoTreeWidget.pos() - QtCore.QPoint(10, 123))

        if self.dataItemStruct["allTreeWidgetItemList"].get(item) == None:
            return

        menu = QtWidgets.QMenu(self)
        sepr1 = QtGui.QAction(self)
        sepr1.setSeparator(True)
        sepr2 = QtGui.QAction(self)
        sepr2.setSeparator(True)
        sepr3 = QtGui.QAction(self)
        sepr3.setSeparator(True)
        sepr4 = QtGui.QAction(self)
        sepr4.setSeparator(True)
        sepr5 = QtGui.QAction(self)
        sepr5.setSeparator(True)

        menu.addAction(sepr1)
        menu.addAction("Open Directory", lambda: self.openItemDir(item))
        menu.addAction(sepr2)
        menu.addAction("Change Item", lambda: self.changeItemDir(item))
        menu.addAction(sepr3)
        menu.addAction("Select Object", lambda: self.selectObjectItem(item))
        menu.addAction(sepr4)
        menu.addAction("NameSpace Add", lambda: self.nameSpaceAdd(item))
        menu.addAction("NameSpace Delete", lambda: self.nameSpaceDelete(item))
        menu.addAction("Delete Object (nameSpace)", lambda: self.deleteConnectObj(item))
        menu.addAction(sepr5)
        menu.addAction("Note", lambda: self.itemComment(item))
        menu.setStyleSheet("left: 20px;")
        menu.popup(pos)

    def openItemDir(self, selectWidgetItem):
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
        # selectItme = ""
        for item in widgetItem:
            if self.dataItemStruct["allTreeWidgetItemList"].get(item) == None:
                return

            allDate = self.dataItemStruct["allTreeWidgetItemList"][item]
            itemDir = self.assetinfos[allDate[0]]["objectList"][allDate[1]]

            if type(itemDir) == type([]):
                itemDir = itemDir[0]

            if "{" in itemDir:
                itemDir = itemDir.split("{")[0]

            if re.search(".ass", itemDir):
                itemDir = os.path.dirname(itemDir)

            if os.path.exists(itemDir):
                # itempath = {}
                # if not selectItme:  # select Path
                if os.path.isfile(itemDir):  # "file"
                    cmd = "nautilus %s" % os.path.dirname(itemDir)
                    print(cmd)
                    Popen(cmd, shell=True, stdout=PIPE)
                else:
                    cmd = "nautilus %s" % itemDir
                    print(cmd)
                    Popen(cmd, shell=True, stdout=PIPE)

    def changeItemDir(self, selectWidgetItem):
        # isCheck
        widgetItem = []
        for rootType in self.rootItemTypes:
            if self.dataItemStruct["partTypeCheckBox"].get(rootType) == None:
                continue
            for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:  # check Box List
                if checkBoxItem.isChecked() == True:
                    #                                 print rootType, checkBoxItem
                    widgetItem.append(self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][2])

        # list
        if not widgetItem:
            widgetItem = [selectWidgetItem]

        notObject = []
        selectItem = ""
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
                if not selectItem:  # select Path
                    if os.path.isfile(itemDir):  # "file"
                        selectItem = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                           "FileName",
                                                                           os.path.dirname(itemDir),
                                                                           "All Files (*);;Text Files (*.txt)")
                        print (selectItem)

                    else:  # dir
                        options = QtWidgets.QFileDialog.DontResolveSymlinks | QtWidgets.QFileDialog.ShowDirsOnly
                        selectItem = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                                "Directory",
                                                                                os.path.dirname(itemDir), options)

                # if not selectItem : # Not Data
                if not selectItem[0]:  # Not Data
                    return

                if allDate[0] == "camera":
                    self.assetinfos[allDate[0]]["objectCheck"][allDate[1]] = {"model": 1, "rig": 1, "ani": 1,
                                                                              "matchmove": 1, "layout": 1, "dyn": 1,
                                                                              "finalize": 1, "cloth": 1, "hair": 1,
                                                                              "clothSim": 1, "lit": 1, "fur": 1,
                                                                              "lookdev": 1, "fx": 1}
                    self.assetinfos[allDate[0]]["updateList"][allDate[1]][0] = "%s" % selectItem[0]
                    self.assetinfos[allDate[0]]["objectList"][allDate[1]][0] = "%s" % selectItem[0]
                else:
                    self.assetinfos[allDate[0]]["objectCheck"][allDate[1]] = {"model": 1, "rig": 1, "ani": 1,
                                                                              "matchmove": 1, "layout": 1, "dyn": 1,
                                                                              "finalize": 1, "cloth": 1, "hair": 1,
                                                                              "clothSim": 1, "lit": 1, "fur": 1,
                                                                              "lookdev": 1, "fx": 1}
                    self.assetinfos[allDate[0]]["updateList"][allDate[1]] = "%s" % selectItem[0]
                    self.assetinfos[allDate[0]]["objectList"][allDate[1]] = "%s" % selectItem[0]
            else:
                notObject.append(allDate[1])

        if notObject:
            txt = ""
            for i in notObject:
                txt += "%-30s" % i

            cmds.confirmDialog(title='Please! File Check!', message=txt, button=['ok'])

        # globalCurrentTake,  globalNewTake, globalNewNum   = itemScript.versionUpTakeName("%s/Take"%self.shots[self.shotItem[self.shotClass]], "take")
        # itemScript.changeSaveTake(globalNewTake ,self.assetinfos) # takeDir, take
        globalCurrentTake, globalNewTake, globalNewNum = takeScript.versionUpTakeName(
            "%s/Take" % self.shots[self.shotItem[self.shotClass]], "take")
        takeScript.changeSaveTake(globalNewTake, self.assetinfos)  # takeDir, take
        self.shot(self.shotClass)  # refresh assetInfoTreeWidget

    def selectObjectItem(self, selectWidgetItem):
        widgetItem = []
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
        for checkBoxItem in self.dataItemStruct["allCheckBoxItemList"]:
            if checkBoxItem.isChecked():
                itemList = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem]
                if ":" in itemName:
                    utilScript.nameSpaceDelete(itemList[1])

    def deleteConnectObj(self, selectWidgetItem):
        itemName = selectWidgetItem.text(1)
        for checkBoxItem in self.dataItemStruct["allCheckBoxItemList"]:
            if checkBoxItem.isChecked():
                itemList = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem]
                if ":" in itemName:
                    # itemScript.deleteConnectObj(itemList[1])
                    utilScript.deleteConnectObj(itemList[1])

    def itemComment(self, selectWidgetItem):
        widgetItem = [selectWidgetItem]

        notObject = []
        selectItme = ""
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
            self.textpubWindow.exec_()

    def textpup(self):
        itemType = self.textpubWindow.dataInfo["itemType"]
        itemName = self.textpubWindow.dataInfo["itemName"]

        text = str(self.textpubWindow.textEdit.toPlainText())

        if not self.assetinfos[itemType].get("comment"):
            self.assetinfos[itemType].update({"comment": {}})

        self.assetinfos[itemType]["comment"].update({itemName: text})

        # itemScript.changeSaveTake( self.textpubWindow.dataInfo["takeDir"], self.assetinfos )
        takeScript.changeSaveTake(self.textpubWindow.dataInfo["takeDir"], self.assetinfos)
        self.textpubWindow.closeWindow()

        self.shot(self.shotClass)

    def meshreplaceOpen(self):
        # self.meshReplaceTool.meshReplace()
        print("DEBUG: meshreplaceOpen called - forcing reload of referenceSettings")
        import sys
        if 'referenceSettings.referenceSettings' in sys.modules:
            del sys.modules['referenceSettings.referenceSettings']
            print("DEBUG: Removed referenceSettings.referenceSettings from sys.modules")
        if 'referenceSettings.nodeModel' in sys.modules:
            del sys.modules['referenceSettings.nodeModel']
            print("DEBUG: Removed referenceSettings.nodeModel from sys.modules")
        if 'referenceSettings' in sys.modules:
            del sys.modules['referenceSettings']
            print("DEBUG: Removed referenceSettings from sys.modules")
        
        import importlib
        import referenceSettings.referenceSettings as referenceSettings_module
        importlib.reload(referenceSettings_module)
        referenceSettings_module.meshReplace()

    def commentPopWindow(self, commentWindowName, button):
        commentWindowName.parent = button
        commentWindowName.moveWindow()
        commentWindowName.show()

    def changeStackedCommentLayout(self, name):
        self.stackeStackedWidget.setCurrentIndex(0)
        self.assetsView.changeStackedLayoutMode(0)

    def changeStackedExportLayout(self, name):
        self.stackeStackedWidget.setCurrentIndex(1)  # Shot tab
        self.assetsView.changeStackedLayoutMode(1)  # Asset tab

    def importItem(self):
        TakeName = self.take_ComboBox.currentText()
        shotNum = str(self.shot_TreeWidget.currentItem().text(0))
        sqcName = str(self.sqc_TreeWidget.currentItem().text(0))
        
        self.import_type = None
        self.set_type = None
        
        # 선택된 아이템 개수 확인하여 배치 모드 설정
        total_checked_items = 0
        for rootType in self.rootItemTypes:
            if self.dataItemStruct["partTypeCheckBox"].get(rootType) is not None:
                for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:
                    if checkBoxItem.isChecked():
                        total_checked_items += 1
        
        # 2개 이상 선택된 경우 배치 모드 활성화
        if total_checked_items > 1:
            print("Multiple items selected (%d items) - enabling batch import mode" % total_checked_items)
            utilScript.setBatchImportMode(True)
        else:
            utilScript.setBatchImportMode(False)

        for rootType in self.rootItemTypes:
                if self.dataItemStruct["partTypeCheckBox"].get(rootType) == None:
                    continue

                for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:  # check Box List
                    if checkBoxItem.isChecked() == True:
                        itemList = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem]

                        # if itemList[0] in clType:
                        type = itemList[4].currentText()
                        ref_check = 0
                        ab_check = 0
                        if type == "reference":
                            ref_check = 1
                        if type == "bundle":
                            ab_check = 1
                        print (type)
                        # objList
                        objList = {itemList[1]: self.assetinfos[rootType]["objectList"][itemList[1]]}
                        for objKey in objList:
                            if not "mergeObjectSpace" in objKey:
                                # check_type = str(clType[rootType])
                                check_type = str(rootType)
                                file_path = objList[objKey]
                                print((check_type, file_path))
                                if check_type == "camera":
                                    ref_check = 1
                                    file_path = file_path[0].replace(".py", ".abc")
                                elif check_type == "frameRange":
                                    file_path = file_path.split("/")[-1].split(".")[0]
                                elif check_type == "resolutionSet":
                                    file_path = file_path.split("/")[-1].split(".")[0]

                                # Skip - this will be handled by the chageItemType mapping below
                                pass
                        # else:
                        #    print "{} 타입을 임포트 할수 없습니다.".format(itemList[0])
                        #    continue
        else:
            projName = str(self.prj_ComboBox.currentText())
            # get take
            chageItemType = {"atom": atomScript.atomImport,
                             "ass": assScript.assImport,
                             "mmAtom": atomScript.atomImport,
                             "modelAtom": atomScript.atomImport,
                             "atomRender": atomScript.atomImport,
                             "geoCache": geoCacheScript.geoCacheImport,
                             "dummy": dummyScript.dummyImport,
                             "mmDummy": dummyScript.dummyImport,
                             "layoutDummy": dummyScript.dummyImport,
                             "modelDummy": dummyScript.dummyImport,
                             "simulGeoCache": geoCacheScript.geoCacheImport,
                             "furGeoCache": geoCacheScript.geoCacheImport,
                             "yetiCache": yetiCacheScript.yetiCacheImport,
                             "furSimGeoCache": geoCacheScript.geoCacheImport,
                             "clothGeoCache": geoCacheScript.geoCacheImport,
                             "mmGeoCache": geoCacheScript.geoCacheImport,
                             "modelGeoCache": geoCacheScript.geoCacheImport,
                             "muscleGeoCache": geoCacheScript.geoCacheImport,
                             "geoCacheRender": geoCacheScript.geoCacheImport,
                             "hairGeoCache": geoCacheScript.geoCacheImport,
                             "hairSimGeoCache": geoCacheScript.geoCacheImport,
                             "clothSimGeoCache": geoCacheScript.geoCacheImport,
                             "gpu": alembicScript.alembicImport,
                             "alembicAni": alembicScript.alembicImport,
                             "alembicCfxCrowd": alembicScript.alembicImport,
                             "alembicCrowdSim": alembicScript.alembicImport,
                             "alembicCrowdAni": alembicScript.alembicImport,
                             "usdAni": usdScript.usdImport,  # Add USD Animation import
                             "alembicModel": alembicScript.alembicImport,
                             "alembicRender": alembicScript.alembicImport,
                             "alembicFur": alembicScript.alembicImport,
                             "alembicFinalize": alembicScript.alembicImport,
                             "alembicMuscle": alembicScript.alembicImport,
                             "alembicCloth": alembicScript.alembicImport,
                             "alembicSimul": alembicScript.alembicImport,
                             "alembicCurve": alembicScript.alembicImport,
                             "alembicHair": alembicScript.alembicImport,
                             "alembicFurSim": alembicScript.alembicImport,
                             "alembicHairSim": alembicScript.alembicImport,
                             "alembicClothSim": alembicScript.alembicImport,
                             "alembicMm": alembicScript.alembicImport,
                             "alembicLayout": alembicScript.alembicImport,
                             "alembicFx": alembicScript.alembicImport,
                             "rig": rigScript.rigImport,
                             "camera": cameraScript.cameraImport,
                             "model": modelScript.modelImport,
                             "frameRange": frameRangeScript.frameRangeImport,
                             "resolutionSet": resolutionScript.resolutionImport,
                             "rigEnv": rigScript.rigImport,
                             "modelEnv": modelScript.modelImport,
                             "vdbFx": fxScript.fxImport,
                             "lookdev": lookdevScript.lookdevImport,
                             "instanceDigienv": instanceScript.instanceImport,
                             "instanceAni": instanceScript.instanceImport,
                             "instanceLayout": instanceScript.instanceImport,
                             "instanceModel": instanceScript.instanceImport,
                             "mayaHair": mayaHairScript.mayaHairImport
                             }

            for rootType in self.rootItemTypes:
                if self.dataItemStruct["partTypeCheckBox"].get(rootType) == None:
                    continue

                if rootType == "atom":
                    checked_items = [{"name": self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][1],
                                      "workCode": self.type_ComboBox.currentText(),
                                      "roottype": rootType,
                                      "atom_path": self.assetinfos["atom"]["objectList"][
                                          self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][1]],
                                      "current_rig_path": self.assetinfos["rig"]["objectList"][
                                          self.dataItemStruct["allCheckBoxItemList"][checkBoxItem][1]]
                                      } for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType] if
                                     checkBoxItem.isChecked()]

                for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:  # check Box List
                    if checkBoxItem.isChecked() == True:
                        itemList = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem]

                        # objList
                        objList = {itemList[1]: self.assetinfos[rootType]["objectList"][itemList[1]]}

                        # reference/ import
                        type = itemList[4].currentText()

                        # rig / model type select
                        if itemList[0] in ["rig", "model", "modelEnv", "lookdev", "rigEnv", "camera", "frameRange",
                                           "resolutionSet", "lightRig", "dummy", "mmDummy", "layoutDummy", "modelDummy",
                                           "vdbFx", "ass", "mayaLayoutDummy", "alembicAni", "alembicCrowdSim",
                                           "alembicCfxCrowd", "alembicCrowdAni", "alembicModel", "alembicRender",
                                           "alembicFur", "alembicMuscle", "alembicCloth", "alembicSimul", "alembicMm",
                                           "alembicLayout", "alembicFinalize", "alembicFx", "alembicCurve",
                                           "alembicHair", "alembicFurSim", "alembicHairSim", "alembicClothSim",
                                           "usdAni",  # Add USD Animation
                                           "instanceDigienv", "instanceAni", "instanceLayout",
                                           "instanceModel"]:  # combobox Item Set None
                            subImportItemType = "None"
                        elif re.match("maya", itemList[0]):
                            subImportItemType = "None"
                        elif itemList[0] == "mayaHair":
                            subImportItemType = "None"
                        elif re.match("atom", itemList[0]):
                            if type == "None":
                                subImportItemType = "atom_rig"
                            else:
                                subImportItemType = "rig"
                        else:
                            subImportItemType = itemList[3].currentText()

                        # import
                        if subImportItemType == "model":
                            print ("model")
                            importItemFn = chageItemType["model"]
                            subObjList = {itemList[1]: self.assetinfos["model"]["objectList"][itemList[1]]}
                            importItemFn(subObjList, type, rootType)

                        if subImportItemType == "rig":
                            print ("rig")
                            importItemFn = chageItemType["rig"]
                            subObjList = {itemList[1]: self.assetinfos["rig"]["objectList"][itemList[1]]}
                            importItemFn(subObjList, type, rootType)

                            # import Item
                        print((">", list(objList.keys())[0]))

                        if "rig" == rootType or "model" == rootType:
                            # low/ mid / hi
                            lod = itemList[3].currentText()
                            importItemFn = chageItemType[rootType]
                            writeItemName = importItemFn(objList, type, rootType, lod)

                        elif re.match('maya', rootType):
                            writeItemName = mayaScript.mayaImport(objList, type, rootType, projName)
                            
                        elif rootType == 'mayaHair':
                            writeItemName = mayaHairScript.mayaHairImport(objList, type, rootType, projName)

                        elif re.match('atom', rootType):
                            if subImportItemType == 'atom_rig' and self.set_type is None:
                                mp = modal_widget.SelectSet(assets=checked_items, parent=self)
                                mp.exec_()
                                self.set_type = mp.set_type
                                self.import_type = mp.import_type

                                # Cancel 버튼을 눌렀을 때 처리
                                if not mp.set_type:  # set_type이 빈 문자열이면 cancel
                                    print("SelectSet cancelled by user - importing with auto numbering")
                                    # Cancel 시에도 atom import 진행 (넘버링 자동 처리)
                                    for checkBoxItem in self.dataItemStruct["partTypeCheckBox"][rootType]:
                                        if checkBoxItem.isChecked():
                                            itemList = self.dataItemStruct["allCheckBoxItemList"][checkBoxItem]
                                            objList = {itemList[1]: self.assetinfos[rootType]["objectList"][itemList[1]]}
                                            # reference로 기본 import
                                            writeItemName = atomScript.atomImport(objList, "reference", rootType)
                                else:
                                    # 정상적으로 선택했을 때
                                    all_subObjList = [{asset['name']: asset['file']} for asset in mp.all_asset_files]
                                    importItemFn = chageItemType["rig"]
                                    for subObjList in all_subObjList:
                                        importItemFn(subObjList, self.import_type, rootType)

                            writeItemName = atomScript.atomImport(objList, type, rootType)

                        elif re.match('instance', rootType):
                            importItemFn = chageItemType[rootType]
                            writeItemName = importItemFn(objList, type, rootType, 1, TakeName, sqcName, shotNum)
                        else:
                            print("=" * 60)
                            print("CACHEEXPORT: importItem() - Processing rootType:", rootType)
                            print("CACHEEXPORT: objList:", objList)
                            print("CACHEEXPORT: type:", type)
                            print("=" * 60)
                            
                            if rootType == "usdAni":
                                print("CACHEEXPORT: usdAni detected! About to reload and call usdScript.usdImport()")
                                importlib.reload(usdScript)
                                print("CACHEEXPORT: usdScript reloaded for import")
                            
                            importItemFn = chageItemType[rootType]
                            print("CACHEEXPORT: importItemFn:", importItemFn)
                            
                            writeItemName = importItemFn(objList, type, rootType)  # type = import / reference
                            print("CACHEEXPORT: importItemFn returned:", writeItemName)

                        # update Save
                        if writeItemName:
                            # itemScript.takeUpdateCheck (objList, rootType, self.shots[self.shotItem[self.shotClass]] )
                            takeScript.takeUpdateCheck(objList, rootType, self.shots[self.shotItem[self.shotClass]])

                        # self.take()
            takeIndex = self.take_ComboBox.currentIndex()
            self.shot(self.shotClass, takeIndex)  # refresh treewidget

        # 배치 모드 비활성화
        utilScript.setBatchImportMode(False)
        
        cmd = 'DISPLAY=:O notify-send "Noar Message" "Import Complete" -t 10000'
        Popen(cmd, shell=True, stdout=PIPE)

    def setStretch(self):
        if self.topFrame.isHidden():
            self.topFrame.show()
            return
        self.topFrame.hide()

    def titleCheck(self, num, name):
        if self.title1CheckBox == name:
            for root in self.dataItemStruct["rootClass"]:
                self.dataItemStruct["rootClass"][root].setExpanded(num)
            self.title1CheckNum = num

        if self.title2CheckBox == name:
            for sub in self.dataItemStruct["subClass"]:
                sub.setExpanded(num)
            self.title2CheckNum = num

        if self.title3CheckBox == name:
            for item in self.dataItemStruct["itemClass"]:
                item.setExpanded(num)
            self.title3CheckNum = num

        # key

    def keyPressEvent(self, event):
        prj = str(self.prj_ComboBox.currentText())
        type = str(self.type_ComboBox.currentText())

        sqc_item = self.sqc_TreeWidget.currentItem()
        seqc = str(self.seqcItem[sqc_item])

        shot_item = self.shot_TreeWidget.currentItem()
        if self.shotItem.get(shot_item):
            shot = str(self.shotItem[shot_item])
        else:
            shot = ""

        if event.key() == QtCore.Qt.Key_Delete:
            treeWidget = self.focusWidget()
            if self.atom_TreeWidget == treeWidget:

                selectItem = self.atom_TreeWidget.selectedItems()
                for item in selectItem:
                    indexItem = self.atom_TreeWidget.indexOfTopLevelItem(item)

                    self.atom_TreeWidget.takeTopLevelItem(indexItem)
            elif self.geoCache_TreeWidget == treeWidget:

                selectItem = self.geoCache_TreeWidget.selectedItems()
                for item in selectItem:
                    indexItem = self.geoCache_TreeWidget.indexOfTopLevelItem(item)

                    self.geoCache_TreeWidget.takeTopLevelItem(indexItem)

            elif self.alembic_TreeWidget == treeWidget:

                selectItem = self.alembic_TreeWidget.selectedItems()
                for item in selectItem:
                    indexItem = self.alembic_TreeWidget.indexOfTopLevelItem(item)

                    self.alembic_TreeWidget.takeTopLevelItem(indexItem)

    def closeEvent(self, event):

        prj = str(self.prj_ComboBox.currentText())
        type = str(self.type_ComboBox.currentText())

        sqc_item = self.sqc_TreeWidget.currentItem()
        if not sqc_item:
            return
        seqc = str(self.seqcItem[sqc_item])

        try:
            shot_item = self.shot_TreeWidget.currentItem()
            shot = str(self.shotItem[shot_item])
        except:
            shot = ""

        assetsOpt = self.assetsView.closeAndSave()

        opt = {}
        cacheOpt = {}
        cacheOpt["prj"] = prj
        cacheOpt["type"] = type
        cacheOpt["seqc"] = seqc
        cacheOpt["shot"] = shot
        cacheOpt["topFrameisHidden"] = self.topFrame.isHidden()
        cacheOpt["title1CheckNum"] = self.title1CheckNum
        cacheOpt["title2CheckNum"] = self.title2CheckNum
        cacheOpt["title3CheckNum"] = self.title3CheckNum
        cacheOpt["envCheckNum"] = self.envCheckNum
        cacheOpt["assetsCheckNum"] = self.assetsCheckNum
        cacheOpt["matchMoveCacheCheckNum"] = self.matchMoveCacheCheckNum
        cacheOpt["layoutCacheCheckNum"] = self.layoutCacheCheckNum
        cacheOpt["aniCacheCheckNum"] = self.aniCacheCheckNum
        cacheOpt["simulCacheCheckNum"] = self.simulCacheCheckNum
        cacheOpt["modelCacheCheckNum"] = self.modelCacheCheckNum
        cacheOpt["renderCacheCheckNum"] = self.renderCacheCheckNum
        cacheOpt["fxCacheCheckNum"] = self.fxCacheCheckNum
        cacheOpt["commentPushButtonkNum"] = self.commentPushButton.isChecked()

        opt["cacheOpt"] = cacheOpt
        opt["assetsOpt"] = assetsOpt

        # cameraExportScript.saveInfo( opt )
        self.saveInfo(opt)
        self.textpubWindow.closeWindow()

    def saveInfo(self, opt):
        opt = convert_byte_to_string.convert_byte_to_string(opt)
        # global Take Save
        with open("/home/m83/maya/cacheExport.json", 'w') as f:
            json.dump(opt, f, indent=4)
    
    def copyItemNameToClipboard(self, item, column):
        """Copy item name to clipboard when Name column (column 1) is clicked"""
        if column == 1:  # Name column
            item_name = item.text(1)
            if item_name:
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(item_name)
                print(f"Copied to clipboard: {item_name}")
    
    def add_usd_tab(self):
        """Add USD tab dynamically after Alembic tab"""
        # Create USD tab widget
        usd_tab = QtWidgets.QWidget()
        usd_tab.setObjectName("usd_tab")
        
        # Create layout for USD tab
        usd_layout = QtWidgets.QVBoxLayout(usd_tab)
        usd_layout.setSpacing(0)
        usd_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create USD menu widget (similar to alembicMenuWidget)
        usd_menu_widget = QtWidgets.QWidget()
        usd_menu_widget.setObjectName("usdMenuWidget")
        usd_menu_layout = QtWidgets.QHBoxLayout(usd_menu_widget)
        usd_menu_layout.setSpacing(0)
        usd_menu_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create USD TreeWidget (copy from alembic_TreeWidget)
        self.usd_TreeWidget = QtWidgets.QTreeWidget()
        self.usd_TreeWidget.setObjectName("usd_TreeWidget")
        self.usd_TreeWidget.setMinimumSize(QtCore.QSize(260, 0))
        self.usd_TreeWidget.setFont(QtGui.QFont("", 10))
        self.usd_TreeWidget.setAlternatingRowColors(True)
        self.usd_TreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.usd_TreeWidget.setSortingEnabled(False)
        
        # Set header properties
        self.usd_TreeWidget.headerItem().setText(0, "_SET, Mesh")
        self.usd_TreeWidget.headerItem().setText(1, "step")
        self.usd_TreeWidget.headerItem().setText(2, "type")
        self.usd_TreeWidget.headerItem().setTextAlignment(0, QtCore.Qt.AlignCenter)
        self.usd_TreeWidget.headerItem().setTextAlignment(1, QtCore.Qt.AlignCenter)
        self.usd_TreeWidget.headerItem().setTextAlignment(2, QtCore.Qt.AlignCenter)
        # Set header properties to match alembic_TreeWidget exactly
        self.usd_TreeWidget.header().setDefaultSectionSize(80)  # Same as alembic
        self.usd_TreeWidget.header().setSortIndicatorShown(False)  # Same as alembic  
        self.usd_TreeWidget.header().setMinimumSectionSize(80)  # Ensure consistent header height
        self.usd_TreeWidget.header().setStretchLastSection(False)  # No stretch like alembic
        self.usd_TreeWidget.setColumnWidth(0, 347)  # Same as alembic_TreeWidget
        
        usd_menu_layout.addWidget(self.usd_TreeWidget, 3)  # Tree widget with higher stretch factor
        
        # Create right layout for USD options (same as alembic - no widget wrapper)
        usd_right_layout = QtWidgets.QVBoxLayout()
        usd_right_layout.setSpacing(5)
        usd_right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add USD step option
        usd_step_frame = QtWidgets.QFrame()
        usd_step_layout = QtWidgets.QHBoxLayout(usd_step_frame)
        
        usd_step_label = QtWidgets.QLabel("step")
        usd_step_label.setObjectName("usd_step_label")
        self.usd_opt_lineEdit = QtWidgets.QLineEdit("1")
        self.usd_opt_lineEdit.setObjectName("usd_opt_lineEdit")
        self.usd_opt_lineEdit.setMaximumSize(QtCore.QSize(40, 16777215))
        
        usd_step_layout.addWidget(usd_step_label)
        usd_step_layout.addWidget(self.usd_opt_lineEdit)
        usd_step_layout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        
        # Add USD Frame Range option (no label, just combo)
        usd_frame_frame = QtWidgets.QFrame()
        usd_frame_layout = QtWidgets.QHBoxLayout(usd_frame_frame)
        
        self.usdFrameRange_combo = QtWidgets.QComboBox()
        self.usdFrameRange_combo.setObjectName("usdFrameRange_combo")
        self.usdFrameRange_combo.addItem("FrameRange")
        self.usdFrameRange_combo.addItem("CurrentFrame")
        self.usdFrameRange_combo.addItem("setFrame")
        self.usdFrameRange_combo.setMaximumSize(QtCore.QSize(120, 16777215))
        
        usd_frame_layout.addWidget(self.usdFrameRange_combo)
        usd_frame_layout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        
        # Add USD load buttons (match alembic button sizes and text)
        self.usdGeoSetLoad_PushButton = QtWidgets.QPushButton("Geo Set Load")  # Same text as alembic
        self.usdGeoSetLoad_PushButton.setObjectName("usdGeoSetLoad_PushButton")
        self.usdGeoSetLoad_PushButton.setMinimumSize(QtCore.QSize(100, 40))  # Same as alembic
        self.usdGeoSetLoad_PushButton.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        
        self.usdSceneSetLoad_pushButton = QtWidgets.QPushButton("scene_SET load")  # Same text as alembic
        self.usdSceneSetLoad_pushButton.setObjectName("usdSceneSetLoad_pushButton")
        self.usdSceneSetLoad_pushButton.setMinimumSize(QtCore.QSize(0, 40))  # Same as alembic
        
        self.usdLoadMeshPushButton = QtWidgets.QPushButton("Load Mesh")  # Same text as alembic
        self.usdLoadMeshPushButton.setObjectName("usdLoadMeshPushButton")
        self.usdLoadMeshPushButton.setMinimumSize(QtCore.QSize(100, 40))  # Same as alembic
        self.usdLoadMeshPushButton.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        
        # Add USD export buttons (match alembic export button)
        self.usdExport_PushButton1 = QtWidgets.QPushButton("Export - Local")
        self.usdExport_PushButton1.setObjectName("usdExport_PushButton1")
        self.usdExport_PushButton1.setMinimumSize(QtCore.QSize(0, 40))  # Same as alembic
        self.usdExport_PushButton1.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.usdExport_PushButton1.setStyleSheet("background-color:rgb(65,138,255); font-size:14px; font-weight:bold;")
        
        self.usdExportFarm_PushButton = QtWidgets.QPushButton("Export - Farm")
        self.usdExportFarm_PushButton.setObjectName("usdExportFarm_PushButton")
        self.usdExportFarm_PushButton.setMinimumSize(QtCore.QSize(0, 40))  # Same as alembic
        self.usdExportFarm_PushButton.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.usdExportFarm_PushButton.setStyleSheet("background-color:rgb(255,138,65); font-size:14px; font-weight:bold;")
        
        # Add widgets to right layout (Frame Range above step)
        usd_right_layout.addWidget(usd_frame_frame)
        usd_right_layout.addWidget(usd_step_frame)
        usd_right_layout.addWidget(self.usdGeoSetLoad_PushButton)
        usd_right_layout.addWidget(self.usdSceneSetLoad_pushButton)
        usd_right_layout.addWidget(self.usdLoadMeshPushButton)
        usd_right_layout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        usd_right_layout.addWidget(self.usdExport_PushButton1)
        usd_right_layout.addWidget(self.usdExportFarm_PushButton)
        
        # Create widget container for right layout with fixed width
        usd_right_widget = QtWidgets.QWidget()
        usd_right_widget.setLayout(usd_right_layout)
        usd_right_widget.setMaximumWidth(200)  # Limit right panel width
        usd_right_widget.setMinimumWidth(150)  # Ensure minimum width
        
        usd_menu_layout.addWidget(usd_right_widget, 0)  # Add with stretch factor 0
        usd_layout.addWidget(usd_menu_widget)
        
        # Insert USD tab after Alembic tab, before Yeti (index 3)
        # Alembic is tab 2, so USD will be tab 3, and Yeti becomes tab 4
        self.shotTabWidget.insertTab(3, usd_tab, "USD")
        
        # Connect USD export buttons
        self.usdExport_PushButton1.clicked.connect(lambda: self.noahExport("usd", "local", self.usd_TreeWidget))
        self.usdExportFarm_PushButton.clicked.connect(lambda: self.noahExport("usd", "farm", self.usd_TreeWidget))
        
        # Connect USD load buttons  
        self.usdGeoSetLoad_PushButton.clicked.connect(self.usdGeoSetLoad)
        self.usdSceneSetLoad_pushButton.clicked.connect(self.usdSceneSetLoad)
        self.usdLoadMeshPushButton.clicked.connect(self.usdLoadMesh)
        
    def usdGeoSetLoad(self):
        """Load USD Geo SET - similar to alembicGeoSetLoad"""
        print("=" * 60)
        print("CACHEEXPORT: usdGeoSetLoad() BUTTON CLICKED")
        print("=" * 60)
        
        if not self.multiBtn_checkBox.isChecked():
            self.usd_TreeWidget.clear()

        lodType = self.lod_ComboBox.currentText()
        print('CACHEEXPORT: lodType >>>>>>>>>>>>>>>>', lodType)
        
        print("CACHEEXPORT: About to reload and call usdScript.usdAllLoadSet()")
        try:
            importlib.reload(usdScript)
            print("CACHEEXPORT: usdScript reloaded successfully")
            selectList = usdScript.usdAllLoadSet(lodType)
            print("CACHEEXPORT: usdScript.usdAllLoadSet() returned:", selectList)
        except Exception as e:
            print("CACHEEXPORT: ERROR calling usdScript.usdAllLoadSet():", str(e))
            import traceback
            traceback.print_exc()
            return

        if not selectList:
            return

        # Load USD objects similar to alembicLoadMesh
        for i in selectList:
            attrDic = selectList[i]
            print('attrDic :', attrDic)

            treeItem = QtWidgets.QTreeWidgetItem(self.usd_TreeWidget)
            treeItem.setText(0, i)
            treeItem.setText(1, attrDic["step"])
            treeItem.setText(2, attrDic["type"])
            treeItem.attrDic = attrDic

        cmds.select(cl=1)
        
    def usdSceneSetLoad(self):
        """Load USD Scene SET - similar to alembicSceneSetLoad"""
        print("=" * 60)
        print("CACHEEXPORT: usdSceneSetLoad() BUTTON CLICKED")
        print("=" * 60)
        
        if not self.multiBtn_checkBox.isChecked():
            self.usd_TreeWidget.clear()

        print("CACHEEXPORT: About to reload and call usdScript.usdSceneSetLoad()")
        try:
            importlib.reload(usdScript)
            print("CACHEEXPORT: usdScript reloaded successfully")
            selectList = usdScript.usdSceneSetLoad()
            print("CACHEEXPORT: usdScript.usdSceneSetLoad() returned:", selectList)
        except Exception as e:
            print("CACHEEXPORT: ERROR calling usdScript.usdSceneSetLoad():", str(e))
            import traceback
            traceback.print_exc()
            return

        if not selectList:
            return

        # Load USD scene objects 
        for i in selectList:
            attrDic = selectList[i]
            print('attrDic :', attrDic)

            treeItem = QtWidgets.QTreeWidgetItem(self.usd_TreeWidget)
            treeItem.setText(0, i)
            treeItem.setText(1, attrDic["step"])
            treeItem.setText(2, attrDic["type"])
            treeItem.attrDic = attrDic

        cmds.select(cl=1)

    def usdLoadMesh(self):
        """Load USD selected mesh objects - similar to alembicLoadMesh"""
        print("=" * 60)
        print("CACHEEXPORT: usdLoadMesh() BUTTON CLICKED")
        print("=" * 60)
        
        if not self.multiBtn_checkBox.isChecked():
            self.usd_TreeWidget.clear()

        print("CACHEEXPORT: About to reload and call usdScript.usdLoadMesh()")
        try:
            importlib.reload(usdScript)
            print("CACHEEXPORT: usdScript reloaded successfully")
            selectList = usdScript.usdLoadMesh()
            print("CACHEEXPORT: usdScript.usdLoadMesh() returned:", selectList)
        except Exception as e:
            print("CACHEEXPORT: ERROR calling usdScript.usdLoadMesh():", str(e))
            import traceback
            traceback.print_exc()
            return

        if not selectList:
            return

        # Load USD selected objects 
        for i in selectList:
            attrDic = selectList[i]
            print('attrDic :', attrDic)

            treeItem = QtWidgets.QTreeWidgetItem(self.usd_TreeWidget)
            treeItem.setText(0, i)
            treeItem.setText(1, attrDic["step"])
            treeItem.setText(2, attrDic["type"])
            treeItem.attrDic = attrDic

        cmds.select(cl=1)


# global cacheExportWin
def cacheExport():
    if "cacheExportWin" in globals():
        cacheExportWin.close()
    # global cacheExportWin

    cacheExportWin = MainWindow()
    cacheExportWin.show()

    # shotgun load
    '''
    cacheExportWin.loadingSvg = QtSvg.QSvgWidget(cacheExportWin.filepath + "/icon/loading.svg")
    cacheExportWin.loadingSvg.setFixedSize(100, 100)
    cacheExportWin.shotgunGridLayout.addWidget(cacheExportWin.loadingSvg)
    cacheExportWin.loadingSvg.hide()

    cacheExportWin.shotgunSvg = QtSvg.QSvgWidget(cacheExportWin.filepath + "/icon/shotgunIcon.svg")
    cacheExportWin.shotgunSvg.show()
    cacheExportWin.shotgunGridLayout.addWidget(cacheExportWin.shotgunSvg)
    #setShotgun(cacheExportWin)
    #shotgunLoad = ShotgunLoad(cacheExportWin)
    #shotgunLoad.setShotgun()
    '''




# Clarisse-related imports removed for Maya-only mode

# ---------------------------------------------------------------
# Shotgun settings
# ---------------------------------------------------------------

'''
class ShotgunLoad():
    def __init__(self, noahWin):
        self.noahWin = noahWin

    def setShotgun(self):
        self.noahWin.loadingSvg.show()
        self.noahWin.shotgunSvg.hide()

        projV = str(self.noahWin.prj_ComboBox.currentText())
        sqc_item = self.noahWin.sqc_TreeWidget.currentItem()
        shot_item = self.noahWin.shot_TreeWidget.currentItem()
        if projV is not None and sqc_item is not None and shot_item is not None:
            seqV = str(sqc_item.text(0))
            shotV = str(shot_item.text(0))

            # shotgun load
            #shotgunThread = ShotgunLoad(cacheExportWin, projV, seqV, shotV)
            shotgunThread = ShotgunThread(cacheExportWin, projV, seqV, shotV)
            shotgunThread.shotgunSignal.connect(self.shotgunLoaded)

            #shotgunThread.shotgunSignal.connect(lambda shotInfo, loadingSvgV=self.noahWin.loadingSvg, shotgunSvgV=self.noahWin.shotgunSvg,windowV=self.noahWin: self.shotgunLoaded(shotInfo, loadingSvgV, shotgunSvgV, windowV))
            shotgunThread.start()
            #shotgunThread.join()
        else :
            self.noahWin.loadingSvg.hide()
            self.noahWin.shotgunSvg.show()

    def shotgunLoaded(self, shotInfo):
        loadingSvg = self.noahWin.loadingSvg
        shotgunSvg = self.noahWin.shotgunSvg
        noahWin = self.noahWin

        noahWin.shotgunListWidget.clear()
        loadingSvg.hide()
        shotgunSvg.show()

        #if shotInfo != None:
        if shotInfo is not None:
            for i in shotInfo['assets']:
                assetName = i['name']
                noahWin.shotgunListWidget.addItem(assetName)

#class ShotgunLoad(QtCore.QThread):
class ShotgunThread(QtCore.QThread):
    #shotgunSignal = QtCore.pyqtSignal('PyQt_PyObject')
    shotgunSignal = QtCore.Signal(object)
    #def __init__(self, noahWin, projV, seqV, shotV, parent=getMayaWindow()):
    def __init__(self, noahWin, projV, seqV, shotV, parent=None):
        super(ShotgunThread, self).__init__(parent)
        self.projV = projV
        self.seqV = seqV
        self.shotV = shotV

    def run(self):
        shotInfo = shotgunScript.getShotInfo(self.projV, self.seqV, self.shotV)
        self.shotgunSignal.emit(shotInfo)
'''
