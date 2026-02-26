'''
Created on Jun 25, 2015

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


def modelEnvExport(fileName, itemdir, itemName):  # exort 5

    fileinfo = {}
    objName = cmds.ls(sl=1)

    for i in objName:
        fileinfo[i] = "%s/%s.mb" % (itemdir, fileName)
    cmds.file("%s/%s.mb" % (itemdir, fileName), force=1, options="v=0;", typ="mayaBinary", pr=1, es=1)

    return fileinfo


def findModelEnvData(proj, itemName):
    # env
    envDir = [glob.glob("%sassets/env/*/" % x) for x in glob.glob("/show/%s/" % proj)]
    envList = []
    list(map(lambda x: x is not [] and envList.extend(x), envDir))

    envL = [glob.glob("%smodel/pub/*.mb" % x) for x in envList]
    envList = []
    list(map(lambda x: x is not [] and envList.extend(x), envL))

    modelList = envList
    modelAssetName = [x.rsplit('/', 1)[1].split("_")[0] for x in modelList]

    modelAssetGrop = dict(list(zip(modelAssetName, modelList)))

    # surch file
    modelfile = {}

    if ":" in itemName:
        item = re.search(" [\D]+([\w]+)?[\D]+(?=([\d]+)?:) ", itemName).group()
    else:
        item = re.search("[a-zA-Z]+", itemName).group()

    modelfile[item] = modelAssetGrop[item]

    return modelfile


# -------------------------------------------------------------------------------------------------
def modelEnvImport(itemInfo, type, rootType):
    for i in itemInfo:
        #         name = "%s1:%s" %(i,i)
        if "import" in type:
            writeItemName = modelEnvImportFile(i, itemInfo[i], rootType)

        elif "reference" in type:
            writeItemName = modelEnvReferenceFile(i, itemInfo[i], rootType)
    return writeItemName


def modelEnvImportFile(itemName, itemDir, rootType):
    cmds.file("%s" % itemDir, pr=1, i=1, type="mayaBinary", namespace="modelEnv", ignoreVersion=1,
              mergeNamespacesOnClash=1, options="v=0;")
    writeItemName = initItemImportWrite(itemName, itemDir)
    return writeItemName


def modelEnvReferenceFile(itemName, itemDir, rootType):
    cmds.file("%s" % itemDir,
              r=1, gl=1, type="mayaBinary", ignoreVersion=1,
              namespace="modelEnv",
              mergeNamespacesOnClash=False, options="v=0;")

    writeItemName = initItemImportWrite(itemName, itemDir)
    return writeItemName


# write
def initItemImportWrite(itemName, itemDir):
    modelEnvObj = cmds.ls('%s' % itemName, r=1)[0]
    if not cmds.ls('%s.modelEnv' % modelEnvObj):
        cmds.addAttr('%s' % modelEnvObj, ln="modelEnv", dt="string")

    cmds.setAttr('%s.modelEnv' % modelEnvObj, "%s,%s" % (itemName, itemDir), type="string")
    return '%s.modelEnv' % modelEnvObj