# -*- coding:utf-8 -*-
'''
Created on Jun 8, 2015

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

def frameRangeExport( fileName, itemdir,itemName):
    startF = cmds.playbackOptions(min=1, q=1)
    endF   = cmds.playbackOptions(max=1, q=1)
    startH = cmds.playbackOptions(ast=1, q=1)
    endH   = cmds.playbackOptions(aet=1, q=1)


    fps = cmds.currentUnit(q=1, time=1)
    handleNum = 8
    dataTx = 'cmds.currentUnit(time="%s")\n' %fps
    dataTx += 'cmds.playbackOptions(min=%s, max=%s)\n' %(startF ,endF )
    dataTx += 'cmds.playbackOptions(ast=%s, aet=%s)\n' %(startH ,endH   )
    dataTx += 'cmds.currentTime(%s)\n' %(startF)

    itemName = "%s_%s" %(int(startF) ,int(endF))
    itemFullName = "%s_%s" %(int(startH) ,int(endH))

    f=open("%s/%s.py" %(itemdir, itemName), 'w')
    f.write(dataTx )
    f.close()

    fileinfo ={}    # :ctrl_SET  ==> :gunShot
    fileinfo[ "%s" %itemName.replace("_", "-") ] = "%s/%s.py" %(itemdir, itemName)

    return fileinfo


# import
def frameRangeImport(objList, type, rootType):  # itemInfo, imagePlane):

    # camera
    for i in objList:  # {u'EO_055_ani_v01_w02_test_rencam': u'/show/JM/seq/EO/EO_055/ani/wip/data/camera/EO_055_ani_v01_w02_test.mb'}
        itemDir = objList[i]
        exec (open("%s" % itemDir))

        startH = cmds.playbackOptions(ast=1, q=1)
        endH = cmds.playbackOptions(aet=1, q=1)

        parttype = "ani"

        # -------------------------------------------

        # if "ani" not in parttype or "matchmove" not in parttype or "layout" not in parttype:
        if "FullFrame" in type:
            cmds.playbackOptions(min=startH, max=endH)
            cmds.playbackOptions(ast=startH, aet=endH)
            cmds.currentTime(startH)
        # -------------------------------------------

        writeItemName = initFrameRangeImportWrite(i, itemDir)

    return writeItemName


# write
def initFrameRangeImportWrite(item, itemDir):
    if not cmds.ls('%s.frameRange' % "time1"):
        cmds.addAttr('%s' % "time1", ln="frameRange", dt="string")

    cmds.setAttr('%s.frameRange' % "time1", "%s,%s" % (item, itemDir), type="string")

    return '%s.frameRange' % "time1"