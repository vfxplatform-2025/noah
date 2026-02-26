# -*- coding:utf-8 -*-
'''
Created on Jun 25, 2015

@author: m83
'''

import os, sys, glob, re, string
import maya.cmds as cmds
import maya.mel as mel
import getpass
from subprocess import *
import xml.etree.ElementTree as et
import json
import socket
import datetime
from script import convert_byte_to_string




#find
def getFileName():
     
    fileDir = cmds.file (q=1, exn = 1)
    
    fileName = fileDir.rsplit('/', 1)[1].split('.')[0]
    fileInfo =  [fileName, fileDir]
    
    return  fileInfo

# def assetGetFileName():
#      
#     fileDir = cmds.file (q=1, exn = 1)
#     print ">", fileDir.rsplit('/', 1)
#     fileName = fileDir.rsplit('/', 1)[1].split('.')[0]
#     fileInfo =  [fileName, fileDir]
#     
#     return  fileInfo



# def versionUpTakeName(asstInfoDir, fileName):
#      
#     takeListDir = glob.glob("%s/%s.*.json" %(asstInfoDir,fileName) )
#     takeListDir.sort()
#     takeList = {}
#     newNum ="0001"
#      
#     
#     if takeListDir:
#         currentTake = takeListDir[-1]
#         
#         currentNum  = re.search ("(?<=\.).*[0-9]{4}", currentTake).group()
#         newNum = "%04d" %( int(currentNum) +1 )
#         
#         newTake = currentTake.replace(currentNum, "%s" %newNum)
#         
# #         takeName = re.search ("(?<=\/)[a-z]+\.[0-9]{4}", currentTake).group()
#         takeName = re.search ("[\w]+.[0-9]{4}.json*$", currentTake).group()
#         
#     else:
# #         takeListDir = []
#         newTake = "%s/%s.0001.json" % (asstInfoDir,fileName)
#         currentTake = "%s/%s.0001.json" % (asstInfoDir,fileName)
#         takeName = "%s.0001" %fileName
#         currentNum = "0001"
# #         takeList[takeName]=newTake
# 
#     return currentTake, newTake, takeName 


# Export  ----------------------------------------------------------------------------------------

# 모델링 검색 항목에 맞게 데이타  분리

def itemRootAssetNameCheck(itemdir): #export 2	
    itemName = itemdir.split("/")[5]

    fileNameList = itemLodAssetNameCheck(itemName)

    #if not cmds.ls(itemName):
    if not fileNameList:
        print("( model Sciprt 76 line ) Erro : Not match Asset Name !!  ")
        return

    #cmds.select(itemName)
    cmds.select(fileNameList, r=True)
    return itemName
# 
# def itemRootAssetNameCheck(itemdir): #export 2
#     itemName = itemdir.split("/")[5]
#     if not cmds.ls(itemName):
#         print "( model Sciprt 85 line ) Erro : Not match Asset Name !!  "
#         return
#     cmds.select(itemName) 
#     return itemName

def itemLodAssetNameCheck(itemName):
    fileNameCheck = ["XHI", "HI", "MID", "LOW", "XLOW", "PROXY"]

    fileNameList = []
    if cmds.objExists(itemName):
        fileNameList.append(itemName)

    for i in fileNameCheck:
        lodName = "{}_{}".format(itemName, i)
        if cmds.objExists(lodName):
            fileNameList.append(lodName)

    return fileNameList

def itemAssetNameCheck(itemdir):
    itemName = itemdir.split("/")[5]
    # AssetName Check
    notMatchObjectName = []
    selectObjectList =  cmds.listRelatives(itemName, ad=1)
    objectList = cmds.ls(selectObjectList, type="transform")
    for i in objectList:
        front_itemName = re.search ("^%s_" %itemName, i)
        if not front_itemName :
            notMatchObjectName.append( i )
    notMatchObjectName.sort()
    return notMatchObjectName
            
def itemAssetShapeNameCheck(itemdir):
    itemName = itemdir.split("/")[5]
    # ShapName Check
    notMatchShapeName = {}

    fileNameList = itemLodAssetNameCheck(itemName)

    for fileName in fileNameList:

        selectObjectList =  cmds.listRelatives(fileName, ad=1)
        objectList = cmds.ls(selectObjectList, type="transform")
        objectShapeList = cmds.ls(selectObjectList, type=["mesh", "nurbsCurve"])

        for i in objectList :
            shapeName = cmds.ls( i, dag=1, type=["mesh", "nurbsCurve"])

            try:
                if cmds.listRelatives(i, s=1) :
                    shapeName = shapeName [0]
                else:
                    continue

                nameV = i.split("|")[-1]
                shapeCheck = shapeName.split("|")
                if len(shapeCheck) == 1:
                    newShapeName = "{}Shape".format(nameV)
                else:
                    newShapeName = "{}|{}Shape".format(i, nameV)

                if shapeName != newShapeName :
                    notMatchShapeName.update( {shapeName :newShapeName })
            except:
                continue
            
    return notMatchShapeName

# rename
def assetNameRename(rootName,  assetNames):
#     print rootName,  assetNames
    for i in assetNames:
        cmds.rename (i , "%s_%s" %(rootName, i))

def assetShapeNameRename( assetShapeName):
    for i in assetShapeName:
        cmds.rename (i , "%s" %assetShapeName[i])
#     return False

def modelExport(fileName, itemdir, itemName=None):  # exort 5
    #    CF_156_ani_v01_w47_text
    #    /show/AS/seq/CF/CF_156/ani/wip/data/geoCache/CF_156_ani_v01_w47_text
    #    OkYunA3:geoCache_SET
    #    10

    print("===============script model Export okokok+========================")
    fileinfo = {}
    # itemLodAssetNameCheck 에서 LOD 선택됨
    objName = cmds.ls(sl=1)[0].split("_")[0]


    """
    fileNameCheck = ["XHI", "HI", "MID", "LOW", "XLOW", "PROXY"]
    for i in fileNameCheck:
        proxyName = "{}_{}".format(objName[0], i)
        if cmds.objExists(proxyName):
            cmds.select(proxyName, add=True)
    """

    #for i in objName:
    #    fileinfo[i] = "%s/%s.mb" % (itemdir, fileName)
    fileinfo[objName] = "%s/%s.mb" % (itemdir, fileName)

    pubMod(itemName, "%s/%s.mb" % (itemdir, fileName))
    cmds.file("%s/%s.mb" % (itemdir, fileName), force=1, options="v=0;", typ="mayaBinary", pr=1, es=1, ch=0, chn=0,
              exp=0, con=0)
    return fileinfo


def itemExport( fileName, itemdir, itemName = None):   # exort 5
#    CF_156_ani_v01_w47_text
#    /show/AS/seq/CF/CF_156/ani/wip/data/geoCache/CF_156_ani_v01_w47_text
#    OkYunA3:geoCache_SET
#    10
    
    print("===============script item Export okokok+========================")
    fileinfo = {}
    objName = cmds.ls(sl=1)

    for i in objName: 
        fileinfo [ i ] = "%s/%s.mb" %(itemdir, fileName)
    
    pubMod(itemName, "%s/%s.mb" %(itemdir, fileName) )
    cmds.file ("%s/%s.mb" %(itemdir, fileName), force=1,  options="v=0;" ,typ= "mayaBinary", pr=1, es=1, ch=0, chn=0, exp=0, con=0 )    
    return fileinfo

##################################
# item Tag
##################################
def pubMod(itemName, itemDir):
    if not cmds.ls( ["%s" %itemName, "%s_*" %itemName] ,r=1, type="transform"):
        print("(modelScirpt - 166) : Don't write Tag")
        return
    
    for i in cmds.ls( ["%s" %itemName, "%s_*" %itemName] ,r=1, type="transform"):
        if not cmds.ls('%s.model' %i):
            cmds.addAttr ('%s' %i, ln= "model", dt= "string" )
        cmds.setAttr('%s.model' %i, "%s,%s" %( itemName, itemDir ) ,type="string")
    
#     #check
#     cmds.select (list(set(map(lambda x : x.split(".")[0], cmds.ls("*.model", r=1)) )))
#     mel.eval( "HideSelectedObjects" )
#     cmds.select (cl=1)
#     return {item : fileDir }



def versionUpTakeName(asstInfoDir, fileName):
     
    takeListDir = glob.glob("%s/%s.*.json" %(asstInfoDir,fileName) )
    takeListDir.sort()
    takeList = {}
    newNum ="0001"
     
    
    if takeListDir:
        currentTake = takeListDir[-1]
        
        currentNum  = re.search ("(?<=\.).*[0-9]{4}", currentTake).group()
        newNum = "%04d" %( int(currentNum) +1 )
        
        newTake = currentTake.replace(".%s." %currentNum, ".%s." %newNum)
        
#         takeName = re.search ("(?<=\/)[a-z]+\.[0-9]{4}", currentTake).group()
        takeName = re.search ("[\w]+.[0-9]{4}.json*$", currentTake).group()
        
    else:
#         takeListDir = []
        newTake = "%s/%s.0001.json" % (asstInfoDir,fileName)
        currentTake = "%s/%s.0001.json" % (asstInfoDir,fileName)
        takeName = "%s.0001" %fileName
        currentNum = "0001"
#         takeList[takeName]=newTake
    #print takeName
    return currentTake, newTake


def getFileList(dir = None):
    # file Dir 
    if dir == None:
        fileDir = cmds.file(q=1, sn=1)
        if "_LOW.mb" in fileDir:
            fileDir = fileDir.replace("_LOW.mb", ".mb")
        elif "_MID.mb" in fileDir:
            fileDir = fileDir.replace("_MID.mb", ".mb")
        elif "_HI.mb" in fileDir:
            fileDir = fileDir.replace("_HI.mb", ".mb")
        elif "_XLOW.mb" in fileDir:
            fileDir = fileDir.replace("_XLOW.mb", ".mb")
        elif "_XHI.mb" in fileDir:
            fileDir = fileDir.replace("_XHI.mb", ".mb")
    else:
        fileDir = dir
    
    # os path
    if fileDir:
        if sys.platform == "win32":
            fileDir = fileDir.replace("Q:/", "/show/")
#     fileName = os.path.basename(fileDir ).split('.')[0]
    # find data
    prjDir = re.search( ".+(?=/[\w]+/(pub|wip)/)",fileDir ).group()
    partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()
    fileName = re.search( "[\w]+(?=\.mb)",fileDir  ).group()        
    if "_LOW.mb" in fileName:
        fileName = fileName.replace("_LOW.mb", ".mb")
    elif "_MID.mb" in fileName:
        fileName = fileName.replace("_MID.mb", ".mb")
    elif "_HI.mb" in fileName:
        fileName = fileName.replace("_HI.mb", ".mb")
    elif "_XLOW.mb" in fileName:
        fileName = fileName.replace("_XLOW.mb", ".mb")
    elif "_XHI.mb" in fileName:
        fileName = fileName.replace("_XHI.mb", ".mb")

    globalTakeDir = "%s/Take" %prjDir
    localTakeDir = "%s/%s/wip/data/Take" % (prjDir, partType)

    return prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir  


def checkTake(itemType, currentTake ):
    takeDir = currentTake.rsplit("/", 1)[0]
    # check dir
    if not os.path.isdir(takeDir):
        os.makedirs(takeDir)

    # global Take
    if not os.path.isfile( currentTake ):
        take = {}

    else:
        with open("%s" %( currentTake ), 'r' ) as f:
            take = json.load(f)

    if not take.get(itemType):
        take["%s" %itemType] ={}
    return take

def saveTake(newTakeDir, take):
    # global Take Save

    take = convert_byte_to_string.convert_byte_to_string(take)
    with open("%s" %newTakeDir, 'w') as f:
        json.dump(take,  f, indent=4)


def assetInfoExport(objList, take,  fileDir, newTakeDir, userName=None):
    #(u'/show/DH/assets/cha/daeho', u'/show/DH/assets/cha/daeho/model/pub/daeho_model_v04.mb', u'model', u'daeho_model_v04', u'/show/DH/assets/cha/daeho/Take', u'/show/DH/assets/cha/daeho/model/wip/data/Take') # 
    # model = {} 
    #take  ={"model": {'username': {u'wolf': 'chdef versionUpTakeName(asstInfoDir, fileName):

    if "_LOW" in list(objList.values())[0]:
        itemType="modelLow"
    elif "_MID" in list(objList.values())[0]:
        itemType="modelMid"
    elif "_HI" in list(objList.values())[0]:
        itemType="modelHi"
    elif "_XLOW" in list(objList.values())[0]:
        itemType="modelXLow"
    elif "_XHI" in list(objList.values())[0]:
        itemType="modelXHi"
    else:
        itemType="model"
    
     
    # asset info
    newTake={}
    newTake[ itemType ] = {}
    newTake[ itemType ]["fileName"] = {}
    newTake[ itemType ]["version"]  = {}
    newTake[ itemType ]["username"] = {}
    newTake[ itemType ]["ipaddr"]   = {}
    newTake[ itemType ]["frame"]    = {}
    newTake[ itemType ]["date"]     = {}
    newTake[ itemType ]["objectList"] ={}
    newTake[ itemType ]["objectCheck"]={}
    newTake[ itemType ]["updateList"] ={}


    globalversionDict={}

    for item in objList:
        # file Name
        newTake[ itemType ]["fileName"].update( { item : fileDir} )

        #take local version
        newTake[ itemType ]["version"].update( { item : newTakeDir} )
        #globalversionDict.update( { item : globalNewNum} )

        # user info
        if userName is None:
            userName = socket.gethostname()
        newTake[ itemType ]["username"].update({ item : userName})

        #ipaddr
        cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
        getipaddr = Popen(cmd, shell = True, stdout = PIPE)
        ipaddr = getipaddr.communicate()[0][:-1]
        newTake[ itemType ]["ipaddr"].update({ item : ipaddr})

        # frame info
        startF = cmds.playbackOptions(min=1, q=1)
        endF   = cmds.playbackOptions(max=1, q=1)
        newTake[ itemType ]["frame"].update({ item : ""})#"%d-%d" %(startF, endF)})

        # date info
        nowdate = str(datetime.datetime.now())
        date = nowdate.rsplit(":",1)[0]
        newTake[ itemType ]["date"].update({ item :  date})

        #object List info
        newTake[ itemType ]["objectList"].update({ item :  objList[item] } )
        
        if "/seq/" in fileDir:
        #object check info
            checkList = {"model":0, "rig" : 0,"ani":1, "matchmove":1, "layout":1, "dyn":0, "cloth":0,"hair":0, "clothSim":0, "lit" : 0, "fur":0, "lookdev" : 0 ,"fx" : 0 }
        else:
            checkList = {"model":1, "rig" : 1,"ani":1, "matchmove":1, "layout":1, "dyn":1, "cloth":1,"hair":1, "clothSim":1, "lit" : 1, "fur":1, "lookdev" : 1 ,"fx" : 1 }

        newTake[ itemType ]["objectCheck"].update({ item :  checkList} )

        #update List info
        newTake[ itemType ]["updateList"].update({ item :  objList[item]})

    # setTake
    addTake={}
    if take.get(itemType) == None:
        take[ itemType ] = {}
        
    if take[ itemType ].get('objectList'):  # is itemType
        addTake =  takeSetInfo(newTake, take, itemType, "objListReplace"  )
    else:
        addTake =  takeSetInfo(newTake, take, itemType, "newItem"  )
        #-------------------------------------------------------- 
    return addTake

def takeSetInfo(newTake, take, itemType, type):
    if type == "objListReplace": #objListReplace 와 newObject는 덮어 씌우는 것 
        for i in newTake[itemType]:
            take[itemType][ i ].update( newTake[itemType][i] ) 
    elif type == "newItem":
        take[itemType] = newTake[itemType]
    return take


# objList = pubMod()
# takeTypeList = ["globalTake", "localTake"]
# exportTake(objList, takeTypeList, "model")

def exportTake(objList, takeTypeList, itemType, userName=None):
    # global? local? Take
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()

    modelData = {}
    notFoundModel = {}
        
    for takeType in takeTypeList:
        # Take Type select
        if takeType == "globalTake":
            currentTake,  newTakeDir   = versionUpTakeName(globalTakeDir, "take")
        elif takeType == "localTake":    
            currentTake,  newTakeDir   = versionUpTakeName(localTakeDir, "%s" %fileName)

        # check Take
        #itemType = "model"

        getTake = checkTake( itemType,  currentTake )
        take = {}
        if prjDir.split("/")[3] in ["assets"] and partType in ["model"]: #daeho  Asset model.
            # write AssetInfo
            take = assetInfoExport(objList, getTake, fileDir, newTakeDir, userName=userName)

        elif partType in ["ani", "matchmove","model" ,"lit", "lookdev", "layout", "crowdAni"]: #daeho1:daeho
            take  = getTake
            for assetName in objList:
                assetTake = findAsset( assetName,takeType ) #{u'username': {u'daeho': u'DOM'}, u'objectCheck': {u'daeho': {u'lit': 1, u'rig': 1, u'model': 1, u'fx': 1, u'lookdev': 1}}, u'frame': {u'daeho': u'1-120'}, u'ipaddr': {u'daeho': u''}, u'fileName': {u'daeho': u'/show/DH/assets/cha/daeho/model/pub/daeho_model_v01.mb'}, u'version': {u'daeho': u'/show/DH/assets/cha/daeho/Take/take.0013.json'}, u'updateList': {u'daeho': u'/show/DH/assets/cha/daeho/model/pub/daeho_model_v01.mb'}, u'date': {u'daeho': u'2015-08-21 18:58'}, u'objectList': {u'daeho': u'/show/DH/assets/cha/daeho/model/pub/daeho_model_v01.mb'}} #
                
                if assetTake != None:
                    modelData.update ( assetTake["objectList"] )
                    if "model" in partType:
                        take = addTake(take, assetTake, assetName, "modelEnv")

                    else:
                        take = addTake(take, assetTake, assetName, "model")

                else:
                    notFoundModel[assetName]=""
        else:
            print("None Team!")
#         print notFindModel
        
        # saveTake
        if take.get(itemType) : 
            saveTake( newTakeDir, take )

    # notOb
    notOb = ""
    for i in notFoundModel:
        notOb += "%-45s \n" %i    

    if notOb:
        cmds.confirmDialog( title='Not Found Model', message=notOb, button=['ok'])
     
    return modelData

#=======================================
def exportTakeAssets(objList, takeTypeList, itemType):
    # global? local? Take
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()            
    
#     print "prjDir", prjDir
#     print "fileDir", fileDir
#     print "partType", partType
#     print "fileName", fileName
#     print "globalTakeDir", globalTakeDir
#     print "localTakeDir", localTakeDir
    
    modelData = {}
    notFoundModel = {}
        

    for takeType in takeTypeList:
        # Take Type select
        if takeType == "globalTake":
            currentTake,  newTakeDir   = versionUpTakeName(globalTakeDir, "take")
        elif takeType == "localTake":    
            currentTake,  newTakeDir   = versionUpTakeName(localTakeDir, "%s" %fileName)

        # check Take
        #itemType = "model"

        getTake = checkTake( itemType,  currentTake )

        take = assetInfoExport(objList, getTake, fileDir, newTakeDir)
        
        # saveTake 
        saveTake( newTakeDir, take )
     
#---------------------------------------------------------
#ani
#assetTake ={'username': {'daeho': 'DOM'}, 'objectCheck': {'daeho': {'lit': 1, 'rig': 1, 'model': 1, u'fx': 1, u'lookdev': 1}}, u'frame': {u'daeho': u'1-120'}, u'ipaddr': {'daeho': ''}, 'fileName': {'daeho': u'/show/DH/assets/cha/daeho/model/pub/daeho_model_v01.mb'}, 'version': {'daeho': '/show/DH/assets/cha/daeho/Take/take.0013.json'}, 'updateList': {'daeho': '/show/DH/assets/cha/daeho/model/pub/daeho_model_v01.mb'}, 'date': {'daeho': '2015-08-21 18:58'}, 'objectList': {'daeho': '/show/DH/assets/cha/daeho/model/pub/daeho_model_v01.mb'}} # 
   
def addTake(getTake, assetTake, assetName, itemType):
    # if model?

    if getTake.get( itemType ) == None:
        getTake[ itemType ] = {}
        for i in assetTake:
            getTake[ itemType ][i] ={}

    #set info
    for i in assetTake:
        for x in assetTake[i]:
#             print i, x #objectList daeho
            if getTake[ itemType ].get(i) == None:
                getTake[ itemType ][i]={}
#             print getTake["model"][i][assetName]
#             print x, assetName, getTake["model"][i][assetName]
            getTake[ itemType ][i][assetName] = assetTake[i][x]

#     print getTake["model"]["objectList"]
    return getTake


def findAsset(assetName,takeType ):
    #assetName = "daeho1:daeho"
    getTake = {}
    if cmds.ls( cmds.ls("%s*.model" %assetName) ):
        # find assetName
        objectList = {}
        selectItemDir=[]

        # find : headWolf,/show/DH/assets/cha/headWolf/model/pub/headWolf_model_v02.mb
        for i in cmds.ls("%s*.model" %assetName):
            
            if assetName.split(":")[1] == cmds.getAttr(i).split(",")[0]:
                getAssetDir = cmds.getAttr(i).split(",")[1]
                if "_LOW.mb" in getAssetDir:
                    getAssetDir = getAssetDir.replace("_LOW.mb", ".mb")
                elif "_MID.mb" in getAssetDir:
                    getAssetDir = getAssetDir.replace("_MID.mb", ".mb")
                elif "_HI.mb" in getAssetDir:
                    getAssetDir = getAssetDir.replace("_HI.mb", ".mb")
                elif "_XLOW.mb" in getAssetDir:
                    getAssetDir = getAssetDir.replace("_XLOW.mb", ".mb")
                elif "_XHI.mb" in getAssetDir:
                    getAssetDir = getAssetDir.replace("_XHI.mb", ".mb")
                selectItemDir.append(getAssetDir)
            else :
                if takeType == "globalTake":
                    print("Check Asset Info !! \n","%-10s : %s \n%-10s : %s \n%-10s : %s \n%-10s : %s\n %s" %("name", assetName,"info Name",cmds.getAttr(i).split(",")[0],"shapeName", i, "infor Path",cmds.getAttr(i).split(",")[1], "-" * 80 ))
    #                 cmds.confirmDialog( title="Check Asset Info !!", message="%-30s : %s \n%-30s : %s \n%-30s : %s \n%-30s : %s\n %s" %("name", assetName,"shapeName", i, "info Name",cmds.getAttr(i).split(",")[0],"infor Path",cmds.getAttr(i).split(",")[1], "-" * 150 ), button=['ok'])
                  

        selectItemDir.sort()
            
#             splitName = cmds.getAttr(i).split(",")
        objectList  [ "%s" %assetName ]   = selectItemDir[-1]

        #search Take
        for assetName in objectList:
            prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList(objectList[assetName ] )
            currentTake,  newTakeDir  = versionUpTakeName(globalTakeDir, "take")
            
            # find asset Take
            takeList = glob.glob("%s/*.*.json" %globalTakeDir)
            takeList.sort(reverse=1)
            
            for currentTake in takeList:
                with open("%s" %( currentTake ), 'r' ) as f:
                        take = json.load(f)
                        
                if not getTake:  
                    # sam sam Take info
                    if take.get("model").get("objectList").get( assetName.split(":")[1] ) == objectList[assetName ]:
                        #getTake =  take["model"]["objectList"][assetName.split(":")[1]]
                        getTake = take["model"]
                        return getTake


#item = {'daeho1:daeho':"/show/DH/assets/cha/daeho/model/pub/daeho_model_v01.mb"} 




    
# def getFileList():
#     fileDir = cmds.file(q=1, sn=1)
# #     fileName = os.path.basename(fileDir ).split('.')[0]
# 
#     prjDir = re.search( ".+(?=/[\w]+/(pub|wip)/)",fileDir ).group()
#     partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()
#     fileName = re.search( "[\w]+(?=\.mb)",fileDir  ).group()        
# 
#     globalTakeDir = "%s/Take" %prjDir
#     localTakeDir = "%s/%s/wip/data/Take" % (prjDir, partType)
# 
#     return prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir  
# 
# 
# def checkTake(itemType):
#     prjDir,fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
#     globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
#     localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)
# 
#     # check dir
#     if not os.path.isdir(globalTakeDir):
#         os.makedirs(globalTakeDir)
# 
#     if not os.path.isdir(localTakeDir):
#         os.makedirs(localTakeDir)
# 
#     # global Take
#     if not os.path.isfile( globalCurrentTake ):
#         take = {}
# 
#     else:
#         with open("%s" %( globalCurrentTake ), 'r' ) as f:
#             take = json.load(f)
# 
#     if not take.get(itemType):
#         take["%s" %itemType] ={}
# 
#     # local Take
#     if not os.path.isfile( localCurrentTake ):
#         local_take = {}
# 
#     else:
#         with open("%s" %( localCurrentTake ), 'r' ) as f:
#             local_take = json.load(f)
# 
#     if not local_take.get(itemType):
#         local_take["%s" %itemType] ={}
#                     
#     return take, local_take    
# 
# 
# def saveTake(itemType, take, local_take):
#     prjDir,fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
#     globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
#     localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)
# 
#     # global Take Save
#     with open("%s" %localNewTake, 'w') as f:
#         json.dump(local_take,  f, indent=4)    
# 
#     # global Take Save
#     with open("%s" %globalNewTake, 'w') as f:
#         json.dump(take,  f, indent=4)
# 
# 
# def subAssetInfoExport( objList, modelList ):
# 
#     prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
#     globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
#     localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)
#     
#     typeList = {"model":"model","rig":"model", "ani":"model","matchmove":"model", "layout":"model"}
#     itemType = typeList [partType]
# 
#     #getTake
#     take, local_take = checkTake(itemType) 
#     
#     fileNameDict= {}
#     versionDict = {}
#     userNameDict= {}
#     ipaddrDict  = {}
#     frameDict   = {}
#     dateDict    = {}
#     objectListDict ={}
#     objectCheckDict={}
#     updateListDict ={}
#     globalversionDict={}
#     
#     modelObjectList={}
# 
#     
# #     print 'modelList : ', modelList, #{u'wolf': u'/show/DH/assets/cha/wolf/model/pub/Wolf_model_v09.mb'}
# #     print objList, '<<<'   #{u'daeho1:daeho': u'/show/DH/seq/GW/GW_030/matchmove/wip/data/ani/GW_030_matchmove_v01_w01/daeho1.atom', u'wolf1:wolf': u'/show/DH/seq/GW/GW_030/matchmove/wip/data/ani/GW_030_matchmove_v01_w01/wolf1.atom'} <<<
# 
#     for item in objList:
# #         print item
#         
#         # file Name
# #         assetName = re.search("[\D]+([\w]+)?[\D]+(?=([\d]+)?:)", item ).group()
#         assetName = item.split(":")[1]
#         fileDir = modelList[assetName]
# 
#         fileNameDict.update( { item : fileDir} )
#         modelObjectList.update( { item : fileDir})  ######################<<
# 
#         #take local version
#         versionDict.update( { item : None})#localNewNum} ) #0rig
#         globalversionDict.update( { item : globalNewNum} )
# 
#         # user info
#         userName =  socket.gethostname()
#         userNameDict.update({ item : None})  #userName
# 
#         #ipaddr
#         cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
#         getipaddr = Popen(cmd, shell = True, stdout = PIPE)
#         ipaddr = getipaddr.communicate()[0][:-1]
#         ipaddrDict.update({ item : None}) #ipaddr
#         
#         # frame info
#         startF = cmds.playbackOptions(min=1, q=1)
#         endF   = cmds.playbackOptions(max=1, q=1)
#         frameDict.update({ item : None} )#"%d-%d" %(startF, endF)})
#                 
#         # date info
#         nowdate = str(datetime.datetime.now())
#         date = nowdate.rsplit(":",1)[0]
#         dateDict.update({ item :  None}) #date
#                 
#         #object List info
#         objectListDict.update({ item :  None } ) #objList[item]
# 
#         #object check info
#         checkList = {"rig" : 1,"ani":1, "lit" : 1, "lookdev" : 1, "fx" : 1 }
#         objectCheckDict.update({ item :  checkList} )
# 
#         #update List info
#         updateListDict.update({ item :  None}) #objList[item]
#                                                                                                                                                     
#     if take[ itemType ].get('objectList'):  # is itemType
# #             if take[ itemType ]['objectList'].get(item):  # is item
#         newTake =  takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, modelObjectList, objectCheckDict )
# #             else:
# #                 newTake = takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
#     else:
#         newTake = takeSetInfo(take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, modelObjectList, objectCheckDict) 
#         
#     if local_take[ itemType ].get('objectList'):  # is itemType
# #             if local_take[ itemType ]['objectList'].get(item):  # is item
# #                 local_Newtake = takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
# #             else:
#         local_Newtake = takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, modelObjectList, objectCheckDict)                
#     else:
#         local_Newtake = takeSetInfo(local_take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, modelObjectList, objectCheckDict)
#         #--------------------------------------------------------
#     
#     
#     take = newTake      
#     local_take = local_Newtake
#     
#     take[ itemType ]["updateList"]= updateListDict 
#     local_take[ itemType ]["updateList"]= updateListDict
#     
#     saveTake( itemType, take ,local_take)
# 
# 
# def takeSetInfo(take, itemType, type, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict):
#     if type == True:  
#         take[ itemType ]["fileName"   ].update( fileNameDict   )
#         take[ itemType ]["version"    ].update( versionDict    )
#         take[ itemType ]['username'   ].update( userNameDict   )
#         take[ itemType ]['ipaddr'     ].update( ipaddrDict     )
#         take[ itemType ][ 'frame'     ].update( frameDict      )
#         take[ itemType ]['date'       ].update( dateDict       )
#         take[ itemType ]['objectList' ].update( objList        )
#         take[ itemType ]['objectCheck'].update( objectCheckDict)    
#     else:
#         take[ itemType ].update( { "fileName"  : fileNameDict } )
#         take[ itemType ].update( {"version"    : versionDict  } ) 
#         take[ itemType ].update( {'username'   : userNameDict } )
#         take[ itemType ].update( {'ipaddr'     : ipaddrDict   } )
#         take[ itemType ].update( { 'frame'     : frameDict    } )
#         take[ itemType ].update( {'date'       : dateDict     } )
#         take[ itemType ].update( {'objectList' : objList      } )
#         take[ itemType ].update( {'objectCheck': objectCheckDict} )
#         
#     return take
# 
# #------------------------------------------------------------------------------------------------
# def assetInfoExport(objList): #( shotDir, objList , partType): #, itemType
#     prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
#     globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
#     localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)
# 
#     typeList = {"model":"model","rig":"model", "ani":"model","matchmove":"model", "layout":"model"}
#     itemType = typeList [partType]
# 
#     take, local_take = checkTake(itemType)
# 
#     # asset info
# #     allnameSpace= list(set(cmds.ls(sns=1)[1::2]))
# #     allnameSpace.remove(':')
# 
#     fileNameDict= {}
#     versionDict = {}
#     userNameDict= {}
#     ipaddrDict  = {}
#     frameDict   = {}
#     dateDict    = {}
#     objectListDict ={}
#     objectCheckDict={}
#     updateListDict ={}
#     globalversionDict={}
# 
#     for item in objList:
#         # file Name
#         fileNameDict.update( { item : fileDir} )
# 
#         #take local version
#         versionDict.update( { item : localNewNum} )
#         globalversionDict.update( { item : globalNewNum} )
# 
#         # user info
#         userName =  socket.gethostname()
#         userNameDict.update({ item : userName})
# 
#         #ipaddr
#         cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
#         getipaddr = Popen(cmd, shell = True, stdout = PIPE)
#         ipaddr = getipaddr.communicate()[0][:-1]
#         ipaddrDict.update({ item : ipaddr})
#         
#         # frame info
#         startF = cmds.playbackOptions(min=1, q=1)
#         endF   = cmds.playbackOptions(max=1, q=1)
#         frameDict.update({ item : "%d-%d" %(startF, endF)})
#                 
#         # date info
#         nowdate = str(datetime.datetime.now())
#         date = nowdate.rsplit(":",1)[0]
#         dateDict.update({ item :  date})
# 
#         #object List info
#         objectListDict.update({ item :  objList[item] } )
# 
#         #object check info
#         checkList = {"rig" : 1, "lit" : 1, "lookdev" : 1 ,"fx" : 1 }
#         objectCheckDict.update({ item :  checkList} )
# 
#         #update List info
#         updateListDict.update({ item :  objList[item]})
#                                                                                                                                                     
#     if take[ itemType ].get('objectList'):  # is itemType
#         if take[ itemType ]['objectList'].get(item):  # is item
#             newTake =  takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict )
#         else:
#             newTake = takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
#     else:
#         newTake = takeSetInfo(take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict) 
#         
#     if local_take[ itemType ].get('objectList'):  # is itemType
#         if local_take[ itemType ]['objectList'].get(item):  # is item
#             local_Newtake = takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
#         else:
#             local_Newtake = takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)                
#     else:
#         local_Newtake = takeSetInfo(local_take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
#         #--------------------------------------------------------
#             
#     take = newTake      
#     local_take = local_Newtake
# 
#     take[ itemType ]["updateList"]= updateListDict 
#     local_take[ itemType ]["updateList"]= updateListDict
# 
#     saveTake( itemType, take ,local_take)
# 
# def takeSetInfo(take, itemType, type, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict):
#     if type == True:
#         take[ itemType ]["fileName"   ].update( fileNameDict   )
#         take[ itemType ]["version"    ].update( versionDict    )
#         take[ itemType ]['username'   ].update( userNameDict   )
#         take[ itemType ]['ipaddr'     ].update( ipaddrDict     )
#         take[ itemType ][ 'frame'     ].update( frameDict      )
#         take[ itemType ]['date'       ].update( dateDict       )
#         take[ itemType ]['objectList' ].update( objList        )
#         take[ itemType ]['objectCheck'].update( objectCheckDict)    
#     else:
#         take[ itemType ].update( { "fileName"  : fileNameDict } )
#         take[ itemType ].update( {"version"    : versionDict  } ) 
#         take[ itemType ].update( {'username'   : userNameDict } )
#         take[ itemType ].update( {'ipaddr'     : ipaddrDict   } )
#         take[ itemType ].update( { 'frame'     : frameDict    } )
#         take[ itemType ].update( {'date'       : dateDict     } )
#         take[ itemType ].update( {'objectList' : objList      } )
#         take[ itemType ].update( {'objectCheck': objectCheckDict} )
#         
#     return take
# 
# 
# def shotInfoExport(prjDir,  objList, itemType ):
#     globalTakeDir = "%s/Take" %prjDir
#     globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
#      
#     # file info
#     fileDir = cmds.file(q=1, sn=1)
#     fileName = os.path.basename(fileDir ).split('.')[0]
# 
#     # check dir
#     if not os.path.isdir(globalTakeDir):
#         os.makedirs(globalTakeDir) 
# 
#     # global
#     if not os.path.isfile( globalCurrentTake ):
#         take = {}
#         take["%s" %itemType] = {}
#          
#     else:
#         with open("%s" %( globalCurrentTake ), 'r' ) as f:
#             take = json.load(f)
#              
#  
#     if not take.get(itemType):
#         take["%s" %itemType] ={}
# 
#     fileNameDict= {}
#     versionDict = {}
#     userNameDict= {}
#     ipaddrDict  = {}
#     frameDict   = {}
#     dateDict    = {}
#     objectListDict ={}
#     objectCheckDict={}
#     updateListDict ={}
#     globalversionDict={}
# 
#     for item in objList:
#         # file Name
#         fileNameDict.update( { item : fileDir} )
# 
#         #take local version
#         versionDict.update( { item : localNewNum} )
#         globalversionDict.update( { item : globalNewNum} )
# 
#         # user info
#         userName =  socket.gethostname()
#         userNameDict.update({ item : userName})
# 
#         #ipaddr
#         cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
#         getipaddr = Popen(cmd, shell = True, stdout = PIPE)
#         ipaddr = getipaddr.communicate()[0][:-1]
#         ipaddrDict.update({ item : ipaddr})
#         
#         # frame info
#         startF = cmds.playbackOptions(min=1, q=1)
#         endF   = cmds.playbackOptions(max=1, q=1)
#         frameDict.update({ item : "%d-%d" %(startF, endF)})
#                 
#         # date info
#         nowdate = str(datetime.datetime.now())
#         date = nowdate.rsplit(":",1)[0]
#         dateDict.update({ item :  date})
#                 
#         #object List info
#         objectListDict.update({ item :  objList[item] } )
# 
#         #object check info
#         checkList = {"rig" : 1, "lit" : 1, "lookdev" : 1 ,"fx" : 1 }
#         objectCheckDict.update({ item :  checkList} )
# 
#         #update List info
#         updateListDict.update({ item :  objList[item]})
# 
#     if take[ itemType ].get('objectList'):  # is itemType
#         if take[ itemType ]['objectList'].get(item):  # is item
#             newTake =  takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict )
#         else:
#             newTake = takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
#     else:
#         newTake = takeSetInfo(take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)         
# 
#     take = newTake      
#     take[ itemType ]["updateList"]= updateListDict 
# 
#     # global Take
#     print globalNewTake
#     with open("%s" %globalNewTake, 'w') as f:
#         json.dump(take,  f, indent=4)

#-------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------
# def modelImport(itemInfo, type, rootType):
#     for i in itemInfo:
# #         name = "%s1:%s" %(i,i)
#         if "import" in type:
#             writeItemName = modelImportFile( i, itemInfo[i],rootType )
# 
#         elif "reference" in type:
#             writeItemName = modelReferenceFile ( i, itemInfo[i],rootType ) 
#     return writeItemName

def modelImport(itemInfo, type, rootType, lod,  num=1):
    isNameSpace = None
    assetName = list(itemInfo.keys())[0]
    itemNames = []
    
    workType = cmds.file ( q=1, sn=1) and cmds.file ( q=1, sn=1).split("/")[3]
    if not ":" in assetName:   #is namespace?
        if "seq" == workType or num > 1: 
            isNameSpace = True

    #filename
    lodfilename = list(itemInfo.values())[0].replace("v01.mb", "v01_%s.mb" %str(lod).upper())
    if not os.path.isfile(lodfilename ):
        lodfilename = list(itemInfo.values())[0]

    for i in range(num):
#         name = "%s1:output_SET" %i
        if isNameSpace: #seq
            namespace = "%s%d" %(assetName, i+1)
            itemName = "%s:%s" %(namespace, assetName)
        else: # assets
            itemName = assetName

        if "import" in type or "None" in type:
            writeItemName = modelImportFile( itemName, lodfilename,rootType , workType)
#             a.keys()[0], a.values()[0]
        elif "reference" in type:
            writeItemName = modelReferenceFile ( itemName, lodfilename,rootType, workType )

        # elif "low" in type:
        #     lowdir = lodfilename.replace("v01.mb", "v01_LOW.mb")
        #     if os.path.isfile(lowdir):
        #         writeItemName = modelReferenceFile ( itemName, lowdir,rootType, workType )
        #     else:
        #         writeItemName = modelReferenceFile ( itemName, lodfilename,rootType , workType)

        itemNames.append(writeItemName)
#         print ">>>>", writeItemName
    return itemNames

def modelImportFile(itemName, itemDir, rootType, workType):
#     name = "%s_Grp" %itemName


    if cmds.ls(itemName):  # obj in ...
        print("There is the same object !! ")
        return

    
#     cmds.file ("%s" % itemDir, 
#             namespace = "%s" %itemName.split(":")[0], 
#             i=1,pr =1, type ="mayaBinary",  ignoreVersion=1, 
#             ra=True,  mergeNamespacesOnClash =False, options ="v=0;"  )

    if workType == "asset" or ":" not in itemName:
        cmds.file("%s" %itemDir, i =True , type ="mayaBinary" ,  ignoreVersion=True,\
                        mergeNamespacesOnClash= 0, options="v=0", pr= True, loadReferenceDepth="all" ,returnNewNodes=1)
    else:
        cmds.file ("%s" % itemDir, 
                    namespace = "%s" %itemName.split(":")[0], 
                    i=1,pr =1, type ="mayaBinary",  ignoreVersion=1, 
                    ra=True,  mergeNamespacesOnClash =False, options ="v=0;"  )
        

    mentalNode = cmds.ls(['mentalrayGlobals', 'mentalrayItemsList'])
    if mentalNode:
        cmds.delete(mentalNode)

    writeItemName = initModelImportWrite(  itemName, itemDir, rootType, workType)
    return writeItemName

def modelReferenceFile(itemName, itemDir, rootType, workType):
    
#     itemName = "%s:output_SET" %item
#     name = itemName
#     if cmds.ls(itemName):  # obj in ...replace
    namespaceName = itemName.split(":")[0]
#     name = "%s_Grp" %itemName
    
    if cmds.objExists(itemName): # replace
        if cmds.namespace(exists= '%s' %namespaceName ) == False:
            cmds.file ("%s" % itemDir, 
                        loadReference = "%s" %itemName.split(":")[0],
                        shd=["displayLayers","shadingNetworks","renderLayersByName"],
                        type ="mayaBinary", options ="v=0;"  )
    
            writeItemName = initModelImportWrite(  itemName, itemDir, rootType, workType)
            return writeItemName
        else:
            print("Check! nameSpace !!( %s )"  %itemName)
            return
    
    if workType == "asset" or ":" not in itemName: # not namespace
        cmds.file ("%s" % itemDir, returnNewNodes=1,
                    namespace = ":", 
                    r=1, gl =1, type ="mayaBinary",  ignoreVersion=1, 
                    shd=["displayLayers","shadingNetworks","renderLayersByName"],
                    mergeNamespacesOnClash =False, options ="v=0;")

    else: # namespace
        cmds.file ("%s" % itemDir, 
                    namespace = "%s" %itemName.split(":")[0], 
                    r=1, gl =1, type ="mayaBinary",  ignoreVersion=1,
                    shd=["displayLayers","shadingNetworks","renderLayersByName"], 
                    mergeNamespacesOnClash =False, options ="v=0;"  )

#     name = "%s_Grp" %itemName
    writeItemName = initModelImportWrite(  itemName, itemDir, rootType, workType)
    return writeItemName

def saveModeltWrite(objList):
    for obj in objList:
        item = obj
        filename = objList[ obj ]
        for i in cmds.ls( ["%s*" %item, "%s_*" %item] ,r=1, type="transform") :
            if not cmds.ls('%s.model' %i):
                cmds.addAttr ('%s' %i, ln= "model",  dt= "string" )

            cmds.setAttr('%s.model' %i, "%s,%s" %( item, filename) ,type="string")


# def initModelImportWrite( item , filename, rootType, workType):
#     itemType = rootType
# 
#     if workType == "asset" or ":" not in item:
#         itemAssetName = item
#         reNameItem = item.replace("%s" %itemAssetName, "output_SET")
#     else:
#         itemAssetName = item.split(":")[1]
# #     reNameItem = "%s:output_SET" %item
#         reNameItem = item.replace(":%s" %itemAssetName, ":output_SET")
# 
#     if not cmds.ls('%s.%s' %(reNameItem, itemType )):
#         cmds.addAttr ('%s' %reNameItem, ln= "%s" %itemType,  dt= "string" )
# 
#     cmds.setAttr('%s.%s' % (reNameItem, itemType), "%s,%s" %( item, filename) ,type="string")
#     return '%s.%s' % (reNameItem, itemType)

#     if "rig" == rootType:
#         if not cmds.ls('%s.rig' %reNameItem):
#             cmds.addAttr ('%s' %reNameItem, ln= "rig",  dt= "string" )
# 
#         cmds.setAttr('%s.rig' %reNameItem, "%s,%s" %( item, filename) ,type="string")
#         return '%s.rig' %reNameItem
#     else:
#         if not cmds.ls('%s.rigEnv' %reNameItem):
#             cmds.addAttr ('%s' %reNameItem, ln= "rigEnv",  dt= "string" )
# 
#         cmds.setAttr('%s.rigEnv' %reNameItem, "%s,%s" %( item, filename) ,type="string")
#         
#         return '%s.rigEnv' %reNameItem
    
def initModelImportWrite( item , filename, rootType, workType):
    itemType = rootType
 
#     print item , filename, rootType
#     print '%s.%s' %(item, itemType )
#     print '%s' %item,  "%s" %itemType
#     print cmds.ls('%s.%s' %(item, itemType ))
 
    if not cmds.ls('%s.%s' %(item, itemType )):
        cmds.addAttr ('%s' %item, ln= "%s" %itemType,  dt= "string" )
 
    cmds.setAttr('%s.%s' % (item, itemType), "%s,%s" %( item, filename) ,type="string")
    return '%s.%s' % (item, itemType)


#-------------------------------------------------------------------------------------------

def modelListInfoWrite(shotDirItem, modelDir): #List
    
    if not modelDir:
        return
    
    for i in modelDir:
        assetDir = re.search( ".+(?=/[\w]+/pub/)",modelDir[i]).group()
        globalTakeList = "%s/Take/takeList.json" %assetDir
        
#         print "%s/Take" % assetDir
        if not os.path.isdir( "%s/Take" % assetDir):
            os.mkdir("%s/Take" %assetDir )
            
        if not os.path.isfile( globalTakeList ):
            takelist = {}
            takelist["model"]={}

        else:
            with open("%s" %( globalTakeList ), 'r' ) as f:
                takelist = json.load(f)

#         shotName = prjDir.rsplit("/",1)[1]
        if not takelist.get("model"):
            takelist["model"]={}
        takelist["model"].update( shotDirItem )   #{"EO_053": "/show/~/EO_053"}    
#         takelist["model"].update( {"%s" %shotName : "%s" %prjDir} )
    takelist = convert_byte_to_string.convert_byte_to_string(takelist)
    # global Take
    with open("%s" %globalTakeList, 'w') as f:
        json.dump(takelist,  f, indent=4)

#-------------------------------------------------------------------------------------------
def shotTakeAssetInfoExport (prjDir, objList  , partType ): #다른 씬들에 모델링 정보를 준다.
    globalTakeList = "%s/Take/takeList.json" %prjDir

    if os.path.isfile( globalTakeList ):
        with open("%s" %( globalTakeList ), 'r' ) as f:
            take = json.load(f)

        if take.get("%s" %partType):
            for i in take["%s" %partType]:
                pass
                #shotInfoExport(take["%s" %partType][i],  objList, partType)
    return
#-------------------------------------------------------------------------------------
# def findModelData(proj, fileList):
#     # prop
#     propDir = map(lambda x : glob.glob("%sassets/prop/*/" %x) , glob.glob("/show/JM/"))  # jm
#     propList = []
#     map(lambda x : x is not [] and propList.extend(x) , propDir)
#
#     propL = map(lambda x : glob.glob("%smodel/pub/*.mb" %x), propList)  #model
#     propList = []
#     map(lambda x : x is not [] and propList.extend(x) , propL)
#
#     #env
#     envDir = map(lambda x : glob.glob("%sassets/env/*/" %x) , glob.glob("/show/JM/"))
#     envList = []
#     map(lambda x : x is not [] and envList.extend(x) , envDir)
#
#     envL = map(lambda x : glob.glob("%smodel/pub/*.mb" %x), envList )
#     envList  = []
#     map(lambda x : x is not [] and envList .extend(x) , envL)
#
#     #cha
#     chaDir = map(lambda x : glob.glob("%sassets/cha/*/" %x) , glob.glob("/show/JM/"))
#     chaList = []
#     map(lambda x : x is not [] and chaList.extend(x) , chaDir)
#
#     chaL = map(lambda x : glob.glob("%smodel/pub/*.mb" %x), chaList )
#     chaList  = []
#     map(lambda x : x is not [] and chaList .extend(x) , chaL)
#
#     #litRig
#     litRigDir = map(lambda x : glob.glob("%sassets/litRig/*/" %x) , glob.glob("/show/JM/"))
#     litRigList = []
#     map(lambda x : x is not [] and litRigList.extend(x) , litRigDir)
#
#     litRigL = map(lambda x : glob.glob("%smodel/pub/*.mb" %x), litRigList )
#     litRigList  = []
#     map(lambda x : x is not [] and litRigList .extend(x) , litRigL)
#
#     modelList = propList + envList + chaList + litRigList
#     modelAssetName = map(lambda x : x.rsplit('/', 1)[1].split("_")[0] , modelList )
#
#     modelAssetGrop = dict(zip(modelAssetName , modelList ))
#
#     #surch file
#     modelfile= {}
#     for i in fileList:
#         if ":" in i:
#             splitItem = re.search("[0-9]+:.*", i)
#             if not splitItem:
#                 splitItem = re.search(":.*", i)
#         item = i.split( splitItem.group() )[0]
#         modelfile[ item ] = modelAssetGrop[item]
#
#     return modelfile

   
