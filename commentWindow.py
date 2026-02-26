# -*- coding:utf-8 -*-
'''
Created on Jun 8, 2015

@author: m83
'''

import os
import json

from cacheExport_module.pyside2_moduleImport import *

# from QtTopUiLoader import *
import QtTopUiLoader
import imp
from script import convert_byte_to_string


class DataStruct(object):
    def __init__(self):
        self.messageInfo = ""
        #self.rootNames = self.messageInfo.keys()
        self.prjdir = ""
        
#         "0001"   : { 
#         "username": "chulho", 
#         "comment": "\ud55c\uae00 \ud14c\uc2a4\ud2b8", 
#         "title"  : "\ud55c\uae00 \ud14c\uc2a4", 
#         "objectCheck": {"lookdev": 1, "fur": 1,"layout": 1,"fx": 1,"clothSim": 1,"ani": 1,"hair": 1,"cloth": 1,"dyn": 1,"matchmove": 1,"rig": 1,"model": 1,"lit": 1}, 
#         "ipaddr" : "192.168.12.69", 
#         "tag"    : [ "Jstone_model_v01_w01" ], 
#         "date"   : "2015-11-12 10:50", 
#         "part"   : "model"   }

        self.itemClass={}
        self.itemClass["treeItem"]   = {}
        self.itemClass["checkBox"]   = {}
        self.itemClass["comboBox1"]  = {}
        self.itemClass["comboBox2"]  = {}
        self.itemClass["allCheckBoxItemList"]= {}
        self.itemClass["allTreeWidgetItemList"]= {}
        
        self.itemClass["partTypeCheckBox"]={}
        self.itemClass["allItemClass"]  = {}
        self.itemClass["rootClass"]  = {}
        self.itemClass["subClass"]   = {}
        self.itemClass["itemClass"]  = {}
    
    def getTake(self, dir):
        commentdir = "%s/Comment/comment.json" %dir
        
        if os.path.isfile( commentdir):
            with open("%s" %commentdir, 'r' ) as f:
                self.take = json.load(f)
        else:
            self.take = {}
        return self.take

    def deleteAssetSaveInfoList(self, takeNameDir, data):
        if not takeNameDir:
            return
        data = convert_byte_to_string.convert_byte_to_string(data)
        with open( "%s" %takeNameDir, 'w') as f:
            json.dump(data, f, indent =4)
            
    def setList(self, itemList):
        for i in itemList:
            if isinstance(i, QtWidgets.QCheckBox):
                self.itemClass["allCheckBoxItemList"].update(itemList )
                
                if self.itemClass["partTypeCheckBox"].get(itemList[i][0]) == None:
                    self.itemClass["partTypeCheckBox"][ itemList[i][0] ]=[]
                self.itemClass["partTypeCheckBox"][ itemList[i][0] ].append(i)
                
            else:
                self.itemClass["allTreeWidgetItemList"].update(itemList )


    def setWidget(self, rootType, itemList):        
        if rootType in self.itemClass["allItemClass"]:
            self.itemClass["allItemClass"][rootType].update(itemList)
        else:
            self.itemClass["allItemClass"].update( {rootType : None } )
            self.itemClass["allItemClass"][rootType] = itemList

        
    def set(self, itemList, rootType =None):
        for item in itemList: 

            font = QtGui.QFont()
            font.setPointSize(9)
            if isinstance(item, QtWidgets.QTreeWidgetItem):
                classType = 'treeItem'
            elif isinstance(item, QtWidgets.QCheckBox):
                classType = 'checkBox'
            elif isinstance(item, QtWidgets.QComboBox):
                classType = 'comboBox'

            if classType == "comboBox":
                if item.objectName() == "opt1":
                    classType = "comboBox1"
                    if item.count() == 0:
                        item.addItems(["None", "model", "rig"])
                        item.setFont(font)

                else:
                    classType = "comboBox2"
                    if item.count() == 0:
                        if rootType in [ "camera", "frameRange", "resolutionSet", "dummy", "mmDummy","modelDummy" ]:
                            item.addItems([ "import"])
                            item.setFont(font)
                        elif rootType in [ "rig" , "model", "modelEnv", "rigEnv"]:
                            item.addItems([ "reference", "import"])
                            item.setFont(font)
                        else:
                            item.addItems(["None", "reference", "import"])
                            item.setFont(font)

            
#             # set Item
            if item not in self.itemClass[ classType ]:
                self.itemClass[ classType ][item ]=[]
                 
            if item in self.itemClass[ classType ]:
                if itemList[item] not in self.itemClass[ classType ][item] and itemList[item] != None: # current item
                    self.itemClass[ classType ][item].append( itemList[item])
#                     print self.itemClass[ classType ][item]
                     
            if itemList[item] != None:
                for selRootItem in self.itemClass[ classType ]:                   
                    if item in self.itemClass[ classType ][selRootItem]: # allitem
                        if  itemList[item] not in self.itemClass[ classType ][selRootItem]:
                            self.itemClass[ classType ][selRootItem].append( itemList[item])


class customTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self,  parent=None, takeinfo=None ):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        
        self.textinfoTree = QtWidgets.QTreeWidgetItem(self)
        self.takeinfo = takeinfo
        
        self.username = self.takeinfo['username'] 
        self.comment = self.takeinfo['comment' ] 
        self.title = self.takeinfo['title'    ]
        self.objectCheck = self.takeinfo['objectCheck']
        self.ipaddr = self.takeinfo['ipaddr']     
        self.number = self.takeinfo['number']
        self.tag = self.takeinfo['tag']
        self.date = self.takeinfo['date']
        self.part = self.takeinfo['part']
        
        self.setTexts()
        self.setColors()                               
#         self.addCheckBox(parent)
        self.addButton(parent)
        self.setExpand()
        self.updateColor()

    def setExpand(self):
        self.setExpanded(1)

    def setTexts(self):
#         self.setText(0, self.number)
        self.setText(0, "%s" %self.number)
        self.setText(1, self.title)
        self.setText(2 ,"%s \n %s" %(self.username,self.date ) )
        self.setTextAlignment(2, 5)                     ## TreewidgetItem setTextAlignment 
        self.textinfoTree.setText(1, self.comment)
    
    def addCheckBox(self, parent):
        self.checkBox = QtWidgets.QCheckBox(self.number)
        self.checkBox.setObjectName(self.number)
        parent.setItemWidget( self, 0, self.checkBox)
    
    def addButton(self, parent):
        
        self.buttonWidget = QtWidgets.QWidget()
        self.buttonWidget.setLayout(QtWidgets.QHBoxLayout())
        self.buttonWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.buttonWidget.layout().setSpacing(3)

        self.editPushButton  = QtWidgets.QPushButton( "Edit" )
        self.deletePushButton  = QtWidgets.QPushButton( "Delet" )
        
        self.editPushButton.setStyleSheet("border: 1px solid gray;")
        self.editPushButton.setMinimumSize(50,20 )
        self.deletePushButton.setStyleSheet("border: 1px solid gray;")
        self.deletePushButton.setMinimumSize(50,20 )

        self.buttonWidget.layout().addWidget( self.editPushButton )
        self.buttonWidget.layout().addWidget( self.deletePushButton )

        parent.setItemWidget( self.textinfoTree, 2, self.buttonWidget)
                
        
    def setColors(self):
        list(map(lambda x : self.setBackground(x, QtGui.QBrush( QtGui.QColor( 80, 100 , 255, 30) )), list(range(3))))
        self.textinfoTree.setBackground(1, QtGui.QBrush( QtGui.QColor( 255, 255, 255 , 10) ))
#         map(lambda x : self.textinfoTree.setBackground(x, QtGui.QBrush( QtGui.QColor( 80, 255, 100 , 30) )), range(2))

    def updateColor(self):
        font = QtGui.QFont()
        font.setBold(1)

        list(map(lambda x : self.setFont(x, font), list(range(3))))
        list(map(lambda x : self.setForeground(x, QtGui.QBrush( QtGui.QColor( 255, 255 , 255, 255) )) , list(range(2))))
        
        font1 = QtGui.QFont()
        font1.setPointSize(7)
        self.setFont(0, font1)


class stackeStackedWidget(QtWidgets.QWidget):
    def __init__(self, prj=None,part=None, parent=None):
        super(stackeStackedWidget, self).__init__(parent)
        
        filepath = os.path.abspath(__file__ + "/../")
        QtTopUiLoader.UiLoader().loadUi(filepath + "/commentWindow.ui", self)

        self.prjdir = prj
        self.partType= part
        self.editTakeNum = None
        
        self.commentTreeWidget.setStyleSheet("""QTreeWidget#commentTreeWidget { background-color: rgba(0, 0, 0,0);}  
            QHeaderView::section {background-color: rgb( 72, 75, 82 ); border: 1px solid transparent;} """) #::item{ border: 1px solid gray;}

        self.writePushButton1.clicked.connect(self.write1)
        self.commentTreeWidget.itemClicked[QtWidgets.QTreeWidgetItem, int].connect(self.commentOpen)
        self.commentTreeWidget.itemDoubleClicked[QtWidgets.QTreeWidgetItem, int].connect(self.commentOpen)

#         self.commentTreeWidget.setColumnWidth(1, 300)
        self.commentTreeWidget.header().setStretchLastSection(False)
        self.commentTreeWidget.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self.commentTreeWidget.setColumnWidth(2, 130)

        self.readComment()

#         self.commentTreeWidget.setMinimumWidth(0)

    def readComment(self):
        self.commentTreeWidget.clear()
        self.dataStruct = DataStruct()
        self.currentTake = self.dataStruct.getTake( self.prjdir )
        Takelist = list(self.currentTake.keys())
        Takelist.sort(reverse=True)
        if self.currentTake :
            for i in Takelist :
                self.customTreeItem = customTreeWidgetItem(self.commentTreeWidget, self.currentTake[i] )
                self.dataStruct.itemClass["rootClass"].update ( {self.customTreeItem : i })
#                 print self.customTreeItem, self.customTreeItem.text(1)
                # emit
                #self.customTreeItem.deletePushButton.clicked.connect(lambda i, name = self.customTreeItem:  self.itemDelete(name))
                #self.customTreeItem.editPushButton.clicked.connect(lambda i, name = self.customTreeItem:  self.itemEdit(name))
                self.customTreeItem.deletePushButton.clicked.connect(lambda name = self.customTreeItem:  self.itemDelete(name))
                self.customTreeItem.editPushButton.clicked.connect(lambda name = self.customTreeItem:  self.itemEdit(name))
                # self.connect(self.customTreeItem.deletePushButton, QtCore.SIGNAL("clicked()"), lambda name = self.customTreeItem:  self.itemDelete(name) )
                # self.connect(self.customTreeItem.editPushButton, QtCore.SIGNAL("clicked()"), lambda name = self.customTreeItem:  self.itemEdit(name) )

    def setPrjDir(self, dir, part):
        self.prjdir = dir
        self.partType= part
        self.dataStruct.getTake( dir)
        self.readComment()

    def addWrite(self):

        font = QtGui.QFont()
        font.setPointSize(10)
        # creat item
        self.titleTreeWidgetItem = QtWidgets.QTreeWidgetItem( self.commentTreeWidget )
        self.titleTreeWidgetItem.setExpanded(1)

        self.messageTreeWidgetItem = QtWidgets.QTreeWidgetItem( self.titleTreeWidgetItem )
        self.messageTreeWidgetItem.setSizeHint(1, QtCore.QSize(0,400))

        # set color, font, text
        self.titleTreeWidgetItem.setTextAlignment(0, QtCore.Qt.AlignCenter)
        list(map(lambda x : self.titleTreeWidgetItem.setFont(x, font), list(range(2))))
        list(map(lambda x : self.messageTreeWidgetItem.setFont(x, font), list(range(2))))
#         map(lambda x : self.titleTreeWidgetItem.setBackground(x, QtGui.QBrush( QtGui.QColor( 255, 255 , 255, 40) )), range(2))
        list(map(lambda x : self.messageTreeWidgetItem.setBackground(x, QtGui.QBrush( QtGui.QColor( 255, 255 , 255, 20) )), list(range(2))))

        self.titleTreeWidgetItem.setText(0, "Title")

        # add item
        self.messageWidget = QtWidgets.QFrame()
        self.messageWidget.setLayout( QtWidgets.QVBoxLayout())
        self.titleLineEdit = QtWidgets.QLineEdit()
        self.titleLineEdit.setFont(font)
        self.commentTreeWidget.setItemWidget( self.titleTreeWidgetItem, 1,self.titleLineEdit)
        self.commentTreeWidget.setItemWidget( self.messageTreeWidgetItem, 1, self.messageWidget)

        #creat edit
        self.commentTextEdit = QtWidgets.QTextEdit()
        #self.commentTextEdit.setMinimumWidth(400)
        self.commentTextEdit.setFont(font)
        self.messageWidget.layout().addWidget( self.commentTextEdit )

#         top_frame.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised)

        # creat option button
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setSpacing(10)

#         self.editPushButton = QtGui.QPushButton( "Edit" )
        self.okPushButton  = QtWidgets.QPushButton( "OK" )
        self.canclePushButton  = QtWidgets.QPushButton( "Cancle" )

        self.okPushButton.setStyleSheet("border: 1px solid gray;")
        self.okPushButton.setMinimumSize(50,20 )
        self.canclePushButton.setStyleSheet("border: 1px solid gray;")
        self.canclePushButton.setMinimumSize(50,20 )

        self.buttonLayout.addSpacerItem( QtWidgets.QSpacerItem(1000,20) )
#         self.buttonLayout.addWidget( self.editPushButton )

        self.buttonLayout.addWidget( self.canclePushButton )
        self.buttonLayout.addWidget( self.okPushButton )

        self.okPushButton.clicked.connect(self.saveMessage)
        self.canclePushButton.clicked.connect(self.cancleMessage)
        # self.connect ( self.okPushButton , QtCore.SIGNAL("clicked()"), self.saveMessage)
        # self.connect ( self.canclePushButton , QtCore.SIGNAL("clicked()"), self.cancleMessage)
        self.messageWidget.layout().addLayout( self.buttonLayout )

    def write1(self):
        self.commentTreeWidget.clear()
        self.addWrite()
        
    def saveMessage(self):
        commentText = str( self.commentTextEdit.toPlainText() )  + "\n"
        commentTitle = str( self.titleLineEdit.text() )

        fileList = {  commentTitle:commentText }
        
        from .script import commentScript 
        imp.reload(commentScript)
        
        self.commentData = commentScript.commentScript(fileList)
        self.commentData.exportComment(self.prjdir, str(self.partType), self.editTakeNum)
        
        self.editTakeNum = None
        self.commentTreeWidget.clear()
        self.readComment()
        
    def cancleMessage(self):
        self.commentTreeWidget.clear()
        self.readComment()
    
    def commentOpen(self, name):
        if name in self.dataStruct.itemClass["rootClass"]:            
            name.setExpanded(not(name.isExpanded()) )
    
    def itemDelete(self, name):
        ret = QtWidgets.QMessageBox.question(self, "Question Message",
              '''Do you want to Delete Item?''', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
        
        if ret == QtWidgets.QMessageBox.Cancel:
            return
        
        globalTake = self.currentTake
        takeDir = "%s/Comment/comment.json" %self.prjdir
        
        numberKey = self.dataStruct.itemClass["rootClass"][name]
        globalTake.pop(numberKey)
        
        self.dataStruct.deleteAssetSaveInfoList( takeDir, globalTake)
        
        self.commentTreeWidget.clear()
        self.readComment()
        
    def itemEdit(self, name):
        self.write1()
        self.titleLineEdit.setText("%s" %name.title) 
        self.commentTextEdit.setText("%s" %name.comment)
        self.editTakeNum = self.dataStruct.itemClass["rootClass"][name]
#         self.commentData.exportComment(self.prjdir, self.partType , self.editTakeNum)  # take num  #################
                
