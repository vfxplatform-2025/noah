'''
Created on Mar 31, 2015

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
from script import convert_byte_to_string

def projectList():
    prjList = glob.glob("/show/*")
    prj={}
    for i in prjList:
        prj[i.rsplit("/", 1)[1]] = i
    return prj

def sequence(prj):
    seqc ={} 
    seqcList = glob.glob("%s/seq/*" %prj)
    for i in seqcList:
        seqc[i.rsplit("/", 1)[1]]= i
    return seqc

def shotList(seq):
    shot ={}
    shotList = glob.glob("%s/*" %seq)
    for i in shotList:
        shot[i.rsplit("/", 1)[1]]= i
    return shot    

def camList(shot, currentType):
    camType ={}

    camDir = "%s/%s/wip/data/camera" %(shot,currentType)

    if not os.path.exists(camDir):
        os.mkdir(camDir)
	
    if not os.path.isdir(camDir):
        return 


    camList = glob.glob("%s/*.py" %camDir)
    
    for i in camList:
        camType[i.rsplit("/",1)[1]] =camList

    return camType

def dummyList(shot, currentType):
    dummyType ={}
#     typeList = glob.glob("%s/%s/wip/" %(shot,currentType))
# 
#     for i in typeList:
#         type[i.rsplit("/", 1)[1]]= i
    dummyDir = "%s/%s/wip/data/dummy" %(shot,currentType)
    
    if not os.path.isdir(dummyDir):
        return
    
    dummyList = glob.glob("%s/*.mb" %dummyDir)
    
    for i in dummyList:
        dummyType[i.rsplit("/",1)[1]] =i 

    return dummyType

def assetInfoList(shot, takeNameDir):
    if not takeNameDir:
        return

    with open( "%s" %takeNameDir, 'r') as f:
#     with open("%s" %assetInfoList[-1], 'r') as f:
        data = json.load(f)
    return data    


def assetSaveInfoList( takeNameDir, data):
    if not takeNameDir:
        return

#     assetInfoType ={}
#     assetInfoDir = "%s/Take" %(shot)
#     
#     if not os.path.isdir(assetInfoDir):
#         return
#      
#     assetInfoList = glob.glob("%s/*.json" %assetInfoDir)
#     assetInfoList.sort()
#     
#     if not assetInfoList:
#         return
    data = convert_byte_to_string.convert_byte_to_string(data)
    with open( "%s" %takeNameDir, 'w') as f:
#     with open("%s" %assetInfoList[-1], 'r') as f:
        json.dump(data, f, indent =4)


def camDirCheck(dir, type):   
    camDir =  "%s/%s/wip/data/camera" %(dir,type)
    
    if not os.path.isdir(camDir): 
        os.makedirs(camDir)
    
    
def assetDirCheck(dir):
    asstInfoDir =  "%s/Take" %(dir)
    
    if not os.path.isdir(asstInfoDir): 
        os.makedirs(asstInfoDir)    


    
def stereoCamCheck():
    camName = cmds.ls(sl=1)
    camList = []
    if len(camName) > 1:
        
        for i in camName:
            if re.search("_[LR][0-9]?[0-9]?$",i ):
                camList.append(i)
                
        if len(camName) == len(camList):
            return "stereo"
            
        else:
            return "noStereo"
    else:
        return


def isStereoCam(num, camName):
    
    if num > 1:
        
        if re.search("_[LR][0-9]?[0-9]?$",camName ):
            return "stereo"
            
        else:
            return "noStereo"
    else:
        return
    
            
def lookThroughCheck():
    lookTh=[]
    for i in cmds.ls(type = "imagePlane" ):
        if cmds.getAttr ("%s.displayOnlyIfCurrent" %i): 
            cmds.setAttr ("%s.displayOnlyIfCurrent" %i, 0)
            lookTh.append(i)
    return lookTh

def lookThroughOn(lookTh):

    for i in lookTh: 
        cmds.setAttr ("%s.displayOnlyIfCurrent" %i, 1)

# def getFileName():
#      
#     fileDir = cmds.file (q=1, exn = 1)
#     
#     fileName = fileDir.rsplit('/', 1)[1].split('.')[0]
#     fileInfo =  [fileName, fileDir]
#     
#     return  fileInfo

def camExport(dir, type):
    item ={}
    
    fileDir = cmds.file (q=1, exn = 1)
    fileName = fileDir.rsplit('/', 1)[1].split('.')[0]
    
    camName = cmds.ls(sl=1)
    
    #check 
    lookTh = lookThroughCheck()
    
    if not cmds.ls(camName, dag=1, type="camera"):
        print("cam select !")
        return 
    
    cmds.refresh(su=1)

    # startFrame, end Frame
    startF = cmds.playbackOptions(min=1, q=1)
    endF   = cmds.playbackOptions(max=1, q=1)
    
    camList = []
    constrainList = []
    imagePlanList = []
    num=0


    for i in camName:
    # copy cam
        cmds.select(i)
        copyCam = cmds.duplicate (rr=1,  un=1)
        copyCam = copyCam[0]
        
        if 1 < cmds.ls(copyCam, l=1)[0].count("|"):
            cmds.parent(copyCam, w=1)


        # nameCheck
        
        CamCheck = isStereoCam(len(camName), i)
        
        if CamCheck == "stereo":
            print("stereo !!!")
#         if re.search("_[LR][0-9][0-9]?$",copyCam ):
            subName = re.search("_[LR]",copyCam ).group()
        elif CamCheck == "noStereo":
            print("stereo Name error!!!")
            subName = "_%s" %string.uppercase[num]
            num+=1;
            
        else:
            print("single")
            subName = ""
            
        newCamName = "%s_rencam" %fileName
        renameCam = cmds.rename ( copyCam , "%s_rencam%s" %(fileName, subName ))
        camList.append(renameCam)
        
        #info - camera
        item["objectList"] = {}
        item["objectList"]["camera"] ={} 
        item["objectList"]["camera"]["list"] = camList
        
        # unlock
    #     print renameCam, '<<'
        cmds.setAttr ("%s.tx" %renameCam, lock= 0)
        cmds.setAttr ("%s.ty" %renameCam, lock= 0)
        cmds.setAttr ("%s.tz" %renameCam, lock= 0)
        cmds.setAttr ("%s.rx" %renameCam, lock= 0)
        cmds.setAttr ("%s.ry" %renameCam, lock= 0)
        cmds.setAttr ("%s.rz" %renameCam, lock= 0)
        
        #mel.eval ('CBunlockAttr "%s.tx"' %renameCam)
        #mel.eval ('CBunlockAttr "%s.rx"' %renameCam)


        # delete key
        cmds.cutKey("%s" %renameCam, at="translateX", clear=1)
        cmds.cutKey("%s" %renameCam, at="translateY", clear=1)
        cmds.cutKey("%s" %renameCam, at="translateZ", clear=1)
        cmds.cutKey("%s" %renameCam, at="rotateX",    clear=1)
        cmds.cutKey("%s" %renameCam, at="rotateY",    clear=1)
        cmds.cutKey("%s" %renameCam, at="rotateZ",    clear=1)
        
        # constrain
        constrainName = cmds.parentConstraint(i , renameCam  ,weight= 1)
        constrainList.append(constrainName[0])
         
        # set xyz
        cmds.setAttr ("%s.rotateOrder" %renameCam, 0)
        
#         # set imageplan
        camShape =cmds.ls(renameCam, dag=1, type="shape")
        if cmds.listConnections("%s" %camShape[0], t="imagePlane"):
            imagePlaneGrp = list(set(cmds.listConnections("%s" %camShape[0], t="imagePlane")))
        else:
            imagePlaneGrp=[]
        
        
        if imagePlaneGrp:   # is imagePlane ?
            imgplane=[]
            
            for imagePlane in imagePlaneGrp:
                print(imagePlaneGrp, '<<<')
                renameImagePlane = cmds.rename(imagePlane, "%s_imagePlane%s" %(fileName, subName))
                 
                imagePlanList.append(renameImagePlane)
                 
                if "->" in renameImagePlane:
                    imagePlane = renameImagePlane.split("->")[1]
                else:
                    imagePlane=renameImagePlane
                   
                imagePlaneShapeGrp = cmds.ls("%s" %imagePlane, dag=1, type="shape")
                if "->" in imagePlaneShapeGrp:
                    imagePlaneShape = renameImagePlane.split("->")[1]
                      
                else:
        #             print imagePlaneShapeGrp,"<<<<<"
                    imagePlaneShape = imagePlaneShapeGrp[0]
                       
                isCheck = cmds.getAttr ("%s.useFrameExtension" %imagePlaneShape)
                   
                cmds.setAttr ("%s.useFrameExtension" %imagePlaneShape, 2- (1+isCheck))
                cmds.setAttr ("%s.useFrameExtension" %imagePlaneShape, isCheck)
                
                imgplane.append(renameImagePlane)
                
                # info - imagePlane
                item["objectList"]["camera"]["imgaePlane"] = imgplane 

#     # bake key

    cmds.bakeResults ( camList, at =["tx", "ty","tz", "rx", "ry","rz"], simulation =True,  t =(startF-10,endF+10), sampleBy =1, disableImplicitControl = True, preserveOutsideKeys =True, sparseAnimCurveBake= False, removeBakedAttributeFromLayer =False , removeBakedAnimFromLayer =False, bakeOnOverrideLayer = False, minimizeRotation = True)

    cmds.filterCurve( camList )
    cmds.delete( constrainList )
    cmds.refresh(su=0)
    # -----------------------
    cmds.select(camList )
    cmds.file ("%s/%s/wip/data/camera/%s.mb" %(dir,type, newCamName), force=1,  options="v=0;" ,typ= "mayaBinary", pr=1, es=1 )

    item["objectList"]["camera"]["num"] = len(item ["objectList"]["camera"]["list"])
    item ["dir"] = {}
    item ["dir"][ "%s" %newCamName ] = "%s/%s/wip/data/camera" %(dir,type)

    ########## python file  #########
    saveFileDir = "%s/%s/wip/data/camera/%s" %(dir,type, newCamName)
    dataTx  = 'cam = cmds.ls(%s)\n' %camList
    dataTx += 'if cmds.ls(cam):\n'
    dataTx += '    cmds.delete( cam )\n'
    dataTx += 'cmds.file ("%s.mb",pr = 1, i=1, type ="mayaBinary",  ignoreVersion=1, mergeNamespacesOnClash=1, options ="v=0;"  )\n' %saveFileDir
    dataTx += 'cmds.currentTime(%s)\n' %(startF)
    dataTx += 'cmds.playbackOptions(min=%s, max=%s)\n' %(startF ,endF )
    if imagePlaneGrp: 
        dataTx += 'cam = cmds.ls(%s)\n' %camList
        dataTx += 'imagePlaneList = cmds.ls(%s)\n' %imagePlanList
        dataTx += 'for  i in cam:\n'
        dataTx += '    for x in imagePlaneList:\n'
        dataTx += '        renameCam = i.replace("rencam", "imagePlane")\n'
        dataTx += '        if renameCam in x:\n'        
        dataTx += '            try:\n'
        dataTx += '                cmds.parent(x , i)\n'
        dataTx += '            except:\n'
        dataTx += '                pass\n'


    f=open("%s.py" %saveFileDir, 'w')
    f.write(dataTx )
    f.close()

    if imagePlanList:
        cmds.delete(imagePlanList )
        lookThroughOn(lookTh)
    cmds.delete(camList)

#     item ={}
#     item["camera"] = camList
#     
#     if imagePlanList:
#         item["imagePlan"] = imagePlanList 
#         return item
    
    return item


def camImport(dir, type, renCamFileName):
    fileName = "%s/%s/wip/data/camera/%s" %(dir,type, renCamFileName)

    cam = renCamFileName.split(".py")[0]
    imagePlane = "%s_imagePlane" %renCamFileName.split("_rencam")[0]

    if os.path.isfile(fileName):
        if cmds.ls(cam):
            cmds.delete( cam )
        if cmds.ls(imagePlane):
            cmds.delete( imagePlane )
                     
        exec(open("%s" %fileName))

    mentalNode = cmds.ls['mentalrayGlobals', 'mentalrayItemsList']
    if mentalNode:
        cmds.delete(mentalNode)


def camOpen(dir, type):
     cmd= "nautilus %s/%s/wip/data/camera" %(dir,type)
     Popen(cmd, shell =1)
    
    
def dummyDirCheck(dir, type):  
    dummyDir =  "%s/%s/wip/data/dummy" %(dir,type)
    
    if not os.path.isdir(dummyDir): 
        os.makedirs(dummyDir)      

def dummyExport(dir, type):
    fileDir = cmds.file (q=1, exn = 1)
    fileName = fileDir.rsplit('/', 1)[1].split('.')[0]

    dirName = "%s/%s/wip/data/dummy" %(dir,type)

#     mesh = cmds.ls(sl=1)
#     if 1 < cmds.ls(mesh, l=1)[0].count("|"):
#         cmds.parent(mesh, w=1)

    cmds.file ("%s/%s_dummy.mb" %(dirName, fileName), force=1,  options="v=0;" ,typ= "mayaBinary", pr=1, es=1 )

def dummyImport(dir, type,dummyFileName):
    dummyFile =  "%s/%s/wip/data/dummy/%s" %(dir,type,dummyFileName)

    cmds.file ("%s" %dummyFile, pr = 1, i=1, type ="mayaBinary",  ignoreVersion=1, mergeNamespacesOnClash=1, options ="v=0;"  )

    mentalNode = cmds.ls['mentalrayGlobals', 'mentalrayItemsList']
    if mentalNode:
        cmds.delete(mentalNode)

def dummyOpen(dir, type):
     cmd= "nautilus %s/%s/wip/data/dummy" %(dir,type)
     Popen(cmd, shell =1)


# def atomAllLoadSet(name):
#     
#     if "atomAllLoadSet" == name:
#         cmds.select("*:output_SET",r =1, ne =1)
#         allCtrlSet = cmds.ls(sl=1)
#         cmds.select(cl=True)
# 
#     else:
#         try:
#             allCtrlSet = filter(lambda x :  ":output_SET" in x ,cmds.ls(sl=1,type="objectSet"))
#             
#         except:
#             print "set Select !"
#             return []
#         
#     return allCtrlSet

# def atomDircheck(name):
#     fileData= getFileName()
#     
#     if name == 'atom_TreeWidget':
#         atomDir = fileData[1].split("/scenes/")[0] + "/data/ani/%s" %fileData[0]
#         if not os.path.isdir(atomDir):
#             os.makedirs(atomDir)
#     
#     return fileData[0], atomDir
# 
# def atomFilecheck(name):
#     
#     if os.path.isfile("%s/%s.atom" %(name["dir"],name["name"])):
#         return True
#     
#     return False
# 
def atomKeyBake(num):
    selectObj = cmds.ls(sl=1)    
    startF = cmds.playbackOptions(min=1, q=1)
    endF   = cmds.playbackOptions(max=1, q=1)
    cmds.refresh(su=1)
     
    #cmds.bakeResults ( camList, at =["tx", "ty","tz", "rx", "ry","rz"], simulation =True,  t =(startF-10,endF+10), sampleBy =1, disableImplicitControl = True, preserveOutsideKeys =True, sparseAnimCurveBake= False, removeBakedAttributeFromLayer =False , removeBakedAnimFromLayer =False, bakeOnOverrideLayer = False, minimizeRotation = True)
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
#     
# def atomListSelect(item):
#     itemList = cmds.ls(map(lambda x : x.replace(":output_SET", ":ctrl_SET"),item))    #ctrl_set select
#     cmds.select( itemList)
# 
# 
# def atomExport( atomFileInfo):
#     fileData= getFileName()
#     
#     atom_animLayer = 0
#     startF = cmds.playbackOptions(min=1, q=1)
#     endF   = cmds.playbackOptions(max=1, q=1)
#     atom_select    = "selectedOnly"
#     filedir        = "%s" %atomFileInfo ["dir"]
#     filename       = "%s" %atomFileInfo ["name"]
#     
# #     print filedir,filename
#     
#     cmd = "precision=8"
#     cmd += ";statics=1;baked=1;sdk=0;constraint=0"
#     cmd += ";animLayers=%d" %atom_animLayer + ";selected=%s" %atom_select + ";whichRange=2;range=%d" %startF + ":%d" %endF + ";hierarchy=none"
#     cmd += ";controlPoints=0;useChannelBox=1;options=keys"
#     cmd += ";copyKeyCmd=-animation objects -time >%d" %startF + ":%d" %endF + "> -float >%d" %startF + ":%d" %endF + "> "
#     cmd += "-option keys -hierarchy none -controlPoints 0"
#     
#     cmds.file( "%s/%s" %(filedir,filename), es =1, force=1, options="%s" %cmd, typ= "atomExport")
#     cmds.select(cl=1)
# 
# 
# def atomImport (atomFileInfo):
#     
#     if atomFileInfo["atom"]:
#         atomFileDir = "%s/%s.atom" % (atomFileInfo["atom"]["fileName"].values()[0], atomFileInfo["atom"]["fileName"].values()[0].rsplit("/")[-1] )
#         atomFileMap = "%swip/data" % (atomFileInfo["atom"]["fileName"].values()[0].split("wip/data")[0] )
#         
#         
#         objList = []
#         map(lambda x : objList.extend(atomFileInfo["atom"]["objectList"][x]["list"]) ,atomFileInfo["atom"]["objectList"] )
#     
#         
#         for i in objList:
#             if not cmds.ls(i):
#                 continue
#             
#             cmds.select(i)
#             
#             for x in cmds.ls(sl=1): # ctrl curve
#                 # if key Delete Key
#                 
#                 if cmds.ls("%s.atom" %i):
#                     map(lambda z: cmds.cutKey(x, at = z),cmds.listAttr(x, k=1) )
#                                         
#                 cmds.select(x)
#                 
#                 cmd  = ";;targetTime=3;option=insert;"
#                 cmd += "match=string;;selected=selectedOnly;"
#                 cmd += "search=%s;replace=%s;prefix=;suffix=;" %( i.split(":")[0], i.split(":")[0] )
#                 cmd += "mapFile=%s;" %atomFileMap
#                  
#                 cmds.file ( "%s" %atomFileDir, i=1,  type= "atomImport", ra= True,  options = "%s" %cmd)     
#                 
#                 
#             # info write
#             
#             initAtomImportWrite ( i,  atomFileDir)


# def atomRigImport(atomFileInfo):
#     assetList =atomFileInfo['atom']['objectList']
# 
#     objList = []
#     map(lambda x : objList.extend(atomFileInfo["atom"]["objectList"][x]["list"]) ,atomFileInfo["atom"]["objectList"] )
#     
#     
#     objectList = atomFileInfo['atom']['objectList']
#     
#     for i in objectList:
#         for x in objectList[i]["list"]:    
# #             print objectList[i]["dir"], '<<'
#         
#             if cmds.ls(i):  # obj in ...
#                 continue
# 
# 
#             cmds.file ("%s" % objectList[i]["dir"], 
#                         namespace = "%s" %x.split(":")[0], 
#                         i=1,pr =1, type ="mayaBinary",  ignoreVersion=1, 
#                         ra=True,  mergeNamespacesOnClash =False, options ="v=0;"  )
#             
#             
#             
#             initRigImportWrite(  x, atomFileInfo['atom']["fileName"].values() )
            

# def initWrite( proj, item ):
#     if not cmds.ls('initialParticleSE.rigInfo'):
#         cmds.addAttr ("initialParticleSE", ln= "rigInfo",  dt= "string"  )
# 
#     if not cmds.ls('initialParticleSE.modelInfo'):
#         cmds.addAttr ("initialParticleSE", ln= "modelInfo",  dt= "string"  )
# 
#     if not cmds.ls('initialParticleSE.cameraInfo'):
#         cmds.addAttr ("initialParticleSE", ln= "cameraInfo",  dt= "string"  )
# 
#     if not cmds.ls('initialParticleSE.dummy'):
#         cmds.addAttr ("initialParticleSE", ln= "dummy",  dt= "string"  )
# 
#     # rig Data
#     objList = rigDataWrite( proj, item )
#     return objList
# 
# 
# def initAtomImportWrite( item , filename):
#     
#     if not cmds.ls('%s.atom' %item):
#         cmds.addAttr ('%s' %item, ln= "atom",  dt= "string" )
#      
#     cmds.setAttr('%s.atom' %item, "%s,%s" %( item, filename) ,type="string")
# 
# 
# def initRigImportWrite( item , filename):
#     
#     if not cmds.ls('%s.rig' %item):
#         cmds.addAttr ('%s' %item, ln= "rig",  dt= "string" )
#     cmds.setAttr('%s.rig' %item, "%s,%s" %( item, filename[0]) ,type="string")    
    


# def findRigData(proj):
#             # prop
#     propDir = map(lambda x : glob.glob("%sassets/prop/*/" %x) , glob.glob("/show/JM/"))  # jm
#     propList = []
#     map(lambda x : x is not [] and propList.extend(x) , propDir)
#     
#     propL = map(lambda x : glob.glob("%smodel/pub/*.mb" %x), propList)  #model
#     propList = []
#     map(lambda x : x is not [] and propList.extend(x) , propL)
#     
#     #env
#     envDir = map(lambda x : glob.glob("%sassets/env/*/" %x) , glob.glob("/show/JM/"))
#     envList = []
#     map(lambda x : x is not [] and envList.extend(x) , envDir)
#     
#     envL = map(lambda x : glob.glob("%smodel/pub/*.mb" %x), envList )
#     envList  = []
#     map(lambda x : x is not [] and envList .extend(x) , envL)
#     
#     #cha
#     chaDir = map(lambda x : glob.glob("%sassets/cha/*/" %x) , glob.glob("/show/JM/"))
#     chaList = []
#     map(lambda x : x is not [] and chaList.extend(x) , chaDir)
#     
#     chaL = map(lambda x : glob.glob("%smodel/pub/*.mb" %x), chaList )
#     chaList  = []
#     map(lambda x : x is not [] and chaList .extend(x) , chaL)
#     
#     #litRig
#     litRigDir = map(lambda x : glob.glob("%sassets/litRig/*/" %x) , glob.glob("/show/JM/"))
#     litRigList = []
#     map(lambda x : x is not [] and litRigList.extend(x) , litRigDir)
#     
#     litRigL = map(lambda x : glob.glob("%smodel/pub/*.mb" %x), litRigList )
#     litRigList  = []
#     map(lambda x : x is not [] and litRigList .extend(x) , litRigL)
#     
#     modelList = propList + envList + chaList + litRigList
#     modelAssetName = map(lambda x : x.rsplit('/', 1)[1].split("_")[0] , modelList )
#     
#     modelAssetGrop = dict(zip(modelAssetName , modelList ))
#     
#     
#     #===========================================================================================
#     # prop
#     propDir = map(lambda x : glob.glob("%sassets/prop/*/" %x) , glob.glob("/show/JM/"))  # jm
#     propList = []
#     map(lambda x : x is not [] and propList.extend(x) , propDir)
#     
#     propL = map(lambda x : glob.glob("%srig/pub/*.mb" %x), propList)  #model
#     propList = []
#     map(lambda x : x is not [] and propList.extend(x) , propL)
#     
#     #env
#     envDir = map(lambda x : glob.glob("%sassets/env/*/" %x) , glob.glob("/show/JM/"))
#     envList = []
#     map(lambda x : x is not [] and envList.extend(x) , envDir)
#     
#     envL = map(lambda x : glob.glob("%srig/pub/*.mb" %x), envList )
#     envList  = []
#     map(lambda x : x is not [] and envList .extend(x) , envL)
#     
#     #cha
#     chaDir = map(lambda x : glob.glob("%sassets/cha/*/" %x) , glob.glob("/show/JM/"))
#     chaList = []
#     map(lambda x : x is not [] and chaList.extend(x) , chaDir)
#     
#     chaL = map(lambda x : glob.glob("%srig/pub/*.mb" %x), chaList )
#     chaList  = []
#     map(lambda x : x is not [] and chaList .extend(x) , chaL)
#     
#     #litRig
#     litRigDir = map(lambda x : glob.glob("%sassets/litRig/*/" %x) , glob.glob("/show/JM/"))
#     litRigList = []
#     map(lambda x : x is not [] and litRigList.extend(x) , litRigDir)
#     
#     litRigL = map(lambda x : glob.glob("%srig/pub/*.mb" %x), litRigList )
#     litRigList  = []
#     map(lambda x : x is not [] and litRigList .extend(x) , litRigL)
#     
#     rigList = propList + envList + chaList + litRigList
#     rigAssetName = map(lambda x : x.rsplit('/', 1)[1].split("_")[0] , rigList )
#     
#     rigAssetGrop = dict(zip(rigAssetName, rigList ))
#     
#     
# #     for i in dictData["unitB"]["list"]:
# #         if rigAssetGrop.get('%s' %i) is not None :
# #             print rigAssetGrop.get('%s' %i)
#     
#     return rigAssetGrop, modelAssetGrop
# 
# 
# def rigDataWrite(proj, item):
#     # rigData
#     #---------------------------------------------------------------------------------------
#     #cmds.addAttr ("initialParticleSE", ln= "rigInfo",  dt= "string"  ) # {"aaa" : {num : 3 ,dir : "/core/show",  list :["aaa:bb","aaa:bb"] } }
#     
# #     allnameSpace= list( set(cmds.ls(sns=1)[1::2]) )
# #     allnameSpace.remove(':')
#     
#     allnameSpace = dict( zip(cmds.ls(item, sns=1)[1::2],cmds.ls(item, sns=1)[0::2]) )
#     
#     assetDict = {}
#     for i in allnameSpace:    
#         assetName = re.search("[a-zA-Z]+", i).group()
#         
#         
#         #print rigData[i]["list"]
#         
#         if assetName  not in assetDict :
#             assetDict[assetName]= {}
#             assetDict[assetName]["num"]= 1
#             assetDict[assetName]["list"] = [allnameSpace[i]]
#             assetDict[assetName]["namespace"] = [i]
#             continue
#     
#         assetDict[assetName]["num"]= assetDict[assetName]["num"] + 1
#         assetDict[assetName]["list"] = assetDict[assetName]["list"] + [allnameSpace[i]]
#         assetDict[assetName]["namespace"] = assetDict[assetName]["namespace"] + [i]
#         
#     # find asset Data
#     for i in  assetDict:
#         rigData, modelData = findRigData(proj) # get Object List ..
#         
# #         if rigData[i]:
#         assetDict[i]["dir"] = rigData[i]
#             
# #         else:
#         assetDict[i]["modeldir"] = modelData[i]
#             
#     
#     # str to dict
#     data = ""
#     modeldata = ""
#     for i in assetDict:
#         if not i:
#             data +=","
#             modeldata +=","
#             
#         data += "%s," %i
#         data += "%s," %assetDict[i]['num'] 
#         data += "%s," %assetDict[i]['dir']
#         
#         modeldata += "%s," %i
#         modeldata += "%s" %assetDict[i]['modeldir']
#         
#         for x in  assetDict[i]['list']:               
#             data += "%s" %x
#             if x != assetDict[i]['list'][-1]:
#                 data +=","
#     
#         data +=';'
#         modeldata += ';'
#         
#     data = data[:-1]
#     modeldata =modeldata[:-1] 
#     
#     
# #     cmds.setAttr('initialParticleSE.rigInfo',"%s" %data, type="string")
# #     cmds.setAttr('initialParticleSE.modelInfo',"%s" %modeldata, type="string")
#     #---------------------------------------------------------------------------------------
#     
#     return assetDict
# 


    
# def takeDircheck(dir):
#     takeDir = dir.split("/wip/data/")[0] + "/wip/data/Take"
#     
#     if not os.path.isdir(takeDir):
#         os.makedirs(takeDir)
#     
#     return takeDir
# 
# 
# def globaltakeDircheck(dir):
#     takeDir = dir +"/Take"
# #     print takeDir, '<<'
#     if not os.path.isdir(takeDir):
#         os.makedirs(takeDir)
#     
#     return takeDir 
    
    
# def assetInfoExport(dir, item, objList):
#     
#     takeDir = takeDircheck(dir)
#     takeList, newTake, takeName, newNum = versionUpTakeName(takeDir)
# 
# 
#     globalDir = dir.split("/wip")[0].rsplit("/",1)[0]
#     globalTakeDir = globaltakeDircheck(globalDir)
# 
# 
#     #global info
#     globalTakeList, globalNewTake, globalTakeName , globalnewNum= versionUpTakeName(globalTakeDir)
#     currentListtake = globalTakeList.keys()
# 
#     
#     globalVersion = "%s" %globalnewNum
#     localVersion  = "%s" %newNum
# 
#     #take={}
#     take= {"Ani": {"atom":None}  }
#     take["Ani"]["atom"] = {"version" : localVersion} 
#     
#     # file info
#     fileDir = cmds.file(q=1, sn=1)
#     fileName = os.path.basename(fileDir ).split('.')[0]
#     
#     # asset info
#     allnameSpace= list(set(cmds.ls(sns=1)[1::2]))
#     allnameSpace.remove(':')
# #     take["Ani"][globalVersion]["atom"].update( { "fileName" : {fileName : allnameSpace}} )
#     take["Ani"]["atom"].update( { "fileName" : {fileName : dir}} )
#     
#     # user info
#     userName =  socket.gethostname()
#     take["Ani"]["atom"].update( {'username' : userName} )
#                                               
#     cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
#     getipaddr = Popen(cmd, shell = True, stdout = PIPE)
#     ipaddr = getipaddr.communicate()[0][:-1]
#     take["Ani"]["atom"].update( {'ipaddr' : ipaddr} )
#     
#     # frame info
#     startF = cmds.playbackOptions(min=1, q=1)
#     endF   = cmds.playbackOptions(max=1, q=1)
#     take["Ani"]["atom"].update( { 'frame' : "%d-%d" %(startF, endF)} )
#     
#     # date info
#     nowdate = str(datetime.datetime.now())
#     date = nowdate.rsplit(":",1)[0]
#     take["Ani"]["atom"].update( {'date': date} ) 
#     
#     # objectList
#     take["Ani"]['atom'].update( {"objectList" : objList} )
#     
#     namesp = []
#     for i in objList:
#         namesp +=  objList[i]["namespace"]
#         
#     take["Ani"]['atom'].update( {"objectNameSpace" : namesp} )
#     
#     # check
#     take["Ani"]['atom'].update( {"check" : 1 } )
# 
#     # local Take
#     with open("%s" %newTake, 'w') as f:
#         json.dump(take,  f, indent=4)
# 
#     # global Take
#     if not glob.glob("%s/*.json" %globalTakeDir) :
#         with open("%s" %globalNewTake, 'w') as f:
#             json.dump(take,  f, indent=4)
#         return
#     
#     
#     currentTakeList =  globalTakeList.keys()
#     currentTakeList.sort()
#     currentTake = currentTakeList[-1]
#     
#     with open("%s/%s.json" %(globalTakeDir, currentTake), 'r') as f:
#         data = json.load(f)
#         
#     data["Ani"] = take["Ani"]  
#     
#     with open("%s" %globalNewTake, 'w') as f:
#         json.dump(data,  f, indent=4)

    # current Scenes Check

# def assetCamInfoExport(dir, objList):
#     
#     takeDir = takeDircheck(dir)
#     takeList, newTake, takeName, newNum = versionUpTakeName(takeDir)
#     
#     
# 
#     globalDir = dir.split("/wip")[0].rsplit("/",1)[0]
#     globalTakeDir = globaltakeDircheck(globalDir)
# 
# 
#     #global info
#     globalTakeList, globalNewTake, globalTakeName , globalnewNum= versionUpTakeName(globalTakeDir)
#     currentListtake = globalTakeList.keys()
# 
#     
#     
#     globalVersion = "%s" %globalnewNum
#     localVersion  = "%s" %newNum
#  
#     #take={}
#     take= {"Ani": {"atom":None}  }
#     take["Ani"]["atom"] = {"version" : localVersion} 
#      
#     # file info
#     fileDir = cmds.file(q=1, sn=1)
#     fileName = os.path.basename(fileDir ).split('.')[0]
#      
#     # asset info
#     allnameSpace= list(set(cmds.ls(sns=1)[1::2]))
#     allnameSpace.remove(':')
# #     take["Ani"][globalVersion]["atom"].update( { "fileName" : {fileName : allnameSpace}} )
#     take["Ani"]["atom"].update( { "fileName" : {fileName : dir}} )
#      
#     # user info
#     userName =  socket.gethostname()
#     take["Ani"]["atom"].update( {'username' : userName} )
#                                                
#     cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
#     getipaddr = Popen(cmd, shell = True, stdout = PIPE)
#     ipaddr = getipaddr.communicate()[0][:-1]
#     take["Ani"]["atom"].update( {'ipaddr' : ipaddr} )
#      
#     # frame info
#     startF = cmds.playbackOptions(min=1, q=1)
#     endF   = cmds.playbackOptions(max=1, q=1)
#     take["Ani"]["atom"].update( { 'frame' : "%d-%d" %(startF, endF)} )
#      
#     # date info
#     nowdate = str(datetime.datetime.now())
#     date = nowdate.rsplit(":",1)[0]
#     take["Ani"]["atom"].update( {'date': date} ) 
#      
#     # objectList
#     take["Ani"]['atom'].update( {"objectList" : objList} )
#      
#     namesp = []
#     for i in objList:
#         namesp +=  objList[i]["namespace"]
#          
#     take["Ani"]['atom'].update( {"objectNameSpace" : namesp} )
#      
#     # check
#     take["Ani"]['atom'].update( {"check" : 1 } )
#  
#     # local Take
#     with open("%s" %newTake, 'w') as f:
#         json.dump(take,  f, indent=4)
#  
#     # global Take
#     if not glob.glob("%s/*.json" %globalTakeDir) :
#         with open("%s" %globalNewTake, 'w') as f:
#             json.dump(take,  f, indent=4)
#         return
#      
#      
#     currentTakeList =  globalTakeList.keys()
#     currentTakeList.sort()
#     currentTake = currentTakeList[-1]
#      
#     with open("%s/%s.json" %(globalTakeDir, currentTake), 'r') as f:
#         data = json.load(f)
#          
#     data["Ani"] = take["Ani"]  
#      
#     with open("%s" %globalNewTake, 'w') as f:
#         json.dump(data,  f, indent=4)        
#     
        
# def versionUpTakeName(asstInfoDir):
#     
#     takeListDir = glob.glob("%s/*.json" %asstInfoDir)
#     takeListDir.sort()
#     takeList = {}
#     newNum ="0001"
#     
#     if takeListDir:
#         take = takeListDir[-1]
#         num  = re.search ("(?<=\.).*[0-9]{4}",take).group()
#         
#         newNum = "%04d" %( int(num) +1 )
#         newTake = take.replace(num, "%s" %newNum)
#         takeName = re.search ("(?<=\/)[a-z]+\.[0-9]{4}",take).group()
#         
#         for i in takeListDir:
#             fileName = re.search ("(?<=\/)[a-z]+\.[0-9]{4}",i).group()
#             takeList [fileName] = i 
#         
#     else:
#         takeListDir = []
#         newTake = "%s/take.0001.json" %asstInfoDir
#         takeName = "take.0001"
#         takeList[takeName]=newTake
#         
#     
#     return takeList, newTake, takeName ,newNum

 
def checkTakeName(asstInfoDir,type=""):
    
    if type:
        dir = "%s/Take/*.*.json" %asstInfoDir
#     else:
#         dir = "%s/take/*.json" %asstInfoDir
          
    takeListDir = glob.glob("%s*" %dir)
    takeListDir.sort()
    takeList = {}
      
    if takeListDir:
        currentTake=takeListDir[-1]
        takeName = re.search ("(?<=\/)[a-z]+\.[0-9]{4}",currentTake).group()
          
        for i in takeListDir:
            fileName = re.search ("(?<=\/)[a-z]+\.[0-9]{4}",i).group()
            takeList [fileName] = i
               
        return takeList, currentTake, takeName
     
#     else:
#         takeListDir = []
#         currenttake = "%s/take.0001.json" %asstInfoDir
#         takeName = "take.0001"
#         takeList[takeName]=currenttake
#     
#         print currenttake


def assetInfoOpen(dir):
    cmd =  "nautilus %s/take" %(dir)
    Popen(cmd, shell =1)

def saveInfo(opt):
    opt = convert_byte_to_string.convert_byte_to_string(opt)
    # global Take Save
    with open("/home/m83/maya/cacheExport.json", 'w') as f:
        json.dump(opt,  f, indent=4)


# def saveInfo(prj, type, seqc, shot,\
#               topFrameisHidden,atomMenuWidgetIsHidden, geoCacheMenuWidgetIsHidden, alembicMenuWidgetIsHidden, \
#               title1CheckNum,title2CheckNum,title3CheckNum, \
#               envCheckNum, assetsCheckNum, matchMoveCacheCheckNum, aniCacheCheckNum, \
#               simulCacheCheckNum, modelCacheCheckNum, renderCacheCheckNum, fxCacheCheckNum):
#     
#     cmds.refresh( su=0 )
#     
#     root = et.Element("cameraExport")
#     
#     tag = et.SubElement(root, "exportInfo")
#     tag.set( "prj",  prj)
#     tag.set( "type", type)
#     tag.set( "seqc", seqc)
#     tag.set( "shot", shot)
# 
#     tag.set( "title1Check" , "%d" %title1CheckNum ) 
#     tag.set( "title2Check", "%d" %title2CheckNum )
#     tag.set( "title3Check", "%d" %title3CheckNum )
#         
#     tag.set( "envCheck" , "%d" %envCheckNum ) 
#     tag.set( "assetsCheck", "%d" %assetsCheckNum )
#     tag.set( "matchMoveCacheCheck", "%d" %matchMoveCacheCheckNum )
#     tag.set( "modelCacheCheck", "%d" %modelCacheCheckNum )
#     
#     tag.set( "aniCacheCheck" , "%d" %aniCacheCheckNum )
#     tag.set( "simulCacheCheck" , "%d" %simulCacheCheckNum )
#     tag.set( "renderCacheCheck" , "%d" %renderCacheCheckNum )
#     tag.set( "fxCacheCheck" , "%d" %fxCacheCheckNum ) 
#    
#     tag.set( "topFrameisHidden" , "%d" %int(topFrameisHidden) )
#     
#     tag.set( "atomMenuWidgetIsHidden" , "%d" %int(atomMenuWidgetIsHidden) )
#     tag.set( "geoCacheMenuWidgetIsHidden" , "%d" %int(geoCacheMenuWidgetIsHidden) )
#     tag.set( "alembicMenuWidgetIsHidden" , "%d" %int(alembicMenuWidgetIsHidden) )
#     
#     
#     tree = et.ElementTree(root)
#     tree.write( "/home/m83/maya/camExport.xml")
    
def camDeleteItem( dir, type,  item):
    cmd= "%s/%s/wip/data/camera/%s" %(dir,type, item)
    if os.path.isfile(cmd):
        print(cmd)
        os.remove(cmd)
        mbfile =  cmd.replace(".py", ".mb")
        print(mbfile)
        os.remove(mbfile)
        
    
def dummyDeleteItem( dir, type,  item):
    cmd= "%s/%s/wip/data/dummy/%s" %(dir,type, item)
    if os.path.isfile(cmd):
        print(cmd)
        os.remove(cmd)
    
    
     
