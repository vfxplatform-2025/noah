# -*- coding:utf-8 -*-

import maya.cmds as cmds

def cloudVDB(projName):
    # check arnold plugin
    if projName == "ZZ":
        projName = "DIARY"

    cloudSetList =  cmds.ls("Cloud_set", "*:Cloud_set")
    for cloudSetName in cloudSetList:
    #if cmds.ls("Cloud_set"):
        confirmBtn = cmds.confirmDialog(title='Confirm', message='Cloud_set이 발견 되었습니다. arnold VDB 노드 세팅을 하시겠습니까?',
                           button=['Yes', 'No'], defaultButton='Yes',
                           cancelButton='No', dismissString='No')

        if confirmBtn == "Yes":
            if not cmds.pluginInfo("mtoa", query=True, loaded=True):
                #cmds.confirmDialog(title='Confirm', message='arnold가 로딩되어 있지 않습니다. arnold VDB노드 세팅은 취소되었습니다. ', button=['ok'])
                print('arnold가 로딩되어 있지 않습니다. arnold VDB노드 세팅은 취소되었습니다. 세팅하시려면 새로 Cloud_set을 지우고, mtoa를 로딩후 다시 시도해주세요.')
                return

            #itemList = cmds.listRelatives("Cloud_set", c=True)
            itemList = cmds.listRelatives(cloudSetName, c=True)
            cloudList = []
            # create arnold volume
            for itemNameV in itemList:
                #create node
                aiVolumeNodeName = cmds.createNode('aiVolume', n="%s_vdbfxCache"%itemNameV)
                aiVolumeTransName = cmds.listRelatives(aiVolumeNodeName, p=1)[0]
                aiVolumeRename = cmds.rename(aiVolumeTransName, "%s_vdbFx" % itemNameV)

                cloudName = itemNameV.split(":")[-2]
                cloudPath = "/show/{}/assets/fx/cloud/pub/cache/cloud/{}.vdb".format(projName, cloudName)
                print(("cloudPath : {}".format(cloudPath)))

                # set name and frame expresstion
                cmds.setAttr("%s.filename" % aiVolumeRename, cloudPath, type="string")
                cmds.setAttr("%s.grids" % aiVolumeRename, "density", type="string")

                #
                #cmds.parent(aiVolumeRename, "Cloud_set")
                cmds.parent(aiVolumeRename, cloudSetName)

                tvalue = cmds.xform(itemNameV, q=True, t=True)
                rvalue = cmds.xform(itemNameV, q=True, ro=True)
                svalue = cmds.xform(itemNameV, q=True, s=True)

                cmds.xform(aiVolumeRename, t=tvalue)
                cmds.xform(aiVolumeRename, ro=rvalue)
                cmds.xform(aiVolumeRename, s=svalue)
                cloudList.append(aiVolumeRename)

                cmds.hide(itemNameV)

            cmds.select(cloudList, r=True)
