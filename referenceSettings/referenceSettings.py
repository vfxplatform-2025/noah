# -*- coding:utf-8 -*-
'''
Created on May 30, 2016

@author: m83
'''

import os
import maya.cmds as cmds
import imp

# PySide6 로 변경
from PySide6 import QtWidgets, QtGui, QtCore

from . import QtTopUiLoader
imp.reload(QtTopUiLoader)
from . import nodeModel
imp.reload(nodeModel)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # 디버깅: 실제 로드되는 파일 경로 확인
        print(f"DEBUG: referenceSettings.py loaded from: {__file__}")
        
        # __file__ 기준으로 UI 파일 경로 설정 및 오류 처리
        this_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(this_dir, "meshReplace.ui")
        
        if not os.path.exists(ui_path):
            raise RuntimeError(f"UI file not found: {ui_path}")
            
        try:
            QtTopUiLoader.UiLoader().loadUi(ui_path, self)
            print(f"DEBUG: UI loaded successfully from {ui_path}")
            
            # UI 위젯들이 제대로 로드되었는지 확인
            if hasattr(self, 'assetInfoTreeWidget'):
                print("DEBUG: assetInfoTreeWidget found")
            else:
                print("DEBUG: ERROR - assetInfoTreeWidget NOT found!")
                
            if hasattr(self, 'checkBoxAll'):
                print("DEBUG: checkBoxAll found")
            else:
                print("DEBUG: ERROR - checkBoxAll NOT found!")
                
        except Exception as e:
            raise RuntimeError(f"Failed to load UI file {ui_path}: {str(e)}")

        self.setWindowTitle("Reference Settings")
        self.treeNameDitc = {}
        self.setObjectName("meshReplace")

        # signal-slot 연결
        self.checkBoxAll.stateChanged[int].connect(lambda: self.searchItem(self.checkBoxAll))
        self.checkBoxModel.stateChanged[int].connect(lambda: self.searchItem(self.checkBoxModel))
        self.checkBoxRigging.stateChanged[int].connect(lambda: self.searchItem(self.checkBoxRigging))
        self.checkBoxLookdev.stateChanged[int].connect(lambda: self.searchItem(self.checkBoxLookdev))
        self.importReferencePushButton.clicked.connect(self.importReference)


    def initUI(self):
        w = self.assetInfoTreeWidget
        w.setColumnWidth(0, 80)
        w.setColumnWidth(1, 40)
        w.setColumnWidth(2, 260)
        w.setColumnWidth(3, 60)
        w.setColumnWidth(4, 100)
        w.setColumnWidth(5, 160)
        w.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        w.sortItems(1, QtCore.Qt.AscendingOrder)
        
        self.selectList = []
        self.selectGrpList = []

        self.checkBox_root  = QtWidgets.QCheckBox()
        self.assetInfoTreeWidget.setItemWidget( self.rootItem, 0, self.checkBox_root)
        
        for item in self.treeNameDitc:
            self.creatOptions(self.treeNameDitc[item], "itemGrp")
            
            for num in range(self.treeNameDitc[item].childCount()):
                self.creatOptions(self.treeNameDitc[item].child(num), "item")
                self.treeNameDitc[item].checkBox.stateChanged[int].connect(self.treeNameDitc[item].child(num).checkBox.setChecked)
#                 self.connect( self.treeNameDitc[item].comboBox, QtCore.SIGNAL( 'activated (int)'), lambda x,className = self.treeNameDitc[item].child(num).comboBox: self.comboboxGrpChange(x, className) )
                self.treeNameDitc[item].comboBox.activated [int].connect(lambda x, name=self.treeNameDitc[item].child(num): self.comboboxGrpChange(x, name))


    # set font
    def setFonts(self, fontSize, Bold, italic):
        font = QtGui.QFont()
        font.setPointSize(fontSize)
        font.setBold(Bold)
        font.setItalic(italic)
        for i in range(9):
            self.setFont(i, font)
        
    def checkBoxDelet(self, name):
        self.selectList.remove(name)
#         print ">>>", self.selectList
        
    def checkBoxAdd(self, name):
        self.selectList.append(name)
#         print ">>>", self.selectList

    def checkBoxGrpDelet(self, name):
        self.selectGrpList.remove(name)
#         print ">>>", self.selectGrpList
        
    def checkBoxGrpAdd(self, name):
        self.selectGrpList.append(name)
#         print ">>>", self.selectGrpList

    def comboboxGrpChange(self, num, name):
        
        if name.checkBox.isChecked():
            if (num-1) < 0:
#                 currentNum = name.comboBox.findText("%s"% name.currentFilename)
#                 name.comboBox.setCurrentIndex(currentNum)
                return
        
            name.comboBox.setCurrentIndex(num-1)
        
    def changeItem(self, treename):
        
        if treename.currentFilename == treename.comboBox.currentText():  ################################################ 중요 @@@@@@@@@@@@@@@
            return
        if treename.checkBox.isChecked():
            dirNode = cmds.referenceQuery(treename.name, filename=1)
            referNode = cmds.referenceQuery(dirNode , referenceNode=True)  # 프록시 경로로 노드 검색
            importList = cmds.file("%s"%treename.list[str(treename.comboBox.currentText())], loadReference="%s"%referNode ,type="mayaBinary", options="v=0;", returnNewNodes=1)
            
            self.setTreeItem(cmds.ls(importList, type="transform")[0], treename)
            treename.currentFilename = treename.comboBox.currentText()

    def changeActiveItem(self, treename):
        dirNode = cmds.referenceQuery(treename.name, filename=1)
        referNode = cmds.referenceQuery(dirNode , referenceNode=True)  # 프록시 경로로 노드 검색
        importList = cmds.file("%s"%treename.list[str(treename.comboBox.currentText())], loadReference="%s" %referNode ,type="mayaBinary", options="v=0;", returnNewNodes=1)
        
        self.setTreeItem( cmds.ls(importList, type="transform")[0], treename )            
        treename.currentFilename = treename.comboBox.currentText()
    
    def importReference(self):
        itemList = list(self.selectList)
        parentList = []
        for item in itemList:
            cmds.file(item.currentRefdir, importReference=True)
            
                    
            self.assetInfoTreeWidget.removeItemWidget(item, 0)
            self.assetInfoTreeWidget.removeItemWidget(item, 5)
            parentItem = item.parent() 
            parentItem.removeChild(item)
            
            if parentItem.childCount() == 0:
                parentList.append(parentItem )
                
            self.selectList.remove( item )
            self.selectGrpList.remove( item )
        
        # parent 0 delete
#         print parentList
        for grp in parentList:
            self.assetInfoTreeWidget.removeItemWidget(grp, 0)
            self.assetInfoTreeWidget.removeItemWidget(grp, 5)
            parentgrp = grp.parent() 
            parentgrp.removeChild(grp)
            
            self.selectGrpList.remove( grp )
                

    def creatOptions(self, name, type=None):
        #check Box
        self.selectType = {0 : self.checkBoxDelet, 2 : self.checkBoxAdd}
        self.selectGrpType = {0 : self.checkBoxGrpDelet, 2 : self.checkBoxGrpAdd}
        
        name.checkBox  = QtWidgets.QCheckBox()
        self.assetInfoTreeWidget.setItemWidget( name, 0, name.checkBox)        
        name.checkBox.stateChanged[int].connect(lambda x : self.selectGrpType[x]( name ))
        
        #combo Box
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        name.comboBox = QtWidgets.QComboBox()
        name.comboBox.setFont(font)
        name.comboBox.setStyleSheet("QComboBox {background-color: transparent;}")
        self.assetInfoTreeWidget.setItemWidget( name, 5, name.comboBox)
        
        #add text item
        if type == "item":
            name.comboBox.addItems( name.listName )
            name.comboBox.setCurrentIndex ( name.comboBox.findText("%s" %name.currentFilename) )
            name.checkBox.stateChanged[int].connect(lambda x : self.selectType[x]( name ))
            name.comboBox.currentIndexChanged[int].connect(lambda : self.changeItem( name))
            name.comboBox.activated [int].connect(lambda : self.changeActiveItem( name))
            
        elif type == "itemGrp":
            name.comboBox.addItem("None")
            name.comboBox.addItems( name.listName )
            self.checkBox_root.stateChanged[int].connect(name.checkBox.setChecked)


    def searchItem(self, name):
        if not name.isChecked() :
            return
        if not self.selectGrpList:
            return

        type = { "checkBoxModel" :"model",  "checkBoxRigging":"rig","checkBoxLookdev":"lookdev", "checkBoxAll" : "All"}
        typeName = type["%s" %name.objectName()]


        for item in self.selectGrpList:
            num = item.comboBox.findText("%s" %item.comboBox.currentText() )
            for i in range( item.comboBox.count()-1, -1, -1):
                if num == i:
                    continue
                item.comboBox.removeItem(i)
            
            itemList = list(item.list.keys())
            itemList.sort()
             
            if typeName == "All":
                for comboBoxItemName in itemList:
                    item.comboBox.addItem( comboBoxItemName)
            else:
                for comboBoxItemName in itemList:
                    if  "/%s/" %typeName in item.list[comboBoxItemName]:# i.name, i.list
                        item.comboBox.addItem( comboBoxItemName)
    
    
    def modelSet(self):
        self.rootItem = QtWidgets.QTreeWidgetItem (self.assetInfoTreeWidget)
        self.rootItem.setExpanded(1)
        self.rootItem.setText(2, "All" )
        
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setItalic(True)
            
        list(map(lambda x : self.rootItem.setFont(x, font), list(range(7))))
        list(map(lambda x : self.rootItem.setBackground(x, QtGui.QBrush( QtGui.QColor( 80, 100 , 255, 130) )), list(range(10))))
         
#         for i in list(set(map(lambda x : cmds.ls(cmds.listHistory(x)[0],l=1)[0].split('|')[1], cmds.ls("*.model" , r=1) ) )):
#             if cmds.referenceQuery(i, isNodeReferenced  =1) :
        refs = cmds.ls(type='reference')
        if "sharedReferenceNode" in refs:
            refs.remove("sharedReferenceNode")
        if "_UNKNOWN_REF_NODE_" in refs:
            refs.remove("_UNKNOWN_REF_NODE_")
        for i in refs :

            if cmds.referenceQuery(i, f=1) :
                            
                # Get Maya Info
                objName = cmds.referenceQuery(i, n=1, dp=1)[0]
                print(f"DEBUG: Processing reference object: {objName}")
                node = nodeModel.Node(objName)
                
                try:
                    print("DEBUG: Calling setCurrentDir...")
                    node.setCurrentDir ( node )
                    print("DEBUG: Calling setNum...")
                    node.setNum( node.name )
                    print("DEBUG: Calling setCurrentFileName...")
                    node.setCurrentFileName ( node.name)
                    print("DEBUG: Calling setAssetName...")
                    node.setAssetName ( node.currentdir)
                    print("DEBUG: Calling setAssetDir...")
                    node.setAssetDir ( node.currentdir )
                    print("DEBUG: Calling setrefNodeName...")
                    node.setrefNodeName ( node.name )
                    print("DEBUG: Calling setList...")
                    node.setList( node.currentdir )
                    print("DEBUG: Calling setpubDir...")
                    node.setpubDir ( node.currentdir )
                    print("DEBUG: Calling setMeshType...")
                    node.setMeshType( node.currentFilename)
                    print("DEBUG: Calling setCurrentType...")
                    node.setCurrentType( node.currentdir )
                    print("DEBUG: Node processing completed successfully")
                except Exception as e:
                    print(f"DEBUG: ERROR processing node: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue

#                 print '---'
#                 print "node.name", node.name
#                 print "node.currentdir", node.currentdir
#                 print "node.curretRefdir", node.currentRefdir
#                 print "node.currentFilename", node.currentFilename                
#                 print "node.assetName", node.assetname
#                 print "node.assetDir", node.assetdir
#                 print "node.refname", node.refname                
# #                 print "node.dir", node.dir  
#                 print "node.list", node.list 
#                 print "node.listName", node.listName
#                 print "node.meshtype", node.meshtype
#                 print '-' * 100

                # creat Qtreewidget
                self.assetItem = QtWidgets.QTreeWidgetItem ()  # create item
                self.assetItem.name = node.name
                self.assetItem.num = node.num
                self.assetItem.currentdir = node.currentdir
                self.assetItem.currentRefdir = node.currentRefdir
                self.assetItem.currentFilename= node.currentFilename
                self.assetItem.assetdir = node.assetdir 
                self.assetItem.refname = node.refname 
                self.assetItem.list = node.list
                self.assetItem.listName = node.listName 
                self.assetItem.meshtype = node.meshtype
                self.assetItem.currenttype = node.currenttype

                self.assetItem.setText(1, " %s" %self.assetItem.num )
                self.assetItem.setText(2, " %s" %self.assetItem.name )
                self.assetItem.setText(3, " %s" %self.assetItem.currenttype)
                self.assetItem.setText(4, " %s" %self.assetItem.meshtype)
#                 map(lambda x : self.assetItem.setForeground(x, QtGui.QBrush( QtGui.QColor( 80, 255 , 0, 160) )), range(10))
                # asset Item GRP
                if node.assetname not in self.treeNameDitc:
                    font1 = QtGui.QFont()
                    font1.setPointSize(10)
                    font1.setBold(True)
                    font1.setItalic(True)
                    self.assetItemGrp = QtWidgets.QTreeWidgetItem(self.rootItem)
                    list(map(lambda x : self.assetItemGrp.setFont(x, font1), list(range(7))))
                    list(map(lambda x :self.assetItemGrp.setBackground(x, QtGui.QBrush( QtGui.QColor( 80, 255 , 0, 70) )), list(range(10))))
#                     self.assetItemGrp.setStyleSheet("border: 2px solid yellow;border-radius: 10px; font:  12px; color :yellow ; background-color : rgb(50, 80 , 100); ")
                    self.assetItemGrp.setExpanded(1)
                    self.assetItemGrp.addChild( self.assetItem )
                    
                    self.assetItemGrp.name = node.assetname
                    self.assetItemGrp.listName = node.listName
                    self.assetItemGrp.list = node.list
                    
                    self.assetItemGrp.setText(2, " %s" %node.assetname ) 
                    self.treeNameDitc[ node.assetname ] = self.assetItemGrp
                else:
                    self.assetItemGrp.addChild( self.assetItem )
                self.assetItemGrp.setText( 1, "%d" %self.assetItemGrp.childCount())
                
    def setTreeItem(self, name, treeItem ):
        node = nodeModel.Node(name)
        node.setCurrentDir ( node )
        node.setNum( node.name )
        node.setCurrentFileName ( node.name)
        node.setAssetName ( node.currentdir)
        node.setAssetDir ( node.currentdir )
        node.setrefNodeName ( node.name )
        node.setList( node.currentdir )
        node.setpubDir ( node.currentdir )
        node.setMeshType( node.currentFilename)
        node.setCurrentType( node.currentdir )

#         print '---'
#         print "node.name", node.name
#         print "node.currentdir", node.currentdir
#         print "node.currentFilename", node.currentFilename                
#         print "node.assetName", node.assetname
#         print "node.assetDir", node.assetdir
#         print "node.refname", node.refname                
# #                 print "node.dir", node.dir  
#         print "node.list", node.list 
#         print "node.listName", node.listName
#         print "node.meshtype", node.meshtype
#         print '-' * 100

        # creat Qtreewidget

        treeItem.name = node.name
        treeItem.num = node.num
        treeItem.currentdir = node.currentdir
        treeItem.currentRefdir = node.currentRefdir
        treeItem.currentFilename= node.currentFilename
        treeItem.assetdir = node.assetdir 
        treeItem.refname = node.refname 
        treeItem.list = node.list
        treeItem.listName = node.listName 
        treeItem.meshtype = node.meshtype
        treeItem.currenttype = node.currenttype

        treeItem.setText(1, " %s" %treeItem.num )
        treeItem.setText(2, " %s" %treeItem.name )
        treeItem.setText(3, " %s" %treeItem.currenttype)
        treeItem.setText(4, " %s" %treeItem.meshtype)
def meshReplace():
    global window
    window = MainWindow()
    window.show()
    window.modelSet()
    window.initUI()


