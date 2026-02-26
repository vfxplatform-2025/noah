'''
Created on Jun 22, 2015

@author: m83
'''
import os, sys, glob, re, string
import maya.cmds as cmds
import maya.mel as mel
import getpass
from subprocess import *
import xml.etree.ElementTree as et
import json
import socket
import datetime
import maya.OpenMaya as OpenMaya
from script import convert_byte_to_string


# read ------------------------------------------------------------------------------------------
def splitItemName(itemNameList):
    
    item = {}
    for itemName in itemNameList:
        if ":" in itemName:
#             splitItem = re.search("([0-9]+)?:.*", itemName)
            splitItem = re.search("[\w]*[\D](?=([\d]+)?:)", itemName).group()
#         assetName = itemName.split(splitItem.group())[0]
        else:
            splitItem = itemName
            
        if splitItem not in item:
            item [ splitItem] = []

        item [ splitItem].append( itemName )
    return item

def currentJopType():
    fileDir = cmds.file(q=1, sn=1)
#     fileName = os.path.basename(fileDir ).split('.')[0]
#     print fileDir
    if fileDir.split("/"):
        partType  = fileDir.split("/")[3]
#     prjDir   = fileDir.split("/")[2]
#     sqcDir   = fileDir.split("/")[4]
#     shotDir  = fileDir.split("/")[5]
#     partType = None
#     if re.search( "[\w]+(?=/(pub|wip)/)",fileDir ) != None:
#         partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()
        
    return  partType 

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
        
    return  partType 

def itemPubDirCheck(): #export 1
    fileData= getFileName()
    
    if "/wip/" in fileData[1]:
        pubDir = fileData[1].split("/wip/")[0] + "/pub"
        
    elif "/pub/" in fileData[1]:
        pubDir = fileData[1].split("/pub/")[0] + "/pub"
        
    else:
        print("( item Sciprt 45 line ) Erro : Not Project Set !!  ")
        return 
    
    if not os.path.isdir(pubDir):
        os.makedirs(pubDir)

    return fileData[0], pubDir

def getMayaFileList():
    fileDir = cmds.file(q=1, sn=1)
    if fileDir:
#     fileName = os.path.basename(fileDir ).split('.')[0]
#     print fileDir
        prjDir   = fileDir.split("/")[2]
        sqcDir   = fileDir.split("/")[4]
        shotDir  = fileDir.split("/")[5]
        partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()
        fileName = re.search( "[\w]+(?=\.mb)",fileDir  ).group()        
    else:
        prjDir   = None
        sqcDir   = None
        shotDir  = None
        partType = None
        fileName = None
        
    return prjDir, sqcDir, shotDir, partType, fileName, fileDir 

def versionUpTakeName(asstInfoDir, fileName):
     
    takeListDir = glob.glob("%s/%s.*.json" %(asstInfoDir,fileName) )
    takeListDir.sort()
    takeList = {}
    newNum ="0001"
     
    if takeListDir:
        currentTake = takeListDir[-1]
        
        currentNum  = re.search ("(?<=\.).*[0-9]{4}", currentTake).group()
        newNum = "%04d" %( int(currentNum) +1 )
        
        newTake = currentTake.replace(".%s." %currentNum, ".%s." %newNum)
#         takeName = re.search ("(?<=\/)[a-z]+\.[0-9]{4}", currentTake).group()
        takeName = re.search ("[\w]+.[0-9]{4}.json*$", currentTake).group()

    else:
#         takeListDir = []
        newTake = "%s/%s.0001.json" % (asstInfoDir,fileName)
        currentTake = "%s/%s.0001.json" % (asstInfoDir,fileName)
        takeName = "%s.0001" %fileName
        currentNum = "0001"

    return currentTake, newTake, takeName 

# Export  ----------------------------------------------------------------------------------------
#find
def getFileName():
     
    fileDir = cmds.file (q=1, exn = 1)
    
    fileName = fileDir.rsplit('/', 1)[1].split('.')[0]
    fileInfo =  [fileName, fileDir]
    
    return  fileInfo

def itemDircheck(name): #export 1
    fileData= getFileName()
    wipDir = fileData[1].split("/scenes/")[0]
    
    if name == 'atom_TreeWidget':
        itemDir = wipDir + "/data/ani/%s" %fileData[0]
            
    elif name == "camera":
        itemDir = wipDir + "/data/camera" 
    
    # creat Dir
    if not os.path.isdir(itemDir):
        os.makedirs(itemDir)        
        
    return fileData[0], itemDir


def itemFilecheck(itemname, itemdir, name): #export 2

    if name == 'atom_TreeWidget':
        if os.path.isfile("%s/%s.atom" %(itemdir,itemname)):
            return True
            
    elif name == "camera":
        if os.path.isfile("%s/%s.mb" %(itemdir,itemname)):
                          return True
    
    return False

def deleteAssetSaveInfoList( takeNameDir, data):
    if not takeNameDir:
        return
    data = convert_byte_to_string.convert_byte_to_string(data)
    with open( "%s" %takeNameDir, 'w') as f:
        json.dump(data, f, indent =4)

# 1======================================================
def itemListSelect(item):  #export 3
    itemList = cmds.ls([x.replace(":output_SET", ":ctrl_SET") for x in item])    #ctrl_set select
    cmds.select( itemList)
    
    return itemList

def itemKeyBake(num): #export 4
    selectObj = cmds.ls(sl=1)
    startF = cmds.playbackOptions(min=1, q=1)
    endF   = cmds.playbackOptions(max=1, q=1)
    cmds.refresh(su=1)
    
    cmds.bakeResults ( selectObj,  
                       shape=True,
                       simulation =True,  
                       t =(startF-num,endF+num), 
                       sampleBy =1, 
                       disableImplicitControl = True, 
                       preserveOutsideKeys =True, 
                       sparseAnimCurveBake= False, 
                       removeBakedAttributeFromLayer =False , 
                       removeBakedAnimFromLayer =False, 
                       bakeOnOverrideLayer = False, 
                       minimizeRotation = True)
    cmds.refresh(su=0)
# 2======================================================

def findModelRigData(proj, fileList):
    
    rigfile  = {}    
    modelfile= {}
    for i in fileList:
        if ":" in i:
#             item = re.search("[\D]+([\w]+)?[\D]+(?=([\d]+)?:)", i).group()
            item = i.split(":")[1]
        else:
            item = i

        # prop
        propList = ""
        modelProplList = glob.glob("/show/%s/assets/prop/%s/model/pub/*.mb" %(proj, item))
        modelProplList.sort()
        propList =  modelProplList[-1] if modelProplList else ""   
    
        
        #env
        envList = ""
        modelEnvList = glob.glob("/show/%s/assets/env/%s/model/pub/*.mb" %(proj, item))
        modelEnvList.sort()
        envList = modelEnvList[-1] if modelEnvList else "" 
    
                
        #cha
        chaList  = ""
        modelChaList = glob.glob("/show/%s/assets/cha/%s/model/pub/*.mb" %(proj, item))
        modelChaList.sort()
        chaList = modelChaList[-1] if modelChaList else "" 
    
    
        #litRig
        litRigList = ""
        modelLitList = glob.glob("/show/%s/assets/litRig/%s/model/pub/*.mb" %(proj, item))
        modelLitList.sort()
        litRigList = modelLitList[-1] if modelLitList else "" 
    
    
        modelList = propList + envList + chaList + litRigList
        modelAssetName = modelList.split('/')[5]
        modelAssetGrop = dict(list(zip(modelAssetName , modelList )))
    
        
        #===========================================================================================
        # prop
        propList = ""
        rigProplList = glob.glob("/show/%s/assets/prop/%s/rig/pub/*.mb" %(proj, item))
        rigProplList.sort()
        propList = rigProplList[-1] if rigProplList else "" 
    
        #env
        envList = ""
        rigEnvList = glob.glob("/show/%s/assets/env/%s/rig/pub/*.mb" %(proj, item))
        rigEnvList.sort()
        envList = rigEnvList[-1] if rigEnvList else "" 
    
        #cha
        chaList  = ""
        rigChaList = glob.glob("/show/%s/assets/cha/%s/rig/pub/*.mb" %(proj, item))
        rigChaList.sort()
        chaList = rigChaList[-1] if rigChaList else "" 
    
        #litRig
        litRigList = ""
        rigLitList = glob.glob("/show/%s/assets/litRig/%s/rig/pub/*.mb" %(proj, item))
        rigLitList.sort()
        litRigList = rigLitList[-1] if rigLitList else "" 
    
    
        rigList = propList + envList + chaList + litRigList
    
        
        #surch file

        if rigList:    
            rigfile.update({ item : rigList})
        else:
            rigfile={}
            
        if modelList:
            modelfile.update({ item : modelList})
        else:
            modelfile={}

    return rigfile, modelfile
#--------------------------------------------------------------------------------
def getFileList():
    fileDir = cmds.file(q=1, sn=1)
#     fileName = os.path.basename(fileDir ).split('.')[0]

    prjDir = re.search( ".+(?=/[\w]+/(pub|wip)/)",fileDir ).group()
    partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()
    fileName = re.search( "[\w]+(?=\.mb)",fileDir  ).group()        

    globalTakeDir = "%s/Take" %prjDir
    localTakeDir = "%s/%s/wip/data/Take" % (prjDir, partType)

    return prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir  

  

# def getFileList(dir = None):
#     # file Dir 
#     if dir == None:
#         fileDir = cmds.file(q=1, sn=1)
#     else:
#         fileDir = dir
#         
#     # os path
#     if fileDir:
#         if sys.platform == "win32":
#             fileDir = fileDir.replace("Q:/", "/show/")
# #     fileName = os.path.basename(fileDir ).split('.')[0]
#     # find data
#     prjDir = re.search( ".+(?=/[\w]+/(pub|wip)/)",fileDir ).group()
#     partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()
#     fileName = re.search( "[\w]+(?=\.mb)",fileDir  ).group()        
# 
#     globalTakeDir = "%s/Take" %prjDir
#     localTakeDir = "%s/%s/wip/data/Take" % (prjDir, partType)
# 
#     return prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir  

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
        with open("%s" %( globalCurrentTake ), 'r' ) as f:
            take = json.load(f)

    if not take.get(itemType):
        take["%s" %itemType] ={}

    # local Take
    if not os.path.isfile( localCurrentTake ):
        local_take = {}

    else:
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
    # global Take Save
    with open("%s" %localNewTake, 'w') as f:
        json.dump(local_take,  f, indent=4)    

    take = convert_byte_to_string.convert_byte_to_string(take)
    # global Take Save
    with open("%s" %globalNewTake, 'w') as f:
        json.dump(take,  f, indent=4)


def assetInfoExport( objList ): #, itemType
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = getFileList()
    globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
    localCurrentTake, localNewTake,localNewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)

    typeList = {"ani":"atom", "model":"modelAtom"}
    itemType = typeList [partType]

    take, local_take = checkTake(itemType)

    # asset info
#     allnameSpace= list(set(cmds.ls(sns=1)[1::2]))
#     allnameSpace.remove(':')

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
        checkList = {"model":1, "rig" : 1,"ani":1, "matchmove":1, "layout":1, "dyn":1, "cloth":1,"hair":1, "clothSim":1, "lit" : 1, "fur":1, "lookdev" : 1 ,"fx" : 1 }
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

def shotTakeAssetInfoExport (prjDir, objList  , partType, shotType ):
    globalTakeList = "%s/Take/takeList.json" %prjDir

    if os.path.isfile( globalTakeList ):
        with open("%s" %( globalTakeList ), 'r' ) as f:
            take = json.load(f)

        for i in take["%s" %partType]:
            assetInfoExport(take["%s" %partType][i],  objList, partType, shotType )


def changeSaveTake(newTakeDir, take):
    take = convert_byte_to_string.convert_byte_to_string(take)
    # global Take Save
    with open("%s" %newTakeDir, 'w') as f:
        json.dump(take,  f, indent=4)

#===============================================================
def proxyAutoConnectShader():
    #select all vray mesh proxy material
    proxyMaterialNodes = cmds.ls(type = "VRayMeshMaterial")
    #select all material
    allMaterials = cmds.ls(materials = True)
    materialClean = list(set(allMaterials) - set(proxyMaterialNodes))
    
    
    if len(proxyMaterialNodes) == 0:
        OpenMaya.MGlobal.displayWarning("No VRayMeshMaterial in the scene !")
    #list all connection name on all vray mesh proxy material
    
    for proxyMaterialNode in proxyMaterialNodes:
        numberOfSlot = cmds.getAttr(proxyMaterialNode + ".shaderNames", size = True)

        for i in range(numberOfSlot):
            nameSlot = cmds.getAttr(proxyMaterialNode + ".shaderNames[" + str(i) + "]")

            #connected or not ?
            if cmds.connectionInfo( proxyMaterialNode + ".shaders[" + str(i) + "]", isDestination=True):
                connected = cmds.connectionInfo( proxyMaterialNode + ".shaders[" + str(i) + "]", sourceFromDestination=True)
                cmds.disconnectAttr(connected, proxyMaterialNode + ".shaders[" + str(i) + "]")
                print("[deeXVrayFast] Disconnect " + proxyMaterialNode + ".shaders[" + str(i) + "]")
            for myMat in materialClean:
                if myMat.split(":")[-1] == nameSlot.split(":")[-1]:
                    #try:
                    cmds.connectAttr(myMat + ".outColor", proxyMaterialNode + ".shaders[" + str(i) + "]", f = True)
                    print("[deeXVrayFast] " + proxyMaterialNode + ".shaders[" + str(i) + "] connected.")



# nameSpace 

# delete obj
def deleteConnectObj(itemName):
#     selOb = cmds.ls(sl=1)
    itemName = str(itemName)
    
    if not cmds.ls(itemName):
        print("Not Object !!!")
        return
    
#     for i in itemName:
    if not ":" in itemName:
        print(itemName,"<<< not NameSpace Select !!") 
        return    
    
    if cmds.referenceQuery(itemName, inr =1):
        ref = cmds.referenceQuery ("%s" %itemName, f= 1)
        cmds.file (ref , removeReference =1)
        return
    
    nameSpace = itemName.split(":")[0]
    cmds.namespace(rm="%s" %nameSpace,  dnc=1)    


                          
def nameSpaceDelete(itemName):
    nameSpaceSet=itemName.split(":")[0]
    itemList = cmds.ls(itemName)
    
    for rootName in itemList:
        try:
            if cmds.referenceQuery(rootName, filename =1):
                print("Not Delete !! reference File !!!")
                continue
        except:
            pass
        
        if cmds.ls(rootName) :
            selectList = cmds.listRelatives(rootName, ad=1)
            selectList.append(rootName )
            for subName in selectList :
                #nameSpace check
                if ":" in subName :
                    currentNamespace = subName.split(":")[0]
                    if cmds.namespace (exists = ':%s' %currentNamespace ) == True:            
                        cmds.namespace(rm = ":%s" %currentNamespace   , mnr=1 )

# add
def nameSpaceAdd( itemName ):
    
    nameSpaceSet=itemName.split(":")[0]
    itemList = cmds.ls(sl=1)
     
    for rootName in itemList:
        #reference 
        try:
            if cmds.referenceQuery(rootName, filename =1): 
                refFilePath = cmds.referenceQuery(rootName, filename =1)
                cmds.file(refFilePath, e=1, namespace="%s" %nameSpaceSet)
                # reference  nameSpace delete
                if cmds.namespace( exists = rootName.split(":")[0]):
                    cmds.namespace( rm =rootName.split(":")[0])
                continue
        except:
            pass

        #nameSpace
        noneNameSpace = rootName
        if ":" in rootName:
            nameSpaceDelete(itemName)
            noneNameSpace =rootName.split(":")[1] 

        selectList = cmds.listRelatives(noneNameSpace, ad=1)
        selectList.append(noneNameSpace )

        for subName in selectList :
            cmds.rename ("%s" %subName , ":%s:%s" %(nameSpaceSet, subName ) )

#---------------------------------------------------------------------------
def takeUpdateCheck(objList, rootType, shotDir):

    takeListDir = glob.glob("%s/Take/take.*.json" %shotDir )
    takeListDir.sort()
    takeDir =takeListDir[-1]
    fileDir = cmds.file(q=1, sn=1)
    if not fileDir:
        return
    
    partType= fileDir.split("/")[6]
    
    for i in objList:
        #open
        with open("%s" %takeDir, 'r' ) as f:
                take = json.load(f)
                
#         take[rootType]["updateList"][i][partType]
        if take[rootType]["objectCheck"].get(i) == None:
            continue
        #save        
        if take[rootType]["objectCheck"][i].get(partType):
            take[rootType]["objectCheck"][i][partType] = 0
            take = convert_byte_to_string.convert_byte_to_string(take)
            with open("%s" %takeDir, 'w') as f:
                json.dump(take,  f, indent=4)
        
def itemExport( fileName, itemdir, itemName = None):   # exort 5
#    CF_156_ani_v01_w47_text
#    /show/AS/seq/CF/CF_156/ani/wip/data/geoCache/CF_156_ani_v01_w47_text
#    OkYunA3:geoCache_SET
#    10
    
    fileinfo = {}
    objName = cmds.ls(sl=1)
    
    for i in objName:
        if i in ['output_SET']:
            continue
        fileinfo [ i ] = "%s/%s.mb" %(itemdir, fileName)
    
    
    #model
#     pubMod(itemName, "%s/%s.mb" %(itemdir, fileName) )
#     cmds.file ("%s/%s.mb" %(itemdir, fileName), force=1,  options="v=0;" ,typ= "mayaBinary", pr=1, es=1 )

    cmds.file( rename="%s/%s.mb" %(itemdir, fileName))
    cmds.file( f=1,  save=1, options ="v=0;")
    return fileinfo



                        
#     for i in itemList:
#         print i
#     cmds.rename ("pSphere1", ":FOO:pSphere1" )
#     cmds.namespace( set=':' )
# def itemExport( filename, itemdir,item, num):   # exort 5  e
# 
#     atom_animLayer = 0
#     startF = cmds.playbackOptions(min=1, q=1)
#     endF   = cmds.playbackOptions(max=1, q=1)
#     atom_select    = "selectedOnly"
#     
#     cmds.select(item)
# 
#     fileinfo ={}
#     fileinfo[ "%s" %item ] = "%s/%s.atom" %(itemdir, "%s" %item.split(":")[0])
# 
#     cmd = "precision=8"
#     cmd += ";statics=1;baked=1;sdk=0;constraint=0"
#     cmd += ";animLayers=%d" %atom_animLayer + ";selected=%s" %atom_select + ";whichRange=2;range=%d" %startF + ":%d" %endF + ";hierarchy=none"
#     cmd += ";controlPoints=0;useChannelBox=1;options=keys"
#     cmd += ";copyKeyCmd=-animation objects -time >%d" %(startF - num) + ":%d" %(endF + num) + "> -float >%d" %startF + ":%d" %endF + "> "
#     cmd += "-option keys -hierarchy none -controlPoints 0"
#     
#     cmds.file( "%s/%s" %(itemdir, item.split(":")[0]), es =1, force=1, options="%s" %cmd, typ= "atomExport")
#     cmds.select(cl=1)
# 
#     return fileinfo




# def assetInfoExport(prjDir,  objList, partType, itemType ):
# 
#     globalTakeDir = "%s/Take" %prjDir
#     localTakeDir = "%s/%s/wip/data/Take" % (prjDir, partType.lower() )
#     
#     globalCurrentTake,  globalNewTake, globalNewNum   = versionUpTakeName(globalTakeDir, "take")
#     
#     # file info
#     fileDir = cmds.file(q=1, sn=1)
#     fileName = os.path.basename(fileDir ).split('.')[0]
#     
#     localCurrentTake, localNewTake,localNuewNum   = versionUpTakeName(localTakeDir, "%s" %fileName)
# 
# 
#     # check dir
#     if not os.path.isdir(globalTakeDir):
#         os.makedirs(globalTakeDir)
# 
#     if not os.path.isdir(localTakeDir):
#         os.makedirs(localTakeDir)
# 
#         
#     # global
#     if not os.path.isfile( globalCurrentTake ):
#         take = {}
#         take["%s" %partType] = {"%s" %itemType : None}
#         take["%s" %partType]["%s" %itemType] ={}
#         
#     else:
#         with open("%s" %( globalCurrentTake ), 'r' ) as f:
#             take = json.load(f)
#             
#     if not take.get(partType):
#         take["%s" %partType] = {}
#         take["%s" %partType] = {"%s" %itemType : None}
#         take["%s" %partType]["%s" %itemType] ={}
# #     print "objectList", take["Ani"]['atom']["objectList"]
# 
#     if not take[partType].get(itemType):
#         take["%s" %partType]["%s" %itemType] ={}    
#     
#     # asset info
#     allnameSpace= list(set(cmds.ls(sns=1)[1::2]))
#     allnameSpace.remove(':')
#     take[ partType ][ itemType ].update( { "fileName" : {fileName : fileDir}} )
#     
#     #take version
# #     take= {"Ani": {"atom":None}  }
#     take[ partType ][ itemType ].update( {"version" : localNuewNum} ) 
# 
#     # user info
#     userName =  socket.gethostname()
#     take[ partType ][ itemType ].update( {'username' : userName} )
#                                               
#     cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
#     getipaddr = Popen(cmd, shell = True, stdout = PIPE)
#     ipaddr = getipaddr.communicate()[0][:-1]
#     take[ partType ][ itemType ].update( {'ipaddr' : ipaddr} )
#     
#     # frame info
#     startF = cmds.playbackOptions(min=1, q=1)
#     endF   = cmds.playbackOptions(max=1, q=1)
#     take[ partType ][ itemType ].update( { 'frame' : "%d-%d" %(startF, endF)} )
#     
#     # date info
#     nowdate = str(datetime.datetime.now())
#     date = nowdate.rsplit(":",1)[0]
#     
#     take[ partType ][ itemType ].update( {'date': date} )
#     
#      
# #     print "objectList", take["Ani"]['atom'].get("objectList") == None
#     if take[ partType ][ itemType].get("objectList") == None:
#         take[ partType ][ itemType ]["objectList"] = {}
#         take[ partType ][ itemType ]["objectList"].update( objList )
#         
#     else:        
#         take[ partType ][ itemType ]["objectList"].update(  objList ) 
#         
#     
#     # check
#     
#     if take[ partType ][ itemType ].get("objectCheck") == None:
#         take[ partType ][ itemType ]["objectCheck"] = {}
#         checkList ={}
#         map(lambda x : checkList.update( {x:1}) , objList)
#         take[ partType ][ itemType ]["objectCheck"].update( checkList )
#         
#     else:
#         checkList ={}
#         map(lambda x : checkList.update( {x:1}) , objList)
#         take[ partType ][ itemType ]["objectCheck"].update( checkList )
#         
#     take[ partType ][ itemType ]["updateList"]= objList 
#     
#     # local Take
#     if not os.path.isfile( localCurrentTake ):
#         with open("%s" %localNewTake, 'w') as f:
#             json.dump(take,  f, indent=4)        
#     else:
#         with open("%s" %( localCurrentTake ), 'r' ) as f:
#             local_take = json.load(f)
# 
#         if  not local_take.get(partType):              #not partType
#             local_take[ partType ] = take [partType]
# 
#         elif not local_take[partType].get(itemType):
#             local_take[ partType ][itemType] = take [partType][itemType]
#                     
#         else:
#             local_take[ partType ][ itemType ]["objectList"].update( take[ partType ][ itemType ]["objectList"])
#             local_take[ partType ][ itemType ]["objectCheck"].update( take[ partType ][ itemType ]["objectCheck"])
#     
#         with open("%s" %localNewTake, 'w') as f:
#             json.dump(take,  f, indent=4)
#     
# 
#     # global Take
#     with open("%s" %globalNewTake, 'w') as f:
#         json.dump(take,  f, indent=4)