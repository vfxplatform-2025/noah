'''
Created on Jun 8, 2015
 
@author: m83
'''

import maya.cmds as cmds
from . import utilScript
import imp
imp.reload(utilScript)
from . import tractorJobScript
imp.reload(tractorJobScript)
from . import takeScript
imp.reload(takeScript)

#def renderLayerExport( fileList , itemdir,  item, num, step_num, frameType="FrameRange"):
def renderLayerExport( fileList , itemdir,  itemList, num, step_num, frameType, scenePath, takeVersionUp, fileType, mayaVersion, scriptPath, exportType, keybake, handleNum):
    utilScript.pluginChecks('abc')

    # frame info
    cmds.refresh(su=1)

    fileinfo = {}
    for item in itemList:
        itemTmp = item.split(",")
        if len(itemTmp) == 1:
            continue

        startF = int(itemTmp[1].split("-")[0])
        endF = int(itemTmp[1].split("-")[1])

        renderLayerName = itemTmp[0]

        collectionItem = cmds.editRenderLayerMembers(renderLayerName, query=True)

        itemDic = {}
        for citem in collectionItem:

            extType = fileType
            fileinfotmp, itemNewDir, fileName = takeScript.takeItem(citem, itemdir, extType, renderLayerName)
            fileinfo.update(fileinfotmp)

            itemDic[citem]={
                "type":"renderlayer",
                "fileinfo":fileinfotmp,
                "exportDir":itemNewDir,
                "fileName": fileName,
                "extType": fileType,
                "renderLayerName":renderLayerName,
                "keybake" : keybake,
                "handleNum" : handleNum
            }

            #if exportType == "local":
            #    mel.eval( 'AbcExport -j "-frameRange %d %d -uvWrite -writeUVSets -eulerFilter -writeVisibility -step %s -worldSpace -dataFormat ogawa -root %s -file %s/%s.abc" ' \
            #          %( startF, endF,step_num, cmds.ls(citem, l=1)[0], itemNewDir,fileName) )

        if exportType == "farm":
            tractorJobScript.tractorExport(startF, endF, fileList, itemDic, num, step_num, frameType, scenePath, takeVersionUp, mayaVersion, "abc", scriptPath)

        #if exportType == "farm":
        #    tractorJobScript.tractorExport(startF, endF, fileList , itemNewDir,  citemList, num, step_num, frameType, scenePath, takeVersionUp, mayaVersion, fileName, "renderlayer", renderLayerName)

    cmds.select(cl=1)
    cmds.refresh(su=0)
    return fileinfo