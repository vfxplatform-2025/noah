# -*- coding:utf-8 -*-
'''
Created on Jun 8, 2015

@author: m83
'''
import maya.cmds as cmds
import maya.mel as mel
from . import utilScript


def dummyExport(fileName, itemdir, itemName):  # exort 5

    #pluginCheck()
    utilScript.pluginChecks("dummy")

    fileinfo = {}

    cmds.refresh(su=1)
    startF = cmds.playbackOptions(min=1, q=1)
    endF = cmds.playbackOptions(max=1, q=1)

    if "/pub/" in itemdir:
        fileinfo[itemName] = itemdir
    else:
        fileinfo[itemName] = "%s/%s.mb" % (itemdir, itemName)

        cmds.file("%s/%s.mb" % (itemdir, itemName), force=1, options="v=0;", typ="mayaBinary", pr=1, es=1)

        # alembic
        mel.eval(
            'AbcExport -j "-frameRange %d %d -uvWrite -writeUVSets -eulerFilter -worldSpace -dataFormat ogawa -root %s -file %s/%s.abc" ' \
            % ((startF), (endF), cmds.ls(sl=1)[0], itemdir, fileName))
    cmds.refresh(su=0)
    return fileinfo


def dummyImport(itemInfo, type, rootType):
    mentalNode = cmds.ls(['mentalrayGlobals', 'mentalrayItemsList'])

    if mentalNode:
        cmds.delete(mentalNode)

    for i in itemInfo:
        #         name = "%s1:output_SET" %i
        if "import" in type or "None" in type:
            writeItemName = dummyImportFile(i, itemInfo[i], rootType)


        elif "reference" in type:
            writeItemName = dummyReferenceFile(i, itemInfo[i], rootType)
    return writeItemName


def dummyImportFile(itemName, itemDir, rootType):
    # check oBject
    if ":" in itemName:
        name = itemName.split(":")[1]
    else:
        name = itemName

    if cmds.ls(name):
        cmds.confirmDialog(title='Message', message=" Delete \"%s \"!!   Please! File Check!" % name, button=['ok'])
        return

    cmds.file("%s" % itemDir, i=True, type="mayaBinary", ignoreVersion=True, \
              mergeNamespacesOnClash=1, options="v=0", pr=True, loadReferenceDepth="all", returnNewNodes=1)

    writeItemName = setWirteItme(rootType, name, itemDir)
    return writeItemName


def dummyReferenceFile(itemName, itemDir, rootType):
    if cmds.ls(itemName):
        cmds.file("%s" % itemDir,
                  loadReference="%s" % itemName,
                  type="mayaBinary", options="v=0;")

        setWirteItme(rootType, itemName, itemDir)
        return

    cmds.file("%s" % itemDir,
              r=1, gl=1, type="mayaBinary", ignoreVersion=1,
              namespace=":",
              mergeNamespacesOnClash=True, options="v=0;")

    writeItemName = setWirteItme(rootType, itemName, itemDir)
    return writeItemName


def setWirteItme(rootType, itemName, itemDir):
    if "dummy" == rootType:
        writeItemName = initItemImportWrite(itemName, itemDir)
    elif "mmDummy" == rootType:
        writeItemName = initMmDummyItemImportWrite(itemName, itemDir)
    elif "layoutDummy" == rootType:
        writeItemName = initLayoutDummyItemImportWrite(itemName, itemDir)
    elif "modelDummy" == rootType:
        writeItemName = initModelDummyItemImportWrite(itemName, itemDir)

    return writeItemName


# write
def initItemImportWrite(itemName, itemDir):
    dummyObj = cmds.ls('%s' % itemName, r=1)[0]
    if not cmds.ls('%s.dummy' % dummyObj):
        cmds.addAttr('%s' % dummyObj, ln="dummy", dt="string")

    cmds.setAttr('%s.dummy' % dummyObj, "%s,%s" % (itemName, itemDir), type="string")
    return '%s.dummy' % dummyObj


def initMmDummyItemImportWrite(itemName, itemDir):
    dummyObj = cmds.ls('%s' % itemName, r=1)[0]
    if not cmds.ls('%s.mmDummy' % dummyObj):
        cmds.addAttr('%s' % dummyObj, ln="mmDummy", dt="string")

    cmds.setAttr('%s.mmDummy' % dummyObj, "%s,%s" % (itemName, itemDir), type="string")
    return '%s.mmDummy' % dummyObj


def initLayoutDummyItemImportWrite(itemName, itemDir):
    dummyObj = cmds.ls('%s' % itemName, r=1)[0]
    if not cmds.ls('%s.layoutDummy' % dummyObj):
        cmds.addAttr('%s' % dummyObj, ln="layoutDummy", dt="string")

    cmds.setAttr('%s.layoutDummy' % dummyObj, "%s,%s" % (itemName, itemDir), type="string")
    return '%s.layoutDummy' % dummyObj


def initModelDummyItemImportWrite(itemName, itemDir):
    dummyObj = cmds.ls('%s' % itemName, r=1)[0]
    if not cmds.ls('%s.modelDummy' % dummyObj):
        cmds.addAttr('%s' % dummyObj, ln="modelDummy", dt="string")

    cmds.setAttr('%s.modelDummy' % dummyObj, "%s,%s" % (itemName, itemDir), type="string")
    return '%s.modelDummy' % dummyObj