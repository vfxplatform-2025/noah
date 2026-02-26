'''
Created on Jun 8, 2015
 
@author: m83
'''
  
import os, glob, re
import maya.cmds as cmds
import maya.mel as mel
from subprocess import *
import socket
import datetime

from . import takeScript
import imp
imp.reload(takeScript)
from . import utilScript
imp.reload(utilScript)
import configparser

from . import assScript
imp.reload(assScript)

def itemExport( fileList , itemdir,  item, num, step_num, frameType="FrameRange", fileType="ass"):

    utilScript.pluginChecks(fileType)

    # frame info
    startF = 0.0
    endF = 0.0
    if frameType == "FrameRange":
        startF = cmds.playbackOptions(min=1, q=1)
        startF = startF-num
        endF = cmds.playbackOptions(max=1, q=1)
        endF = endF+num
    if frameType == "CurrentFrame":
        startF = cmds.currentTime(q=1)
        endF = cmds.currentTime(q=1)

    fileinfo ={}
    cmds.refresh(su=1)
    # print ">>>", fileList, itemdir, item, num

    if ":" in item:
        assetName = re.search("[\w]*[\D](?=([\d]+)?:)", item).group()

        if "out_cur_Grp" in item:
            itemName = item.split(":")[0]  # org
            assetName = item.split(":")[1]  # org

        else:
            itemName = item.split(":")[0] # asset name
        fileName = item.replace(":", "_")
        itemNewDir = "%s/%s" % (itemdir, itemName )
        fileinfo[ "%s:%s" %(itemName,assetName) ] = "%s/%s.%s" %(itemNewDir,  fileName, fileType)

    else:
        assetName = item
        itemName = item
        fileName = item
        itemNewDir = "%s/%s" % (itemdir, itemName )
        fileinfo[ "%s" %itemName ] = "%s/%s.%s" %(itemNewDir, fileName, fileType)

    if os.path.isfile( "%s/%s.%s" %(itemNewDir, fileName, fileType) ):
#         print "delete %s" %itemNewDir
        print("delete %s/%s.%s" %(itemNewDir, fileName, filetype))
        os.system("rm -rf %s/%s.%s" %(itemNewDir, fileName, fileType) )

    if not os.path.isdir( itemNewDir ):
        os.mkdir( itemNewDir )

    if fileType == "ass":
        exportCmd = assScript.assExport(startF, endF, step_num, itemNewDir, fileName)
        mel.eval(exportCmd)

    if fileType == "abc":
        exportCmd = 'AbcExport -j "-frameRange %d %d -uvWrite -writeUVSets -eulerFilter -writeVisibility -step %s -worldSpace -dataFormat ogawa -root %s -file %s/%s.abc" ' \
              %( startF, endF, step_num, cmds.ls(item, l=1)[0], itemNewDir,fileName)
        print(exportCmd)
        mel.eval(exportCmd)

    cmds.select(cl=1)
    cmds.refresh(su=0)
    return fileinfo

def infoExport( objList, spoolType="local", frameType="FrameRange", fileType="ass" ): #, itemType

    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = utilScript.getFileList()
    globalCurrentTake,  globalNewTake, globalNewNum   = takeScript.versionUpTakeName(globalTakeDir, "take")
    localCurrentTake, localNewTake, localNewNum = takeScript.versionUpTakeName(localTakeDir, "%s" % fileName)

    typeConfig = configparser.ConfigParser()
    typeConfigFile = os.path.abspath(__file__ + "/../../config/typeConfig.ini")
    typeConfig.read(typeConfigFile)

    itemType = typeConfig.get(fileType, partType)
    take, local_take = takeScript.checkTake(itemType)

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
        startF = 0.0
        endF = 0.0
        if frameType == "FrameRange" :
            startF = cmds.playbackOptions(min=1, q=1)
            endF   = cmds.playbackOptions(max=1, q=1)
        if frameType == "CurrentFrame" :
            startF = cmds.currentTime(q=1)
            endF   = cmds.currentTime(q=1)
        frameDict.update({ item : "%d-%d" %(startF, endF)})
                
        # date info
        nowdate = str(datetime.datetime.now())
        date = nowdate.rsplit(":",1)[0]
        dateDict.update({ item :  date})
                
        #object List info
        objectListDict.update({ item :  objList[item] })

        #object check info
        checkList = {"model":1, "rig" : 1,"ani":1, "matchmove":1, "layout":1, "dyn":1, "cloth":1,"hair":1,"hairSim":1, "clothSim":1, "lit" : 1, "furSim":1, "fur":1, "lookdev" : 1 ,"fx" : 1 }
        objectCheckDict.update({ item :  checkList})

        #update List info
        updateListDict.update({ item :  objList[item]})
                                                                                                                                                    
    if take[ itemType ].get('objectList'):  # is itemType
        if take[ itemType ]['objectList'].get(item):  # is item
            newTake =  takeScript.takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict, frameDict, dateDict, objList, objectCheckDict)
        else:
            newTake = takeScript.takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict, frameDict, dateDict, objList, objectCheckDict)
    else:
        newTake = takeScript.takeSetInfo(take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict, frameDict, dateDict, objList, objectCheckDict)
        
    if local_take[ itemType ].get('objectList'):  # is itemType
        if local_take[ itemType ]['objectList'].get(item):  # is item
            local_Newtake = takeScript.takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict, frameDict, dateDict, objList, objectCheckDict)
        else:
            local_Newtake = takeScript.takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict, frameDict, dateDict, objList, objectCheckDict)
    else:
        local_Newtake = takeScript.takeSetInfo(local_take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict, frameDict, dateDict, objList, objectCheckDict)
        #--------------------------------------------------------
            
    take = newTake      
    local_take = local_Newtake
    
    take[ itemType ]["updateList"]= updateListDict 
    local_take[ itemType ]["updateList"]= updateListDict

    if spoolType == "local":
        takeScript.saveTake(itemType, take, local_take)
    if spoolType == "farm":
        takeScript.saveTakeFarm(itemType, take, local_take)

#import 
def itemImport (itemInfo, type, rootType, itemNum=None):
    for i in itemInfo:
        writeItemName = itemImportFile( i, itemInfo[i], rootType, type)

    return writeItemName

def itemImportFile(item, itemDir, rootType, type):
    itemDirList =  itemDir.split("/")
    itemDirRoot = "/".join(itemDirList[:-1])
    itemFileName = itemDirList[-1].split(".")[0]+".*" # remove padding

    itemExistsCheck = glob.glob(itemDirRoot+"/"+itemFileName)
    #if not os.path.isfile(itemDirRoot+"/"+itemFileName):
    if not itemExistsCheck:
        print("Not File !!")
        return

    print("=====================================")
    print(rootType, type)
    print("=====================================")
    if re.match("alembic", rootType):
        if type == "alembic":
            utilScript.nameSpaceCheck(item)
            if ":" in item:
                returnList = cmds.file("%s" %itemDir , namespace = "%s" %item.split(":")[0], i=1, pr =1, ra=True,  mergeNamespacesOnClash =True, type ="Alembic", rnn=1)
                # print ">" * 10, returnList
            else:
                returnList = cmds.file("%s" %itemDir, i =True , type ="Alembic" ,  ignoreVersion=True, mergeNamespacesOnClash= 1, options="v=0", pr= True, loadReferenceDepth="all" ,returnNewNodes=1)
                # print ">" * 10, returnList

            topGroup= [x for x in returnList if x.count("|") == 1]
            tranName = topGroup[0].split("|")[1]

            # rename
            print(tranName)
            if ("_geo_Grp" not in tranName) and ("_geo_grp" not in tranName)  and not cmds.listRelatives(tranName,p=1, type="mesh"): # if group rename and
                tranName = cmds.rename ( tranName ,item )

            elif "_geo_Grp" in tranName or "_geo_grp" in tranName:
                cmds.group(":%s" %tranName, n=item)

        elif type == "gpu":
            gpuNodeName = cmds.createNode("gpuCache", n="%s_gpuCache"%item)
            gpuTransName = cmds.listRelatives(gpuNodeName, p=1)[0]
            cmds.rename(gpuTransName, "%s_gpu"%item)
            cmds.setAttr("%s.cacheFileName"%gpuNodeName, itemDir, type="string")

        elif type == "import":
            if cmds.ls("%s:abcCache_SET" %item):
                item_cacheSetGrp_name = "%s:%s" % (item, item)
                cmds.select(item_cacheSetGrp_name )
                cmds.AbcImport("%s" % itemDir, reparent = "%s" %item_cacheSetGrp_name, mode='import')
            else:
                cmds.AbcImport("%s" % itemDir, mode='import', debug=1, connect="/")

        elif type == "proxy":
            utilScript.nameSpaceCheck(item)
            utilScript.pluginCheck()
            mel.eval('vrayCreateProxy -node "%s"  -dir "%s" -existing -createProxyNode ' % (item, itemDir))
            shapename = "".join(cmds.ls(sl=1))
            tranName = "".join(cmds.listRelatives(shapename, p=1))

            cmds.rename("%s" % tranName, "vrayFroxyFileTMP")
            cmds.rename("%s_vraymesh" % tranName, "vrayFroxyFileTMP_vraymesh")
            cmds.rename("%s_vraymeshmtl" % tranName, "vrayFroxyFileTMP_vraymeshmtl")

            tranName = "vrayFroxyFileTMP"

            cmds.setAttr("%s_vraymesh.animType" % tranName, 1)
            cmds.setAttr("%s_vraymesh.useAlembicOffset" % tranName, 1)

            # is namespace
            if ":" in item:
                cmds.rename("%s" % tranName, ":%s" % item)
                cmds.rename("%s_vraymesh" % tranName, ":%s_vraymesh" % item)
                cmds.rename("%s_vraymeshmtl" % tranName, ":%s_vraymeshmtl" % item)
            else:
                cmds.rename("%s" % tranName, "%s" % item)
                cmds.rename("%s_vraymesh" % tranName, "%s_vraymesh" % item)
                cmds.rename("%s_vraymeshmtl" % tranName, "%s_vraymeshmtl" % item)

    elif re.match("ass", rootType):
        if type == "import":
            item = assScript.assImport(item, itemDir, rootType)

    elif re.match("dummy", rootType.lower()):
        if type == "import":
            item = mayaScript.mayaImport(item, itemDir,rootType)
        if type == "reference":
            item = mayaScript.mayaReference(item, itemDir,rootType)
    else:
        print("Error : Check Type")

    # import info write
    print(rootType, type)
    writeItemName = importInfoWrite(item,  itemDir, rootType)
    print(writeItemName)

    cmds.select(cl=1)

    return writeItemName 

# write
def importInfoWrite( item , filename, itemType):

    if cmds.ls('%s.%s' %(item, itemType) ):
        cmds.deleteAttr("%s.%s" %(item, itemType) )

    if cmds.ls(item) and not cmds.ls('%s.%s' %(item, itemType)):
        cmds.addAttr ('%s' %item, ln="%s" %itemType,  dt="string" )

    if cmds.ls(item):
        cmds.setAttr('%s.%s' %(item, itemType), "%s,%s" %(item, filename), type="string")   # item !!
    
    return '%s.%s' %(item, itemType)

# Load
def alembicAllLoadSet(lodType=None):
    if lodType != "None":
        cmds.ls("*:abcCache_%s_SET" % lodType) and cmds.select("*:abcCache_%s_SET" %lodType)

    else:
        cmds.ls("*:abcCache_SET") and cmds.select("*:abcCache_SET")

    allAbcSet = cmds.ls(sl=1)

    if allAbcSet:
        cmds.select(cl=True)

    return list(set(allAbcSet))

def alembicCurveLoadSet():
    if cmds.ls("*:abcHairCache_SET"):
        cmds.select("*:abcHairCache_SET")
        allAbcSet = cmds.ls(sl=1)
        print(">>>", allAbcSet)
        if allAbcSet:
            cmds.select(cl=True)

        return list(set(allAbcSet))

def alembicLoadMesh():
    return cmds.ls(sl=1)
