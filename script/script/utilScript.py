# -*- coding:utf-8 -*-

import os, re
import glob
import json
import sys
sys.path.append(os.path.abspath(__file__+'/../..'))
from cacheExport_module.app_moduleImport import *
from script import convert_byte_to_string

# UI ----------------------------------
def projectList():
    prjList = glob.glob("/show/*")
    prj={}
    for i in prjList:
        prj[i.rsplit("/", 1)[1]] = i
    return prj

def sequence(prj):
    seqc ={}
    seqcList = glob.glob("%s/seq/*" %prj)
    for i in seqcList:
        seqc[i.rsplit("/", 1)[1]]= i
    return seqc

def shotList(seq):
    shot ={}
    shotList = glob.glob("%s/*" %seq)
    for i in shotList:
        shot[i.rsplit("/", 1)[1]]= i
    return shot

# assetInfoTreeWidget
def splitItemName(itemNameList):
    item = {}
    for itemName in itemNameList:
        if ":" in itemName:
            splitItem = re.search("[\w]*[\D](?=([\d]+)?:)", itemName).group()
        else:
            splitItem = itemName

        if splitItem not in item:
            item[splitItem] = []

        item[splitItem].append(itemName)

    return item


# Export  ----------------------------------------------------------------------------------------
def itemDircheck(dirname, objname=""):
    fileData = getFileName()

    if dirname == "lookdev":
        if "/pub/" in fileData[1]:
            exportDir = fileData[1]

        else:
            exportDir = fileData[1].split("/wip/")[0] + "/pub/"
            if not os.path.isdir(exportDir):
                os.makedirs(exportDir)
    else:
        if "/pub/" in fileData[1]:
            fileData[1] = fileData[1].replace("/pub/", "/wip/scenes/")

        exportDir = fileData[1].split("/scenes/")[0] + "/data/%s/%s" % (dirname, fileData[0])

        if not os.path.isdir(exportDir):
            os.makedirs(exportDir)

    return fileData[0], exportDir


def itemPubDirCheck(deptType=""):  # export 1
    fileData = getFileName()

    if "/wip/" in fileData[1]:
        pubDir = fileData[1].split("/wip/")[0] + "/pub"

    elif "/pub/" in fileData[1]:
        pubDir = fileData[1].split("/pub/")[0] + "/pub"

    else:
        print("( item Sciprt 45 line ) Erro : Not Project Set !!  ")
        return

    if "lookdev" == deptType:
        pubDir = pubDir.replace("/pub/", "/wip/data/shader")

    if not os.path.isdir(pubDir):
        os.makedirs(pubDir)

    return fileData[0], pubDir


def itemExport(fileName, itemdir, itemName=None):  # exort 5

    fileinfo = {}
    try:
        objName = cmds.ls(sl=1)

        for i in objName:
            if i in ['output_SET']:
                continue
            fileinfo[i] = "%s/%s.mb" % (itemdir, fileName)

        cmds.file(rename="%s/%s.mb" % (itemdir, fileName))
        cmds.file(f=1, save=1, options="v=0;")
    except:
        pass

    return fileinfo


def itemFilecheck(itemDir, itemname="", name=""):
    if "/pub/" in itemDir:
        return False

    if os.path.isdir(itemDir):
        return True
    return False

def itemListSelect(typeV="", itemList=[]):  # export 3
    if not itemList:
        itemList = cmds.ls(sl=1)  # ctrl_set select

    if typeV:
        if typeV == "modelEnv":
            itemName = re.search("[\w]+$", itemList[0]).group()
            return itemName
        elif typeV == "geoCache":
            itemList = cmds.ls([x.replace(":output_SET", ":ctrl_SET") for x in itemList])  # ctrl_set select
            cmds.select(itemList)
            return itemList
        elif typeV == "atom":
            itemList = cmds.ls([x.replace(":output_SET", ":ctrl_SET") for x in itemList])  # ctrl_set select
            cmds.select(itemList)
            return itemList
        else:
            if not cmds.ls(itemList, dag=1, type=typeV) or itemList == []:
                print("Error : {} not selected!".format(typeV))
                return
    return itemList

# Export Asset
def itemRootAssetNameCheck(itemdir, type=""): #export 2
    itemName = itemdir.split("/")[5]

    if type == "digienv":
        if not cmds.ls("instance_SET"):
            print("Error : instance_SET 이 없습니다. ")
            return
        instanceSET = cmds.sets("instance_SET", q=True)
        cmds.select("instance_SET", ne=True, r=True)
        cmds.select(instanceSET, ne=True, add=True)

    if type == "model":
        fileNameList = itemLodAssetNameCheck(itemName)
        if not fileNameList:
            print("Error : Not match Asset Name !!  ")
            return

        cmds.select(fileNameList, r=True)

    if type == "rig":
        if not cmds.ls(itemName):
            print("Error : Not match Asset Name !!  ")
            return

        cmds.select(itemName)
        cmds.select( "output_SET", ne=1, add=1)

    return itemName


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
# --------------------------------------------------------------------------

def getFileList(fileDir=""):
    if not fileDir:
        fileDir = cmds.file(q=1, sn=1)

    prjDir = re.search(".+(?=/[\w]+/(pub|wip)/)", fileDir).group()
    partType = re.search("[\w]+(?=/(pub|wip)/)", fileDir).group()
    fileName = ""
    if ".mb" in fileDir:
        fileName = re.search("[\w]+(?=\.mb)", fileDir).group()
    if ".project" in fileDir:
        fileName = re.search("[\w]+(?=\.project)", fileDir).group()

    globalTakeDir = "%s/Take" % prjDir
    localTakeDir = "%s/%s/wip/data/Take" % (prjDir, partType)

    return prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir


def getMayaFileList():
    fileDir = cmds.file(q=1, sn=1)
    if fileDir:
        #     fileName = os.path.basename(fileDir ).split('.')[0]
        #     print fileDir
        prjDir = fileDir.split("/")[2]
        sqcDir = fileDir.split("/")[4]
        shotDir = fileDir.split("/")[5]
        partType = re.search("[\w]+(?=/(pub|wip)/)", fileDir).group()
        fileName = re.search("[\w]+(?=\.mb)", fileDir).group()
    else:
        prjDir = None
        sqcDir = None
        shotDir = None
        partType = None
        fileName = None

    return prjDir, sqcDir, shotDir, partType, fileName, fileDir

# find
def getFileName():

    fileDir = cmds.file(q=1, exn=1)

    fileName = fileDir.rsplit('/', 1)[1].split('.')[0]
    fileInfo = [fileName, fileDir]

    return fileInfo

#------------------------------------------------------------------------

def currentPartType():

    fileDir = cmds.file(q=1, sn=1)

    partType = None
    if re.search( "[\w]+(?=/(pub|wip)/)",fileDir ) != None:
        partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()

    return partType

def pluginCheck():
    if os.path.isdir("/usr/autodesk/maya2017/vray/plug-ins"):
        pluginDir = "/usr/autodesk/maya2017/vray/plug-ins"

    if not cmds.pluginInfo("vrayformaya", q=1, loaded=1):
        cmds.loadPlugin("%s/vrayformaya.so" % pluginDir)

    if cmds.getAttr('defaultRenderGlobals.currentRenderer') != "vray":
        cmds.setAttr('defaultRenderGlobals.currentRenderer', "vray", type="string")
        mel.eval('vrayCreateVRaySettingsNode();')

def pluginChecks(pluginName):
    if "vray" == pluginName:
        if os.path.isdir("/usr/autodesk/maya2017/vray/plug-ins"):
            pluginDir = "/usr/autodesk/maya2017/vray/plug-ins"

        if not cmds.pluginInfo("vrayformaya", q=1, loaded=1):
            cmds.loadPlugin("%s/vrayformaya.so" % pluginDir)

        if cmds.getAttr('defaultRenderGlobals.currentRenderer') != "vray":
            cmds.setAttr('defaultRenderGlobals.currentRenderer', "vray", type="string")
            mel.eval('vrayCreateVRaySettingsNode();')
    if "abc" == pluginName:
        if not cmds.pluginInfo("AbcExport.so", q=1, loaded=1):
            cmds.loadPlugin("AbcExport.so")
        if not cmds.pluginInfo("AbcImport.so", q=1, loaded=1):
            cmds.loadPlugin("AbcImport.so")
    if "alembic" == pluginName:
        if not cmds.pluginInfo("AbcExport.so", q=1, loaded=1):
            cmds.loadPlugin("AbcExport.so")
        if not cmds.pluginInfo("AbcImport.so", q=1, loaded=1):
            cmds.loadPlugin("AbcImport.so")

    if "mayaDummy" == pluginName:
        if not cmds.pluginInfo("fbxmaya", q=1, loaded=1):
            cmds.loadPlugin("fbxmaya.so")
        if not cmds.pluginInfo("AbcExport.so", q=1, loaded=1):
            cmds.loadPlugin("AbcExport.so")
        if not cmds.pluginInfo("AbcImport.so", q=1, loaded=1):
            cmds.loadPlugin("AbcImport.so")

    if "atom" == pluginName:
        if not cmds.pluginInfo("atomImportExport", q=1, loaded=1):
            cmds.loadPlugin("atomImportExport.so")

        if not cmds.pluginInfo("animImportExport", q=1, loaded=1):
            cmds.loadPlugin("animImportExport.so")

    if "yetiCache" == pluginName:
        if not cmds.pluginInfo("pgYetiMaya", q=1, loaded=1):
            cmds.loadPlugin("pgYetiMaya.so")

    if "mtoa" == pluginName:
        if not cmds.pluginInfo("mtoa", q=1, loaded=1):
            cmds.loadPlugin("mtoa.so")


# Delete Item------------------------------------------------------------------------------------------------
def deleteAssetSaveInfoList( takeNameDir, data):
    if not takeNameDir:
        return

    data = convert_byte_to_string.convert_byte_to_string(data)
    with open( "%s" %takeNameDir, 'w') as f:
        json.dump(data, f, indent =4)

# namespace --------------------------------------------------------------------------------------------------
def getNameSpace(item):
    # ToDo : get namespace
    pass


def nameSpaceCheck(item):
    if cmds.ls(item):
        reply = cmds.confirmDialog(title='Question!',
                                   message='It\'s already exists Name!! Delete Object and Object Reflace ??',
                                   button=['ok', 'cancel'])
        if reply == "ok":
            deleteConnectObj(item)
        else:
            return
    elif "_mergeObjectSpace" in item:
        pass
    else:
        # delete namespace
        if cmds.namespace(exists="%s" % item.split(':')[0]):
            cmds.namespace(rm="%s" % item.split(':')[0], mnr=1)

# Add
def nameSpaceAdd(itemName):
    nameSpaceSet = itemName.split(":")[0]
    itemList = cmds.ls(sl=1)

    for rootName in itemList:
        # reference
        try:
            if cmds.referenceQuery(rootName, filename=1):
                refFilePath = cmds.referenceQuery(rootName, filename=1)
                cmds.file(refFilePath, e=1, namespace="%s" % nameSpaceSet)
                # reference  nameSpace delete
                if cmds.namespace(exists=rootName.split(":")[0]):
                    cmds.namespace(rm=rootName.split(":")[0])
                continue
        except:
            pass

        # nameSpace
        noneNameSpace = rootName
        if ":" in rootName:
            nameSpaceDelete(itemName)
            noneNameSpace = rootName.split(":")[1]

        selectList = cmds.listRelatives(noneNameSpace, ad=1)
        selectList.append(noneNameSpace)

        for subName in selectList:
            cmds.rename("%s" % subName, ":%s:%s" % (nameSpaceSet, subName))

# Remove
def nameSpaceDelete(itemName):
    nameSpaceSet = itemName.split(":")[0]
    itemList = cmds.ls(itemName)

    for rootName in itemList:
        try:
            if cmds.referenceQuery(rootName, filename=1):
                print("Not Delete !! reference File !!!")
                continue
        except:
            pass

        if cmds.ls(rootName):
            selectList = cmds.listRelatives(rootName, ad=1)
            selectList.append(rootName)
            for subName in selectList:
                # nameSpace check
                if ":" in subName:
                    currentNamespace = subName.split(":")[0]
                    if cmds.namespace(exists=':%s' % currentNamespace) == True:
                        cmds.namespace(rm=":%s" % currentNamespace, mnr=1)
#  Remove child
def deleteConnectObj(itemName):
    itemName = str(itemName)

    if not cmds.ls(itemName):
        print("Not Object !!!")
        return

    if not ":" in itemName:
        print(itemName, "<<< not NameSpace Select !!")
        return

    if cmds.referenceQuery(itemName, inr=1):
        ref = cmds.referenceQuery("%s" % itemName, f=1)
        cmds.file(ref, removeReference=1)
        return

    nameSpace = itemName.split(":")[0]
    cmds.namespace(rm="%s" % nameSpace, dnc=1)







