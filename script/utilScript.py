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
        project_name = i.rsplit("/", 1)[1]
        # 폴더만 인식하고 파일은 제외
        if not os.path.isdir(i):
            continue
        # @eaDir은 Synology NAS 메타데이터 폴더이므로 제외
        if project_name == "@eaDir":
            continue
        # M83으로 시작하는 폴더는 제외
        if project_name.startswith("M83"):
            continue
        # _로 시작하는 폴더는 제외
        if project_name.startswith("_"):
            continue
        prj[project_name] = i
    return prj

def sequence(prj):
    seqc ={}
    seqcList = glob.glob("%s/seq/*" %prj)
    for i in seqcList:
        # 폴더만 인식하고 파일은 제외
        if not os.path.isdir(i):
            continue
        seqc[i.rsplit("/", 1)[1]]= i
    return seqc

def shotList(seq):
    shot ={}
    shotList = glob.glob("%s/*" %seq)
    for i in shotList:
        # 폴더만 인식하고 파일은 제외
        if not os.path.isdir(i):
            continue
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

    try:
        prjDir = re.search(".+(?=/[\w]+/(pub|wip)/)", fileDir).group()
        partType = re.search("[\w]+(?=/(pub|wip)/)", fileDir).group()
    except AttributeError:
        print("ERROR: Cannot parse file path: {}".format(fileDir))
        print("Expected path format: /path/to/project/seq_name/wip/ or /path/to/project/seq_name/pub/")
        # Fallback parsing - try to extract from current path structure
        if "/ani/wip/" in fileDir:
            prjDir = fileDir.split("/ani/wip/")[0]
            partType = "ani"
        elif "/wip/" in fileDir:
            parts = fileDir.split("/wip/")
            prjDir = parts[0].rsplit("/", 1)[0]
            partType = parts[0].split("/")[-1]
        else:
            raise ValueError("Unsupported file path format: {}".format(fileDir))
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


# 글로벌 변수: 다중 어셋 import 시 사용자 선택 기억
_batch_import_choice = None
_batch_import_active = False

def setBatchImportMode(active):
    """다중 import 모드 설정"""
    global _batch_import_choice, _batch_import_active
    _batch_import_active = active
    if not active:
        _batch_import_choice = None

def nameSpaceCheck(item):
    global _batch_import_choice, _batch_import_active
    
    print("=== nameSpaceCheck DEBUG ===")
    print("Checking item: %s" % item)
    print("Object exists: %s" % cmds.objExists(item))
    
    # 동일한 오브젝트가 실제로 존재하는 경우에만 확인
    if cmds.objExists(item):
        # 배치 모드가 활성화되어 있고 이미 선택이 있으면 그 선택을 사용
        if _batch_import_active and _batch_import_choice is not None:
            reply = _batch_import_choice
            print("Using previous choice: %s for item: %s" % (reply, item))
        else:
            # 첫 번째 팝업 또는 배치 모드가 아닌 경우
            message = 'It\'s already exists Name!! Delete Object and Object Reflace ??'
            if _batch_import_active:
                message += '\n\n(This choice will be applied to all remaining items)'
            
            reply = cmds.confirmDialog(title='Question!',
                                       message=message,
                                       button=['ok', 'cancel'])
            
            # 배치 모드인 경우 선택을 저장
            if _batch_import_active:
                _batch_import_choice = reply
                print("Saved batch choice: %s" % reply)
        
        if reply == "ok":
            deleteConnectObj(item)
            return True  # Replace 진행
        else:
            # Cancel 버튼을 눌렀을 때 - 넘버링된 네임스페이스 사용
            print("User cancelled - will use numbered namespace")
            
            originalItem = item
            if ":" in item:
                namespace = item.split(":")[0]
                assetName = item.split(":")[1]
                
                # 사용 가능한 네임스페이스 번호 찾기 (오브젝트가 아닌 네임스페이스 레벨에서)
                num = 1  
                while True:
                    newNamespace = "%s%d" % (namespace, num)
                    # 해당 네임스페이스에 어떤 오브젝트도 없는지 확인
                    if not cmds.namespace(exists=newNamespace) or not cmds.ls(newNamespace + ":*"):
                        newItem = "%s:%s" % (newNamespace, assetName)
                        print("Using new namespace: %s" % newNamespace)
                        return newItem
                    num += 1
            
            return item  # Fallback
    elif "_mergeObjectSpace" in item:
        pass
    # 네임스페이스가 없을 때만 생성 - 제거 (Maya가 임포트 시 자동 생성하도록)
    # elif ":" in item:
    #     namespace = item.split(':')[0]
    #     if not cmds.namespace(exists=namespace):
    #         cmds.namespace(add=namespace)
    
    return True  # 정상 진행

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







