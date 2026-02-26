# -*- coding:utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel
import glob
import re, os
from . import utilScript
import imp
imp.reload(utilScript)

def assExport(fileList , itemdir,  item, num, step_num, frameType="FrameRange"):
    utilScript.pluginChecks("mtoa")
    # frame info
    startF = 0.0
    endF = 0.0
    if frameType == "FrameRange":
        startF = cmds.playbackOptions(min=1, q=1)
        startF = startF - num
        endF = cmds.playbackOptions(max=1, q=1)
        endF = endF + num
    if frameType == "CurrentFrame":
        startF = cmds.currentTime(q=1)
        endF = cmds.currentTime(q=1)

    fileinfo = {}
    cmds.refresh(su=1)
    # print ">>>", fileList, itemdir, item, num

    if ":" in item:
        assetName = re.search("[\w]*[\D](?=([\d]+)?:)", item).group()

        if "out_cur_Grp" in item:
            itemName = item.split(":")[0]  # org
            assetName = item.split(":")[1]  # org

        else:
            itemName = item.split(":")[0]  # asset name
        fileName = item.replace(":", "_")
        itemNewDir = "%s/%s" % (itemdir, itemName)
        fileinfo["%s:%s" % (itemName, assetName)] = "%s/%s.ass" % (itemNewDir, fileName)

    else:
        assetName = item
        itemName = item
        fileName = item
        itemNewDir = "%s/%s" % (itemdir, itemName)
        fileinfo["%s" % itemName] = "%s/%s.ass" % (itemNewDir, fileName)

    if os.path.isfile("%s/%s.ass" % (itemNewDir, fileName)):
        #         print "delete %s" %itemNewDir
        print("delete %s/%s.ass" % (itemNewDir, fileName))
        os.system("rm -rf %s/%s.ass" % (itemNewDir, fileName))

    if not os.path.isdir(itemNewDir):
        os.mkdir(itemNewDir)

    exportCmd = 'arnoldExportAss -startFrame %s -endFrame %s -frameStep %s -f "%s/%s.ass" -s -shadowLinks 1  -mask 2303 -lightLinks 1  -boundingBox -cam perspShape;' \
                % (startF, endF, step_num, itemNewDir, fileName)
    print(exportCmd)
    mel.eval(exportCmd)

    cmds.select(cl=1)
    cmds.refresh(su=0)
    return fileinfo


def assImport (itemInfo, type, rootType, itemNum=None):

    importType = type
    for i in itemInfo:
        writeItemName = assImportFile( i, itemInfo[i], rootType, importType)

    return writeItemName

def assImportFile(itemName, itemDir, rootType, importType):
    utilScript.pluginChecks("mtoa")


    print(itemName, itemDir, rootType)
    itemDirList =  itemDir.split("/")
    itemDirRoot = "/".join(itemDirList[:-1])
    itemFileName = itemDirList[-1].split(".")[0]+".*"

    itemExistsCheck = glob.glob(itemDirRoot+"/"+itemFileName)
    #if not os.path.isfile(itemDirRoot+"/"+itemFileName):
    if not itemExistsCheck:
        print("Not File !!")
        return

    import mtoa.ui.arnoldmenu
    # create arnold node
    #create node
    aiNodeName = mtoa.ui.arnoldmenu.createStandIn()
    aiTransName = mel.eval('listRelatives -p "%s"'%aiNodeName)[0]
    #aiTransName = cmds.listRelatives(aiNodeName, p=1)[0] # error in 2017
    aiRename = cmds.rename(aiTransName, "%s_ass" % itemName)

    # path rename
    itemPathList = itemDir.split(".")
    itemPathDir = ".".join(itemPathList[:-1])
    itemPathExt = itemPathList[-1]
    newitemPath = itemPathDir+".####."+itemPathExt

    # set name and frame expresstion
    cmds.setAttr("%s.dso" % aiRename, newitemPath, type="string")
    cmds.setAttr("%s.useFrameExtension" % aiRename, 1)

    item = itemName+"_ass"
    writeItemName = importInfoWrite(item,  itemDir, rootType)

    return writeItemName


def importInfoWrite(item, filename, itemType):
    if cmds.ls('%s.%s' % (item, itemType)):
        cmds.deleteAttr("%s.%s" % (item, itemType))

    if cmds.ls(item) and not cmds.ls('%s.%s' % (item, itemType)):
        cmds.addAttr('%s' % item, ln="%s" % itemType, dt="string")

    if cmds.ls(item):
        cmds.setAttr('%s.%s' % (item, itemType), "%s,%s" % (item, filename), type="string")  # item !!

    return '%s.%s' % (item, itemType)