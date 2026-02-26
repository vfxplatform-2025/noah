# -*- coding:utf-8 -*-

import maya.cmds as cmds
import json, re
from . import takeScript
import imp
imp.reload(takeScript)
from . import utilScript
imp.reload(utilScript)

def instanceSetLoad(exportSeqToAsset):
    cmds.select(cl=True)

    instanceList = cmds.ls("instance_SET")
    if not instanceList:
        instanceList = cmds.ls("*:instance_SET")

    instanceDic = {}
    for i in instanceList:

        instanceSetChild = cmds.sets(i, q=True)
        print(instanceSetChild)

        for x in instanceSetChild:
            if "point_" in x:
                instanceDic[x]={"type":"point"}

            #if not exportSeqToAsset:
            #    if "mb_" in x:
            #        instanceDic[x] = {"type": "mb"}

    if instanceDic:
        cmds.select(cl=True)

    return instanceDic

def instanceImport(objList , type, rootType, itemNum=1, takeName="", sqcV="", shotV=""):
    print(objList , type, rootType, itemNum)

    itemExists = []
    workType = cmds.file(q=1, sn=1) and cmds.file(q=1, sn=1).split("/show/")[1].split("/")[1]

    for itemName, itemDir in list(objList.items()):
        if type == "reference":
            namespaceName = itemName.split(":")[0]
            if cmds.objExists(itemName):  # replace
                #         print "AAA"
                if cmds.namespace(exists='%s' % namespaceName) == False:

                    cmds.file("%s" % itemDir,
                              loadReference="%s" % itemName.split(":")[0],
                              shd=["displayLayers", "shadingNetworks", "renderLayersByName"],
                              type="mayaBinary", options="v=0;")
                    instanceImportInfo(itemName, itemDir, rootType, takeName, sqcV, shotV, namespaceName=namespaceName)

                    writeItemName = initRigImportWrite(itemName, itemDir, rootType, workType)
                    return writeItemName
                else:
                    dirNode = cmds.referenceQuery(itemName, filename=1)
                    fileDir = re.search("/[\w].+.mb", dirNode).group()
                    instanceImportInfo(itemName, itemDir, rootType, takeName, sqcV, shotV, namespaceName=namespaceName, refCheck=fileDir)
                    print("Check! nameSpace !!( %s )" % itemName)
                    return

            if workType == "assets" or ":" not in itemName:
                '''
                cmds.file("%s" % itemDir, returnNewNodes=1,
                          namespace=":",
                          r=1, gl=1, type="mayaBinary", ignoreVersion=1,
                          shd=["displayLayers", "shadingNetworks", "renderLayersByName"],
                          mergeNamespacesOnClash=True, options="v=0;")
                '''
                instanceImportInfo(itemName, itemDir, rootType, takeName, sqcV, shotV)

            else:
                cmds.file("%s" % itemDir, returnNewNodes=1,
                          namespace="%s" % itemName.split(":")[0],
                          r=1, gl=1, type="mayaBinary", ignoreVersion=1,
                          shd=["displayLayers", "shadingNetworks", "renderLayersByName"],
                          mergeNamespacesOnClash=True, options="v=0;")
                instanceImportInfo(itemName, itemDir, rootType, takeName, sqcV, shotV, namespaceName=namespaceName)

        #if type == "import":
        #    cmds.file("%s" % itemDir, i=True, type="mayaBinary", ignoreVersion=True, \
        #              mergeNamespacesOnClash=0, options="v=0", pr=True, loadReferenceDepth="all", returnNewNodes=1)

        writeItemName = initInstanceImportWrite(itemName, itemDir, rootType, workType)
        itemExists.append(writeItemName)

    return itemExists

def instanceImportInfo(itemName, itemDir, rootType, takeName, sqcV, shotV, namespaceName="", refCheck=""):
    if 'instance' in rootType: # seq, instanceAni
        takeFile = "/show/{}/seq/{}/{}/Take/{}.json".format(itemDir.split("/show/")[1].split("/")[0], sqcV, shotV, takeName)
    else: # assets, digienv
        takeFile = "{}Take/{}.json".format(itemDir.split(rootType)[0], takeName)

    with open(takeFile, 'r' ) as f:
        jsonData = json.load(f)

    objectPath = jsonData[rootType]["objectList"][itemName]
    if refCheck:
        if refCheck != objectPath:
            refNode = cmds.referenceQuery(itemName, rfn=1)
            cmds.file(objectPath, loadReference=refNode, type="mayaBinary", options="v=0")

    instanceInfo  = jsonData[rootType]["instance"][itemName]
    for instanceName, infos in list(instanceInfo.items()):
        if namespaceName:
            instanceName2 = "|".join(instanceName.split("|")[:-1]).replace("|", "|{}:".format(namespaceName))
        else:
            instanceName2 = "|".join(instanceName.split("|")[:-1])
        try:
            cmds.setAttr("{}.translateX".format(instanceName2), infos["translate"]["x"])
            cmds.setAttr("{}.translateY".format(instanceName2), infos["translate"]["y"])
            cmds.setAttr("{}.translateZ".format(instanceName2), infos["translate"]["z"])

            cmds.setAttr("{}.rotateX".format(instanceName2), infos["rotate"]["x"])
            cmds.setAttr("{}.rotateY".format(instanceName2), infos["rotate"]["y"])
            cmds.setAttr("{}.rotateZ".format(instanceName2), infos["rotate"]["z"])

            cmds.setAttr("{}.scaleX".format(instanceName2), infos["scale"]["x"])
            cmds.setAttr("{}.scaleY".format(instanceName2), infos["scale"]["y"])
            cmds.setAttr("{}.scaleZ".format(instanceName2), infos["scale"]["z"])

            cmds.setAttr("{}.visibility".format(instanceName2), infos["visibility"])
        except:
            print("Error :{}".format(instanceName2))

    print("instanceImportInfo Loaded: {}, {}".format(namespaceName, takeFile))

def initInstanceImportWrite(item, filename, rootType, workType):
    if workType == "assets" or ":" not in item:
        itemAssetName = item
        reNameItem = item.replace("%s" % itemAssetName, "instance_SET")
    else:
        itemAssetName = item.split(":")[1]
        reNameItem = item.replace(":%s" % itemAssetName, ":instance_SET")

    cmds.lockNode(reNameItem, l=False)

    if not cmds.ls('%s.%s' % (reNameItem, rootType)):
        cmds.addAttr('%s' % reNameItem, ln=rootType, dt="string")

    cmds.setAttr('%s.%s' % (reNameItem, rootType), "%s,%s" % (item, filename), type="string")
    return '%s.%s' % (reNameItem, rootType)


def instanceExport(fileName, itemdir, itemName="", itemList=[], exportSeqToAsset=0, fileTypeV=""):

    fileinfo = {}
    pointInfo = {}
    fileDirV = ""

    cmds.file(save=True)
    pubfilePath = "%s/%s.mb" % (itemdir, fileName)

    curFileName = cmds.file(q=1, sn=1)
    workType = ""
    namespace = ""
    if curFileName:
        workType = curFileName.split("/show/")[1].split("/")[1]

    if workType == "assets" or itemList==[]: # asset
        objName = cmds.ls(sl=1)
        fileinfo['%s:instance_SET' % itemName] = pubfilePath

    else: #seq
        namespace = itemList[0].split(":")[0]
        itemList.append("%s:instance_SET"%namespace)
        objName = itemList

        dirNode = cmds.referenceQuery(objName[0], filename =1)
        fileDir = re.search("/[\w].+.mb",dirNode ).group()

        fileinfo['%s:instance_SET' % namespace] = fileDir
        if exportSeqToAsset:
            fileDirV = fileDir
            fileTypeV = fileDir.split("/show/")[1].split("/")[4]
        else:
            fileDirV = curFileName
            fileTypeV = 'instance'
        #else:
        #fileinfo['%s:instance_SET' % namespace] = pubfilePath

    cmds.progressWindow(title='Pub.....', progress=0, status='Ing', ii=True)

    for i in objName:
        if 'mb_SET' in i:
            if workType == "assets":
                grpList = cmds.sets(i, q=True)

                cmds.select(objName, ne=True,r=True)
                cmds.select(grpList, add=True)

                cmds.file(pubfilePath, force=1, options="v=0;", typ="mayaBinary", pr=1, es=1)

        if 'point_SET' in i:
            grpList = cmds.sets(i, q=True)
            for grpName in grpList:
                shapeList = cmds.ls(grpName, dag=True, ap=True, s=True, l=True)
                for shapeName in shapeList:
                    transformNode = "|".join(shapeName.split("|")[:-1])

                    tvalue = cmds.xform(transformNode, t=True, q=True, ws=True)
                    rvalue = cmds.xform(transformNode, ro=True, q=True, ws=True)
                    svalue = cmds.xform(transformNode, s=True, q=True, ws=True)
                    vizvalue = cmds.getAttr("%s.visibility"%transformNode)

                    if ":" in shapeName:
                        shapeName = shapeName.replace("|{}:".format(namespace), "|")

                    pointInfo[shapeName] = {
                        "translate":{"x":tvalue[0], "y":tvalue[1], "z":tvalue[2]},
                        "rotate":{"x":rvalue[0], "y":rvalue[1], "z":rvalue[2]},
                        "scale": {"x":svalue[0], "y":svalue[1], "z":svalue[2]},
                        "visibility": vizvalue
                    }

        cmds.select(cl=True)

    cmds.progressWindow(e=True, progress=100, status='Done')
    cmds.pause(seconds=1)
    cmds.progressWindow(endProgress=1)

    return fileinfo, pointInfo, fileDirV, fileTypeV
