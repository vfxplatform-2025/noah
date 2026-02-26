'''
Created on Jun 8, 2015
 
@author: m83
'''
  
import os, glob, re
import maya.cmds as cmds
import maya.mel as mel

from . import utilScript
import imp
imp.reload(utilScript)


def geoCacheAllLoadSet(name):
    allGeoSet=[]
    if "geoCacheSetAllLoad" == name:
        if cmds.ls("*:geoCache_SET", r=1):
            cmds.select("*:geoCache_SET",r =1, ne =1)
            allGeoSet = cmds.ls(sl=1)
            # cmds.select(cl=True)
    else:
        try:
            allGeoSet =[]
            [x for x in cmds.ls(sl=1,type="objectSet") if cmds.ls( x.rsplit(":",1)[0] +  ":geoCache_SET" ) and allGeoSet.append(x .replace(":output_SET", ":geoCache_SET") )]
        except:
            print("set Select !")
            return []

    return list(set(allGeoSet))

def checkCacheNum(fileList, meshList=None):

    if not meshList:  # not simulGeoCache
        print("not simul")
        objList = [x for x in cmds.ls(sl=1, dag=1, type="mesh") if cmds.getAttr("%s.intermediateObject" % x) is False]

    else:  # simulGeoCache
        print("simul")
        objList = [x for x in cmds.ls(fileList, dag=1, type="mesh") if cmds.getAttr("%s.intermediateObject" % x) is False]

    print(">>> Select Cache num: %s" %len(objList))


def geoCacheExportSet(filename, itemdir, item):

    assetName = re.search("[\w]*[\D](?=([\d]+)?:)", item).group()
    itemName = item.split(":")[0]
    itemNewDir = "%s/%s" % (itemdir, itemName)

    if os.path.isdir(itemNewDir):
        #         print "delete %s" %itemNewDir

        os.system("rm -rf %s" % itemNewDir)
    if not os.path.isdir(itemNewDir):
        os.mkdir(itemNewDir)

    fileData = utilScript.getFileName()

    #     filename       = "%s" %geoCahceFileInfo ["name"]
    fileinfo = {}
    namespaceName = item.split(":")[0]
    fileinfo["%s:%s" % (namespaceName, assetName)] = "%s" % itemNewDir

    return fileinfo


def geoCacheExport(fileList, itemdir, num, meshList=None):
    startF = cmds.playbackOptions(min=1, q=1)
    endF = cmds.playbackOptions(max=1, q=1)

    cmds.refresh(su=1)
    if not meshList:  # not simulGeoCache
        print("not simul")
        objList = [x for x in cmds.ls(sl=1, dag=1, type="mesh") if cmds.getAttr("%s.intermediateObject" % x) is False]

    else:  # simulGeoCache
        print("simul")
        objList = [x for x in cmds.ls(fileList, dag=1, type="mesh") if cmds.getAttr("%s.intermediateObject" % x) is False]

    print(">>> OutCache Num : %s" % len(objList))
    cmds.cacheFile(dir="%s/tmp" % itemdir,
                   fm="OneFile",
                   st=(startF - num), et=(endF + num),
                   cacheFormat="mcc", doubleToFloat=1, points=objList)

    print(glob.glob("%s/tmp/*" % itemdir))
    for i in glob.glob("%s/tmp/*" % itemdir):
        print("ShapeDeformed!!!")
        if "ShapeDeformed" in i:
            os.rename(i, "%sShape%s" % (i.split("ShapeDeformed")[0], i.split("ShapeDeformed")[1]))

    for i in fileList:
        selectMcFile = "%s/tmp/%s" % (itemdir, i.replace(":", "_"))
        moveItemDir = "%s/%s" % (itemdir, i.split(":")[0])

        os.system("mv %s* %s &" % (selectMcFile, moveItemDir))

    cmds.refresh(su=0)
    cmds.select(cl=1)

#import
def geoCacheImport (itemInfo, type, rootType):
    for i in itemInfo:
#         if "geoCache" in itemType:
        writeItemName = geoCacheImportFile    ( i, itemInfo[i], rootType)

#         elif "simulGeoCache" in itemType:
#             geoCacheReferenceFile ( i, itemInfo[i] , itemType)
    return writeItemName



def geoCacheImportFile(item, itemDir, rootType):
    # OkYunA3:OkYunA
    # /show/AS/seq/CF/CF_156/ani/wip/data/geoCache/CF_156_ani_v01_w47_text/OkYunA3.mc
    # geoCache

    #     namespaceName = item.split(":")[0]
    #     outputSetName = "%s:output_SET" %namespaceName

    # NameSpace check
    if not cmds.ls(item):
        # delete namespace
        if ":" in item and cmds.namespace(exists="%s" % item.split(':')[0]):
            cmds.namespace(rm="%s" % item.split(':')[0], mnr=1)
        print(item, "not Object !!")
        return

    #     xmlDir = glob.glob("%s/.xml" %itemDir )
    mcDir = glob.glob("%s/*.mc" % itemDir)
    if not os.path.isdir(itemDir):
        cmds.select(cl=1)
        return

    # import
    for mcFile in mcDir:
        shapName = re.search("[\w]+(?=\.mc)", mcFile).group().replace("_", ":", 1)

        # Cache Delete
        if not cmds.ls(shapName):
            continue

        transfName = cmds.listRelatives(shapName, p=1)[0]
        cmds.select(transfName)

        if cmds.ls("%s.geoCache" % item, r=1) or cmds.ls("%s.simulGeoCache" % item, r=1) or \
                cmds.ls("%s.mmGeocache" % item, r=1) or cmds.ls("%s.modelGeocache" % item, r=1) or \
                cmds.ls("%s.furGeoCache" % item, r=1) or cmds.ls("%s.clothGeoCache" % item, r=1) or \
                cmds.ls("%s.furSimGeoCache" % item, r=1) or cmds.ls("%s.hairSimGeoCache" % item, r=1) or \
                cmds.ls("%s.hairGeoCache" % item, r=1) or cmds.ls("%s.clothSimGeoCache" % item, r=1) or \
                cmds.ls("%s.geoCacheRender" % item, r=1) or cmds.ls("%s.muscleGeoCache" % item, r=1):

            try:
                mel.eval("deleteCacheFile 3 { \"keep\" , \"\" , \"geometry\" }")
            except:
                print("deleteCacheFile Error!!  geoCacheScript - 622")
        #             print "deleteCacheFile"

        # delete Deformed
        # ----------------------------------------------
        if cmds.ls("%s.geoCache" % item, r=1) or cmds.ls("%s.simulGeoCache" % item, r=1) or \
                cmds.ls("%s.mmGeocache" % item, r=1) or cmds.ls("%s.modelGeocache" % item, r=1) or \
                cmds.ls("%s.furGeoCache" % item, r=1) or cmds.ls("%s.clothGeoCache" % item, r=1) or \
                cmds.ls("%s.furSimGeoCache" % item, r=1) or cmds.ls("%s.hairSimGeoCache" % item, r=1) or \
                cmds.ls("%s.hairGeoCache" % item, r=1) or cmds.ls("%s.clothSimGeoCache" % item, r=1) or \
                cmds.ls("%s.geoCacheRender" % item, r=1) or cmds.ls("%s.muscleGeoCache" % item, r=1):
            #             for x in selectObjList:
            cmds.setAttr("%s.intermediateObject" % shapName, 0)
            tranNode = cmds.listRelatives(shapName, p=1)
            shapeList = cmds.ls(tranNode, dag=1, type="shape")
            deformedList = list(
                set(shapeList) - set(["%sOrig" % shapName]) - set([shapName]))  # Orig and deformed Delete
            if deformedList:
                cmds.delete(deformedList)
                #         #-----------------------------------------------

        cmds.select(shapName)

        mel.eval("source doImportCacheArgList")
        mel.eval('importCacheFile ( "%s", "xml"  )' % mcFile)

    # info write
    if "geoCache" == rootType:
        writeItemName = initGeoCacheImportWrite(item, itemDir, "geoCache")

    elif "simulGeoCache" == rootType:
        print("simulGeocache")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "simulGeoCache")
    #         initsimulGeoCacheImportWrite( item,  itemDir, "simulGeocache")

    elif "mmGeoCache" == rootType:
        print("mmGeocache")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "mmGeoCache")
    #         initMmGeoCacheImportWrite( item,  itemDir, "mmGeocache")

    elif "modelGeoCache" == rootType:
        print("modelGeocache")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "modelGeoCache")
    #         initModelGeoCacheImportWrite( item,  itemDir, "modelGeocache")

    elif "muscleGeoCache" == rootType:
        print("muscleGeoCache")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "musleGeoCache")
    #         initModelGeoCacheImportWrite( item,  itemDir, "musleGeocache")

    elif "geoCacheRender" == rootType:
        print("geoCacheRender")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "geoCacheRender")
    #         initRenderGeoCacheImportWrite( item,  itemDir, "geoCacheRender")

    elif "furGeoCache" == rootType:
        print("furGeoCache")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "furGeoCache")
    #         initRenderGeoCacheImportWrite( item,  itemDir, "furGeoCache")

    elif "furSimGeoCache" == rootType:
        print("furSimGeoCache")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "furSimGeoCache")
    #         initRenderGeoCacheImportWrite( item,  itemDir, "furGeoCache")

    elif "clothGeoCache" == rootType:
        print("clothGeoCache")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "clothGeoCache")
    #         initRenderGeoCacheImportWrite( item,  itemDir, "clothGeoCache")

    elif "hairGeoCache" == rootType:
        print("hairGeoCache")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "hairGeoCache")
    #         initRenderGeoCacheImportWrite( item,  itemDir, "furGeoCache")

    elif "hairSimGeoCache" == rootType:
        print("hairSimGeoCache")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "hairSimGeoCache")
    #         initRenderGeoCacheImportWrite( item,  itemDir, "furGeoCache")

    elif "clothSimGeoCache" == rootType:
        print("clothSimGeoCache")
        writeItemName = initGeoCacheImportWrite(item, itemDir, "clothSimGeoCache")
    #         initRenderGeoCacheImportWrite( item,  itemDir, "clothGeoCache")

    cmds.select(cl=1)
    return writeItemName


# write
def initGeoCacheImportWrite(item, filename, itemType):
    #     itemAssetName = item.split(":")[1]
    #     reNameItem = item.replace(":%s" %itemAssetName, ":output_SET")
    #     item = item.replace("geoCache_SET", "output_SET")

    if cmds.ls('%s.%s' % (item, itemType)):
        cmds.deleteAttr("%s.%s" % (item, itemType))

    if not cmds.ls('%s.%s' % (item, itemType)):
        cmds.addAttr('%s' % item, ln="%s" % itemType, dt="string")
    cmds.setAttr('%s.%s' % (item, itemType), "%s,%s" % (item, filename), type="string")  # item !!

    return '%s.%s' % (item, itemType)
