'''
Created on Jun 8, 2015
 
@author: m83
'''

import os
import glob
import maya.cmds as cmds
import maya.mel as mel
import pyseq
from . import utilScript
import imp
imp.reload(utilScript)

def yetiCacheAllLoadSet(name):
    allGeoSet=[]
    if "yetiCacheSetAllLoad" == name:
        if cmds.ls("*:yetiCache_SET"):
            cmds.select("*:yetiCache_SET")
            allGeoSet = cmds.ls(sl=1)
            cmds.select(cl=True)

    return allGeoSet

# #import
def yetiCacheImport (itemInfo, type, rootType):
    utilScript.pluginChecks('yetiCache')
    for i in itemInfo:
#         if "geoCache" in itemType:
        writeItemName = yetiCacheImportFile    ( i, itemInfo[i], rootType)

#         elif "simulGeoCache" in itemType:
#             geoCacheReferenceFile ( i, itemInfo[i] , itemType)
    return writeItemName


def yetiCacheImportFile (item, itemDir, rootType):
    #OkYunA3:OkYunA
    #/show/AS/seq/CF/CF_156/ani/wip/data/geoCache/CF_156_ani_v01_w47_text/OkYunA3.mc
    #geoCache

    filepath = pyseq.getSequences(glob.glob("%s/*.fur" % itemDir))

    # print filepath,filepath[0].format("%h%p%t")
    if not os.path.isdir(itemDir):
        print("Not file !!!")
        return


    if not cmds.ls(item):
        print(">> Not %s" %item)
        yetishape = mel.eval("pgYetiCreate()")
        yetitransform = cmds.listRelatives(yetishape, p=1)[0]
        yetinode = cmds.rename(yetitransform, ":%s" % item)
        yetishapenode = cmds.ls(yetinode, dag=1, type="shape")[0]

    else:
        yetishapenode = cmds.ls(item, dag=1, type="shape" )[0]

    # import
    for path in filepath:
        yeticachepath = "%s/%s" %(itemDir, path.format("%h%p%t") )



    cmds.setAttr("%s.cacheFileName" %yetishapenode , "%s" %yeticachepath , type="string")
    #cmds.setAttr("%s.overrideCacheWithInputs" %yetishapenode , 1)
    cmds.setAttr("%s.fileMode" % yetishapenode, 1)


    # info write
    if "yetiCache" == rootType:
        writeItemName = initGeoCacheImportWrite ( item,  yeticachepath, "yetiCache")

    cmds.select(cl=1)
    return writeItemName

# # write
def initGeoCacheImportWrite( item , filename, itemType):
#     itemAssetName = item.split(":")[1]
#     reNameItem = item.replace(":%s" %itemAssetName, ":output_SET")
#     item = item.replace("geoCache_SET", "output_SET")

    if cmds.ls('%s.%s' %(item, itemType) ):
       cmds.deleteAttr("%s.%s" %(item, itemType) )

    if not cmds.ls('%s.%s' %(item, itemType)):
        cmds.addAttr ('%s' %item, ln= "%s" %itemType,  dt= "string" )
    cmds.setAttr('%s.%s' %(item, itemType), "%s,%s" %( item, filename) ,type="string")   # item !!

    return '%s.%s' %(item, itemType)


def yetiCacheExport(filename, itemdir, item):
    utilScript.pluginChecks("yetiCache")

    fileInfo = {}

    print("yetiCacheExport")
    return fileInfo