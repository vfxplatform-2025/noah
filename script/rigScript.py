# -*- coding:utf-8 -*-
'''
Created on Jun 25, 2015

@author: m83
'''
import os, sys, glob, re
import maya.cmds as cmds
from subprocess import *
import json
import datetime
from . import takeScript
sys.path.append('/storage/core/MAYA_2018/Production/Global/Armo/')
import urllib.request, urllib.error, urllib.parse
#import ArmoIO
import socket
from script import convert_byte_to_string

# ---------------------------------------------------------------------------------
def findRigData(fileList, typeList=[]):
    rigfile = {}
    notFileList = []

    findAssetPart = typeList
    fileDir = cmds.file(q=1, sn=1)
    showName = fileDir.split("/show/")[1].split("/")[0]
    findAssetRoot = "/show/{}/assets".format(showName)

    for itemName in fileList:

        checkRef = 1
        if cmds.ls(itemName) and cmds.ls(itemName)[0] == itemName:
            if cmds.referenceQuery(itemName, inr=1):
                checkRef = 1
            else:
                checkRef = 0
        else:
            checkRef = 0

        # find current scene reference rig
        if checkRef:
            referenceFileDir = cmds.referenceQuery(itemName, filename=1)
            print(referenceFileDir)
            if "{" in referenceFileDir:
                referenceFileDir = referenceFileDir.split("{")[0]
            if "_LOW.mb" in referenceFileDir:
                referenceFileDir = referenceFileDir.replace("_LOW.mb", ".mb")
            elif "_MID.mb" in referenceFileDir:
                referenceFileDir = referenceFileDir.replace("_MID.mb", ".mb")
            elif "_HI.mb" in referenceFileDir:
                referenceFileDir = referenceFileDir.replace("_HI.mb", ".mb")
            elif "_XLOW.mb" in referenceFileDir:
                referenceFileDir = referenceFileDir.replace("_XLOW.mb", ".mb")
            elif "_XHI.mb" in referenceFileDir:
                referenceFileDir = referenceFileDir.replace("_XHI.mb", ".mb")
            elif "_MOCAP.mb" in referenceFileDir:
                referenceFileDir = referenceFileDir.replace("_MOCAP.mb", ".mb")
            rigfile.update({itemName.split(":")[1]: referenceFileDir})
        # find asset rig
        else:
            checkAsset = 0
            assetName = re.search("[\w]*[\D](?=([\d]+)?:)", itemName).group()
            for partName in findAssetPart:
                assetPath = "{}/{}/{}".format(findAssetRoot, partName, assetName)
                if os.path.exists(assetPath):
                    takeList, justTakeList, currentTake, takeName = takeScript.checkTakeName(assetPath)
                    with open(currentTake, 'r') as f:
                        take = json.load(f)
                        rigfile.update(take['rig']['fileName'])
                    checkAsset = 1
                    break
            if not checkAsset:
                notFileList.append(itemName)

    txt = ""
    for i in notFileList:
        txt += "%s\n" % i
    if txt:
        cmds.confirmDialog(title='Not Found Rig', message=txt, button=['ok'])
        print("=" * 20, "Not Found Rig", "=" * 20)
        print(txt)
        print("=" * 55)
    print(("rigFile : {}".format(rigfile)))
    return rigfile


# --------------------------------------------------------------------------------------------------------------------
def rigImport(itemInfo, type, rootType, lod=None, num=1):
    # 네임스페이스 먼저 확인을 하고
    # 네임스페이스가 없으면 샷인지 확인을 하고
    # 샷이면 네임스페이스를 붙이고
    # 어셋이면 네임스페이스가 없이 불러와지고.
    # 개수를 확인한다.

    # seq 나 개수가 여러개면  네임스페이를 붙이고

    isNameSpace = None
    assetName = list(itemInfo.keys())[0]
    itemNames = []

    workType = cmds.file(q=1, sn=1) and cmds.file(q=1, sn=1).split("/")[3]
    if not ":" in assetName:  # is namespace?
        if "seq" == workType or num > 1:
            isNameSpace = True

    # filename
    lodfilename = ""
    if lod == "None":
        lodfilename = list(itemInfo.values())[0]
    elif lod == "miarmy":
        lodfilename = list(itemInfo.values())[0].replace(".mb", "_%s.mb" % str(lod))
    else:
        lodfilename = list(itemInfo.values())[0].replace(".mb", "_%s.mb" % str(lod).upper())
    print(">>>", lodfilename)
    if not os.path.isfile(lodfilename):
        lodfilename = list(itemInfo.values())[0]

    for i in range(num):
        #         name = "%s1:output_SET" %i
        if isNameSpace:  # seq
            namespace = "%s%d" % (assetName, i + 1)
            itemName = "%s:%s" % (namespace, assetName)
        else:  # assets
            itemName = assetName

        if "import" in type or "None" in type:
            writeItemName = rigImportFile(itemName, lodfilename, rootType, workType)
        #             a.keys()[0], a.values()[0]
        elif "reference" in type:
            writeItemName = rigReferenceFile(itemName, lodfilename, rootType, workType)

        # elif "low" in type:
        #     lowdir = itemInfo.values()[0].replace("v01.mb", "v01_LOW.mb")
        #     if os.path.isfile(lowdir):
        #         writeItemName = rigReferenceFile ( itemName, lowdir,rootType, workType )
        #     else:
        #         writeItemName = rigReferenceFile( itemName, lodfilename,rootType , workType)

        elif "lookdevproxy" in type:
            proxydir = lodfilename.replace("rig", "lookdev").replace(".mb", "_PROXY.mb")
            writeItemName = rigImportFile(itemName, proxydir, rootType, workType)

        elif "instance" in type:
            if cmds.ls(itemName.split(":")[1], r=1):
                writeItemName = rigInstanceFile(itemName, lodfilename, rootType, workType)

            else:
                proxydir = lodfilename.replace("rig", "lookdev").replace(".mb", "_PROXY.mb")
                writeItemName = rigReferenceFile(itemName, proxydir, rootType, workType)

            return
        #             writeItemName = rigReferenceFile ( itemName, lodfilename,rootType, workType )

        itemNames.append(writeItemName)
    return itemNames


def rigImportFile(itemName, itemDir, rootType, workType):
    # 동일한 어셋이 있을 때 번호를 붙여서 import
    originalItemName = itemName
    if cmds.ls(itemName):  # obj already exists
        print("There is the same rig object !! Finding available number...")
        
        # 네임스페이스가 있는지 확인
        if ":" in itemName:
            namespace = itemName.split(":")[0]
            assetName = itemName.split(":")[1]
            
            # 사용 가능한 번호 찾기
            num = 2  # 1은 이미 존재하므로 2부터 시작
            while True:
                newNamespace = "%s%d" % (namespace.rstrip('0123456789'), num)
                newItemName = "%s:%s" % (newNamespace, assetName)
                
                if not cmds.ls(newItemName):
                    itemName = newItemName
                    print("Using new rig name: %s" % itemName)
                    break
                num += 1
        else:
            # 네임스페이스가 없는 경우
            num = 2
            while True:
                newItemName = "%s%d" % (originalItemName.rstrip('0123456789'), num)
                
                if not cmds.ls(newItemName):
                    itemName = newItemName
                    print("Using new rig name: %s" % itemName)
                    break
                num += 1
    
    # NameSpace check (기존 로직 유지)
    if not cmds.ls(itemName):
        # delete namespace
        if ":" in itemName and cmds.namespace(exists="%s" % itemName.split(':')[0]):
            cmds.namespace(rm="%s" % itemName.split(':')[0], mnr=1)
        print(itemName, "not Object !!")

    if workType == "asset" or ":" not in itemName:
        cmds.file("%s" % itemDir, i=True, type="mayaBinary", ignoreVersion=True, \
                  mergeNamespacesOnClash=0, options="v=0", pr=True, loadReferenceDepth="all", returnNewNodes=1)
    else:
        cmds.file("%s" % itemDir,
                  namespace="%s" % itemName.split(":")[0],
                  i=1, pr=1, type="mayaBinary", ignoreVersion=1,
                  ra=True, mergeNamespacesOnClash=False, options="v=0;")

    mentalNode = cmds.ls(['mentalrayGlobals', 'mentalrayItemsList'])

    if mentalNode:
        cmds.delete(mentalNode)

    writeItemName = initRigImportWrite(itemName, itemDir, rootType, workType)
    return writeItemName


#     subAssetInfoExport(  {itemName : itemDir}, "import" )

def rigInstanceFile(itemName, itemDir, rootType, workType):
    instanceName = [x for x in cmds.ls(itemName.split(":")[1], r=1) if cmds.referenceQuery(x, isNodeReferenced=1)]

    #     itemName = "auroraPlaza2:auroraPlaza"
    itemNameSpace = itemName.split(":")[0]
    instanceName = [x for x in cmds.ls(itemName.split(":")[1], r=1) if cmds.referenceQuery(x, isNodeReferenced=1)][0]

    nullGroup = cmds.group(em=True, name='null')
    cmds.rename(nullGroup, ":%s" % itemName)
    world_con = cmds.listRelatives("%s" % instanceName, c=1)[0]

    instace_con = cmds.instance(world_con, n="%s:auroraPlaza_world_CON" % itemNameSpace)[0]

    cmds.parent(instace_con, itemName)

    newSet1 = cmds.sets(n=":%s:ctrl_SET" % itemNameSpace)
    newSet2 = cmds.sets(newSet1, n=":%s:output_SET" % itemNameSpace)
    cmds.sets(instace_con, add=newSet1)

    writeItemName = initRigImportWrite(itemName, itemDir, rootType, workType)
    return writeItemName


def rigReferenceFile(itemName, itemDir, rootType, workType):
    #     itemName = "%s:output_SET" %item

    namespaceName = itemName.split(":")[0]
    if cmds.objExists(itemName):  # replace
        #         print "AAA"
        if cmds.namespace(exists='%s' % namespaceName) == False:

            cmds.file("%s" % itemDir,
                      loadReference="%s" % itemName.split(":")[0],
                      shd=["displayLayers", "shadingNetworks", "renderLayersByName"],
                      type="mayaBinary", options="v=0;")
            writeItemName = initRigImportWrite(itemName, itemDir, rootType, workType)
            return writeItemName
        else:
            print("Check! nameSpace !!( %s )" % itemName)
            return

    if workType == "asset" or ":" not in itemName:
        #         print "BBB"
        cmds.file("%s" % itemDir, returnNewNodes=1,
                  namespace=":",
                  r=1, gl=1, type="mayaBinary", ignoreVersion=1,
                  shd=["displayLayers", "shadingNetworks", "renderLayersByName"],
                  mergeNamespacesOnClash=False, options="v=0;")
    else:
        #         print "CCC"
        cmds.file("%s" % itemDir, returnNewNodes=1,
                  namespace="%s" % itemName.split(":")[0],
                  r=1, gl=1, type="mayaBinary", ignoreVersion=1,
                  shd=["displayLayers", "shadingNetworks", "renderLayersByName"],
                  mergeNamespacesOnClash=False, options="v=0;")

    #     file -r -type "mayaBinary"  -ignoreVersion -gl -mergeNamespacesOnClash true -namespace ":" -options "v=0;" "/show/DH/assets/prop/Box/rig/wip/scenes/Box_rig_v01_w03.mb";

    writeItemName = initRigImportWrite(itemName, itemDir, rootType, workType)
    return writeItemName


#     subAssetInfoExport(  {itemName : itemDir}, "import" )

def initRigImportWrite(item, filename, rootType, workType):
    if workType == "asset" or ":" not in item:
        itemAssetName = item
        reNameItem = item.replace("%s" % itemAssetName, "output_SET")
    else:
        itemAssetName = item.split(":")[1]
        #     reNameItem = "%s:output_SET" %item
        reNameItem = item.replace(":%s" % itemAssetName, ":output_SET")

    cmds.lockNode(reNameItem, l=False)
    if "rig" == rootType:

        if not cmds.ls('%s.rig' % reNameItem):
            cmds.addAttr('%s' % reNameItem, ln="rig", dt="string")

        #         assetName = re.search("[\D]+([\w]+)?[\D]+(?=([\d]+)?:)", item).group()
        #         assetName =  item.split("/")[1]
        cmds.setAttr('%s.rig' % reNameItem, "%s,%s" % (item, filename), type="string")
        return '%s.rig' % reNameItem
    else:
        if not cmds.ls('%s.rigEnv' % reNameItem):
            cmds.addAttr('%s' % reNameItem, ln="rigEnv", dt="string")

        #         assetName = re.search("[\D]+([\w]+)?[\D]+(?=([\d]+)?:)", item).group()
        #         assetName =  item.split("/")[1]
        cmds.setAttr('%s.rigEnv' % reNameItem, "%s,%s" % (item, filename), type="string")

        return '%s.rigEnv' % reNameItem


# -------------------------------------------------------------------------------------------

#find
def getFileName():
     
    fileDir = cmds.file (q=1, exn = 1)
    fileName = fileDir.rsplit('/', 1)[1].split('.')[0]
    fileInfo =  [fileName, fileDir]
    
    return  fileInfo

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

    return currentTake, newTake, takeName 


# Export  ---------------------------------------------------------------------------------------
# assetesExport.py def pupFile으로 실행됨.
def rigExport(fileName=None, itemdir=None, itemName=None, opts={}, user=None, comment=None):  # exort 5
    exported_files = []
    #fileNameCheck = ["_XHI", "_HI", "_MID", "_LOW", "_XLOW", "_PROXY", "_MOCAP"]
    fileNameCheck = ["_XHI", "_HI", "_MID", "_LOW", "_XLOW", "_PROXY"]
    fcheck = 0
    mocapCheck = 0
    msg = ''
    for fname in fileNameCheck:
        msg += fname + "\n"
        if fname in fileName:
            fcheck = 1

    if "_MOCAP" in fileName:
        mocapCheck = 1

    if fcheck:
        cmds.confirmDialog(title='Confirm', message='이제 마야 파일에 다음 이름은 노아에서 자동펍되기 때문에 제거하고 다시 저장해주세요.\n' + msg)
        raise RuntimeError("Name Error")

    cmds.file(save=True)
    origfilePath = cmds.file(q=True, sn=True)

    fileinfo = {}
    objName = cmds.ls(sl=1)
    mayaVersion=cmds.about(version=True)

    cmds.progressWindow(title='Pub.....', progress=0, status='Ing', ii=True)

    # output_SET check, _MOCAP파일은 체크 제외.
    outputSetList = []
    if not mocapCheck:
        if not 'output_SET' in objName:
            cmds.confirmDialog(title='Confirm', message='어셋의 output_SET이 없습니다..\n' + msg)
            cmds.pause(seconds=1)
            cmds.progressWindow(endProgress=1)
            raise RuntimeError("Name Error")

        outputSetList = cmds.sets("output_SET", q=True)
        if not 'ctrl_SET' in outputSetList:
            cmds.confirmDialog(title='Confirm', message='output_SET에 ctrl_SET이 없습니다..\n')
            cmds.pause(seconds=1)
            cmds.progressWindow(endProgress=1)
            raise RuntimeError("Name Error")

    setLOD = {
        "_XHI":['ctrl_SET'],
        "_HI":['ctrl_SET'],
        "_MID": ['ctrl_SET'],
        "_LOW": ['ctrl_SET', 'mocapJointBake_SET'],
        "_XLOW": ['ctrl_SET'],
        "_PROXY": ['ctrl_SET', 'mocapJointBake_SET'],
        "_MOCAP": ['mocapJointBake_SET']
    }

    for setName in outputSetList:
        if "XHI" in setName:
            setLOD['_XHI'].append(setName)
        if "HI" in setName:
            setLOD['_HI'].append(setName)
        if "MID" in setName:
            setLOD['_MID'].append(setName)
        if "LOW" in setName:
            setLOD['_LOW'].append(setName)
        if "XLOW" in setName:
            setLOD['_XLOW'].append(setName)
        if "PROXY" in setName:
            setLOD['_PROXY'].append(setName)
        if "MOCAP" in setName:
            setLOD['_MOCAP'].append(setName)

    tmpList = outputSetList
    for lod in list(setLOD.values()):
        tmpList = list(set(tmpList)-set(lod))

    setLOD["BASE"]=tmpList
    setLOD["BASE"].append('ctrl_SET')
    setLOD["BASE"].append('mocapJointBake_SET')

    for i in objName:
        #if i in ['output_SET']:
        if i == 'output_SET':
            continue

        pubfilePath = "%s/%s.mb" %(itemdir, fileName)

        # check grp name
        rigName = "| {0} | {0}_rig_Grp".format(i)
        checkObjName = [
            "| {0} | {0}_geo_Grp".format(i),
            "| {0} | {0}_XHI_geo_Grp".format(i),
            "| {0} | {0}_HI_geo_Grp".format(i),
            "| {0} | {0}_MID_geo_Grp".format(i),
            "| {0} | {0}_LOW_geo_Grp".format(i),
            "| {0} | {0}_XLOW_geo_Grp".format(i),
            "| {0} | {0}_PROXY_geo_Grp".format(i)
        ]
        objChildren = cmds.listRelatives(i, c=True, f=True)
        checkNameDic = {}
        checkName = 0
        for x in checkObjName:
            geoName = x.split("| {0} | ".format(i))[1]
            for objCname in objChildren:
                objCnameList = objCname.split("|")
                if len(objCnameList) == 3:
                    if geoName in objCnameList[2]:
                        objCheck = objCnameList[2].split(geoName)
                        if len(objCheck) == 2 and objCheck[0] == "" and objCheck[1] =="":
                            checkNameDic[x] = geoName.split("{0}".format(i))[1]
                        else:
                            checkName = 1
        #print checkNameDic
        mocapSetList = []
        if cmds.ls("mocapJointBake_SET"):
            mocapSetList = cmds.sets("mocapJointBake_SET", q=True)
            if mocapSetList:
                checkNameDic["mocapJointBake_SET"]="_MOCAP_geo_Grp"
                checkName = 0

        if checkName:
            checkNameDic={}
        if mocapCheck:
            fileinfo[i] = pubfilePath.replace("_MOCAP", "")
        else:
            fileinfo[i] = pubfilePath

        # lod and pub file
        if not mocapCheck:
            if checkNameDic:
                # export
                for cname, checkNameV in list(checkNameDic.items()):
                    # export select
                    if cmds.objExists(cname):

                        if cmds.objExists(rigName):

                            suffixName = checkNameV.split("_geo_Grp")[0]

                            unsetList = []
                            if suffixName == "":
                                if opts['includeProxy']:
                                    unsetList = list(set(outputSetList).difference(set(setLOD["BASE"]) | set(setLOD["_PROXY"])))

                                else:
                                    unsetList = list(set(outputSetList).difference(set(setLOD["BASE"])))
                                print("unsetList : {}".format(unsetList))

                            elif suffixName in setLOD:
                                unsetList = list(set(outputSetList).difference(set(setLOD[suffixName])))
                                print("unsetList : {}".format(unsetList))
                            else:
                                pass

                            nfileName = "{}{}.mb".format(fileName, suffixName)
                            nfilePath = "%s/%s" % (itemdir, nfileName)

                            print((">>> {} {} Pub : {}".format(i, suffixName, nfilePath)))

                            cmds.sets(unsetList, e=True, rm="output_SET")
                            print(("output_SET : {}".format(cmds.sets("output_SET", q=True))))
                            print(("selected geo grp : {}".format(cname)))
                            print(("selected rig grp : {}".format(rigName)))

                            mocap_HipsParent = ""
                            mocap_Hips = ""
                            if "mocapJointBake_SET" in cname:
                                for setobj in mocapSetList:
                                    if 'Root' == setobj:
                                        mocap_Hips = setobj
                                # mocap_Hips = mocapSetList[0]

                                mocap_Hips_dagName = cmds.ls(mocap_Hips, l=True)
                                mocap_HipsParent = "|".join(mocap_Hips_dagName[0].split("|")[:-1])
                                cmds.parent(mocap_Hips, w=True)

                            cmds.select(cl=True)
                            cmds.select(cname, r=True)
                            if suffixName == "" and opts['includeProxy']:
                                proxyName  = cname.replace("_geo_Grp", "_PROXY_geo_Grp")
                                cmds.select(proxyName, add=True)
                                print(("selected proxy grp : {}".format(proxyName)))

                            if not mocap_Hips:
                                cmds.select(rigName, add=True)

                            mocaphikList = cmds.ls(
                                type=["HIKState2SK", "HIKCharacterNode", "HIKProperty2State", "HIKSolverNode"])

                            cmds.select("output_SET", ne=True, add=True)
                            cmds.select(mocaphikList, add=True)
                            cmds.file(nfilePath, force=1, options="v=0;", typ="mayaBinary", pr=1, es=1)
                            exported_files.append(nfilePath)

                            cmds.sets(unsetList, e=True, fe="output_SET")
                            if mocap_HipsParent:
                                cmds.parent(mocap_Hips, mocap_HipsParent)
                        else:
                            cmds.confirmDialog(title='Confirm', message='어셋 리그 {}이 없습니다.\n'.format(rigName))

                            cmds.pause(seconds=1)
                            cmds.progressWindow(endProgress=1)

                            raise RuntimeError("Name Error")

                    # cmds.file(rename="%s/%s.mb" % (itemdir, fileName))
                    # cmds.file(f=1, save=1, options="v=0;")

                cmds.progressWindow(e=True, progress=100, status='Done')
                cmds.pause(seconds=1)
                cmds.progressWindow(endProgress=1)

                cmds.select(cl=True)

            else:
                msg = ''
                for cname in checkObjName:
                    msg += cname+"\n"

                cmds.confirmDialog(title='Confirm', message='어셋 geo_Grp 이름은 다음 규칙을 따라야합니다.\n'+msg)

                cmds.pause(seconds=1)
                cmds.progressWindow(endProgress=1)

                raise RuntimeError("Name Error")

        else: # _MOCAP.mb file
            #mocaphikList = cmds.ls(type="HIKState2SK")
            mocaphikList = cmds.ls(type=["HIKState2SK", "HIKCharacterNode", "HIKProperty2State", "HIKSolverNode"])
            cmds.select(cl=True)
            cmds.select(i, r=True)
            cmds.select("output_SET", ne=True, add=True)
            cmds.select(mocaphikList, add=True)
            cmds.file(pubfilePath, force=1, options="v=0;", typ="mayaBinary", pr=1, es=1)
            print((">>> MOCAP Pub : {}".format(pubfilePath)))
            exported_files.append(pubfilePath)

            cmds.progressWindow(e=True, progress=100, status='Done')
            cmds.pause(seconds=1)
            cmds.progressWindow(endProgress=1)

            cmds.select(cl=True)
    pub_xml_update(exported_files=exported_files, comment=comment)
    return fileinfo

def pub_xml_update(exported_files=None, comment=None):

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    def _get_user_infomation_2(ip):
        url = "http://gw.m83.co.kr/_service/path.php?mode=get_user_info&ip={}".format(ip)
        url_result = urllib.request.urlopen(url)
        user_info = json.load(url_result)
        return user_info

    user_info = _get_user_infomation_2(IPAddr)[0]

    for pub_file in exported_files:
        xml = ArmoIO.XMLhandler(pub_file)
        result = xml.setInfo(user_info['mb_name'], comment)



def itemRootAssetNameCheck(itemdir): #export 2
    itemName = itemdir.split("/")[5]
    if not cmds.ls(itemName):
        print("( model Sciprt 93 line ) Erro : Not match Asset Name !!  ")
        return
    cmds.select(itemName) 
    cmds.select( "output_SET", ne=1, add=1)
    return itemName

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
    selectObjectList =  cmds.listRelatives(itemName, ad=1)
    objectList = cmds.ls(selectObjectList, type="transform")
    objectShapeList = cmds.ls(selectObjectList, type="mesh")
    
    for i in objectList :
        shapeName = cmds.ls( i, dag=1, type="mesh")
        
        if cmds.listRelatives(i, s=1) :
            shapeName = shapeName [0]
        else:
            continue
        newShapeName = "%sShape" %i
        
        if shapeName != newShapeName :
            notMatchShapeName.update( {shapeName :newShapeName })
            
    return notMatchShapeName

def getFileList():
    fileDir = cmds.file(q=1, sn=1)
#     fileName = os.path.basename(fileDir ).split('.')[0]

    prjDir = re.search( ".+(?=/[\w]+/(pub|wip)/)",fileDir ).group()
    partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()
    fileName = re.search( "[\w]+(?=\.mb)",fileDir  ).group()        

    globalTakeDir = "%s/Take" %prjDir
    localTakeDir = "%s/%s/wip/data/Take" % (prjDir, partType)

    return prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir  


def checkTake(itemType):
    prjDir,fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
    globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
    localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)

    # check dir
    if not os.path.isdir(globalTakeDir):
        os.makedirs(globalTakeDir)

    if not os.path.isdir(localTakeDir):
        os.makedirs(localTakeDir)

    # global Take
    if not os.path.isfile( globalCurrentTake ):
        take = {}

    else:
        with open("%s" %( globalCurrentTake ), 'r' ) as f:
            take = json.load(f)

    if not take.get(itemType):
        take["%s" %itemType] ={}

    # local Take
    if not os.path.isfile( localCurrentTake ):
        local_take = {}

    else:
        with open("%s" %( localCurrentTake ), 'r' ) as f:
            local_take = json.load(f)

    if not local_take.get(itemType):
        local_take["%s" %itemType] ={}
                    
    return take, local_take

def saveTake(itemType, take, local_take):
    prjDir,fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
    globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
    localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)

    local_take = convert_byte_to_string.convert_byte_to_string(local_take)
    # local Take Save
    with open("%s" %localNewTake, 'w') as f:
        json.dump(local_take,  f, indent=4)    

    take = convert_byte_to_string.convert_byte_to_string(take)
    # global Take Save
    with open("%s" %globalNewTake, 'w') as f:
        json.dump(take,  f, indent=4)

def saveLocalTake(itemType, take, local_take):
    prjDir,fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
    globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
    localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)

    local_take = convert_byte_to_string.convert_byte_to_string(local_take)
    # local Take Save
    with open("%s" %localNewTake, 'w') as f:
        json.dump(local_take,  f, indent=4)    

#     # global Take Save
#     with open("%s" %globalNewTake, 'w') as f:
#         json.dump(take,  f, indent=4)



def subAssetInfoExport( objList, rigList ):

    if not rigList:
        return
    
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
    globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
    localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)

    typeList = {"rig":"rig", "ani":"rig", "matchmove":"rig", "layout":"rig", "model":"rigEnv", "lit":"rig","postviz":"rig"}
    itemType = typeList [partType]
    
    #getTake
    take, local_take = checkTake(itemType) 

    fileNameDict= {}
    versionDict = {}
    userNameDict= {}
    ipaddrDict  = {}
    frameDict   = {}
    dateDict    = {}
    objectListDict ={}
    objectCheckDict={}
    updateListDict ={}
    globalversionDict={}

    rigObjectList={}
#     print objList, rigList

#     print  "rig", rigList
#     print "rig", objList
    
#     print ">", rigList
#     print ">", objList
    for item in objList:
        # file Name
        if not cmds.ls(item) :
            return
        
        assetName = item.split(":")[1]

        if type(rigList) == type({}):
#             print ">", assetName
            fileDir = rigList.get(assetName)
            if fileDir== None:
                continue
            fileNameDict.update( { item : fileDir} )
            rigObjectList.update( { item : fileDir})  ######################<<
        else:
#             print ">>>", objList
            rigObjectList = objList
        

        #take local version
        versionDict.update( { item : None})#localNewNum} ) #0rig
        globalversionDict.update( { item : globalNewNum} )

        # user info
        userName =  socket.gethostname()
        userNameDict.update({ item : None})  #userName

        #ipaddr
        cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
        getipaddr = Popen(cmd, shell = True, stdout = PIPE)
        ipaddr = getipaddr.communicate()[0][:-1]
        ipaddrDict.update({ item : None}) #ipaddr
        
        # frame info
        startF = cmds.playbackOptions(min=1, q=1)
        endF   = cmds.playbackOptions(max=1, q=1)
        frameDict.update({ item : None} )#"%d-%d" %(startF, endF)})
                
        # date info
        nowdate = str(datetime.datetime.now())
        date = nowdate.rsplit(":",1)[0]
        dateDict.update({ item :  None}) #date

        #object List info
        objectListDict.update({ item :  None } ) #objList[item]

        #object check info
        checkList = {"model":0, "rig" : 0,"ani":1, "matchmove":1, "layout":1, "dyn":0, "cloth":0,"hair":0, "clothSim":0, "lit" : 0, "fur":0, "lookdev" : 0 ,"fx" : 0 }
        objectCheckDict.update({ item :  checkList} )

        #update List info
        updateListDict.update({ item :  None}) #objList[item]
                                                                                                                                                    
    if take[ itemType ].get('objectList'):  # is itemType
#             if take[ itemType ]['objectList'].get(item):  # is item
        newTake =  subtakeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, rigObjectList, objectCheckDict )
#             else:
#                 newTake = takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
    else:
        newTake = subtakeSetInfo(take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, rigObjectList, objectCheckDict) 
        
    if local_take[ itemType ].get('objectList'):  # is itemType
#             if local_take[ itemType ]['objectList'].get(item):  # is item
#                 local_Newtake = takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
#             else:
        local_Newtake = subtakeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, rigObjectList, objectCheckDict)                
    else:
        local_Newtake = subtakeSetInfo(local_take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, rigObjectList, objectCheckDict)
        #--------------------------------------------------------

    take = newTake
    local_take = local_Newtake

    take[ itemType ]["updateList"]= updateListDict 
    local_take[ itemType ]["updateList"]= updateListDict
    
    if type(rigList) == type({}):
        
        saveTake( itemType, take ,local_take)
    else:
        saveLocalTake( itemType, take ,local_take)


def subtakeSetInfo(take, itemType, type, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict):
    if type == True:
        take[ itemType ]["fileName"   ].update( fileNameDict   )  # 모델링꺼 데이타 가져 오기..
        take[ itemType ]["version"    ].update( versionDict    )
        take[ itemType ]['username'   ].update( userNameDict   )
        take[ itemType ]['ipaddr'     ].update( ipaddrDict     )
        take[ itemType ][ 'frame'     ].update( frameDict      )
        take[ itemType ]['date'       ].update( dateDict       )
        take[ itemType ]['objectList' ].update( objList        )
        take[ itemType ]['objectCheck'].update( objectCheckDict)    
    else:
        take[ itemType ].update( { "fileName"  : fileNameDict } )
        take[ itemType ].update( {"version"    : versionDict  } ) 
        take[ itemType ].update( {'username'   : userNameDict } )
        take[ itemType ].update( {'ipaddr'     : ipaddrDict   } )
        take[ itemType ].update( { 'frame'     : frameDict    } )
        take[ itemType ].update( {'date'       : dateDict     } )
        take[ itemType ].update( {'objectList' : objList      } )
        take[ itemType ].update( {'objectCheck': objectCheckDict} )
        
    return take

# def assetInfoExport(prjDir,  objList, partType, itemType ):
#     globalTakeDir = "%s/Take" %prjDir
#     localTakeDir = "%s/%s/wip/data/Take" % (prjDir, partType.lower() )
# 
#     globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
#     
#     # file info
#     fileDir = cmds.file(q=1, sn=1)
#     fileName = os.path.basename(fileDir ).split('.')[0]
#     
#     localCurrentTake, localNewTake,localNuewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)
# 
# 
#     # check dir
#     if not os.path.isdir(globalTakeDir):
#         os.makedirs(globalTakeDir)
# 
#     if not os.path.isdir(localTakeDir):
#         os.makedirs(localTakeDir)
# 
# 
#     # global
#     if not os.path.isfile( globalCurrentTake ):
#         take = {}
#         take["%s" %partType] = {"%s" %itemType : None}
#         take["%s" %partType]["%s" %itemType] ={}
# 
#     else:
#         with open("%s" %( globalCurrentTake ), 'r' ) as f:
#             take = json.load(f)
#             
#     if not take.get(partType):
#         take["%s" %partType] = {}
#         take["%s" %partType] = {"%s" %itemType : None}
#         take["%s" %partType]["%s" %itemType] ={}
# #     print "objectList", take["Ani"]['atom']["objectList"]
# 
#     if not take[partType].get(itemType):
#         take["%s" %partType]["%s" %itemType] ={}    
#     
#     # asset info
#     allnameSpace= list(set(cmds.ls(sns=1)[1::2]))
#     allnameSpace.remove(':')
#     take[ partType ][ itemType ].update( { "fileName" : {fileName : fileDir}} )
#     
#     #take version
# #     take= {"Ani": {"atom":None}  }
#     take[ partType ][ itemType ].update( {"version" : localNuewNum} ) 
# 
#     # user info
#     userName =  socket.gethostname()
#     take[ partType ][ itemType ].update( {'username' : userName} )
#                                               
#     cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
#     getipaddr = Popen(cmd, shell = True, stdout = PIPE)
#     ipaddr = getipaddr.communicate()[0][:-1]
#     take[ partType ][ itemType ].update( {'ipaddr' : ipaddr} )
#     
#     # frame info
#     startF = cmds.playbackOptions(min=1, q=1)
#     endF   = cmds.playbackOptions(max=1, q=1)
#     take[ partType ][ itemType ].update( { 'frame' : "%d-%d" %(startF, endF)} )
#     
#     # date info
#     nowdate = str(datetime.datetime.now())
#     date = nowdate.rsplit(":",1)[0]
#     
#     take[ partType ][ itemType ].update( {'date': date} )
#     
#      
# #     print "objectList", take["Ani"]['atom'].get("objectList") == None
#     if take[ partType ][ itemType].get("objectList") == None:
#         take[ partType ][ itemType ]["objectList"] = {}
#         take[ partType ][ itemType ]["objectList"].update( objList )
#     else:        
#         take[ partType ][ itemType ]["objectList"].update(  objList ) 
#         
#     # check
#     if take[ partType ][ itemType ].get("objectCheck") == None:
#         take[ partType ][ itemType ]["objectCheck"] = {}
#         checkList ={}
#         map(lambda x : checkList.update( {x:1}) , objList)
#         take[ partType ][ itemType ]["objectCheck"].update( checkList )
#         
#     else:
#         checkList ={}
#         map(lambda x : checkList.update( {x:1}) , objList)
#         take[ partType ][ itemType ]["objectCheck"].update( checkList )
# 
#     take[ partType ][ itemType ]["updateList"]= objList 
# 
#     # local Take
#     if not os.path.isfile( localCurrentTake ):
#         with open("%s" %localNewTake, 'w') as f:
#             json.dump(take,  f, indent=4)        
#          
#     else:
#         with open("%s" %( localCurrentTake ), 'r' ) as f:
#             local_take = json.load(f)
# 
#         if  not local_take.get(partType):              #not partType
#             local_take[ partType ] = take [partType]
# 
#         elif not local_take[partType].get(itemType):
#             local_take[ partType ][itemType] = take [partType][itemType]
#                     
#         else:
#             local_take[ partType ][ itemType ]["objectList"].update( take[ partType ][ itemType ]["objectList"])
#             local_take[ partType ][ itemType ]["objectCheck"].update( take[ partType ][ itemType ]["objectCheck"])
#     
#         with open("%s" %localNewTake, 'w') as f:
#             json.dump(take,  f, indent=4)
# 
# 
#     # global Take
#     with open("%s" %globalNewTake, 'w') as f:
#         json.dump(take,  f, indent=4)

#------------------------------------------------------------------------------------------------
def exportTake(objList, takeTypeList, itemType):
    # global? local? Take
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()            

    notFoundRig = {}
    rigData = {}
    
    for takeType in takeTypeList:
        # Take Type select
        if takeType == "globalTake":
            currentTake,  newTakeDir   = versionUpTakeName(globalTakeDir, "take")
        elif takeType == "localTake":    
            currentTake,  newTakeDir   = versionUpTakeName(localTakeDir, "%s" %fileName)

        # check Take
        #itemType = "model"
        
        getTake = checkTake( itemType,  currentTake )
        
        if prjDir.split("/")[3] in ["assets"] and partType in ["rig"]: #daeho  Asset model.
            # write AssetInfo
            take = assetInfoExport(objList, getTake, fileDir, newTakeDir)
            
#         elif partType in ["ani", "matchmove","model" ,"lit"]: #daeho1:daeho
#             take  = getTake
#             for assetName in objList:
#                 
#                 assetTake = findAsset( assetName,takeType ) #{u'username': {u'daeho': u'DOM'}, u'objectCheck': {u'daeho': {u'lit': 1, u'rig': 1, u'model': 1, u'fx': 1, u'lookdev': 1}}, u'frame': {u'daeho': u'1-120'}, u'ipaddr': {u'daeho': u''}, u'fileName': {u'daeho': u'/show/DH/assets/cha/daeho/model/pub/daeho_model_v01.mb'}, u'version': {u'daeho': u'/show/DH/assets/cha/daeho/Take/take.0013.json'}, u'updateList': {u'daeho': u'/show/DH/assets/cha/daeho/model/pub/daeho_model_v01.mb'}, u'date': {u'daeho': u'2015-08-21 18:58'}, u'objectList': {u'daeho': u'/show/DH/assets/cha/daeho/model/pub/daeho_model_v01.mb'}} #
#                 
#                 if assetTake != None:
#                     modelData.update ( assetTake["objectList"] )
#                     if "model" in partType:
#                         take = addTake(take, assetTake, assetName, "modelEnv")
#                     else:
#                         take = addTake(take, assetTake, assetName, "model")
#                 else:
#                     notFoundModel[assetName]=""
#         print notFindModel

        # saveTake 
#         saveTake( newTakeDir, take )
# 
#     # notOb
#     notOb = ""
#     for i in notFoundModel:
#         notOb += "%-45s \n" %i    
#     
#     if notOb:
#         cmds.confirmDialog( title='Not Found Model', message=notOb, button=['ok'])
#      
#     return modelData
#-----------------------------------------------------------------------------------------

def assetInfoExport(objList): # ( shotDir, objList , partType): #, itemType
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
    globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
    localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)

    typeList = {"rig":"rig", "ani":"rig","matchmove":"rig", "layout":"rig", "lit":"rig", "dyn":"rig"}
    itemType = typeList [partType]
    
    if "_LOW" in list(objList.values())[0]:
        itemType="rigLow"
    elif "_MID" in list(objList.values())[0]:
        itemType="rigMid"
    elif "_HI" in list(objList.values())[0]:
        itemType="rigHi"
    elif "_XLOW" in list(objList.values())[0]:
        itemType="rigLow"
    elif "_XHI" in list(objList.values())[0]:
        itemType="rigXHi"
    elif "_MOCAP" in list(objList.values())[0]:
        itemType="mocapRig"
    else:
        itemType = typeList [partType]

    take, local_take = checkTake(itemType)
#     print take, local_take
    # asset info
#     allnameSpace= list(set(cmds.ls(sns=1)[1::2]))
#     allnameSpace.remove(':')

    fileNameDict= {}
    versionDict = {}
    userNameDict= {}
    ipaddrDict  = {}
    frameDict   = {}
    dateDict    = {}
    objectListDict ={}
    objectCheckDict={}
    updateListDict ={}
    globalversionDict={}

    for item in objList:
        # file Name
        fileNameDict.update( { item : fileDir} )

        #take local version
        versionDict.update( { item : localNewNum} )
        globalversionDict.update( { item : globalNewNum} )

        # user info
        userName =  socket.gethostname()
        userNameDict.update({ item : userName})

        #ipaddr
        cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
        getipaddr = Popen(cmd, shell = True, stdout = PIPE)
        ipaddr = getipaddr.communicate()[0][:-1]
        ipaddrDict.update({ item : ipaddr})
        
        # frame info
        startF = cmds.playbackOptions(min=1, q=1)
        endF   = cmds.playbackOptions(max=1, q=1)
        frameDict.update({ item : "%d-%d" %(startF, endF)})
                
        # date info
        nowdate = str(datetime.datetime.now())
        date = nowdate.rsplit(":",1)[0]
        dateDict.update({ item :  date})
                
        #object List info
        objectListDict.update({ item :  objList[item] } )

        #object check info
        checkList = {"model":1, "rig" : 1,"ani":1, "matchmove":1, "layout":1, "dyn":1, "cloth":1,"hair":1, "clothSim":1, "lit" : 1, "fur":1, "lookdev" : 1 ,"fx" : 1 }
        objectCheckDict.update({ item :  checkList} )

        #update List info
        updateListDict.update({ item :  objList[item]})

    if take.get(itemType) == None:
        take[ itemType ] = {}
        
    if take[ itemType ].get('objectList'):  # is itemType
        if take[ itemType ]['objectList'].get(item):  # is item
            newTake =  takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict )
        else:
            newTake = takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
    else:
        newTake = takeSetInfo(take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict) 
        
    if local_take[ itemType ].get('objectList'):  # is itemType
        if local_take[ itemType ]['objectList'].get(item):  # is item
            local_Newtake = takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
        else:
            local_Newtake = takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)                
    else:
        local_Newtake = takeSetInfo(local_take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
        #--------------------------------------------------------

    take = newTake      
    local_take = local_Newtake

    take[ itemType ]["updateList"]= updateListDict 
    local_take[ itemType ]["updateList"]= updateListDict

    saveTake( itemType, take ,local_take)

def takeSetInfo(take, itemType, type, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict):
    if type == True:
        take[ itemType ]["fileName"   ].update( fileNameDict   )
        take[ itemType ]["version"    ].update( versionDict    )
        take[ itemType ]['username'   ].update( userNameDict   )
        take[ itemType ]['ipaddr'     ].update( ipaddrDict     )
        take[ itemType ][ 'frame'     ].update( frameDict      )
        take[ itemType ]['date'       ].update( dateDict       )
        take[ itemType ]['objectList' ].update( objList        )
        take[ itemType ]['objectCheck'].update( objectCheckDict)    
    else:
        take[ itemType ].update( { "fileName"  : fileNameDict } )
        take[ itemType ].update( {"version"    : versionDict  } ) 
        take[ itemType ].update( {'username'   : userNameDict } )
        take[ itemType ].update( {'ipaddr'     : ipaddrDict   } )
        take[ itemType ].update( { 'frame'     : frameDict    } )
        take[ itemType ].update( {'date'       : dateDict     } )
        take[ itemType ].update( {'objectList' : objList      } )
        take[ itemType ].update( {'objectCheck': objectCheckDict} )
        
    return take


def shotInfoExport(prjDir,  objList, itemType ):
    globalTakeDir = "%s/Take" %prjDir
    globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
    
    # file info
    fileDir = cmds.file(q=1, sn=1)
    fileName = os.path.basename(fileDir ).split('.')[0]

    # check dir
    if not os.path.isdir(globalTakeDir):
        os.makedirs(globalTakeDir) 

    # global
    if not os.path.isfile( globalCurrentTake ):
        take = {}
        take["%s" %itemType] = {}
         
    else:
        with open("%s" %( globalCurrentTake ), 'r' ) as f:
            take = json.load(f)
             
#     if not take.get(partType):
#         take["%s" %partType] = {}
#         take["%s" %partType] = {"%s" %itemType : None}
#         take["%s" %partType]["%s" %itemType] ={}
#     print "objectList", take["Ani"]['atom']["objectList"]

    if not take.get(itemType):
        take["%s" %itemType] ={}

    fileNameDict= {}
    versionDict = {}
    userNameDict= {}
    ipaddrDict  = {}
    frameDict   = {}
    dateDict    = {}
    objectListDict ={}
    objectCheckDict={}
    updateListDict ={}
    globalversionDict={}

    for item in objList:
        # file Name
        fileNameDict.update( { item : fileDir} )

        #take local version
        versionDict.update( { item :globalNewNum}) # localNewNum} ) ##################
        globalversionDict.update( { item : globalNewNum} )

        # user info
        userName =  socket.gethostname()
        userNameDict.update({ item : userName})

        #ipaddr
        cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
        getipaddr = Popen(cmd, shell = True, stdout = PIPE)
        ipaddr = getipaddr.communicate()[0][:-1]
        ipaddrDict.update({ item : ipaddr})
        
        # frame info
        startF = cmds.playbackOptions(min=1, q=1)
        endF   = cmds.playbackOptions(max=1, q=1)
        frameDict.update({ item : "%d-%d" %(startF, endF)})
                
        # date info
        nowdate = str(datetime.datetime.now())
        date = nowdate.rsplit(":",1)[0]
        dateDict.update({ item :  date})
                
        #object List info
        objectListDict.update({ item :  objList[item] } )

        #object check info
        checkList = {"model":1, "rig" : 1,"ani":1, "matchmove":1, "layout":1, "dyn":1, "cloth":1,"hair":1, "clothSim":1, "lit" : 1, "fur":1, "lookdev" : 1 ,"fx" : 1 }
        objectCheckDict.update({ item :  checkList} )

        #update List info
        updateListDict.update({ item :  objList[item]})

    if take[ itemType ].get('objectList'):  # is itemType
        if take[ itemType ]['objectList'].get(item):  # is item
            newTake =  takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict )
        else:
            newTake = takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
    else:
        newTake = takeSetInfo(take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)         

    take = newTake      
    take[ itemType ]["updateList"]= updateListDict 

    # global Take
    take = convert_byte_to_string.convert_byte_to_string(take)
    with open("%s" %globalNewTake, 'w') as f:
        json.dump(take,  f, indent=4)



def rigListInfoWrite(shotDirItem, rigDir):
    if not rigDir:
        return
    
    for i in rigDir:
        if "/seq/" in rigDir[i]:
            return
        assetDir = re.search( ".+(?=/[\w]+/pub/)",rigDir[i]).group()
        globalTakeList = "%s/Take/takeList.json" %assetDir
        
        if not os.path.isdir( "%s/Take" %assetDir ):
            os.mkdir("%s/Take" %assetDir )
        
        if not os.path.isfile( globalTakeList ):
            takelist = {}
            takelist["rig"]={}
        else:
            with open("%s" %( globalTakeList ), 'r' ) as f:
                takelist = json.load(f)

#         shotName = prjDir.rsplit("/",1)[1]
        if not takelist.get("rig"):
            takelist["rig"]={}
#         takelist["rig"].update( {"%s" %shotName : "%s" %prjDir} )
        takelist["rig"].update( shotDirItem )

    takelist = convert_byte_to_string.convert_byte_to_string(takelist)
    # global Take
    with open("%s" %globalTakeList, 'w') as f:
        json.dump(takelist,  f, indent=4)

#-------------------------------------------------------------------------------------------
def shotTakeAssetInfoExport (prjDir, objList  , partType ):
    globalTakeList = "%s/Take/takeList.json" %prjDir

    if os.path.isfile( globalTakeList ):
        with open("%s" %( globalTakeList ), 'r' ) as f:
            take = json.load(f)

        if take.get("%s" %partType):
            for i in take["%s" %partType]:
                shotInfoExport(take["%s" %partType][i],  objList, partType)
    return


