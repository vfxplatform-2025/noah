#-*-coding:utf-8-*-

import os, sys
import imp

sys.path.append("/core/Linux/APPZ/renderFam/tractor/pixar/Tractor-2.2/lib/python2.7/site-packages")

import tractor.api.author as author
imp.reload(author)

import maya.cmds as cmds
from . import takeScript
imp.reload(takeScript)

import configparser

#import alembicScript
#reload(alembicScript)

def tractorExport(startF, endF, fileList , itemDic, num, step_num, frameType, farmSceneName, takeVersionUp, mayaVersion, fileType="", scriptPath="", tractorEngineV="tractor4"):
    #get Take
    #localNewTakeFarm, localNewTake, globalNewTakeFarm, globalNewTake = takeScript.saveTakeFarm("", "", "", "move")
    #takeName = globalNewTake.split("/")[-1]

    #postTaskCmd

    #postTaskCmd = "python -c \"import sys;sys.path.append('/core/MAYA_2017/Production/Global/chacheExport_dev/script');" \
    #              "import tractorCmdScript;tractorCmdScript.takeFarmCopy('%s', '%s');tractorCmdScript.takeFarmCopy('%s', '%s')\""\
    #              % (localNewTakeFarm, takeVersionUp, globalNewTakeFarm, takeVersionUp)

    localNewTakeFarm, localNewTake, globalNewTakeFarm, globalNewTake = takeScript.saveTakeFarm("tractor", "", "", "move")
    postTaskCmd = "python -c \"import sys;sys.path.append('%s/script');" \
                  "import tractorCmdScript;tractorCmdScript.farmTakeUpdate('%s');tractorCmdScript.farmTakeUpdate('%s')\"" \
                  % (scriptPath, localNewTakeFarm, globalNewTakeFarm)
    taskCmdList = []
    renderLayerName = ""
    renderlayerOpt = ""
    takeName = globalNewTake.split("/")[-1]
    sceneName = farmSceneName.split("/")[-1]

    miarmyVer = ""
    if os.getenv('SHOW') == 'BANDO':
        miarmyVer = '7.0.07_'

    for item, itemInfo in list(itemDic.items()):
        exportDir = itemInfo["exportDir"]
        fileName = itemInfo["fileName"]
        exportType = itemInfo["type"]
        handleNum = itemInfo["handleNum"]

        startF = int(startF)
        endF = int(endF)

        # taskCmd
        taskCmd = "source /core/Linux/ENV/maya%s_renderFarm.env && source /core/Linux/ENV/miarmy%s_%spro.env && source /core/Linux/ENV/arnold%s.env && "%(mayaVersion, mayaVersion, miarmyVer, mayaVersion)
        taskCmd += "mayapy -c \"import os;import sys;sys.path.append('%s/script');"%scriptPath
        taskCmd += "from maya import standalone, cmds;standalone.initialize();"
        if mayaVersion == "2017":
            taskCmd += "cmds.loadPlugin('MiarmyProForMaya2017.so');"
        if mayaVersion == "2018":
            taskCmd += "cmds.loadPlugin('MiarmyProForMaya2018.so');"
        if mayaVersion == "2020":
            taskCmd += "cmds.loadPlugin('MiarmyProForMaya2020.so');"
        taskCmd += "cmds.file('%s', force=True, open=True);"% farmSceneName

        if exportType == "renderlayer":
            postTaskCmd = "echo \"postTask\""
            renderLayerName = itemInfo["renderLayerName"]
            takeName = ""
            taskCmd += "cmds.editRenderLayerGlobals(currentRenderLayer='%s');" % renderLayerName

        if exportType == "abc" or exportType == "renderlayer":
            abcConfig = configparser.ConfigParser()
            abcConfigFile = os.path.abspath(__file__ + "/../../config/alembicOption.ini")
            abcConfig.read(abcConfigFile)

            abcAttrOptList = abcConfig.get("attr", "ALL").split(",")
            abcAttrOpt = "-attr {}".format(" -attr ".join(abcAttrOptList))

            taskCmd += "cmds.loadPlugin('AbcExport.so');"
            taskCmd += "cmds.AbcExport(j='-frameRange %d %d -uvWrite -writeUVSets -eulerFilter -writeVisibility -step %s %s -dataFormat ogawa -root %s -worldSpace -file %s/%s.abc');" % \
                       (startF-handleNum, endF+handleNum, step_num, abcAttrOpt, cmds.ls(item, l=1)[0], exportDir, fileName)

        if exportType == "atom":
            opt = itemInfo["opt"]
            taskCmd += "import atomScript;atomScript.atomEulerFilter('%s');"%item
            keybake = itemInfo["keybake"]
            if keybake:
                taskCmd += "cmds.bakeResults('{}', shape=True, simulation=True, t=({}-{}, {}+{})," \
                           "sampleBy=1, disableImplicitControl=True, preserveOutsideKeys=True, sparseAnimCurveBake=False," \
                           "removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False, bakeOnOverrideLayer=False," \
                           "minimizeRotation=True);".format(item, startF, handleNum, endF, handleNum)

            taskCmd += "cmds.loadPlugin('atomImportExport.so');"
            taskCmd += "cmds.select('%s', r=True);"%item
            taskCmd += "cmds.file('%s/%s.atom', es=1, force=1, options='%s', typ='atomExport');" % (exportDir, fileName, opt)
            taskCmd += "cmds.select(cl=1);"

        if mayaVersion == "2017":
            taskCmd += "standalone.uninitialize()\""
        if mayaVersion == "2018":
            taskCmd += "standalone.uninitialize();os._exit(0)\""
        if mayaVersion == "2020":
            taskCmd += "standalone.uninitialize();os._exit(0)\""

        taskCmdList.append(taskCmd)

    #tractor spool
    #spool("[AbcExport] %s ( %s )"%(sceneName, takeName), postTaskCmd, taskCmd)
    spool("[{}Export] {} {} ({})".format(fileType, sceneName, renderLayerName, takeName), postTaskCmd, taskCmdList, tractorEngineV, farmSceneName)
    cmds.select(cl=1)

def spool(title, postTaskCmd, taskCmdList, tractorEngineV="tractor4", commentV=""):

    serviceV = ""
    tractorIP = ""
    if tractorEngineV == "tractor4":
        serviceV = "ANI"
        tractorIP = "192.168.10.11"

    if tractorEngineV == "tractor5":
        serviceV = "All"
        tractorIP = "192.168.10.11"

    #create job
    job = author.Job()
    job.title = str(title)
    job.priority = 200
    job.comment = str("Scene File: " + commentV)
    #job.service = "ANI"
    job.service = serviceV
    #job.newTask(title="Frame 1-1", argv=["echo", "'ttt'"])

    # create task
    postTask = author.Task(title="postTask", argv=["/bin/bash", "-c", postTaskCmd])

    for cmdV in taskCmdList:
        task = author.Task(title="Task", argv=["/bin/bash", "-c", cmdV])
        postTask.addChild(task)

    #print cmdOpt

    # value=0 : processed at once, value=1 : processed one after the other
    postTask.serialsubtasks=0

    # task into job
    job.addChild(postTask)

    # print job.asTcl()

    # spool
    hostName = os.getenv("HOSTNAME")
    #author.setEngineClientParam(hostname="192.168.10.11", port=80, user=hostName, debug=True)
    #author.setEngineClientParam(hostname=tractorIP, port=80, user=hostName, debug=True)

    # job spool
    newJid = job.spool(hostname=tractorIP, port=80, spoolhost=hostName, owner=hostName)
    print("---------- ID:{} to {} ----------".format(newJid, tractorIP))
    #newJid =job.spool()
    author.closeEngineClient()


def itemExport(fileList , itemdir,  itemList, num, frameType, scenePath, takeVersionUp, fileType, mayaVersion, scriptPath, tractorEngineV="tractor4", smap=False, startFrame=None, endFrame=None):
    #localNewTakeFarm, localNewTake, globalNewTakeFarm, globalNewTake = alembicScript.saveTakeFarm("", "", "", "move")
    localNewTakeFarm, localNewTake, globalNewTakeFarm, globalNewTake = takeScript.saveTakeFarm("", "", "", "move", file_path=scenePath)
    takeName = globalNewTake.split("/")[-1]
    sceneName = scenePath.split("/")[-1]

    #create job
    serviceV = ""
    tractorIP = ""
    if tractorEngineV == "tractor4":
        serviceV = "ANI"
        tractorIP = "192.168.10.11"

    if tractorEngineV == "tractor5":
        serviceV = "All"
        tractorIP = "192.168.10.11"

    job = author.Job()
    job.title = str("[%sExport] %s ( %s )"%(fileType, sceneName, takeName))
    job.priority = 200
    job.comment = str("Scene File: " + scenePath)
    #job.service = "ANI"
    job.service = serviceV



    startF = 1001
    endF = 1001

    if frameType == "FrameRange":
        startF = cmds.playbackOptions(min=1, q=1)
        startF = startF - num
        endF = cmds.playbackOptions(max=1, q=1)
        endF = endF + num
    if frameType == "CurrentFrame":
        startF = cmds.currentTime(q=True)
        endF = cmds.currentTime(q=True)
    if frameType == "setFrame":
        startF = startFrame - num
        endF = endFrame + num

    cmds.refresh(su=1)
    fileinfo = {}
    miarmyVer = ""
    if os.getenv('SHOW') == 'BANDO':
        miarmyVer = '7.0.07_'

    # postTaskCmd
    postTaskCmd = "python -c \"import sys;sys.path.append('%s/script');" \
                  "import tractorCmdScript;tractorCmdScript.farmTakeUpdate('%s');tractorCmdScript.farmTakeUpdate('%s')\"" \
                  % (scriptPath, localNewTakeFarm, globalNewTakeFarm)
    #              "import tractorCmdScript;tractorCmdScript.takeFarmCopy('%s', '%s');tractorCmdScript.takeFarmCopy('%s', '%s')\"" \
    #              % (scriptPath, localNewTakeFarm, takeVersionUp, globalNewTakeFarm, takeVersionUp)

    if fileType == "abc_sceneCreate":
        postTaskCmd = ""
        scenePathList = scenePath.split("/")
        sceneSetPath = "/".join(scenePathList[:-1])+"/"+scenePathList[-1].split(".")[0]+"_sceneSet.mb"
        sceneSetPath = sceneSetPath.replace("/tmp", "")
        postTaskCmd += "source /core/Linux/ENV/maya%s_renderFarm.env && source /core/Linux/ENV/miarmy%s_%spro.env && source /core/Linux/ENV/arnold%s.env && " \
                    "mayapy -c \"import os;from maya import standalone, cmds;standalone.initialize();cmds.loadPlugin('MiarmyProForMaya%s.so');" \
                    "cmds.loadPlugin('AbcImport.so');import sys;sys.path.append('%s');sys.path.append('%s/script');import alembicScript;alembicScript.alembicImportByJson('%s', 'alembic', '');" \
                    "cmds.file(rename='%s');cmds.file(save=True);standalone.uninitialize();os._exit(0);\"" % \
                    (mayaVersion, mayaVersion, miarmyVer, mayaVersion, mayaVersion, scriptPath, scriptPath, globalNewTakeFarm, sceneSetPath)
        postTaskCmd += "&& python -c \"import sys;sys.path.append('%s/script');" \
                      "import tractorCmdScript;tractorCmdScript.farmTakeUpdate('%s');tractorCmdScript.farmTakeUpdate('%s')\"" \
                      % (scriptPath, localNewTakeFarm, globalNewTakeFarm)
        fileType = "abc_scene"

    postTask = author.Task(title="postTask", argv=["/bin/bash", "-c", postTaskCmd])

    if smap:
        smap_post_task = ["/bin/bash", "-c", postTaskCmd]
        smap_task_list = []

    # taskCmd
    for item, attriDic in list(itemList.items()):
        step_num = attriDic["step"]
        typeV = attriDic["type"]
        hiddenV = attriDic["hidden"]

        typeList = typeV.split(",")
        if fileType == "abc_scene":
            item = typeList[2]

        fileinfotmp, itemNewDir, fileName = takeScript.takeItem(item, itemdir, fileType)
        fileinfo.update(fileinfotmp)

        taskCmd = ""
        if fileType in ["abc", "abc_scene"]:
            # file open option
            fileOpt = "cmds.file('%s', force=True, open=True)" % scenePath
            if fileType == "abc_scene":
                refNode = typeList[1]
                fileOpt = "cmds.loadPlugin('qualoth_44_Maya%s_x64.so');cmds.file('%s', force=True, open=True, lrd='none');cmds.file(lr='%s')" % (mayaVersion, scenePath, refNode)

            # abc attribute option
            abcConfig = configparser.ConfigParser()
            abcConfigFile = os.path.abspath(__file__ + "/../../config/alembicOption.ini")
            abcConfig.read(abcConfigFile)

            abcAttrOptList = abcConfig.get("attr", "ALL").split(",")
            abcAttrOpt = "-attr {}".format(" -attr ".join(abcAttrOptList))

            # abc option
            abcOpt = ""
            if smap:
                if typeV == "mergeObjectSpace":
                    abcOpt = "-frameRange %d %d -uvWrite -eulerFilter -writeVisibility -step %s %s -dataFormat ogawa -root %s " \
                             "-file %s/%s.abc" % (
                             startF, endF, step_num, abcAttrOpt, item.replace("_mergeObjectSpace", ""), itemNewDir, fileName)

                elif typeV == "mergeWorldSpace":
                    abcOpt = "-frameRange %d %d -uvWrite -eulerFilter -writeVisibility -step %s %s -dataFormat ogawa -root %s -worldSpace " \
                             "-file %s/%s.abc" % (
                             startF, endF, step_num, abcAttrOpt, item.replace("_mergeWorldSpace", ""), itemNewDir, fileName)
                else:
                    abcOpt = "-frameRange {:d} {:d} -uvWrite -eulerFilter -writeVisibility -step {} {} -dataFormat ogawa -root {} -worldSpace -file {}/{}.abc".format(
                            int(startF), int(endF), step_num, abcAttrOpt, item, itemNewDir, fileName)
            else:
                if typeV == "mergeObjectSpace":
                    abcOpt = "-frameRange %d %d -uvWrite -eulerFilter -writeVisibility -step %s %s -dataFormat ogawa -root %s " \
                             "-file %s/%s.abc" % (startF, endF, step_num, abcAttrOpt, cmds.ls(item.replace("_mergeObjectSpace", ""), l=1)[0], itemNewDir, fileName)
                elif typeV == "mergeWorldSpace":
                    abcOpt = "-frameRange %d %d -uvWrite -eulerFilter -writeVisibility -step %s %s -dataFormat ogawa -root %s -worldSpace " \
                             "-file %s/%s.abc" % (startF, endF, step_num, abcAttrOpt, cmds.ls(item.replace("_mergeWorldSpace", ""), l=1)[0], itemNewDir, fileName)
                else:
                    abcOpt = "-frameRange %d %d -uvWrite -eulerFilter -writeVisibility -step %s %s -dataFormat ogawa -root %s -worldSpace -file %s/%s.abc" % (startF, endF, step_num, abcAttrOpt, cmds.ls(item, l=1)[0], itemNewDir, fileName)

            # close option
            exitCmd = "standalone.uninitialize();os._exit(0)"
            if mayaVersion == "2017":
                exitCmd="standalone.uninitialize();"
            if mayaVersion == "2018":
                exitCmd = "standalone.uninitialize();os._exit(0)"
            if mayaVersion == "2020":
                exitCmd = "standalone.uninitialize();os._exit(0)"

            if hiddenV:
                hideCmdList = []
                for grpV in hiddenV:
                    hideCmdList.append("cmds.hide('%s')"%grpV)
                hideCmd = ";".join(hideCmdList)

                taskCmd = "source /core/Linux/ENV/maya%s_renderFarm.env && source /core/Linux/ENV/miarmy%s_%spro.env && source /core/Linux/ENV/arnold%s.env && " \
                          "mayapy -c \"import os;from maya import standalone, cmds;standalone.initialize();cmds.loadPlugin('MiarmyProForMaya%s.so');%s;" \
                          "cmds.loadPlugin('AbcExport.so');%s;cmds.AbcExport(j='%s');%s\"" % \
                          (mayaVersion, mayaVersion, miarmyVer, mayaVersion, mayaVersion, fileOpt, hideCmd, abcOpt, exitCmd)
            else:
                taskCmd = "source /core/Linux/ENV/maya%s_renderFarm.env && source /core/Linux/ENV/miarmy%s_%spro.env && source /core/Linux/ENV/arnold%s.env && " \
                          "mayapy -c \"import os;from maya import standalone, cmds;standalone.initialize();cmds.loadPlugin('MiarmyProForMaya%s.so');%s;" \
                          "cmds.loadPlugin('AbcExport.so');cmds.AbcExport(j='%s');%s\"" % \
                          (mayaVersion, mayaVersion, miarmyVer, mayaVersion, mayaVersion, fileOpt, abcOpt, exitCmd)

        if fileType == "ass":
            exportCmd = 'arnoldExportAss -startFrame %s -endFrame %s -frameStep %s -f \\\\"%s/%s.ass\\\\" -s -shadowLinks 1  -mask 2303 -lightLinks 1  -boundingBox -cam perspShape %s;'\
                % (startF, endF, step_num, itemNewDir, fileName, cmds.ls(item, l=1)[0])
            taskCmd = "source /core/Linux/ENV/maya%s_renderFarm.env && source /core/Linux/ENV/miarmy%s_%spro.env && source /core/Linux/ENV/arnold%s.env && " \
                      "mayapy -c \"import os;from maya import standalone, cmds, mel;standalone.initialize();cmds.loadPlugin('mtoa.so');cmds.loadPlugin('MiarmyProForMaya%s.so');cmds.file('%s', force=True, open=True);" \
                      "mel.eval('%s');standalone.uninitialize();os._exit(0)\"" % (mayaVersion, mayaVersion, miarmyVer, mayaVersion, mayaVersion, scenePath, exportCmd)

        task = author.Task(title="Task", argv=["/bin/bash", "-c", taskCmd])
        if smap:
            smap_task_list.append(["/bin/bash", "-c", taskCmd])

        postTask.addChild(task)

    if smap:
        fileList = {}
        fileList.update(fileinfo)

        takeScript.takeExport(fileList, "alembic", {}, "farm", frameType, startFrame=startFrame, endFrame=endFrame)
        return smap_post_task, smap_task_list, fileList
    else:
        postTask.serialsubtasks=0

        # task into job
        job.addChild(postTask)
        # print job.asTcl()

        # spool
        hostName = os.getenv("HOSTNAME")
        #author.setEngineClientParam(hostname="192.168.10.11", port=80, user=hostName, debug=True)
        print(job.asTcl())
        # job spool
        newJid =job.spool(hostname=tractorIP, port=80, spoolhost=hostName, owner=hostName)
        author.closeEngineClient()

        cmds.select(cl=1)
        cmds.refresh(su=0)
        return fileinfo
