# -*- coding:utf-8 -*-

import maya.cmds as cmds

def fxImport(itemName, itemDir,rootType):
    # check arnold plugin
    if not cmds.pluginInfo("mtoa", query=True, loaded=True):
        cmds.warning("Error: Check arnold plugin settings")
        return 0

    # create arnold volume
    for itemNameV, itemPathV in list(itemName.items()):
        #create node
        aiVolumeNodeName = cmds.createNode('aiVolume', n="%s_vdbfxCache"%itemNameV)
        aiVolumeTransName = cmds.listRelatives(aiVolumeNodeName, p=1)[0]
        aiVolumeRename = cmds.rename(aiVolumeTransName, "%s_vdbFx" % itemNameV)

        # path rename
        itemPathList = itemPathV.split(".")
        itemPathDir = ".".join(itemPathList[:-2])
        itemPathExt = itemPathList[-1]
        newitemPath = itemPathDir+".#."+itemPathExt

        # set name and frame expresstion
        cmds.setAttr("%s.filename" % aiVolumeRename, newitemPath, type="string")
        cmds.expression(aiVolumeNodeName, s="%s.frame=frame;"%aiVolumeNodeName, ae=1, uc=all)

        print(rootType, type)
        writeItemName = importInfoWrite(aiVolumeRename, itemPathV, rootType)
        print(writeItemName)

    cmds.select(cl=1)

    return 1

# write
def importInfoWrite(item, filename, itemType):
    if cmds.ls('%s.%s' % (item, itemType)):
        cmds.deleteAttr("%s.%s" % (item, itemType))

    if cmds.ls(item) and not cmds.ls('%s.%s' % (item, itemType)):
        cmds.addAttr('%s' % item, ln="%s" % itemType, dt="string")

    if cmds.ls(item):
        cmds.setAttr('%s.%s' % (item, itemType), "%s,%s" % (item, filename), type="string")  # item !!

    return '%s.%s' % (item, itemType)


