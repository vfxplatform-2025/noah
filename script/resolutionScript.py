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


def resolutionExport(fileName, itemdir, itemName):  # exort 5  e

    # resolution
    wSize = cmds.getAttr("defaultResolution.width")
    hSize = cmds.getAttr("defaultResolution.height")

    if not cmds.pluginInfo("atomImportExport", q=1, loaded=1):
        cmds.loadPlugin("atomImportExport.so")

    if not cmds.pluginInfo("animImportExport", q=1, loaded=1):
        cmds.loadPlugin("animImportExport.so")

    dataTx_list = [
        'cmds.setAttr("{0}.lockDeviceAspectRatio", 1)',
        'cmds.setAttr("{0}.width", {1})',
        'cmds.setAttr("{0}.height", {2})',
        'cmds.setAttr("{0}.deviceAspectRatio", float({1})/float({2}))',
        'cmds.setAttr("{0}.lockDeviceAspectRatio", 0)'
    ]

    dataTx = str('\n'.join(dataTx_list))

    default_res_str = "defaultResolution"
    if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
        default_res_str = "vraySettings"
    dataTx = dataTx.format(default_res_str, wSize, hSize)

    itemName = "%s_%s" % (int(wSize), int(hSize))

    with open("%s/%s.py" % (itemdir, itemName), 'w') as f:
        f.write(dataTx)


    fileinfo = {}  # :ctrl_SET  ==> :gunShot
    fileinfo["%s" % itemName.replace("_", "-")] = "%s/%s.py" % (itemdir, itemName)

    return fileinfo


# import
def resolutionImport(objList, type, rootType):  # itemInfo, imagePlane):
    # camera
    print(objList)
    pixelAspect = True
    for i in objList:  # {u'EO_055_ani_v01_w02_test_rencam': u'/show/JM/seq/EO/EO_055/ani/wip/data/camera/EO_055_ani_v01_w02_test.mb'}
        item_file = objList[i]

        width = None
        height = None
        pixelAspect = False
        render_type = "defaultResolution"

        with open(item_file, 'r') as f:
            file_txt = f.readlines()

            for line in file_txt:
                if line != "\n":
                    if 'deviceAspectRatio' in line:
                        pixelAspect = True
                        if "vraySettings" in line:
                            render_type = "vraySettings"
                    elif 'width' in line:
                        width = int(re.findall(r'\d+', line)[0])
                    elif 'height' in line:
                        height = int(re.findall(r'\d+', line)[0])

        if not pixelAspect:
            with open(item_file, 'w') as f:
                dataTx_list = [
                    'cmds.setAttr("{0}.lockDeviceAspectRatio", 1)',
                    'cmds.setAttr("{0}.width", {1})',
                    'cmds.setAttr("{0}.height", {2})',
                    'cmds.setAttr("{0}.deviceAspectRatio", float({1})/float({2}))',
                    'cmds.setAttr("{0}.lockDeviceAspectRatio", 0)'
                ]

                dataTx = str('\n'.join(dataTx_list))
                dataTx = dataTx.format(render_type, width, height)
                f.write(dataTx)

        exec (open("%s" % item_file))

        writeItemName = initResolutionImportWrite(i, item_file)

    return writeItemName


# write
def initResolutionImportWrite(item, itemDir):
    if not cmds.ls('%s.resolutionSet' % "time1"):
        cmds.addAttr('%s' % "time1", ln="resolutionSet", dt="string")

    cmds.setAttr('%s.resolutionSet' % "time1", "%s,%s" % (item, itemDir), type="string")
    return '%s.resolutionSet' % "time1"
