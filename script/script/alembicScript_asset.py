'''
Created on Jun 8, 2015
 
@author: m83
'''
  
import os, glob, re
import maya.cmds as cmds
import maya.mel as mel
from subprocess import *
import json
import socket
import datetime
from . import utilScript
import base64
import imp
imp.reload(utilScript)

from . import itemScript
imp.reload(itemScript)
from script import convert_byte_to_string

#find
def getFileName():
    fileDir = cmds.file (q=1, exn = 1)

    fileName = fileDir.rsplit('/', 1)[1].split('.')[0]
    fileInfo =  [fileName, fileDir]

    return  fileInfo


def versionUpTakeName(asstInfoDir, fileName):

    takeListDir = glob.glob("%s/%s.*.json" %(asstInfoDir,fileName) )
    takeListDir.sort()
    takeList = {}
    newNum ="0001"


    if takeListDir:
        currentTake = takeListDir[-1]
        
        currentNum  = re.search ("(?<=\.).*[0-9]{4}", currentTake).group()
        newNum = "%04d" %( int(currentNum) +1 )

        newTake = currentTake.replace("."+currentNum+".", ".%s." %newNum)

#         takeName = re.search ("(?<=\/)[a-z]+\.[0-9]{4}", currentTake).group()
        takeName = re.search ("[\w]+.[0-9]{4}.json*$", currentTake).group()
        
#         print currentTake
#         print newTake

    else:
#         takeListDir = []
        newTake = "%s/%s.0001.json" % (asstInfoDir,fileName)
        currentTake = "%s/%s.0001.json" % (asstInfoDir,fileName)
        takeName = "%s.0001" %fileName
        currentNum = "0001"
#         takeList[takeName]=newTake

    return currentTake, newTake, takeName 

# Export  ----------------------------------------------------------------------------------------
def itemDircheck(name, dirname):                      # edit
    fileData= getFileName()
    if "/pub/" in fileData[1]:
        fileData[1] =fileData[1].replace("/pub/", "/wip/scenes/")

    if name == 'alembic_TreeWidget':
        alembicDir = fileData[1].split("/scenes/")[0] + "/data/%s/%s" %(dirname, fileData[0])


        if not os.path.isdir(alembicDir):
            os.makedirs(alembicDir)
     
    return fileData[0], alembicDir


def itemFilecheck(itemdir): #export 2
    
    if os.path.isdir("%s" %itemdir):
        return True
    
    return False


def itemLodCheck(itemName):
    fileNameCheck = ["XHI", "HI", "MID", "LOW", "XLOW", "PROXY"]

    fileNameList = []
    if cmds.objExists(itemName):
        fileNameList.append(itemName)

    for i in fileNameCheck:
        lodName = "{}_{}".format(itemName, i)
        if cmds.objExists(lodName):
            fileNameList.append(lodName)
        lodNameGeoGrp = "{}_geo_Grp".format(lodName)
        if cmds.objExists(lodNameGeoGrp):
            fileNameList.append(lodNameGeoGrp)


    return fileNameList


def itemExport( fileName, itemdir,  item):
    # maoDawang_geo_Grp
    startF = 0
    endF   = 1

    fileinfo ={}
    cmds.refresh(su=1)

    print("===== AlembicExport : Start =====")
    print(">>>", fileName, itemdir, item)

    itemInfo = "%s_geo_Grp" % item
    itemNewDir = itemdir.split("/pub")[0] + "/wip/data/alembic/%s" % fileName
    fileinfo["%s" % item] = "%s/%s.abc" % (itemNewDir, itemInfo)  # maoDawang_geo_Grp

    if os.path.isdir(itemNewDir):
        os.system("rm -rf %s" % itemNewDir)
    if not os.path.isdir(itemNewDir):
        os.makedirs(itemNewDir)

    fileNameList = itemLodCheck(item)
    for item in fileNameList:
        itemName = item

        if "/model/" not in itemdir:
            if not "_geo_Grp" in item:
                item = "%s_geo_Grp" %item
        elif "/model/" in itemdir:
            print (">>>>>>>>> model")
            if cmds.ls("%s_geo_Grp" %item):
                item = "%s_geo_Grp" % item
            else:
                cmds.rename ( item, "%s_geo_Grp" %item)
                cmds.group( "%s_geo_Grp" %item, n=item)
                item = "%s_geo_Grp" % item

        if not cmds.ls(item) and "/model/" not in itemdir:
            print("Not %s !!! Make %s" %(item, item))
            cmds.refresh(su=0)
            return

        #print '>>>> "-frameRange %d %d -uvWrite -worldSpace -dataFormat ogawa -root %s %s -file %s/%s.abc" ' \
                  # %( (startF-num ), (endF+num), cmds.ls(item, l=1)[0], cmds.ls(item, l=1), itemNewDir,fileName)

        cmds.setKeyframe(itemName, attribute="translateX", v=1, t=0)
        cmds.setKeyframe(itemName, attribute="translateX", v=0, t=1)

        #cmds.setKeyframe(itemName, attribute="translateX", v=1, t=0)
        #cmds.setKeyframe(itemName, attribute="translateX", v=0, t=1)
        print(cmds.ls(item, l=1)[0])
        utilScript.pluginChecks('abc')
        print("{}/{}.abc".format(itemNewDir, item))
        mel.eval( 'AbcExport -j "-frameRange %d %d -uvWrite -writeUVSets -eulerFilter -writeVisibility -worldSpace -dataFormat ogawa -root %s -file %s/%s.abc" ' \
                  %( (startF), (endF), cmds.ls(item, l=1)[0], itemNewDir, item) )

        cmds.currentTime(1)
        cmds.cutKey(itemName, cl=1)

        if "/model/" in itemdir:
            cmds.parent(item, w=1)
            cmds.delete( itemName )
            cmds.rename(item , itemName)

        cmds.select(cl=1)

    cmds.refresh(su=0)

    print("===== AlembicExport : Done =====")
    return fileinfo

#--------------------------------------------------------------------------
def getFileList():
    fileDir = cmds.file(q=1, sn=1)
#     fileName = os.path.basename(fileDir ).split('.')[0]

    prjDir = re.search( ".+(?=/[\w]+/(pub|wip)/)",fileDir ).group()
    partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()
    fileName = re.search( "[\w]+(?=\.mb)",fileDir  ).group()        

    globalTakeDir = "%s/Take" %prjDir
    localTakeDir = "%s/%s/wip/data/Take" % (prjDir, partType)

    return prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir  


def checkTake(itemType):
    prjDir,fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
    globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
    localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)

    # check dir
    if not os.path.isdir(globalTakeDir):
        os.makedirs(globalTakeDir)

    if not os.path.isdir(localTakeDir):
        os.makedirs(localTakeDir)

    # global Take
    if not os.path.isfile( globalCurrentTake ):
        take = {}

    else:
        globalCurrentTake = convert_byte_to_string.convert_byte_to_string(globalCurrentTake)
        with open("%s" %( globalCurrentTake ), 'r' ) as f:
            take = json.load(f)

    if not take.get(itemType):
        take["%s" %itemType] ={}

    # local Take
    if not os.path.isfile( localCurrentTake ):
        local_take = {}

    else:
        localCurrentTake = convert_byte_to_string.convert_byte_to_string(localCurrentTake)
        with open("%s" %( localCurrentTake ), 'r' ) as f:
            local_take = json.load(f)

    if not local_take.get(itemType):
        local_take["%s" %itemType] ={}
                    
    return take, local_take    



def saveTake(itemType, take, local_take):
    prjDir,fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
    globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
    localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)

    local_take = convert_byte_to_string.convert_byte_to_string(local_take)
    take = convert_byte_to_string.convert_byte_to_string(take)

    # global Take Save
    with open("%s" %localNewTake, 'w') as f:
        json.dump(local_take,  f, indent=4)    

    # global Take Save
    with open("%s" %globalNewTake, 'w') as f:
        json.dump(take,  f, indent=4)


def assetInfoExport( objList ): #, itemType
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
    globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
    localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)
    
    
    typeList = {"ani"       :"alembicAni", 
                "crowdSim"  :"alembicCrowdSim",
                "crowdAni"  :"alembicCrowdAni",
                "model"     :"alembicModel",
                "lit"       :"alembicRender",
                "fur"       :"alembicFur",
                "furSim"    :"alembicFurSim",
                "musle"     :"alembicMusle", 
                "cloth"     :"alembicCloth",
                "dyn"       :"alembicSimul",
                "fx"        :"alembicFx",
                "matchmove" :"alembicMm", 
                "layout"    :"alembicLayout",
                "hair"      :"alembicHair",
                "hairSim": "alembicHairSim",
                "clothSim"  :"alembicClothSim",
                 "rig":"alembicRig"
                }
    
    itemType = typeList [partType]
    take, local_take = checkTake(itemType)
    
    
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

    print(">>>", objList)
    if not objList:
        return

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
        startF = cmds.playbackOptions(min=1, q=1)
        endF   = cmds.playbackOptions(max=1, q=1)
        frameDict.update({ item : "%d-%d" %(startF, endF)})
                
        # date info
        nowdate = str(datetime.datetime.now())
        date = nowdate.rsplit(":",1)[0]
        dateDict.update({ item :  date})
                
        #object List info
        objectListDict.update({ item :  objList[item] } )

        #object check info
        checkList = {"model":1, "rig" : 1,"ani":1, "matchmove":1, "layout":1, "dyn":1, "cloth":1,"hair":1,"hairSim":1, "clothSim":1, "lit" : 1, "furSim":1, "fur":1, "lookdev" : 1 ,"fx" : 1 }
        objectCheckDict.update({ item :  checkList} )

        #update List info
        updateListDict.update({ item :  objList[item]})
                                                                                                                                                    
    if take[ itemType ].get('objectList'):  # is itemType
        if take[ itemType ]['objectList'].get(item):  # is item
            newTake =  takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict )
        else:
            newTake = takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
    else:
        newTake = takeSetInfo(take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict) 
        
    if local_take[ itemType ].get('objectList'):  # is itemType
        if local_take[ itemType ]['objectList'].get(item):  # is item
            local_Newtake = takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
        else:
            local_Newtake = takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)                
    else:
        local_Newtake = takeSetInfo(local_take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict)
        #--------------------------------------------------------
            
    take = newTake      
    local_take = local_Newtake
    
    take[ itemType ]["updateList"]= updateListDict 
    local_take[ itemType ]["updateList"]= updateListDict
    
    saveTake( itemType, take ,local_take)

def takeSetInfo(take, itemType, type, fileNameDict, versionDict, userNameDict, ipaddrDict,frameDict, dateDict, objList, objectCheckDict):
    if type == True:
        take[ itemType ]["fileName"   ].update( fileNameDict   )
        take[ itemType ]["version"    ].update( versionDict    )
        take[ itemType ]['username'   ].update( userNameDict   )
        take[ itemType ]['ipaddr'     ].update( ipaddrDict     )
        take[ itemType ][ 'frame'     ].update( frameDict      )
        take[ itemType ]['date'       ].update( dateDict       )
        take[ itemType ]['objectList' ].update( objList        )
        take[ itemType ]['objectCheck'].update( objectCheckDict)    
    else:
        take[ itemType ].update( { "fileName"  : fileNameDict } )
        take[ itemType ].update( {"version"    : versionDict  } ) 
        take[ itemType ].update( {'username'   : userNameDict } )
        take[ itemType ].update( {'ipaddr'     : ipaddrDict   } )
        take[ itemType ].update( { 'frame'     : frameDict    } )
        take[ itemType ].update( {'date'       : dateDict     } )
        take[ itemType ].update( {'objectList' : objList      } )
        take[ itemType ].update( {'objectCheck': objectCheckDict} )

    return take



#------------------------------------------------------------------------
def currentPartType():
    fileDir = cmds.file(q=1, sn=1)
#     fileName = os.path.basename(fileDir ).split('.')[0]
#     print fileDir

#     prjDir   = fileDir.split("/")[2]
#     sqcDir   = fileDir.split("/")[4]
#     shotDir  = fileDir.split("/")[5]
    partType = None
    if re.search( "[\w]+(?=/(pub|wip)/)",fileDir ) != None:
        partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()
#     fileName = re.search( "[\w]+(?=\.mb)",fileDir  ).group()        
    return  partType 

#import 
def alembicImport (itemInfo, type, rootType, num=None):
    for i in itemInfo:
#         if "geoCache" in itemType:
        writeItemName = alembicImportFile    ( i, itemInfo[i], rootType, type)
#         elif "simulGeoCache" in itemType:
#             geoCacheReferenceFile ( i, itemInfo[i] , itemType)
    return writeItemName

def pluginCheck():
    if os.path.isdir("/usr/autodesk/maya2017/vray/plug-ins"):
        pluginDir = "/usr/autodesk/maya2017/vray/plug-ins"
        
    if not cmds.pluginInfo("vrayformaya", q=1, loaded=1):
        cmds.loadPlugin ("%s/vrayformaya.so"%pluginDir )
   
    if cmds.getAttr ('defaultRenderGlobals.currentRenderer') != "vray":
        cmds.setAttr ('defaultRenderGlobals.currentRenderer', "vray", type = "string" )
        mel.eval('vrayCreateVRaySettingsNode();')


def nameSpaceCheck (item):
    if cmds.ls(item):
        reply = cmds.confirmDialog(title='Question!',
                                   message='It\'s already exists Name!! Delete Object and Object Reflace ??',
                                   button=['ok', 'cancel'])
        if reply == "ok":
            itemScript.deleteConnectObj(item)
        else:
            return
    else:
        # delete namespace
        if cmds.namespace(exists="%s" % item.split(':')[0]):
            cmds.namespace(rm="%s" % item.split(':')[0], mnr=1)

def alembicImportFile (item, itemDir, rootType, type):
    #OkYunA3:OkYunA 
    #/show/AS/seq/CF/CF_156/ani/wip/data/geoCache/CF_156_ani_v01_w47_text/OkYunA3.mc 
    #geoCache

#     namespaceName = item.split(":")[0]
#     outputSetName = "%s:output_SET" %namespaceName
    
#     if cmds.ls ( item, item.split(":")[0]  ): #itemName
#         print item , item.split(":")[0], "already Object !!"
#         return


    if not os.path.isfile(itemDir):
        print("Not File !!")
        return

#     # import
#     if cmds.ls("%s" %item):
#         cmds.confirmDialog ( title ='Aready Name! Name Check!' , message ='%s' %item, button=[ 'ok' ])
#         return
    
#     mel.eval('AbcImport -mode import -fitTimeRange -setToStartFrame "%s"' %itemDir)


    if type == "alembic": #cherryBranch9_cherryBranch.abc
        utilScript.pluginChecks("abc")
        nameSpaceCheck(item)
        if ":" in item:
            returnList = cmds.file("%s" %itemDir , namespace = "%s" %item.split(":")[0], i=1, pr =1, ra=True,  mergeNamespacesOnClash =False, type ="Alembic", rnn=1)
            # print ">" * 10, returnList
        else:
#             returnList = cmds.file("%s" %itemDir , namespace = ":", i=1, pr =1, ra=True,  mergeNamespacesOnClash =False, type ="Alembic", rnn=1)
            returnList = cmds.file("%s" %itemDir, i =True , type ="Alembic" ,  ignoreVersion=True, mergeNamespacesOnClash= 0, options="v=0", pr= True, loadReferenceDepth="all" ,returnNewNodes=1)
            # print ">" * 10, returnList

        topGroup= [x for x in returnList if x.count("|") == 1]
        tranName = topGroup[0].split("|")[1]

        # rename
        if ("_geo_Grp" not in tranName)  and not cmds.listRelatives(tranName,p=1, type="mesh"): # if group rename and
            tranName = cmds.rename ( tranName ,item )


        elif "_geo_Grp" in tranName:
            cmds.group(":%s" %tranName, n=item)


    elif type == "import":
        if cmds.ls("%s:abcCache_SET" %item):
            item_cacheSetGrp_name = "%s:%s" % (item, item)
            cmds.select(item_cacheSetGrp_name )
            cmds.AbcImport("%s" % itemDir, reparent = "%s" %item_cacheSetGrp_name, mode='import')

        else:
            cmds.AbcImport("%s" % itemDir, mode='import', debug=1, connect="/", removeIfNoUpdate=1)
            # if item:
            #     cmds.rename ( item, "%s_geo_Grp" %item  ) #orgname rename
            #     cmds.select( "%s_geo_Grp" %item  )
            #     cmds.AbcImport ("%s" %itemDir, mode='import',  debug=1,  connect ="/", removeIfNoUpdate =1)
            #     cmds.rename("%s_geo_Grp" % item, item)
            # else:
            #     cmds.AbcImport("%s" % itemDir, mode='import', debug=1, connect="/", removeIfNoUpdate=1)

        #'AbcImport -mode import -connect "/" "/show/HS/seq/AO/AO_002/ani/wip/data/alembic/AO_002_ani_v03_w11/troll1/troll1_troll_geo_Grp.abc";'
    else: #proxy
        nameSpaceCheck(item)
        pluginCheck()
        mel.eval('vrayCreateProxy -node "%s"  -dir "%s" -existing -createProxyNode ' %(item, itemDir))
        shapename = "".join( cmds.ls(sl=1) )
        tranName  = "".join( cmds.listRelatives (shapename , p =1) )
        
        cmds.rename ("%s" %tranName , "vrayFroxyFileTMP")
        cmds.rename ("%s_vraymesh" %tranName , "vrayFroxyFileTMP_vraymesh")
        cmds.rename ("%s_vraymeshmtl" %tranName , "vrayFroxyFileTMP_vraymeshmtl")

        tranName="vrayFroxyFileTMP"

        cmds.setAttr ( "%s_vraymesh.animType" %tranName, 1 )
        cmds.setAttr ("%s_vraymesh.useAlembicOffset" %tranName, 1)
        
    # is namespace
        if ":" in item:
            cmds.rename ("%s" %tranName , ":%s" %item)
            cmds.rename ("%s_vraymesh" %tranName , ":%s_vraymesh" %item)
            cmds.rename ("%s_vraymeshmtl" %tranName , ":%s_vraymeshmtl" %item)
        else:
            cmds.rename ("%s" %tranName , "%s" %item)
            cmds.rename ("%s_vraymesh" %tranName , "%s_vraymesh" %item)
            cmds.rename ("%s_vraymeshmtl" %tranName , "%s_vraymeshmtl" %item)
                        
#             for i in cmds.listRelatives(":%s" %item, ad=1):
#                 cmds.rename (i, ":%s:%s" %(item.split(":")[0], i ) )
            

    # info write
    if "alembicAni" == rootType:
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicAni")

    if "alembicCrowdSim" == rootType:
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicCrowdSim")

    if "alembicCrowdAni" == rootType:
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicCrowdAni")
                
    elif "alembicModel" == rootType:
        print("alembicModel")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicModel")
#         initsimulGeoCacheImportWrite( item,  itemDir, "simulGeocache")

    elif "alembicRender" == rootType:
        print("alembicRender")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicRender")
#         initMmGeoCacheImportWrite( item,  itemDir, "mmGeocache")

    elif "alembicFur" == rootType:
        print("alembicFur")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicFur")
#         initModelGeoCacheImportWrite( item,  itemDir, "modelGeocache")

    elif "alembicFurSim" == rootType:
        print("alembicFurSim")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicFurSim")
    #         initModelGeoCacheImportWrite( item,  itemDir, "modelGeocache")

    elif "alembicMusle" == rootType:
        print("alembicMusle")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicMusle")
#         initModelGeoCacheImportWrite( item,  itemDir, "modelGeocache")

    elif "alembicCloth" == rootType:
        print("alembicCloth")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicCloth")
#         initRenderGeoCacheImportWrite( item,  itemDir, "geoCacheRender")

    elif "alembicSimul" == rootType:
        print("alembicSimul")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicSimul")
#         initRenderGeoCacheImportWrite( item,  itemDir, "furGeoCache")

    elif "alembicMm" == rootType:
        print("alembicMm")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicMm")
#         initRenderGeoCacheImportWrite( item,  itemDir, "clothGeoCache")

    elif "alembicFx" == rootType:
        print("alembicFx")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicFx")
#         initRenderGeoCacheImportWrite( item,  itemDir, "clothGeoCache")

    elif "alembicHair" == rootType:
        print("alembicHair")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicHair")
#         initRenderGeoCacheImportWrite( item,  itemDir, "clothGeoCache")

    elif "alembicHairSim" == rootType:
        print("alembicHairSim")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicHairSim")
    #         initRenderGeoCacheImportWrite( item,  itemDir, "clothGeoCache")

    elif "alembicClothSim" == rootType:
        print("alembicClothSim")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicClothSim")

    elif "alembicRig" == rootType:
        print("alembicRig")
        writeItemName = initAlembicImportWrite ( item,  itemDir, "alembicRig")

#         initRenderGeoCacheImportWrite( item,  itemDir, "clothGeoCache")
    cmds.select(cl=1)

    return writeItemName 

# write
def initAlembicImportWrite( item , filename, itemType):
#     itemAssetName = item.split(":")[1]
#     reNameItem = item.replace(":%s" %itemAssetName, ":output_SET")
#     item = item.replace("geoCache_SET", "output_SET")


    if cmds.ls('%s.%s' %(item, itemType) ):
        cmds.deleteAttr("%s.%s" %(item, itemType) )
    
#     print ">>>", item, itemType
    if cmds.ls(item) and not cmds.ls('%s.%s' %(item, itemType)):
            cmds.addAttr ('%s' %item, ln= "%s" %itemType,  dt= "string" )


    if cmds.ls(item):
        cmds.setAttr('%s.%s' %(item, itemType), "%s,%s" %( item, filename) ,type="string")   # item !!
    
    return '%s.%s' %(item, itemType)

def alembicAllLoadSet():
    cmds.select("*:abcCache_SET")
    allAbcSet = cmds.ls(sl=1)
    print(">>>", allAbcSet)
    if allAbcSet:
        cmds.select(cl=True)

    return list(set(allAbcSet))

def alembicCurveLoadSet():
    cmds.select("*:abcHairCache_SET")
    allAbcSet = cmds.ls(sl=1)
    print(">>>", allAbcSet)
    if allAbcSet:
        cmds.select(cl=True)

    return list(set(allAbcSet))

def alembicLoadMesh():
    return cmds.ls(sl=1)
