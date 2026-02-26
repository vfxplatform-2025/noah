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


# # Export  ----------------------------------------------------------------------------------------
def itemRootAssetNameCheck(itemdir):  # export 2
    itemName = itemdir.split("/")[5]
    if not cmds.ls(itemName):
        print("( lightRigScript 59 line ) Erro : Not match Asset Name !!  ")
        return
    cmds.select(itemName)
    return itemName


def litRigExport(fileName, itemdir, itemName):  # exort 5
    #    CF_156_ani_v01_w47_text
    #    /show/AS/seq/CF/CF_156/ani/wip/data/geoCache/CF_156_ani_v01_w47_text
    #    OkYunA3:geoCache_SET
    #    10

    #     pluginCheck()
    fileinfo = {}


    fileinfo[itemName] = "%s/%s.mb" % (itemdir, fileName)

    cmds.file(save=1)
    os.system("cp -f %s %s%s.mb" % (cmds.file(q=1, sn=1), itemdir, fileName))
    print(">>", itemdir, fileName, fileinfo)

    return fileinfo



def litRigImport(itemInfo, type, rootType, num=1):
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

        itemName = assetName

        if "import" in type or "None" in type:
            writeItemName = litRigImportFile(itemName, list(itemInfo.values())[0], rootType, workType)
        # a.keys()[0], a.values()[0]
        elif "reference" in type:
            writeItemName = litRigImportFile(itemName, list(itemInfo.values())[0], rootType, workType)
        itemNames.append(writeItemName)
    return itemNames


def litRigImportFile(itemName, itemDir, rootType, workType):
    #     print ">>>>", itemName
    if cmds.ls(itemName):  # obj in ...
        if ":" in itemName and cmds.namespace(exists="%s" % itemName.split(':')[0]):
            cmds.namespace(rm="%s" % itemName.split(':')[0], mnr=1)
        return
    # print ">>", itemName, itemDir,rootType, workType
    if workType == "asset" or ":" not in itemName:
        #         print ">>>>>>> a ", itemName
        cmds.file("%s" % itemDir, i=True, type="mayaBinary", ignoreVersion=True, \
                  mergeNamespacesOnClash=1, options="v=0", pr=True, loadReferenceDepth="all", returnNewNodes=1)
    else:
        #         print ">>>>>>> b ", itemName
        cmds.file("%s" % itemDir,
                  namespace="%s" % itemName.split(":")[0],
                  i=1, pr=1, type="mayaBinary", ignoreVersion=1,
                  ra=True, mergeNamespacesOnClash=True, options="v=0;")

    mentalNode = cmds.ls(['mentalrayGlobals', 'mentalrayItemsList'])

    if mentalNode:
        cmds.delete(mentalNode)
    writeItemName = initLitRigImportWrite(itemName, itemDir, rootType, workType)
    return writeItemName

#     subAssetInfoExport(  {itemName : itemDir}, "import" )
def litRigReferenceFile(itemName, itemDir, rootType, workType):
    #     itemName = "%s:output_SET" %item
    namespaceName = itemName.split(":")[0]
    if cmds.objExists(itemName):  # replace
        #         print "AAA"
        if cmds.namespace(exists='%s' % namespaceName) == False:

            cmds.file("%s" % itemDir,
                      loadReference="%s" % itemName.split(":")[0],
                      shd=["displayLayers", "shadingNetworks", "renderLayersByName"],
                      type="mayaBinary", options="v=0;")
            writeItemName = initLitRigImportWrite(itemName, itemDir, rootType)
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
                  mergeNamespacesOnClash=True, options="v=0;")
    else:
        #         print "CCC"
        cmds.file("%s" % itemDir, returnNewNodes=1,
                  namespace="%s" % itemName.split(":")[0],
                  r=1, gl=1, type="mayaBinary", ignoreVersion=1,
                  shd=["displayLayers", "shadingNetworks", "renderLayersByName"],
                  mergeNamespacesOnClash=True, options="v=0;")

    if cmds.ls("vraySettings"):
        cmds.setAttr("vraySettings.relements_usereferenced", 1)
    writeItemName = initLitRigImportWrite(itemName, itemDir, rootType, workType)
    return writeItemName


def initLitRigImportWrite(item, filename, rootType, workType):
    reNameItem = item

    if "litRig" == rootType:
        if not cmds.ls('%s.litRig' % reNameItem):
            cmds.addAttr('%s' % reNameItem, ln="litRig", dt="string")

        # assetName = re.search("[\D]+([\w]+)?[\D]+(?=([\d]+)?:)", item).group()
        #         assetName =  item.split("/")[1]
        cmds.setAttr('%s.litRig' % reNameItem, "%s,%s" % (item, filename), type="string")
        return '%s.litRig' % reNameItem