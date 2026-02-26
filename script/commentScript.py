# -*- coding:utf-8 -*-
'''
Created on Jun 8, 2015

@author: m83
'''

import os, sys, glob, re, string
import getpass
from subprocess import *
import xml.etree.ElementTree as et
import json
import socket
import datetime
from script import convert_byte_to_string
from cacheExport_module.pyside2_moduleImport import *
from cacheExport_module.commentWindow_moduleImport import *

#from PyQt5 import QtCore, uic, QtWebKit, QtWebKitWidgets
#import maya.cmds as cmds
#import maya.mel as mel


class commentScript:
    def __init__(self, info):
        self.messageInfo = info
 
#         prjDir = re.search( ".+(?=/[\w]+/(pub|wip)/)",fileDir ).group()
#         partType = re.search( "[\w]+(?=/(pub|wip)/)",fileDir ).group()
#         fileName = re.search( "[\w]+(?=\.mb)",fileDir  ).group()        


    def exportComment(self, prjDir, partType, editTakeNum=None):

        # check Take Comment Dir
        getTake, commentDir = self.checkCommentFile( "%s/Comment" %prjDir)
        
        # write AssetInfo
        newTake = self.messageInfoExport(self.messageInfo,  partType)

        # saveTake 
        self.saveTake( commentDir,getTake, newTake ,editTakeNum)
         
        return newTake

    def checkCommentFile(self, commentDir ):
        
        # check dir
        if not os.path.isdir(commentDir):
            os.makedirs(commentDir)
            
        commentFile =""
        commentFile = "%s/comment.json" % commentDir
         
        # global Take
        if not os.path.isfile( commentFile ):
            take = {}    
        else:
            with open("%s" %( commentFile ), 'r' ) as f:
                take = json.load(f)

        return take, commentFile

    def messageInfoExport(self, commentInfo, partType = None):
        # asset info
        newTake={}

        #take local version
#         newTake["takeNum"]["version"] = takeNum 

        # user info
        userName =  socket.gethostname()
        newTake["username"] = userName

        #ipaddr
        cmd = "echo $(ifconfig eth0 |awk -F: '/inet addr:/ {print $2}' | awk ' { print $1 }')"
        getipaddr = Popen(cmd, shell = True, stdout = PIPE)
        ipaddr = getipaddr.communicate()[0][:-1]
        newTake["ipaddr"] = ipaddr

        # date info
        nowdate = str(datetime.datetime.now())
        date = nowdate.rsplit(":",1)[0]
        newTake["date"] = date

        #object check info
        checkList = { "model":1, "rig" : 1,"ani":1, "matchmove":1, "layout":1, "dyn":1, "cloth":1,"hair":1, "clothSim":1, "lit" : 1, "fur":1, "lookdev" : 1 ,"fx" : 1 }
        newTake["objectCheck"] = checkList

        # tag
        newTake["tag"]   = [""]

        # title
        newTake["title"]   = list(commentInfo.keys())[0]

        # comment
        newTake["comment"] = list(commentInfo.values())[0]

        # part
        newTake["part"]    = partType
        
        return newTake
        
    # save
    def saveTake(self, takeDir, take, newTake, editTakeNum=None):
        
        if editTakeNum:
            takeNum = int(editTakeNum)
        elif take:
            takeKeys = list(take.keys())
            takeKeys.sort()
            takeNum = int(takeKeys[-1]) + 0o001
        else:
            takeNum = 1
        print(takeDir)
        newTake.update( { "number": "%04d" %takeNum }  )
        take.update( { "%04d" %takeNum : newTake } )
        take = convert_byte_to_string.convert_byte_to_string(take)
        # global Take Save
        with open("%s" %takeDir, 'w') as f:
            json.dump(take,  f, indent=4)


                    
#=================================================
#                 
