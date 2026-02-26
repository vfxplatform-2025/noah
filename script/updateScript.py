# -*- coding:utf-8 -*-
'''
Created on Jul 20, 2015
  
@author: m83
'''
  
import sys
from PyQt5 import QtCore, QtWidgets
import imp

sys.path.append("/home/m83/workspace/scripts/5_Ani/2_cache")
   
#from cacheExport.script import cameraExportScript
#reload(cameraExportScript)
   
from . import atomScript
imp.reload(atomScript)
    
from . import geoCacheScript
imp.reload(geoCacheScript)
    
# from cameraExport.script import simulGeoCacheScript
# reload(simulGeoCacheScript)
    
from . import cameraScript
imp.reload(cameraScript)
    
from . import dummyScript
imp.reload(dummyScript)
    
from . import rigScript
imp.reload(rigScript)
    
from . import modelScript
imp.reload(modelScript)


from . import frameRangeScript
imp.reload(frameRangeScript)
 
from . import resolutionScript
imp.reload(resolutionScript)
 
from . import modelEnvScript
imp.reload(modelEnvScript)


class TableWidget(QtWidgets.QWidget):
    def __init__(self,dictItem,takeDir, parent=None):
        super(TableWidget, self).__init__()
        
        num = 0
        for i in dictItem:
            num += len(dictItem[i])

        self.resize(900, 100 + (30*num))
        self.setWindowTitle( "UPDATE")
        
        self.dictItem =dictItem
        self.takeDir = takeDir
#         print self.dictItem, '<<<'
        self.tableWidget = QtWidgets.QTableWidget(self)
          
        self.tableWidget.setColumnCount(5)
#         self.tableWidget.setRowCount(5)
        self.pressetsDir=""

        #self.font = EditFont()
        self.setRowTable()
        #self.tableWidget.setFont(self.font)
        self.tableWidget.setHorizontalHeaderLabels(["","Type", "Item", "Opt","Path"])
  
        self.tableWidget.setColumnWidth(0, 20)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setColumnWidth(2, 150)
  
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.setAlternatingRowColors(True)
        #self.tableWidget.setShowGrid(False)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.tableWidget.itemClicked [QtWidgets.QTableWidgetItem, int].connect(lambda i, name = self.select:self.select(name))

        self.buttonOk = QtWidgets.QPushButton("Load")
        self.buttonOk.setFixedSize(100,25)

        self.buttonCancel = QtWidgets.QPushButton("Cancel")
        self.buttonCancel.setFixedSize(100,25)

        self.buttonCheck = QtWidgets.QPushButton("Check")
        self.buttonCheck.setFixedSize(100,25)
        self.checkType = 0

        self.buttonOk.clicked .connect(self.okButton)
        self.buttonCancel.clicked .connect(self.cancelButton)
        self.buttonCheck.clicked .connect(self.checkButton)

        Hlayout = QtWidgets.QHBoxLayout()

        Hlayout.addWidget(self.buttonCheck )
        spacerItem = QtWidgets.QSpacerItem(20,40,  QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Minimum)
        Hlayout.addItem(spacerItem)
        Hlayout.addWidget(self.buttonCancel )
        Hlayout.addWidget(self.buttonOk )
        Hlayout.setAlignment(QtCore.Qt.AlignRight)
        Hlayout.setSpacing(0)
        Hlayout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout()        
        layout.addWidget(self.tableWidget)
        layout.addLayout(Hlayout)
        self.setLayout(layout)

        self.setStyleSheet("QComboBox {background-color: transparent;}")

    def setRowTable(self):
        #dictItem= {'model': {'OkYunA': '/show/AS/assets/cha/OkYunA/model/pub/OkYunA_model_v01.mb'}, 'geoCache': {'OkYunA3:geoCache_SET': '/show/AS/seq/CF/CF_156/ani/wip/data/geoCache/CF_156_ani_v01_w47_text/OkYunA3.mc'},
        #'anim': {'OkYunA': '/show/AS/assets/cha/OkYunA/model/pub/OkYunA_model_v01.mb'}}
   
        itemList = []
        for partType in self.dictItem:
            for item in self.dictItem[partType]:
                itemList.append( [partType , item, self.dictItem[partType][item]] )

        self.getPressets = itemList
        self.tableWidget.setRowCount(len(self.getPressets))

        self.comboBoxDict = {}
        self.checkBoxDict = {}

        for num, row in enumerate(self.getPressets):
            comboBox = QtWidgets.QComboBox()
            comboBox.setFixedSize(100,25)
    
            checkBox = QtWidgets.QCheckBox()
            checkBox.setFixedSize(100,25)
                
            self.comboBoxDict[num]=comboBox
            self.checkBoxDict[num]=checkBox
#                
            for num1, col in enumerate(row):
                if type( col ) == type( [] ):
                    item = QtWidgets.QTableWidgetItem(col[0])
                else:
                    item = QtWidgets.QTableWidgetItem(col)
                #vrayPresset = re.search("((?<=/)\w+_\w+(?=\.mel))", row).group()
                #item.setFont(self.font)
                item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsEnabled) 

                if num1 == 0:
                    self.tableWidget.setCellWidget(num, 0,checkBox)
                    comboBoxOpt ={ "rig" :["reference", "import"], "model" :[ "reference", "import"], "atom" :["import"], 
                    "geoCache" :["import"], "simulGeoCache" :["import"], "dummy" :["reference", "import" ],"camera" :["import"],
                    "frameRange":["import"],"modelEnv":["reference","import"], "resolutionSet": ["import"] }
                    comboBox.addItems(comboBoxOpt[col])

                if num1 > 1 :
                    self.tableWidget.setItem(num, num1+2, item)
                else:
                    self.tableWidget.setItem(num, num1+1, item)

                if num1 != 2:
                    item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)     #text               
            self.tableWidget.setCellWidget(num, 3,comboBox)


    def select(self, name):
        num = self.tableWidget.currentRow()
        comClass = self.comboBoxDict[num]
        checkClass = self.checkBoxDict[num]


#         print checkClass.isChecked()
#         print comClass.currentText()
#         print self.getPressets[num]
  
  
    def okButton(self):
        checkRow = []
        for i in self.checkBoxDict:
            if self.checkBoxDict[i].isChecked():
                checkRow.append(i)


        objectList = {}
        for num in checkRow:
            type = self.comboBoxDict[num].currentText()
            itemList={ self.getPressets[num][1]: self.getPressets[num][2]}
            item =self.getPressets[num][1]
            i = self.getPressets[num][0]

            objectList[i]=[itemList, str(type)]


        chageItemType = { "atom"        : atomScript.atomImport,  
                         "geoCache"     : geoCacheScript.geoCacheImport, 
                         "dummy"        : dummyScript.dummyImport,
                         "simulGeoCache": geoCacheScript.geoCacheImport,
                         "rig"          : rigScript.rigImport,
                         "camera"       : cameraScript.cameraImport,
                         "model"        : modelScript.modelImport,
                         "frameRange"   : frameRangeScript.frameRangeImport,
                         "resolutionSet": resolutionScript.resolutionImport,
                         "modelEnv"     : modelEnvScript.modelEnvImport}


        rootItemTypes = ["camera", "model", "modelEnv","dummy", "rig",  "atom", "geoCache","simulGeoCache","frameRange","resolutionSet"]
#         objectList = map(lambda x : cmds.getAttr("%s" %x).split(",")[0], cmds.ls("*.%s" %rootType, r=1) )

        for rootType in rootItemTypes:
            if objectList.get( rootType ):
                getItem = objectList[rootType][0]
                type = objectList[rootType][1]
                importItemFn = chageItemType[ rootType ]
                importItemFn(getItem , type, rootType)


#         if "":
#             if "rig" == i:
#                 rigScript.rigImport( itemList, type )
#    
#             if "model" == i:
#                 modelScript.modelImport( itemList, type )
#    
#             if "atom" == i:
#                 if "import" == type:
#                     atomScript.atomImport( itemList )
# #                     print itemList[i] #{u'gunShot1:ctrl_SET': u'/show/JM/seq/EO/EO_055/ani/wip/data/ani/EO_055_ani_v01_w02_test/gunShot1.atom'} 
#    
#             if "geoCache" == i:
#                 if "import" == type:
#                     #print "key", itemList[i]
#                     geoCacheScript.geoCacheImport( itemList, type ,"geoCache")
#     
#     
#             if "simulGeoCache" == i:
#                 if "import" == type:
#                     geoCacheScript.geoCacheImport( itemList, type, "simulGeoCache")
#     
#             if "camera" == i:
#                 if "import" == type:
#                     if self.assetinfos["ani"]["camera"].get("imagePlaneList"):
#                         imagePlane = self.assetinfos["ani"]["camera"]["imagePlaneList"]
#                     else:
#                         imagePlane={}
#                     cameraScript.cameraImport(itemList,imagePlane)
#     
#             if "dummy" == i: #{u'BG_guide_grp': u'/show/JM/seq/EO/EO_055/ani/wip/data/dummy/EO_055_ani_v01_w02_test.mb'}
#                 if "import" == type:
#                     dummyScript.dummyImport( itemList )
#                 elif "reference" == type:
#                     dummyScript.dummyReferenceImport( itemList )


    def checkButton(self):
        if self.checkType == 0:
            for i in self.checkBoxDict:
                    self.checkBoxDict[i].setChecked(1)
            self.checkType=1
        else:
            for i in self.checkBoxDict:
                    self.checkBoxDict[i].setChecked(0)
            self.checkType=0

#         if not checkRow:
#             self.tableWidget.currentRow()
  
#     def colorChecked(self, check=None, type=None, item=None):
#           
#         try:
#             self.assetinfos = cameraExportScript.assetInfoList ("" , self.takeDir)
#         except:
#             return
#           
#                   
#         for x in self.assetinfos:
# #             print x
#             for y in self.assetinfos[x]:
# #                 print y,'<'
#                 if y == type:
# #                     for z in self.assetinfos[x][type]:
#                     for i in self.assetinfos[x][type]["objectCheck"]:
#   
#                         if item == i:
#                             self.assetinfos[x][type]["objectCheck"][i] = 0   
#                             cameraExportScript.assetSaveInfoList(self.takeDir, self.assetinfos)

  
    def cancelButton(self):
        self.close()
  
def updateScript(data, take):
#     print data
    window = TableWidget(data, take)
    window.show()
      
      
