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
import shutil


def proxyAutoConnectShader():
    # select all vray mesh proxy material
    proxyMaterialNodes = cmds.ls(type="VRayMeshMaterial")
    # select all material
    allMaterials = cmds.ls(materials=True)
    materialClean = list(set(allMaterials) - set(proxyMaterialNodes))

    if len(proxyMaterialNodes) == 0:
        OpenMaya.MGlobal.displayWarning("No VRayMeshMaterial in the scene !")
    # list all connection name on all vray mesh proxy material

    for proxyMaterialNode in proxyMaterialNodes:
        numberOfSlot = cmds.getAttr(proxyMaterialNode + ".shaderNames", size=True)

        for i in range(numberOfSlot):
            nameSlot = cmds.getAttr(proxyMaterialNode + ".shaderNames[" + str(i) + "]")

            # connected or not ?
            if cmds.connectionInfo(proxyMaterialNode + ".shaders[" + str(i) + "]", isDestination=True):
                connected = cmds.connectionInfo(proxyMaterialNode + ".shaders[" + str(i) + "]",
                                                sourceFromDestination=True)
                cmds.disconnectAttr(connected, proxyMaterialNode + ".shaders[" + str(i) + "]")
                print("[deeXVrayFast] Disconnect " + proxyMaterialNode + ".shaders[" + str(i) + "]")
            for myMat in materialClean:
                if myMat.split(":")[-1] == nameSlot.split(":")[-1]:
                    # try:
                    cmds.connectAttr(myMat + ".outColor", proxyMaterialNode + ".shaders[" + str(i) + "]", f=True)
                    print("[deeXVrayFast] " + proxyMaterialNode + ".shaders[" + str(i) + "] connected.")
