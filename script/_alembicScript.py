# -*- coding:utf-8 -*-
'''
Created on Jun 8, 2015
 
@author: m83
'''
  
import os, re
import configparser
import maya.cmds as cmds
import maya.mel as mel
import json
from . import utilScript
import imp
imp.reload(utilScript)
from script import convert_byte_to_string
#from cacheExport.script import itemScript
#reload(itemScript)

# jiho import Module!!!!! <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#import exportFilmOffset
#import find2DPZ

def all_ref_list():
    pattern = r"^(\w+)\d+:\1$"
    objects = cmds.ls(long=True)
    matched_objects = []

    for obj in objects:
        short_name = obj.split('|')[-1]
        if re.match(pattern, short_name):
            matched_objects.append(short_name)

    return matched_objects

def alembicAllLoadSet(lodType="Default"):
    cmds.select(cl=True)

    abcDic = {}

    # abcCache_SET, abcCache_lod_SET
    if lodType != "Default":
        cmds.ls("*:abcCache_%s_SET" % lodType) and cmds.select("*:abcCache_%s_SET" %lodType)
    else:
        alembic_all_list = all_ref_list()
        cmds.select(alembic_all_list)
        # cmds.ls("*:abcCache_SET") and cmds.select("*:abcCache_SET")

    allAbcSet = cmds.ls(sl=1)
    for i in list(set(allAbcSet)):
        abcDic[i]={"step":"1", "type":"base"}

    # abcCache_step_SET
    cmds.select(cl=True)
    cmds.ls("*:abcCache_step_SET") and cmds.select("*:abcCache_step_SET")

    allAbcStepSet = cmds.ls(sl=1)
    for i in list(set(allAbcStepSet)):
        abcDic[i] = {"step": "0.1", "type":"merge"}

    # abcCache_numberPlate_SET
    cmds.select(cl=True)
    cmds.ls('*:abcCache_numberPlate_SET') and cmds.select('*:abcCache_numberPlate_SET')

    allAbcnumberPlateSet = cmds.ls(sl=1)
    if allAbcnumberPlateSet:
        for i in list(set(allAbcnumberPlateSet)):
            abcDic[i] = {"step": "1", "type":"merge"}

    #if allAbcSet:
    if abcDic:
        cmds.select(cl=True)

    #return list(set(allAbcSet))
    return abcDic

def alembicCurveLoadSet():
    cmds.select(cl=True)

    abcDic = {}

    if cmds.ls("*:abcHairCache_SET"):
        cmds.select("*:abcHairCache_SET")
        allAbcSet = cmds.ls(sl=1)

        for i in list(set(allAbcSet)):
            abcDic[i] = {"step": "1", "type":"base"}

        print(">>>", allAbcSet)
        #if allAbcSet:
        if abcDic:
            cmds.select(cl=True)

        #return list(set(allAbcSet))
        return abcDic

def alembicLoadMesh():
    abcDic = {}
    for i in cmds.ls(sl=1):
        abcDic[i] = {"step": "1", "type":"base"}

    #return cmds.ls(sl=1)
    print('abcDic >>>>>>>>>>>>>>> : ', abcDic)
    return abcDic

def alembicSceneSetLoad():
    cmds.select(cl=True)

    abcDic = {}

    # abcCache_SET, abcCache_lod_SET
    #cmds.ls("*:scene_SET") and cmds.select("*:scene_SET")

    #allAbcSet = cmds.ls(sl=1)
    #for i in list(set(allAbcSet)):
    for i in cmds.ls("*:scene_SET"):
        cmds.select(i)
        setGrp = cmds.ls(sl=1)[0]
        cmds.select(i.split(":")[0]+":abcCache_SET")
        setAbcGrp = cmds.ls(sl=1)[0]
        refName = cmds.referenceQuery( setGrp, referenceNode=True )
        abcDic[i]={"step":"1", "type":"scene,{},{}".format(refName,setAbcGrp)}

    if abcDic:
        cmds.select(cl=True)

    return abcDic


def scale_checker(item):
    if cmds.referenceQuery(item, isNodeReferenced=True):
        current_item = item
        last_reference_item = None
        while True:
            parents = cmds.listRelatives(current_item, parent=True)
            if not parents:
                top_group = last_reference_item if last_reference_item else current_item
                break

            if cmds.referenceQuery(parents[0], isNodeReferenced=True):
                last_reference_item = parents[0]

            current_item = parents[0]

        child_list = cmds.listRelatives(top_group, children=True) or []
        for z in child_list:
            if any('rig_grp' in item for item in child_list):
                if cmds.ls(z.split(':')[0] + ':main_*_con'):
                    con_list = cmds.ls(z.split(':')[0] + ':main_*_con')
                    for k in con_list:
                        scaleX = round(cmds.getAttr(k + '.scaleX'), 3)
                        scaleY = round(cmds.getAttr(k + '.scaleY'), 3)
                        scaleZ = round(cmds.getAttr(k + '.scaleZ'), 3)
                        if 1.0 != scaleX and 1.0 != scaleY and 1.0 != scaleZ:
                            if scaleX == scaleY == scaleZ:
                                return scaleX
                            else:
                                print('Each scale XYZ has a different size.')
                                exit()
                        elif 1.0 == scaleX and 1.0 == scaleY and 1.0 == scaleZ:
                            return scaleX
                else:
                    descendants = cmds.listRelatives(item, allDescendents=True, fullPath=True) or []
                    non_uniform_scales = set()
                    for child in descendants:
                        if cmds.nodeType(child) == 'transform':
                            scaleX = round(cmds.getAttr(child + '.scaleX'), 3)
                            scaleY = round(cmds.getAttr(child + '.scaleY'), 3)
                            scaleZ = round(cmds.getAttr(child + '.scaleZ'), 3)

                            if scaleX == scaleY == scaleZ != 1:
                                non_uniform_scales.add(scaleX)
                            if len(non_uniform_scales) > 1:
                                return None

                    return non_uniform_scales.pop() if non_uniform_scales else 1
            else:
                descendants = cmds.listRelatives(item, allDescendents=True, fullPath=True) or []
                non_uniform_scales = set()
                for child in descendants:
                    if cmds.nodeType(child) == 'transform':
                        scaleX = round(cmds.getAttr(child + '.scaleX'), 3)
                        scaleY = round(cmds.getAttr(child + '.scaleY'), 3)
                        scaleZ = round(cmds.getAttr(child + '.scaleZ'), 3)

                        if scaleX == scaleY == scaleZ != 1:
                            non_uniform_scales.add(scaleX)
                        if len(non_uniform_scales) > 1:
                            return None

                return non_uniform_scales.pop() if non_uniform_scales else 1
    else:
        descendants = cmds.listRelatives(item, allDescendents=True, fullPath=True) or []
        non_uniform_scales = set()
        for child in descendants:
            if cmds.nodeType(child) == 'transform':
                scaleX = round(cmds.getAttr(child + '.scaleX'), 3)
                scaleY = round(cmds.getAttr(child + '.scaleY'), 3)
                scaleZ = round(cmds.getAttr(child + '.scaleZ'), 3)

                if scaleX == scaleY == scaleZ != 1:
                    non_uniform_scales.add(scaleX)
                if len(non_uniform_scales) > 1:
                    return None

        return non_uniform_scales.pop() if non_uniform_scales else 1

def alembicExport( fileList , itemdir,  item, num, step_num, frameType="FrameRange", typeV="", hiddenV=[]):
    utilScript.pluginChecks('abc')
    print(">>>> alembic option <<<", fileList, itemdir, item, num, step_num, frameType, typeV, hiddenV)
    # get config
    abcConfig = configparser.ConfigParser()
    abcConfigFile = os.path.abspath(__file__ + "/../../config/alembicOption.ini")
    abcConfig.read(abcConfigFile)

    abcAttrOptList = abcConfig.get("attr", "ALL").split(",")
    abcAttrOpt = "-attr {}".format(" -attr ".join(abcAttrOptList))

    # ToDo : get namespace

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

    scale = scale_checker(item)
    if scale == None:
        scale = 1.0
    else:
        pass

    if ":" in item:
        assetName = re.search("[\w]*[\D](?=([\d]+)?:)", item).group()

        if "out_cur_Grp" in item:
            itemName = item.split(":")[0]  # org
            assetName = item.split(":")[1]  # org

        else:
            if not "geo_Grp" in item:
                assetName = item.split(":")[1]  # org
            itemName = item.split(":")[0] # asset name
        fileName = item.replace(":", "_")
        itemNewDir = "%s/%s" % (itemdir, itemName )
        fileinfo[ "%s:%s" %(itemName,assetName) ] = "%s/%s_scale%s.abc" %(itemNewDir,  fileName, str(scale))

    else:
        assetName = item
        itemName = item
        fileName = item
        itemNewDir = "%s/%s" % (itemdir, itemName )
        fileinfo[ "%s" %itemName ] = "%s/%s_scale%s.abc" %(itemNewDir, fileName, str(scale))
        if "_crowd_Grp" in item:
            itemName = item

            selected_chrs = cmds.listRelatives(item, type='transform', c=True)
            namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)

            all_chr_namespace = [chr.split(':')[0] for chr in selected_chrs if chr.split(':')[0] in namespaces]
            namespace_dic = {'namespace': all_chr_namespace}
            if not os.path.exists(itemNewDir):
                os.mkdir(itemNewDir)

            namespace_dic = convert_byte_to_string.convert_byte_to_string(namespace_dic)
            with open("{}/{}_scale{}.json".format(itemNewDir, fileName, str(scale)), 'w') as namespace_data:
                json.dump(namespace_dic, namespace_data, indent=4)

    if os.path.isfile( "%s/%s_scale%s.abc" %(itemNewDir, fileName,str(scale)) ):
        print("delete %s/%s_scale%s.abc" %(itemNewDir, fileName, str(scale)))
        os.system("rm -rf %s/%s_scale%s.abc" %(itemNewDir, fileName, str(scale)) )

    if not os.path.isdir( itemNewDir ):
        os.mkdir( itemNewDir )
    if typeV == "mergeObjectSpace":
        print("aaaaa")
        mel.eval(
            'AbcExport -j "-frameRange %d %d -attr horizontalPan -attr verticalPan -attr zoom -attr horizontalFilmAperture -uvWrite -writeUVSets -eulerFilter -writeVisibility -step %s %s -dataFormat ogawa -root %s -file %s/%s_scale%s.abc" ' \
            % (startF, endF, step_num, abcAttrOpt, cmds.ls(item.replace("_mergeObjectSpace", ""), l=1)[0], itemNewDir, fileName, str(scale)))

        # >>>>>>>>>>>>>>>>>>>>>> jiho Editing!!!!!!! <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        #exportFilmOffset.checkOffset(item)

    elif typeV == "mergeWorldSpace":
        print("bbbbb")
        mel.eval(
            'AbcExport -j "-frameRange %d %d -attr horizontalPan -attr verticalPan -attr zoom -attr horizontalFilmAperture -uvWrite -writeUVSets -eulerFilter -writeVisibility -step %s %s -worldSpace -dataFormat ogawa -root %s -file %s/%s_scale%s.abc" ' \
            % (startF, endF, step_num, abcAttrOpt, cmds.ls(item.replace("_mergeWorldSpace", ""), l=1)[0], itemNewDir, fileName, str(scale)))

        # >>>>>>>>>>>>>>>>>>>>>> jiho Editing!!!!!!! <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        #exportFilmOffset.checkOffset(item)

    else:
        print("cccc")
        if hiddenV:
            cmds.hide(hiddenV)
        mel.eval(
            'AbcExport -j "-frameRange %d %d -attr horizontalPan -attr verticalPan -attr zoom -attr horizontalFilmAperture -uvWrite -writeUVSets -eulerFilter -writeVisibility -step %s %s -worldSpace -dataFormat ogawa -root %s -file %s/%s_scale%s.abc" ' \
                  %( startF, endF, step_num, abcAttrOpt, cmds.ls(item, l=1)[0], itemNewDir,fileName, str(scale)) )

        # >>>>>>>>>>>>>>>>>>>>>> jiho Editing!!!!!!! <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        #exportFilmOffset.checkOffset(item)

        print('AbcExport -j "-frameRange %d %d -attr horizontalPan -attr verticalPan -attr zoom -attr horizontalFilmAperture -uvWrite -writeUVSets -eulerFilter -writeVisibility -step %s %s -worldSpace -dataFormat ogawa -root %s -file %s/%s_scale%s.abc" ' \
        % (startF, endF, step_num, abcAttrOpt, cmds.ls(item, l=1)[0], itemNewDir, fileName, str(scale)))
        if hiddenV:
            cmds.showHidden(hiddenV)

    # >>>>>>>>>>>>>>>>>>>>>> jiho Editing!!!!!!! <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #find2DPZ.find2DPZ(item)

    cmds.select(cl=1)
    cmds.refresh(su=0)
    return fileinfo
    

# import
def alembicImport(itemInfo, type, rootType, itemNum=None, lod="None"):
    print("========= Alembic Import : Strat ============")

    baseItemList = []
    mergeObjectSpaceItemList = []
    mergeWorldSpaceItemList = []

    for i in itemInfo:
        if "_mergeObjectSpace" in i:
            mergeObjectSpaceItemList.append(i)
        elif "_mergeWorldSpace" in i:
            mergeWorldSpaceItemList.append(i)
        else:
            baseItemList.append(i)
    # basetItem,mergeObjectSpaceItem import / mergeWorldSpaceItem not import.
    writeItemName = ""
    for baseItem in baseItemList:
        writeItemName = alembicImportFile(baseItem, itemInfo[baseItem], rootType, type, lod)
    for mergeObjectSpaceItem in mergeObjectSpaceItemList:
        writeItemName = alembicImportFile(mergeObjectSpaceItem, itemInfo[mergeObjectSpaceItem], rootType, type, lod)

    print("========= Alembic Import : Done ============")

    #for i in itemInfo:
    #    writeItemName = alembicImportFile(i, itemInfo[i], rootType, type)

    return writeItemName

def alembicImportByJson(takeJsonPath, type, rootType='alembicFarm', itemNum=None, lod="None"):
    print("========= Alembic Import : Strat ============")

    baseItemList = []
    mergeObjectSpaceItemList = []
    mergeWorldSpaceItemList = []

    with open("%s" %( takeJsonPath ), 'r' ) as f:
        takeInfo = json.load(f)

    itemInfo = {}
    for takeRoot in takeInfo:
        itemInfo = takeInfo[takeRoot]["objectList"]
        frameRangeKey = list(takeInfo[takeRoot]["frame"].keys())[0]
        frameRange = takeInfo[takeRoot]["frame"][frameRangeKey].split("-")

        cmds.playbackOptions(min=frameRange[0], max=frameRange[1])
        cmds.playbackOptions(ast=frameRange[0], aet=frameRange[1])
        cmds.currentTime(frameRange[0])

        for i in itemInfo:
            if "_mergeObjectSpace" in i:
                mergeObjectSpaceItemList.append(i)
            elif "_mergeWorldSpace" in i:
                mergeWorldSpaceItemList.append(i)
            else:
                baseItemList.append(i)
        # basetItem,mergeObjectSpaceItem import / mergeWorldSpaceItem not import.
        writeItemName = ""
        for baseItem in baseItemList:
            writeItemName = alembicImportFile(baseItem, itemInfo[baseItem], rootType, type, lod)
        for mergeObjectSpaceItem in mergeObjectSpaceItemList:
            writeItemName = alembicImportFile(mergeObjectSpaceItem, itemInfo[mergeObjectSpaceItem], rootType, type, lod)

        print("----- Alembic Import : {} -----".format(i))

    print("========= Alembic Import : Done ============")

    #for i in itemInfo:
    #    writeItemName = alembicImportFile(i, itemInfo[i], rootType, type)


def alembicImportFile(item, itemDir, rootType, type, lod="None"):

    print("LOD:{}, Type:{}, Item:{}".format(lod, type, item))

    if lod != "None":
        itemDir = itemDir.replace("_geo_Grp", "_{}_geo_Grp".format(lod))

    if not os.path.isfile(itemDir):
        print("Not File !! : {}".format(itemDir))
        return

    print("File : {}".format(itemDir))

    if not cmds.pluginInfo("AbcExport.so", q=1, loaded=1):
        cmds.loadPlugin("AbcExport.so")
    if not cmds.pluginInfo("AbcImport.so", q=1, loaded=1):
        cmds.loadPlugin("AbcImport.so")


    if type == "alembic":  # cherryBranch9_cherryBranch.abc
        utilScript.nameSpaceCheck(item)
        print("ImportType : alembic")

        if "_crowd_Grp" in item:
            # get namespace from json file
            json_file = "{}.json".format(os.path.splitext(itemDir)[0])
            if os.path.exists(json_file):
                with open(json_file) as jsons:
                    namespace_list = json.load(jsons)['namespace']
                for namespace in namespace_list:
                    if not cmds.namespace(exists=namespace):
                        cmds.namespace(add=namespace)
                cmds.AbcImport("%s" % itemDir, mode='import', debug=1)

            else:
                pass

        elif "_mergeObjectSpace" not in item:
            if ":" in item:
                returnList = cmds.file("%s" % itemDir, namespace="%s" % item.split(":")[0], i=1, pr=1, ra=True,
                                       mergeNamespacesOnClash=False, type="Alembic", rnn=1)
                # print ">" * 10, returnList
            else:
                returnList = cmds.file("%s" % itemDir, i=True, type="Alembic", ignoreVersion=True,
                                       mergeNamespacesOnClash=0,
                                       options="v=0", pr=True, loadReferenceDepth="all", returnNewNodes=1)
                # print ">" * 10, returnList
            topGroup = [x for x in returnList if x.count("|") == 1]
            tranName = topGroup[0].split("|")[1]

            # rename
            try:
                if ("_geo_Grp" not in tranName) and ("_geo_grp" not in tranName) and not cmds.listRelatives(tranName, p=1,
                                                                                                            type="mesh"):  # if group rename and
                    print("rename({}, {})".format(tranName, item))
                    tranName = cmds.rename(tranName, item)

                elif "_geo_Grp" in tranName or "_geo_grp" in tranName:
                    print("okok")
                    cmds.group(":%s" % tranName, n=item)
            except:
                print("ValueError : More than one object match name")

            print("Base alembic : {}".format(item))
        else: # _mergeObjectSpace
            mergeItem = item.replace("_mergeObjectSpace", "")

            if cmds.objExists(mergeItem):
                cmds.AbcImport("%s" % itemDir, mode='import', debug=1, connect=mergeItem)
                cmds.showHidden(mergeItem)
                print("Merge alembic ObjectSpace: {}".format(mergeItem))
            elif cmds.objExists(mergeItem.split(":")[-1]):
                cmds.AbcImport("%s" % itemDir, mode='import', debug=1, connect=mergeItem.split(":")[-1])
                cmds.showHidden(mergeItem.split(":")[-1])
                print("Merge alembic ObjectSpace: {}".format(mergeItem.split(":")[-1]))
            else:
                print("Merge alembic ObjectSpace Error : {}".format(mergeItem))


    elif type == "gpu":
        gpuNodeName = cmds.createNode("gpuCache", n="%s_gpuCache" % item)
        gpuTransName = cmds.listRelatives(gpuNodeName, p=1)[0]
        cmds.rename(gpuTransName, "%s_gpu" % item)
        cmds.setAttr("%s.cacheFileName" % gpuNodeName, itemDir, type="string")

    elif type == "import":
        if cmds.ls("%s:abcCache_SET" % item):
            item_cacheSetGrp_name = "%s:%s" % (item, item)
            cmds.select(item_cacheSetGrp_name)
            cmds.AbcImport("%s" % itemDir, reparent="%s" % item_cacheSetGrp_name, mode='import')

        else:
            cmds.AbcImport("%s" % itemDir, mode='import', debug=1, connect="/")  # , removeIfNoUpdate=1)

    else:  # proxy
        utilScript.nameSpaceCheck(item)
        # pluginCheck()
        utilScript.pluginChecks('vray')

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

    writeItemName = ""
    # info write
    if "alembicAni" == rootType:
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicAni")

    if "alembicCrowdSim" == rootType:
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicCrowdSim")

    if "alembicCrowdAni" == rootType:
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicCrowdAni")

    elif "alembicModel" == rootType:
        print("alembicModel")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicModel")

    elif "alembicRender" == rootType:
        print("alembicRender")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicRender")

    elif "alembicFur" == rootType:
        print("alembicFur")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicFur")

    elif "alembicFurSim" == rootType:
        print("alembicFurSim")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicFurSim")

    elif "alembicFinalize" == rootType:
        print("alembicFinalize")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicFinalize")

    elif "alembicMusle" == rootType:
        print("alembicMusle")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicMusle")

    elif "alembicCloth" == rootType:
        print("alembicCloth")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicCloth")

    elif "alembicSimul" == rootType:
        print("alembicSimul")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicSimul")

    elif "alembicMm" == rootType:
        print("alembicMm")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicMm")

    elif "alembicLayout" == rootType:
        print("alembicLayout")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicLayout")

    elif "alembicFx" == rootType:
        print("alembicFx")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicFx")

    elif "alembicHair" == rootType:
        print("alembicHair")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicHair")

    elif "alembicHairSim" == rootType:
        print("alembicHairSim")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicHairSim")

    elif "alembicClothSim" == rootType:
        print("alembicClothSim")
        writeItemName = initAlembicImportWrite(item, itemDir, "alembicClothSim")

    cmds.select(cl=1)

    return writeItemName


# write
def initAlembicImportWrite(item, filename, itemType):
    if cmds.ls('%s.%s' % (item, itemType)):
        cmds.deleteAttr("%s.%s" % (item, itemType))

    #     print ">>>", item, itemType
    if cmds.ls(item) and not cmds.ls('%s.%s' % (item, itemType)):
        cmds.addAttr('%s' % item, ln="%s" % itemType, dt="string")

    if cmds.ls(item):
        cmds.setAttr('%s.%s' % (item, itemType), "%s,%s" % (item, filename), type="string")  # item !!

    return '%s.%s' % (item, itemType)

