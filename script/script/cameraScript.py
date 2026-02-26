'''
Created on Jun 8, 2015

@author: m83
'''
import re, string
import maya.cmds as cmds
import maya.mel as mel
from . import imagePlaneScript
import imp
imp.reload(imagePlaneScript)

from . import utilScript
imp.reload(utilScript)
from . import exportFilmOffset
from . import find2DPZ
from . import sg_focalLength

def cameraExport(fileName, fileDir, itemName, num, userOrigRO, itemNum=None, editedItems=None):  # dir, type
    utilScript.pluginChecks('abc')

    # check
    lookTh = lookThroughCheck()
    cmds.refresh(su=1)

    # startFrame, end Frame
    startF = cmds.playbackOptions(min=1, q=1)
    endF = cmds.playbackOptions(max=1, q=1)

    camList = []
    constrainList = []
    imagePlanList = []

    camItem = {}
    planeItem = []

    # orig cam rename
    origCamName = itemName
    itemName = cmds.rename(itemName, itemName+"_origCam")

    # copy cam
    # -----------------------------------------------------------
    cmds.select(itemName)
    copyCam = cmds.duplicate(rr=1, un=1)
    copyCam = copyCam[0]

    if 1 < cmds.ls(copyCam, l=1)[0].count("|"):
        try:
            cmds.parent(copyCam, w=1)
        except Exception:
            pass

    # nameCheck
    CamCheck = isStereoCam(itemName)

    if itemNum == None:
        print("single")
        subName = ""

    elif CamCheck == "stereo":
        print("stereo !!!")
        #         if re.search("_[LR][0-9][0-9]?$",copyCam ):
        subName = re.search("_[LR]", copyCam).group()

    elif CamCheck == "noStereo":
        print("multiple Camera!!!")
        if editedItems != None:
            subName = editedItems
        else:
            subName = "_%s" % string.uppercase[itemNum]

    #newCamName = "%s_rencam" % fileName
    newCamName = fileName

    if '_arcm_' in fileName:
        fileName = fileName.split('_arcm_')[0]

    if subName:
        renameCam = cmds.rename(copyCam, "%s_%s" % (fileName, subName))
    else:
        renameCam = cmds.rename(copyCam, fileName)
    camList.append(renameCam)
    #     print subName

    # unlock
    # print renameCam, '<<'
    cmds.setAttr("%s.translate" % renameCam, lock=0)
    cmds.setAttr("%s.translateX" % renameCam, lock=0)
    cmds.setAttr("%s.translateY" % renameCam, lock=0)
    cmds.setAttr("%s.translateZ" % renameCam, lock=0)
    cmds.setAttr("%s.rotate" % renameCam, lock=0)
    cmds.setAttr("%s.rotateX" % renameCam, lock=0)
    cmds.setAttr("%s.rotateY" % renameCam, lock=0)
    cmds.setAttr("%s.rotateZ" % renameCam, lock=0)
    cmds.setAttr("%s.scale" % renameCam, lock=0)
    cmds.setAttr("%s.scaleX" % renameCam, lock=0)
    cmds.setAttr("%s.scaleY" % renameCam, lock=0)
    cmds.setAttr("%s.scaleZ" % renameCam, lock=0)

    # translate
    # mel.eval ('CBunlockAttr "%s.tx"' %renameCam)
    # mel.eval ('CBunlockAttr "%s.rx"' %renameCam)

    # delete key
    cmds.cutKey("%s" % renameCam, at="translate", clear=1)
    cmds.cutKey("%s" % renameCam, at="translateX", clear=1)
    cmds.cutKey("%s" % renameCam, at="translateY", clear=1)
    cmds.cutKey("%s" % renameCam, at="translateZ", clear=1)
    cmds.cutKey("%s" % renameCam, at="rotate", clear=1)
    cmds.cutKey("%s" % renameCam, at="rotateX", clear=1)
    cmds.cutKey("%s" % renameCam, at="rotateY", clear=1)
    cmds.cutKey("%s" % renameCam, at="rotateZ", clear=1)
    cmds.cutKey("%s" % renameCam, at="scale", clear=1)
    cmds.cutKey("%s" % renameCam, at="scaleX", clear=1)
    cmds.cutKey("%s" % renameCam, at="scaleY", clear=1)
    cmds.cutKey("%s" % renameCam, at="scaleZ", clear=1)

    # scale set 1
    cmds.setAttr("%s.scale" % renameCam, 1, 1, 1)

    # constrain
    constrainName = cmds.parentConstraint(itemName, renameCam, weight=1)
    constrainList.append(constrainName[0])

    # set xyz
    if not userOrigRO:
        cmds.setAttr("%s.rotateOrder" % renameCam, 0)

    # set imageplan
    camShape = cmds.ls(renameCam, dag=1, type="shape")
    if cmds.listConnections("%s" % camShape[0], t="imagePlane"):
        imagePlaneGrp = list(set(cmds.listConnections("%s" % camShape[0], t="imagePlane")))
    else:
        imagePlaneGrp = []

    if imagePlaneGrp:  # is imagePlane ?
        for imagePlane in imagePlaneGrp:

            renameImagePlane = cmds.rename(imagePlane, "%s_imagePlane%s" % (fileName, subName))

            if "->" in renameImagePlane:
                imagePlane = renameImagePlane.split("->")[1]
            else:
                imagePlane = renameImagePlane

            imagePlanList.append(imagePlane)

            # plane Info
            planeItem.append(imagePlane)

            # reset imagePlane
            imagePlaneShapeGrp = cmds.ls("%s" % imagePlane, dag=1, type="shape")
            if "->" in imagePlaneShapeGrp:
                imagePlaneShape = renameImagePlane.split("->")[1]

            else:
                #             print imagePlaneShapeGrp,"<<<<<"
                imagePlaneShape = imagePlaneShapeGrp[0]
            isCheck = cmds.getAttr("%s.useFrameExtension" % imagePlaneShape)

            cmds.setAttr("%s.useFrameExtension" % imagePlaneShape, 2 - (1 + isCheck))
            cmds.setAttr("%s.useFrameExtension" % imagePlaneShape, isCheck)

    #     # bake key

    cmds.bakeResults(camList, at=["tx", "ty", "tz", "rx", "ry", "rz"], simulation=True,
                     t=(startF - num, endF + num), sampleBy=1, disableImplicitControl=True,
                     preserveOutsideKeys=True, sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False,
                     removeBakedAnimFromLayer=False, bakeOnOverrideLayer=False, minimizeRotation=True)

    cmds.filterCurve(camList)
    cmds.delete(constrainList)

    # -----------------------
    cmds.select(camList)
    #     mb
    cmds.file("%s/%s.mb" % (fileDir, renameCam), force=1, options="v=0;", typ="mayaBinary", pr=1, es=1)

    # fbx
    #     pluginCheck()
    #     cmds.file ("%s/%s.fbx" %(fileDir, renameCam), force=1,  options="v=0;" ,typ= "FBX export", pr=1, es=1 )

    # alembic
    planeName = ""
    if imagePlaneGrp:
        planeName, expressionName = imagePlaneScript.polyImagePlane(camList)
    else:
        try:
            imagePlaneN = mel.eval('createImagePlane("{}")'.format(camList[0]))
        except:
            print('imagePlaneN error go to python code')
            imagePlaneN = cmds.imagePlane(c=camList[0])
        planeName, expressionName = imagePlaneScript.polyImagePlane(camList)
    cmds.select(camList)
    mel.eval(
        'AbcExport -j "-frameRange %d %d -attr horizontalPan -attr verticalPan -attr zoom -attr horizontalFilmAperture -uvWrite -writeUVSets -eulerFilter -worldSpace -dataFormat ogawa -root %s -file %s/%s.abc" ' \
        #% ((startF - num), (endF + num), ' -root '.join(cmds.ls(sl=1, l=1)), fileDir, renameCam))
        % ((startF - num), (endF + num), ' -root '.join(cmds.ls(sl=1, l=1)), fileDir, renameCam))

    exportFilmOffset.checkOffset(itemName)
    find2DPZ.find2DPZ(itemName)
    sg_focalLength.sg_focalLength(itemName)

    if imagePlaneGrp:
        cmds.delete(planeName)
    else:
        cmds.delete(planeName)
        cmds.delete(imagePlaneN[0])

    cmds.refresh(su=0)

    ########## python file  #########
    saveFileDir = "%s/%s" % (fileDir, renameCam)
    dataTx = 'cam = cmds.ls(%s)\n' % camList
    dataTx += 'if cmds.ls(cam):\n'
    dataTx += '    cmds.delete( cam )\n'
    dataTx += 'imagePlaneList = cmds.ls(%s)\n' % imagePlanList
    dataTx += 'if cmds.ls(imagePlaneList):\n'
    dataTx += '    cmds.delete( imagePlaneList )\n'
    dataTx += 'cmds.file ("%s.mb",pr = 1, i=1, type ="mayaBinary",  ignoreVersion=1, mergeNamespacesOnClash=1, options ="v=0;"  )\n' % saveFileDir
    #     dataTx += 'mel.eval(\'AbcImport -mode import -fitTimeRange -setToStartFrame "%s.abc"\' )\n' %saveFileDir
    #     dataTx += 'cmds.currentTime(%s)\n' %(startF)
    #     dataTx += 'cmds.playbackOptions(min=%s, max=%s)\n' %(startF ,endF )
    #     dataTx += 'cmds.setAttr("defaultResolution.width" , %d)\n' %wSize
    #     dataTx += 'cmds.setAttr("defaultResolution.height", %d)\n' %hSize
    #     dataTx += 'cmds.setAttr ("vraySettings.width", %d)\n' %wSize
    #     dataTx += 'cmds.setAttr ("vraySettings.height", %d)\n' %hSize

    if imagePlaneGrp:
        dataTx += 'cam = cmds.ls(%s)\n' % camList
        dataTx += 'imagePlaneList = cmds.ls(%s)\n' % imagePlanList
        dataTx += 'for  i in cam:\n'
        dataTx += '    for x in imagePlaneList:\n'
        dataTx += '        renameCam = i.replace("rencam", "imagePlane")\n'
        dataTx += '        if renameCam in x:\n'
        dataTx += '            try:\n'
        dataTx += '                cmds.parent(x , i)\n'
        dataTx += '            except:\n'
        dataTx += '                pass\n'

    f = open("%s.py" % saveFileDir, 'w')
    f.write(dataTx)
    f.close()

    if imagePlanList:
        cmds.delete(imagePlanList)
        lookThroughOn(lookTh)
    cmds.delete(camList)

    # rename origcam
    cmds.rename(itemName, origCamName)

    # cameraInfo
    objectList = {}
    if planeItem:
        objectList.update({renameCam: ["%s/%s.py" % (fileDir, renameCam), planeItem[0]]})
    else:
        objectList.update({renameCam: ["%s/%s.py" % (fileDir, renameCam)]})

    # "carmera"    : {u'EO_054_ani_v04_w04_projectionCam_rencam': u'/show/JM/seq/EO/EO_054/ani/wip/data/camera/EO_054_ani_v04_w04_projectionCam.py'}
    # "imagePlane" : {u'EO_054_ani_v04_w04_projectionCam_rencam': u'EO_054_ani_v04_w04_projectionCam_imagePlane_B'}
    return objectList


def cameraImport(objList, type, rootType):  # itemInfo, imagePlane):
    # delete mentalray Node
    mentalNode = cmds.ls(['mentalrayGlobals', 'mentalrayItemsList'])
    if mentalNode:
        cmds.delete(mentalNode)

    # camera
    writeItemName = ""

    for i in objList:  # {u'EO_055_ani_v01_w02_test_rencam': u'/show/JM/seq/EO/EO_055/ani/wip/data/camera/EO_055_ani_v01_w02_test.py'}
        itemName = i
        itemDir = objList[i][0]
        # if "import" in type:
        #     exec (open("%s" % itemDir))
        #
        #     writeItemName = initCameraImportWrite(itemName, itemDir)
        if "import" in type:
            try:
                with open(itemDir, 'r') as file:
                    code = file.read()
                    exec (code)
            except FileNotFoundError:
                pass
            except Exception as e:
                pass

            writeItemName = initCameraImportWrite(itemName, itemDir)

        if "alembic" in type:
            utilScript.pluginChecks('abc')

            itemDirAbc = itemDir.replace(".py", ".abc")

            cmds.AbcImport("%s" % itemDirAbc, mode='import', debug=1)

            writeItemName = initCameraImportWrite(itemName, itemDir)

    return writeItemName


# write
def initCameraImportWrite(item, itemDir):

    if not cmds.ls('%s.camera' % item):
        cmds.addAttr('%s' % item, ln="camera", dt="string")

    cmds.setAttr('%s.camera' % item, "%s,%s" % (item, itemDir), type="string")

    return '%s.camera' % item


def stereoCamCheck():
    camName = cmds.ls(sl=1)
    camList = []
    if len(camName) > 1:
        for i in camName:
            if re.search("_[LR][0-9]?[0-9]?$", i):
                camList.append(i)

        if len(camName) == len(camList):
            return "stereo"

        else:
            return "noStereo"
    else:
        return

def isStereoCam(camName):
#     if num > 1:
    if re.search("_[LR]([0-9]+)?$",camName ):
        return "stereo"
    else:
        return "noStereo"
#     else:
#         return

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



#------------------------------------------------------------------------------------------------------------------------
