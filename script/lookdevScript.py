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
#

# # Export  ----------------------------------------------------------------------------------------
def itemRootAssetNameCheck(itemdir): #export 2
    itemName = itemdir.split("/")[5]
    if not cmds.ls(itemName):
        print("( lookdev 60 line ) Erro : Not match Asset Name !!  ")
        return
    cmds.select(itemName)
    if "_PROXY" in itemdir:
        cmds.select( "output_SET", ne=1, add=1)
    return itemName

def lookdevExport( fileName, itemdir,itemName):   # exort 5
    fileinfo = {}
    fileinfo [ itemName ] = "%s%s.mb" %(itemdir, fileName)
    print(">>>>>", fileinfo)
    cmds.file(save=1)
    os.system("cp -f %s %s%s.mb" %(cmds.file(q=1, sn=1), itemdir,fileName))
    print(">>", itemdir,fileName)

    return fileinfo

# #--------------------------------------------------------------------------------------------------------------------
def lookdevImport(itemInfo, type, rootType, num=1):
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

        #     for i in range(num):
        #
        #         print "okok"
        #         if isNameSpace: #seq
        #             print "okok AA"
        #             namespace = "%s%d" %(assetName, i+1)
        #             itemName = "%s:%s" %(namespace, assetName)
        #         else: # assets
        #             print "nono BB"
        #             itemName = assetName
        itemName = assetName

        if "import" in type or "None" in type:
            writeItemName = lookdevImportFile(itemName, list(itemInfo.values())[0], rootType, workType)
        #             a.keys()[0], a.values()[0]
        elif "reference" in type:
            writeItemName = lookdevReferenceFile(itemName, list(itemInfo.values())[0], rootType, workType)
        itemNames.append(writeItemName)
    return itemNames


def lookdevImportFile(itemName, itemDir, rootType, workType):
    #     print ">>>>", itemName
    if cmds.ls(itemName):  # obj in ...
        return
    #     print ">>", itemName, itemDir,rootType, workType
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

    writeItemName = initLookdevImportWrite(itemName, itemDir, rootType, workType)
    return writeItemName

#     subAssetInfoExport(  {itemName : itemDir}, "import" )

def lookdevReferenceFile(itemName, itemDir, rootType, workType):
    #     itemName = "%s:output_SET" %item

    namespaceName = itemName.split(":")[0]
    if cmds.objExists(itemName):  # replace
        #         print "AAA"
        if cmds.namespace(exists='%s' % namespaceName) == False:

            cmds.file("%s" % itemDir,
                      loadReference="%s" % itemName.split(":")[0],
                      shd=["displayLayers", "shadingNetworks", "renderLayersByName"],
                      type="mayaBinary", options="v=0;")
            writeItemName = initLookdevImportWrite(itemName, itemDir, rootType)
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

    #     file -r -type "mayaBinary"  -ignoreVersion -gl -mergeNamespacesOnClash true -namespace ":" -options "v=0;" "/show/DH/assets/prop/Box/rig/wip/scenes/Box_rig_v01_w03.mb";
    if cmds.ls("vraySettings"):
        cmds.setAttr("vraySettings.relements_usereferenced", 1)
    writeItemName = initLookdevImportWrite(itemName, itemDir, rootType, workType)
    return writeItemName


#     subAssetInfoExport(  {itemName : itemDir}, "import" )

def initLookdevImportWrite(item, filename, rootType, workType):
    reNameItem = item
    if "lookdev" == rootType:
        if not cmds.ls('%s.lookdev' % reNameItem):
            cmds.addAttr('%s' % reNameItem, ln="lookdev", dt="string")

        #         assetName = re.search("[\D]+([\w]+)?[\D]+(?=([\d]+)?:)", item).group()
        #         assetName =  item.split("/")[1]
        cmds.setAttr('%s.lookdev' % reNameItem, "%s,%s" % (item, filename), type="string")
        return '%s.lookdev' % reNameItem
