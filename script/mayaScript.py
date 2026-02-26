# -*- coding:utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel

from . import utilScript
import imp
imp.reload(utilScript)
from . import takeScript
imp.reload(takeScript)
from . import vdbScript
imp.reload(vdbScript)


def mayaExport(fileName, itemdir, itemList, fileType, mayaExt, mayaAlembic, frameType):  # exort 5

    #pluginCheck()
    utilScript.pluginChecks(fileType)

    fileinfo = {}

    cmds.refresh(su=1)
    if frameType == "FrameRange":
        startF = cmds.playbackOptions(min=1, q=1)
        endF = cmds.playbackOptions(max=1, q=1)
    if frameType == "CurrentFrame":
        startF = cmds.currentTime(q=1)
        endF = cmds.currentTime(q=1)

    for item in itemList:
        extType = mayaExt
        fileinfotmp, itemNewDir, fileName = takeScript.takeItem(item, itemdir, extType, "", "maya")
        fileinfo.update(fileinfotmp)
        print (fileinfo)

        if "/pub/" in itemNewDir:
            fileinfo[item] = itemNewDir
        else:
            #fileinfo[item] = "%s/%s.%s" % (itemNewDir, item, mayaExt)
            fileinfo[item] = "%s/%s.%s" % (itemNewDir, fileName, mayaExt)

            if mayaExt == "mb":
                mayaType = "mayaBinary"
            if mayaExt == "ma":
                mayaType = "mayaAscii"

            cmds.select(item, r=True)
            #cmds.file("%s/%s.%s" % (itemNewDir, item, mayaExt), force=1, options="v=0;", typ=mayaType, pr=1, es=1)
            cmds.file("%s/%s.%s" % (itemNewDir, fileName, mayaExt), force=1, options="v=0;", typ=mayaType, pr=1, es=1)

            # alembic
            if mayaAlembic:
                mel.eval(
                    'AbcExport -j "-frameRange %d %d -uvWrite -writeUVSets -eulerFilter -worldSpace -dataFormat ogawa -root %s -file %s/%s.abc" ' \
                    % ((startF), (endF), cmds.ls(sl=1)[0], itemNewDir, fileName))

    cmds.select(cl=1)
    cmds.refresh(su=0)
    return fileinfo


def mayaImport(itemInfo, type, rootType, projName):
    mentalNode = cmds.ls(['mentalrayGlobals', 'mentalrayItemsList'])

    if mentalNode:
        cmds.delete(mentalNode)

    for i in itemInfo:
        print (i)
        # name = "%s1:output_SET" %i
        if "import" in type or "None" in type:
            writeItemName = mayaImportFile(i, itemInfo[i], rootType)

        elif "reference" in type:
            writeItemName = mayaReferenceFile(i, itemInfo[i], rootType)

    vdbScript.cloudVDB(projName)

    return writeItemName


def mayaImportFile(itemName, itemDir, rootType):
    # check oBject
    if ":" in itemName:
        name = itemName.split(":")[1]
    else:
        name = itemName

    if cmds.ls(name):
        cmds.confirmDialog(title='Message', message=" Delete \"%s \"!!   Please! File Check!" % name, button=['ok'])
        return

    mayaExt = itemDir.split(".")[-1]
    if mayaExt == "mb":
        mayaType = "mayaBinary"
    if mayaExt == "ma":
        mayaType = "mayaAscii"

    cmds.file("%s" % itemDir, i=True, type=mayaType, ignoreVersion=True, \
              mergeNamespacesOnClash=0, options="v=0", pr=True, loadReferenceDepth="all", returnNewNodes=1)

    writeItemName = setWirteItme(rootType, name, itemDir)
    return writeItemName


def mayaReferenceFile(itemName, itemDir, rootType):
    mayaExt = itemDir.split(".")[-1]
    if mayaExt == "mb":
        mayaType = "mayaBinary"
    if mayaExt == "ma":
        mayaType = "mayaAscii"

    if cmds.ls(itemName):
        cmds.file("%s" % itemDir,
                  loadReference="%s" % itemName,
                  type=mayaType, options="v=0;")

        #setWirteItme(rootType, itemName, itemDir)
        writeItemName = initMayaItemImportWrite(itemName, itemDir, rootType)
        return

    cmds.file("%s" % itemDir,
              r=1, gl=1, type=mayaType, ignoreVersion=1,
              namespace=":",
              mergeNamespacesOnClash=True, options="v=0;")

    #writeItemName = setWirteItme(rootType, itemName, itemDir)
    writeItemName = initMayaItemImportWrite(itemName, itemDir, rootType)
    return writeItemName


def setWirteItme(rootType, itemName, itemDir):

    writeItemName = initMayaItemImportWrite(itemName, itemDir, rootType)

    return writeItemName

# write
def initMayaItemImportWrite(itemName, itemDir, rootType):
    mayaObj = cmds.ls('%s' % itemName, r=1)[0]
    if not cmds.ls('%s.%s' % (mayaObj, rootType)):
        cmds.addAttr('%s' % mayaObj, ln=rootType, dt="string")

    cmds.setAttr('%s.%s' % (mayaObj, rootType), "%s,%s" % (itemName, itemDir), type="string")
    return '%s.%s' % (mayaObj, rootType)