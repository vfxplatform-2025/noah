# -*- coding:utf-8 -*-
'''
Created on Jun 8, 2015

@author: m83
'''
import os, sys, glob, re, string
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import maya.cmds as cmds
import maya.mel as mel
import getpass
from subprocess import *
import xml.etree.ElementTree as et
import json
import socket
import datetime
import utilScript
import imp
imp.reload(utilScript)
import tractorJobScript
imp.reload(tractorJobScript)
import takeScript
imp.reload(takeScript)


def atomAllLoadSet(name):
    allCtrlSet = []
    if "atomSetAllLoad" == name:
        if cmds.ls("*:ctrl_SET", r=1):
            cmds.select("*:ctrl_SET", r=1, ne=1)
            allCtrlSet = cmds.ls(sl=1)
            cmds.select(cl=True)
        elif cmds.ls("*:AniControlSet", r=1):
            cmds.select("*:AniControlSet", r=1, ne=1)
            allCtrlSet = cmds.ls(sl=1)
            cmds.select(cl=True)

    elif "atomMocapSetLoad" == name:
        if cmds.ls("*:mocapJointBake_SET", r=1):
            cmds.select("*:mocapJointBake_SET", r=1, ne=1)
            allCtrlSet = cmds.ls(sl=1)
            cmds.select(cl=True)
    else:
        try:
            allCtrlSet = []
            [x for x in cmds.ls(sl=1, type="objectSet") if cmds.ls(x.rsplit(":", 1)[0] + ":ctrl_SET") and allCtrlSet.append(
                x.rsplit(":", 1)[0] + ":ctrl_SET")]
        except:
            print("set Select !")
            return []
    # todo: asset category 추가 준비 참조 code.
    # ref_list = cmds.ls(references=True)
    # print ref_list
    #
    # for ref in ref_list:
    #     print cmds.referenceQuery(ref, namespace=True, shortName=True)
    #
    # all_list = [
    #     {'file': cmds.referenceQuery(ref, f=True, withoutCopyNumber=True),
    #      'name_space': cmds.referenceQuery(ref, namespace=True, shortName=True)}
    #     for ref in ref_list]
    # print all_list
    # for i in range(len(allCtrlSet)):
    #     category = None
    #     item_name = allCtrlSet[i].split(':')[0]
    #     for ref in all_list:
    #         if ref['name_space'] == item_name:
    #             category = ref['file'].split('assets')[1].split('/')[1]
    #     allCtrlSet[i] = (allCtrlSet[i], category)
    #
    return list(set(allCtrlSet))

def atomKeyBake(num): #export 4
    print("Key Bake !")
    selectObj = cmds.ls(sl=1)
    startF = cmds.playbackOptions(min=1, q=1)
    endF   = cmds.playbackOptions(max=1, q=1)
    cmds.refresh(su=1)

    cmds.bakeResults ( selectObj,
                       shape=True,
                       simulation =True,
                       t =(startF-num,endF+num),
                       sampleBy =1,
                       disableImplicitControl = True,
                       preserveOutsideKeys =True,
                       sparseAnimCurveBake= False,
                       removeBakedAttributeFromLayer =False ,
                       removeBakedAnimFromLayer =False,
                       bakeOnOverrideLayer = False,
                       minimizeRotation = True)
    cmds.refresh(su=0)
    print("bake OK!")

def atomEulerFilter(item):
    # euler filter
    if cmds.nodeType(item) == "objectSet":
        setList = cmds.sets(item, q=True)
        cmds.select(setList, r=True)
        cmds.filterCurve()

def atomExport( filename, itemdir,item, num):
    utilScript.pluginChecks('atom')

    #atom setting
    atom_animLayer = 0
    startF = cmds.playbackOptions(min=1, q=1)
    endF   = cmds.playbackOptions(max=1, q=1)
    atom_select    = "selectedOnly"
    cmds.select(item, r=True)

    fileinfo ={}    # :ctrl_SET  ==> :gunShot
    print(filename, itemdir,item, num)
    itemName = re.search("[\w]*[\D](?=([\d]+)?:)", item).group()

    namespaceName = item.split(":")[0]
    atom_file_name = item.replace(":", "_")
    fileinfo[ "%s:%s" %(namespaceName,itemName) ] = "%s/%s.atom" %(itemdir, atom_file_name)

    cmd = "precision=8"
    cmd += ";statics=1;baked=1;sdk=0;constraint=0"
    cmd += ";animLayers=%d" %atom_animLayer + ";selected=%s" %atom_select + ";whichRange=2;range=%d" %startF + ":%d" %endF + ";hierarchy=none"
    cmd += ";controlPoints=0;useChannelBox=1;options=keys"
    cmd += ";copyKeyCmd=-animation objects -time >%d" %(startF - num) + ":%d" %(endF + num) + "> -float >%d" %startF + ":%d" %endF + "> "
    cmd += "-option keys -hierarchy none -controlPoints 0"

    # cmds.file( "%s/%s.atom" %(itemdir, item.split(":")[0]), es =1, force=1, options="%s"%cmd, typ= "atomExport")
    cmds.file( "%s/%s.atom" %(itemdir, atom_file_name), es =1, force=1, options="%s"%cmd, typ= "atomExport")

    cmds.select(cl=1)

    return fileinfo

def atomExport2( currentSceneName, exportDir, itemList, num, step_num, frameType, farmSceneName, takeVersionUp,
                 fileType, mayaVersion, scriptPath, exportType, keybake, handleNum, tractorEngineV):

    utilScript.pluginChecks('atom')

    atom_animLayer = 0
    startF = cmds.playbackOptions(min=1, q=1)
    endF   = cmds.playbackOptions(max=1, q=1)
    atom_select    = "selectedOnly"

    print(currentSceneName, exportDir, step_num)

    if exportType == "local" and keybake:
        atomKeyBake(handleNum)

    fileinfo = {}  # :ctrl_SET  ==> :gunShot
    itemDic = {}
    for item in itemList:

        itemName = re.search("[\w]*[\D](?=([\d]+)?:)", item).group()

        namespaceName = item.split(":")[0]
        atom_file_name = item.replace(":", "_")
        fileinfo[ "%s:%s" %(namespaceName,itemName) ] = "%s/%s.atom" %(exportDir, atom_file_name)

        opt = "precision=8"
        opt += ";statics=1;baked=1;sdk=0;constraint=0"
        opt += ";animLayers=%d" %atom_animLayer + ";selected=%s" %atom_select + ";whichRange=2;range=%d" %startF + ":%d" %endF + ";hierarchy=none"
        opt += ";controlPoints=0;useChannelBox=1;options=keys"
        opt += ";copyKeyCmd=-animation objects -time >%d" %(startF - num) + ":%d" %(endF + num) + "> -float >%d" %startF + ":%d" %endF + "> "
        opt += "-option keys -hierarchy none -controlPoints 0"

        itemDic[item] = {
            "type" : "atom",
            "fileinfo" : fileinfo,
            "exportDir" : exportDir,
            "fileName" : atom_file_name,
            "opt" : opt,
            "keybake" : keybake,
            "handleNum" : handleNum
        }
        if exportType == "local":

            cmds.select(item, r=True)
            # cmds.file( "%s/%s.atom" %(exportDir, item.split(":")[0]), es =1, force=1, options="%s"%opt, typ= "atomExport")
            cmds.file( "%s/%s.atom" %(exportDir, atom_file_name), es =1, force=1, options="%s"%opt, typ= "atomExport")
            cmds.select(cl=1)

    if exportType == "farm":
        tractorJobScript.tractorExport(startF, endF, currentSceneName, itemDic, num, step_num, frameType, farmSceneName,
                                       takeVersionUp, mayaVersion, fileType, scriptPath, tractorEngineV)

    return fileinfo


def atomImport(itemInfo, type, rootType, *args):
    utilScript.pluginChecks('atom')

    for i in itemInfo:
        writeItemName = atomImportFile(i, itemInfo[i], rootType, type)
    return writeItemName


def atomImportFile(itemName, atome_file, rootType, type=None, set_type=None):
    namespaceName = itemName.split(":")[0]
    itemAssetName = itemName.split(":")[1]
    ctrlSetName = ""

    if "_SET" in atome_file:
        try:
            set_type = os.path.basename(atome_file).split('_', 1)[1].split('.')[0]
        except:
            set_type = "ctrl_SET"
        ctrlSetName = "%s:%s" % (namespaceName, set_type)

        cmds.select(ctrlSetName, r=True)
        if not cmds.ls(sl=True):
            ctrlSetName = ""
    else:
        # atom파일 이름에 set정보가 없는 경우.
        # atom파일을 읽어서 정규식으로 object 리스트를 가져와서 갯수를 비교해서 같은 개수인 경우에 SET을 선택하도록 만들었음.
        set_type_name = ['mocapJointBake_SET', 'ctrl_SET']
        atom_re = '(?<={0}:)\w+'.format(namespaceName)
        atom_items = list()

        with open(atome_file, 'r') as f:
            atom = f.read()
            match = re.findall(atom_re, atom)
            if match:
                atom_items = ['{0}:{1}'.format(namespaceName, item) for item in match]
        for set_name in set_type_name:
            set_name_str = '{0}:{1}'.format(namespaceName, set_name)
            cmds.select(set_name_str)
            selectItem = cmds.ls(sl=1)
            if len(atom_items) == len(selectItem):
                ctrlSetName = set_name_str
                cmds.select(ctrlSetName, r=True)
                break

    if not cmds.ls(ctrlSetName):
        # delete namespace
        if ":" in ctrlSetName and cmds.namespace(exists="%s" % ctrlSetName.split(':')[0]):
            cmds.namespace(rm="%s" % ctrlSetName.split(':')[0], mnr=1)
        print(ctrlSetName, "not Object !!")
        return

    atomFileMap = "%swip/data" % (atome_file.split("wip/data")[0])

    print(ctrlSetName)
    # if key Delete Key
    if cmds.ls("%s.atom" % itemName.replace(":%s" % itemAssetName, ":output_SET")):
        cmds.select(ctrlSetName)
        selectItem = cmds.ls(sl=1)
        list(map(lambda x: cmds.cutKey(ctrlSetName, at=x), cmds.listAttr(selectItem, k=1)))

    cmds.select(ctrlSetName)

    # key Delete
    selectCtrlSet = cmds.ls(sl=1)
    cmds.cutKey(selectCtrlSet, cl=1)

    cmd = ";;targetTime=3;option=insert;"
    cmd += "match=string;;selected=selectedOnly;"
    cmd += "search=%s;replace=%s;prefix=;suffix=;" % (namespaceName, namespaceName)
    cmd += "mapFile=%s;" % atomFileMap
    print(">>", atome_file)
    cmds.file("%s" % atome_file, i=1, type="atomImport", ra=True, options="%s" % cmd)

    # info write
    writeItemName = None
    if "atom" == rootType:
        writeItemName = initAtomImportWrite(itemName, atome_file)

    elif "mmAtom" == rootType:
        writeItemName = initMmAtomImportWrite(itemName, atome_file)

    elif "modelAtom" == rootType:
        writeItemName = initModelAtomImportWrite(itemName, atome_file)
    #     assetImportInfoExport( {itemName :  atome_file}, rootItem )
    elif "atomRender" == rootType:
        writeItemName = initRenderAtomImportWrite(itemName, atome_file)

    return writeItemName


# write
def initAtomImportWrite(item, filename):
    itemAssetName = item.split(":")[1]
    reNameItem = item.replace(":%s" % itemAssetName, ":output_SET")

    deleteUsrAttr(reNameItem)

    if not cmds.ls('%s.atom' % reNameItem):
        cmds.addAttr('%s' % reNameItem, ln="atom", dt="string")

    cmds.setAttr('%s.atom' % reNameItem, "%s,%s" % (item, filename), type="string")
    return '%s.atom' % reNameItem


def initMmAtomImportWrite(item, filename):
    itemAssetName = item.split(":")[1]
    reNameItem = item.replace(":%s" % itemAssetName, ":output_SET")

    deleteUsrAttr(reNameItem)

    if not cmds.ls('%s.mmAtom' % reNameItem):
        cmds.addAttr('%s' % reNameItem, ln="mmAtom", dt="string")

    cmds.setAttr('%s.mmAtom' % reNameItem, "%s,%s" % (item, filename), type="string")
    return '%s.mmAtom' % reNameItem


def initModelAtomImportWrite(item, filename):
    itemAssetName = item.split(":")[1]
    reNameItem = item.replace(":%s" % itemAssetName, ":output_SET")

    deleteUsrAttr(reNameItem)

    if not cmds.ls('%s.modelAtom' % reNameItem):
        cmds.addAttr('%s' % reNameItem, ln="modelAtom", dt="string")

    cmds.setAttr('%s.modelAtom' % reNameItem, "%s,%s" % (item, filename), type="string")
    return '%s.modelAtom' % reNameItem


def initRenderAtomImportWrite(item, filename):
    itemAssetName = item.split(":")[1]
    reNameItem = item.replace(":%s" % itemAssetName, ":output_SET")

    deleteUsrAttr(reNameItem)

    if not cmds.ls('%s.atomRender' % reNameItem):
        cmds.addAttr('%s' % reNameItem, ln="atomRender", dt="string")

    cmds.setAttr('%s.atomRender' % reNameItem, "%s,%s" % (item, filename), type="string")
    return '%s.atomRender' % reNameItem


def deleteUsrAttr(reNameItem):
    if cmds.ls('%s.geoCache' % reNameItem):
        cmds.deleteAttr("%s.geoCache" % reNameItem)

    if cmds.ls('%s.mmGeoCache' % reNameItem):
        cmds.deleteAttr("%s.mmGeeoCache" % reNameItem)