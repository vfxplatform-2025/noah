import os, re, glob, json, configparser, socket, datetime
from subprocess import *
import sys
import imp
sys.path.append(os.path.abspath(__file__+'/../..'))
from cacheExport_module.app_moduleImport import *
import script.utilScript as utilScript
imp.reload(utilScript)
from script import convert_byte_to_string

def takeExport(objList, fileType="", rigList={}, spoolType="local", frameType="FrameRange", versionUp=True, instanceInfo={}, fileDirV="", startFrame=None, endFrame=None, userName=None):
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = utilScript.getFileList(fileDirV)
    globalCurrentTake, globalNewTake, globalNewNum = versionUpTakeName(globalTakeDir, "take", versionUp)
    localCurrentTake, localNewTake, localNewNum = versionUpTakeName(localTakeDir, fileName, versionUp)
    typeConfig = configparser.ConfigParser()
    typeConfigFile = os.path.abspath(__file__ + "/../../config/typeConfig.ini")
    typeConfig.read(typeConfigFile)

    try:
        itemType = typeConfig.get(fileType, partType)
    except:
        itemType = fileType

    take, local_take = checkTake(itemType, spoolType, fileDirV=fileDirV)

    fileNameDict = {}
    versionDict = {}
    userNameDict = {}
    ipaddrDict = {}
    frameDict = {}
    dateDict = {}
    objectListDict = {}
    objectCheckDict = {}
    updateListDict = {}
    globalversionDict = {}
    rigObjectList = {}
    # ToDo : get namespace
    namespaceDict = {}
    instanceDict = {}

    for item in objList:
        # file Name

        if fileType == "rig":
            #if not cmds.ls(item):
            #    return
            assetName = item.split(":")[1]

            if type(rigList) == type({}):
                fileDir = rigList.get(assetName)
                if fileDir == None:
                    continue
                fileNameDict.update({item: fileDir})
                rigObjectList.update({item: fileDir})
            else:
                rigObjectList = objList
        else:
            fileNameDict.update({item: fileDir})


        # take local version
        versionDict.update({item: localNewNum})
        globalversionDict.update({item: globalNewNum})

        # user info
        if userName is None:
            userName = socket.gethostname()

        userNameDict.update({item: userName})

        # ipaddr
        ipaddr = ""
        try:
            cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
            getipaddr = Popen(cmd, shell=True, stdout=PIPE)
            ipaddr = getipaddr.communicate()[0][:-1]
        except:
            ipaddr = ""
        ipaddrDict.update({item: ipaddr})

        # frame info
        if frameType == "FrameRange" :
            if fileType == "frameRange":
                startF = cmds.playbackOptions(ast=1, q=1)
                endF = cmds.playbackOptions(aet=1, q=1)
            else:
                startF = cmds.playbackOptions(min=1, q=1)
                endF = cmds.playbackOptions(max=1, q=1)
        if frameType == "CurrentFrame" :
            startF = cmds.currentTime(q=1)
            endF   = cmds.currentTime(q=1)

        if frameType == "setFrame":
            startF = startFrame
            endF = endFrame

        frameDict.update({item: "%d-%d" % (startF, endF)})

        # date info
        nowdate = str(datetime.datetime.now())
        date = nowdate.rsplit(":", 1)[0]
        dateDict.update({item: date})

        # object List info
        if fileType == "camera":
            objectListDict.update({item: objList})
        elif fileType == "rig":
            objectListDict.update({item: None})
        else:
            objectListDict.update({item: objList[item]})

        # object check info
        checkList = {"model": 1, "rig": 1, "ani": 1, "matchmove": 1, "layout": 1, "dyn": 1, "cloth": 1, "hair": 1, "hairSim":1,
                     "clothSim": 1, "lit": 1, "furSim":1, "fur": 1, "lookdev": 1, "fx": 1}
        objectCheckDict.update({item: checkList})

        # update List info
        if fileType == "camera":
            updateListDict.update({item: objList})
        elif fileType == "rig":
            updateListDict.update({item: None})
        else:
            updateListDict.update({item: objList[item]})

        instanceDict.update({item:instanceInfo})

    if fileType == "rig":
        objList = rigObjectList

    if take[itemType].get('objectList'):  # is itemType
        newTake, justTake = takeSetInfo(take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict, frameDict,
                              dateDict, objList, objectCheckDict, namespaceDict, instanceDict)
    else:
        newTake, justTake = takeSetInfo(take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict, frameDict,
                              dateDict, objList, objectCheckDict, namespaceDict, instanceDict)

    if local_take[itemType].get('objectList'):  # is itemType
        local_Newtake, local_JustTake = takeSetInfo(local_take, itemType, True, fileNameDict, versionDict, userNameDict, ipaddrDict,
                                    frameDict, dateDict, objList, objectCheckDict, namespaceDict, instanceDict)
    else:
        local_Newtake, local_JustTake = takeSetInfo(local_take, itemType, False, fileNameDict, versionDict, userNameDict, ipaddrDict,
                                    frameDict, dateDict, objList, objectCheckDict, namespaceDict, instanceDict)

    # --------------------------------------------------------

    take = newTake
    local_take = local_Newtake

    take[itemType]["updateList"] = updateListDict
    local_take[itemType]["updateList"] = updateListDict

    if spoolType == "local":
        saveTake( itemType, take, justTake, local_take, versionUp=versionUp, fileDirV=fileDirV)
    if spoolType == "farm":
        saveTakeFarm(itemType, take, local_take, versionUp=versionUp)

def takeAddExport(shotDirItem, attrDir, attrType="model"):
    if not attrDir:
        return

    for i in attrDir:
        if "/seq/" in attrDir[i]:
            return
        assetDir = re.search(".+(?=/[\w]+/pub/)", attrDir[i]).group()
        globalTakeList = "%s/Take/takeList.json" % assetDir

        if not os.path.isdir("%s/Take" % assetDir):
            os.mkdir("%s/Take" % assetDir)

        if not os.path.isfile(globalTakeList):
            takelist = {}
            takelist[attrType] = {}
        else:
            with open("%s" % (globalTakeList), 'r') as f:
                takelist = json.load(f)

        if not takelist.get(attrType):
            takelist[attrType] = {}

        takelist[attrType].update(shotDirItem)

    # global Take
    with open("%s" % globalTakeList, 'w') as f:
        takelist = convert_byte_to_string.convert_byte_to_string(takelist)
        json.dump(takelist, f, indent=4)


def takeInfoList(shot, takeNameDir):
    if not takeNameDir:
        return
    with open("%s" % takeNameDir, 'r') as f:
        data = json.load(f)
    return data

def assetInfoList(shot, takeNameDir):
    if not takeNameDir:
        return

    with open( "%s" %takeNameDir, 'r') as f:
#     with open("%s" %assetInfoList[-1], 'r') as f:
        data = json.load(f)
    return data

def deleteAssetSaveInfoList( takeNameDir, data):
    if not takeNameDir:
        return

    with open( "%s" %takeNameDir, 'w') as f:
        data = convert_byte_to_string.convert_byte_to_string(data)
        json.dump(data, f, indent =4)

def versionUpTakeName(asstInfoDir, fileName, versionUp=True):
    takeListDir = glob.glob("%s/%s.*.json" % (asstInfoDir, fileName))
    takeListDir.sort()
    takeList = {}
    newNum = "0001"

    newTake=""
    if takeListDir:
        currentTake = takeListDir[-1]

        if versionUp:
            currentNum = re.search("(?<=\.).*[0-9]{4}", currentTake).group()
            newNum = "%04d" % (int(currentNum) + 1)
            newTake = currentTake.replace("." + currentNum + ".", ".%s." % newNum)
        else:
            newTake = currentTake

        takeName = re.search("[\w]+.[0-9]{4}.json*$", currentTake).group()

    else:
        newTake = "%s/%s.0001.json" % (asstInfoDir, fileName)
        currentTake = "%s/%s.0001.json" % (asstInfoDir, fileName)
        takeName = "%s.0001" % fileName
        currentNum = "0001"

    return currentTake, newTake, takeName

def changeSaveTake(newTakeDir, take):
    # global Take Save
    with open("%s" %newTakeDir, 'w') as f:
        take = convert_byte_to_string.convert_byte_to_string(take)
        json.dump(take,  f, indent=4)

def checkTakeName(asstInfoDir, type=""):

    #if type:
    dir = "%s/Take/take.*.json" % asstInfoDir
    dir2 = "%s/Take/take_just.*.json" % asstInfoDir

    takeListDir = glob.glob("%s*" % dir)
    takeListDir.sort()
    takeList = {}

    justTakeListDir = glob.glob("%s*" % dir2)
    justTakeListDir.sort()
    justTakeList = {}

    currentTake = ""

    if takeListDir:
        currentTake = takeListDir[-1]
        takeName = re.search("(?<=\/)[a-z]+\.[0-9]{4}", currentTake).group()

        for i in takeListDir:
            fileName = re.search("(?<=\/)[a-z]+\.[0-9]{4}", i).group()
            takeList[fileName] = i

    if justTakeListDir:
        for i in justTakeListDir:
            fileName = re.search("(?<=\/)[a-z]+_[a-z]+\.[0-9]{4}", i).group()
            justTakeList[fileName] = i

    return takeList, justTakeList, currentTake, takeName

def checkTake(itemType, spoolType, versionUp=True, fileDirV=""):
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = utilScript.getFileList(fileDirV)
    globalCurrentTake, globalNewTake, globalNewNum = versionUpTakeName(globalTakeDir, "take", versionUp)
    localCurrentTake, localNewTake, localNewNum = versionUpTakeName(localTakeDir, "%s" % fileName, versionUp)
    globalTakeFarmDir = globalTakeDir.replace("/Take", "/Take/farm")
    localTakeFarmDir = localTakeDir.replace("/Take", "/Take/farm")


    # check dir
    if not os.path.isdir(globalTakeDir):
        os.makedirs(globalTakeDir)

    if not os.path.isdir(localTakeDir):
        os.makedirs(localTakeDir)

    if not os.path.isdir(globalTakeFarmDir):
        os.makedirs(globalTakeFarmDir)

    if not os.path.isdir(localTakeFarmDir):
        os.makedirs(localTakeFarmDir)

    # global Take
    if not os.path.isfile(globalCurrentTake):
        take = {}
    elif spoolType == "farm":
        globalNewTakeFarm = globalNewTake.replace("/Take/", "/Take/farm/")
        # globalNewTakeFarm : /show/ZZ/seq/TST/TST_0020/Take/fram/take.0001.json

        if itemType == 'rig':
            print(("checkTake farm load: {}".format(globalNewTakeFarm)))
            with open(globalNewTakeFarm, 'r') as f:
                take = json.load(f)
        else:
            print(("checkTake farm create: {}".format(globalNewTakeFarm)))
            take = {}
        #take = {}
    else:
        with open(globalCurrentTake, 'r') as f:
            take = json.load(f)

    if not take.get(itemType):
        take[itemType] = {}

    # local Take
    if not os.path.isfile(localCurrentTake):
        local_take = {}
    elif spoolType == "farm":
        local_take = {}
    else:
        with open(localCurrentTake, 'r') as f:
            local_take = json.load(f)

    if not local_take.get(itemType):
        local_take["%s" % itemType] = {}

    return take, local_take


def takeUpdateCheck(objList, rootType, shotDir):
    takeListDir = glob.glob("%s/Take/take.*.json" % shotDir)
    takeListDir.sort()
    takeDir = takeListDir[-1]
    fileDir = cmds.file(q=1, sn=1)
    if not fileDir:
        return

    partType = fileDir.split("/")[6]

    for i in objList:
        # open
        with open("%s" % takeDir, 'r') as f:
            take = json.load(f)

        #         take[rootType]["updateList"][i][partType]
        if take[rootType]["objectCheck"].get(i) == None:
            continue
        # save
        if take[rootType]["objectCheck"][i].get(partType):
            take[rootType]["objectCheck"][i][partType] = 0
            with open("%s" % takeDir, 'w') as f:
                take = convert_byte_to_string.convert_byte_to_string(take)
                json.dump(take, f, indent=4)


def takeSetInfo(take, itemType, type, fileNameDict, versionDict, userNameDict, ipaddrDict, frameDict, dateDict, objList, objectCheckDict, namespaceDict={}, instanceDict={}):
    infoDic = {
        "fileName":fileNameDict ,
        "version":versionDict,
        "username":userNameDict,
        "ipaddr":ipaddrDict,
        "frame":frameDict,
        "date":dateDict,
        "objectList":objList,
        "objectCheck":objectCheckDict,
        "namespace":namespaceDict,
        "instance": instanceDict
    }
    justTake = {itemType: {}}

    keyList = list(take[ itemType ].keys())
    for keyV, itemV in list(infoDic.items()):
        if keyV in keyList:
            if type == True:
                take[itemType][keyV].update(itemV)
            else:
                take[itemType].update({keyV: itemV})
        else:
            take[itemType].update({keyV : itemV})

        justTake[itemType].update({keyV: itemV})

    return take, justTake


def saveTake(itemType, take, justTake, local_take, versionUp=True, fileDirV=""):
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = utilScript.getFileList(fileDirV)
    globalCurrentTake, globalNewTake, globalNewNum = versionUpTakeName(globalTakeDir, "take", versionUp)
    localCurrentTake, localNewTake, localNewNum = versionUpTakeName(localTakeDir, "%s" % fileName, versionUp)

    print(("{} take local : {}".format(itemType, globalNewTake)))

    local_take = convert_byte_to_string.convert_byte_to_string(local_take)
    take = convert_byte_to_string.convert_byte_to_string(take)
    justTake = convert_byte_to_string.convert_byte_to_string(justTake)

    # local Take Save
    with open("%s" % localNewTake, 'w') as f:
        local_take = convert_byte_to_string.convert_byte_to_string(local_take)
        json.dump(local_take, f, indent=4)

    # global Take Save
    with open("%s" % globalNewTake, 'w') as f:
        take = convert_byte_to_string.convert_byte_to_string(take)
        json.dump(take, f, indent=4)
    with open("%s" % globalNewTake.replace("/take.", "/take_just."), 'w') as f:
        justTake = convert_byte_to_string.convert_byte_to_string(justTake)
        json.dump(justTake, f, indent=4)


def saveTakeFarm(itemType, take, local_take, mode="write", versionUp=True, file_path=""):
    prjDir, fileDir, partType, fileName, globalTakeDir, localTakeDir = utilScript.getFileList(fileDir=file_path)
    globalCurrentTake, globalNewTake, globalNewNum = versionUpTakeName(globalTakeDir, "take", versionUp)
    if not fileName:
        fileName = os.path.splitext(os.path.basename(file_path))[0]

    localCurrentTake, localNewTake, localNewNum = versionUpTakeName(localTakeDir, fileName, versionUp)

    localNewTakeFarm = localNewTake.replace("/Take", "/Take/farm")
    globalNewTakeFarm = globalNewTake.replace("/Take", "/Take/farm")

    print(("{} take farm : {}".format(itemType, globalNewTakeFarm)))

    if mode == "write":
        # local Take Farm Save
        local_take = convert_byte_to_string.convert_byte_to_string(local_take)
        with open("%s" % localNewTakeFarm, 'w') as f:
            json.dump(local_take, f, indent=4)

        take = convert_byte_to_string.convert_byte_to_string(take)
        # global Take Farm Save
        with open("%s" % globalNewTakeFarm, 'w') as f:
            json.dump(take, f, indent=4)
    if mode == "move":
        return localNewTakeFarm, localNewTake, globalNewTakeFarm, globalNewTake

def takeItem(item, itemdir, extType, renderLayerName="", tabType=""):

    if extType == "abc_scene":
        extType = "abc"

    fileinfo = {}
    if ":" in item:
        assetName = re.search("[\w]*[\D](?=([\d]+)?:)", item).group()

        if "out_cur_Grp" in item:
            itemName = item.split(":")[0]  # org
            assetName = item.split(":")[1]  # org
        elif tabType == "maya":
            itemName = item.split(":")[0]  # org
            assetName = item.split(":")[1]  # or
        else:
            if not "geo_Grp" in item:
                assetName = item.split(":")[1]  # org
            itemName = item.split(":")[0] # asset name
        fileName = item.replace(":", "_")
        if renderLayerName:
            itemNewDir = "%s/%s/%s" % (itemdir, renderLayerName, itemName)
        else:
            itemNewDir = "%s/%s" % (itemdir, itemName )
        fileinfo[ "%s:%s" %(itemName,assetName) ] = "%s/%s.%s" %(itemNewDir, fileName, extType)

    else:
        assetName = item
        itemName = item
        fileName = item
        if renderLayerName:
            itemNewDir = "%s/%s/%s" % (itemdir, renderLayerName, itemName)
        elif extType == "abc":
            itemNewDir = "%s/%s" % (itemdir, itemName)
        elif extType == "ass":
            itemNewDir = "%s/%s" % (itemdir, itemName)
        else:
            itemNewDir = itemdir

        fileinfo[ "%s" %itemName ] = "%s/%s.%s" %(itemNewDir, fileName, extType)

    if os.path.isfile( "%s/%s.%s" %(itemNewDir, fileName, extType) ):
        print("delete %s/%s.%s" %(itemNewDir, fileName, extType))
        os.system("rm -rf %s/%s.%s" %(itemNewDir, fileName, extType) )

    if not os.path.isdir( itemNewDir ):
        os.makedirs( itemNewDir )

    return fileinfo, itemNewDir, fileName