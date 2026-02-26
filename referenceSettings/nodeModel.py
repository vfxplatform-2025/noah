# -*- coding:utf-8 -*-
'''
Created on May 30, 2016

@author: m83
'''
import os, sys, re, glob
import maya.cmds as cmds

class Node:
    def __init__(self, Name, parent=None):
        self._name = Name
        self._assetName =""
        self._assetdir =""        
        self._currentdir = ""
        self._currentRefdir=""
        self._currentFilename=""
        self._currenttype=""
        self._dir =""
        self._list={}
        self._listName=[]
        self._type={}
        self._meshtype=""
        self._pubdir=""
        self._refNodeName =""
        self._lowDir=""
        self._hiDir=""
        self._hi=""
        self._low=""
        self._num=""
    
    @property
    def name(self):
        return self._name

    @property
    def assetname(self):
        return self._assetName

    @property
    def assetdir(self):
        return self._assetdir
        
    @property    
    def currentdir(self):
        return self._currentdir

    @property    
    def currentRefdir(self):
        return self._currentRefdir
    
    @property
    def currentFilename(self):
        return self._currentFilename

    @property
    def refname(self):
        return self._refNodeName
        
    @property    
    def meshtype(self):
        return self._meshtype

    @property
    def dir(self):
        return self._dir

    @property
    def list(self):
        return self._list

    @property
    def listName(self):
        return self._listName
    
    @property
    def currenttype(self):
        return self._currenttype
    
                                
    @property
    def pubdir(self):
        return self._pubdir

    @property
    def num(self):
        return self._num

    def setAssetName(self, dir):
        print(f"DEBUG: setAssetName called with dir: {dir}")
        # 파일명에서 애셋 이름 추출 (더 안전한 방법)
        import os
        base_name = os.path.basename(dir)
        # 확장자 제거하고 언더스코어 기준으로 분리해서 애셋명 추출
        name_without_ext = os.path.splitext(base_name)[0]
        # 일반적으로 애셋명은 첫 부분에 있음
        parts = name_without_ext.split('_')
        if len(parts) >= 3:
            # c0086ma_e200_heartsping_geo -> c0086ma_e200_heartsping
            self._assetName = '_'.join(parts[:-1])  # 마지막 부분 제거
        else:
            self._assetName = name_without_ext
        print(f"DEBUG: setAssetName result: {self._assetName}")

    def setAssetDir(self,  dir):
        print(f"DEBUG: setAssetDir called with dir: {dir}, assetname: {self.assetname}")
        # 현재 파일이 있는 디렉토리를 기준으로 pub 폴더 찾기
        import os
        current_dir = os.path.dirname(dir)
        # 상위 디렉토리들을 순회하면서 pub 폴더가 있는지 확인
        while current_dir and current_dir != '/':
            pub_dir = os.path.join(current_dir, 'pub')
            if os.path.exists(pub_dir):
                self._assetdir = current_dir + '/'
                print(f"DEBUG: setAssetDir found pub directory, result: {self._assetdir}")
                return
            current_dir = os.path.dirname(current_dir)
        
        # pub 폴더를 찾지 못한 경우 현재 디렉토리 사용
        self._assetdir = os.path.dirname(dir) + '/'
        print(f"DEBUG: setAssetDir fallback, result: {self._assetdir}") 

    def setCurrentDir(self, name):
        dirNode = cmds.referenceQuery(name, filename =1)
        print(f"DEBUG: setCurrentDir called with dirNode: {dirNode}")
        # .mb, .ma, .abc 등 다양한 확장자를 지원하도록 수정
        match = re.search("/[\w].+\.\w+", dirNode)
        if match:
            fileDir = match.group()
            print(f"DEBUG: setCurrentDir regex match: {fileDir}")
        else:
            # 정규식이 실패하면 전체 경로 사용
            fileDir = dirNode
            print(f"DEBUG: setCurrentDir fallback: {fileDir}")
        self._currentRefdir=dirNode 
        self._currentdir = fileDir 

    def setCurrentFileName(self, name):
        print(f"DEBUG: setCurrentFileName called with {name}")
        print(f"DEBUG: nodeModel.py file location: {__file__}")
        dirNode = cmds.referenceQuery(name, filename =1)
        print(f"DEBUG: dirNode from Maya: {dirNode}")
        # .mb, .ma, .abc 등 다양한 확장자를 지원하도록 수정
        match = re.search( "[\w]+(?=\.\w+)", dirNode)
        if match:
            fileDir = match.group()
            print(f"DEBUG: Regex match found: {fileDir}")
        else:
            # 정규식이 실패하면 파일명에서 확장자를 제거
            import os
            fileDir = os.path.splitext(os.path.basename(dirNode))[0]
            print(f"DEBUG: Using fallback filename extraction: {fileDir} from {dirNode}")
#         print fileDir, "<<<" 
        self._currentFilename = fileDir

    def setrefNodeName(self, name):
        referNode = cmds.referenceQuery( name, referenceNode = True)
        self._refNodeName = referNode 

    def setList(self, value):
        listName ={}
        print(f"DEBUG: setList called with assetdir: {self.assetdir}")
        
        # .mb, .ma, .abc 파일들을 모두 찾도록 수정
        search_patterns = [
            "%s*/pub/*.mb" % self.assetdir,
            "%s*/pub/*.ma" % self.assetdir, 
            "%s*/pub/*.abc" % self.assetdir
        ]
        
        for pattern in search_patterns:
            found_files = glob.glob(pattern)
            print(f"DEBUG: Pattern '{pattern}' found {len(found_files)} files")
            for file_path in found_files:
                # 확장자에 관계없이 파일명 추출
                import os
                filename_without_ext = os.path.splitext(os.path.basename(file_path))[0]
                listName[filename_without_ext] = file_path
                print(f"DEBUG: Added to list: {filename_without_ext} -> {file_path}")
        
        self._list= listName
        self._listName =list(self._list.keys())
        self._listName.sort()
        print(f"DEBUG: Final list has {len(self._listName)} items: {self._listName}") 
        
    def setDir(self, dir):
        self._dir= dir.split("/", 5) 

    def setpubDir(self, dirNode):
        print(f"DEBUG: setpubDir called with: {dirNode}")
        # .mb, .ma, .abc 등 다양한 확장자를 지원하도록 수정
        match = re.search( ".+(?=/.+\.\w+)", dirNode)
        if match:
            dir = match.group()
            print(f"DEBUG: setpubDir regex match: {dir}")
        else:
            # 정규식이 실패하면 파일명 부분을 제거
            import os
            dir = os.path.dirname(dirNode)
            print(f"DEBUG: setpubDir fallback: {dir}")
        self._pubdir= dir

    def setMeshType(self, dir):  #low hi proxy
        fileNameCheck = ["_XHI", "_HI", "_MID", "_LOW", "_XLOW", "_PROXY"]
        for i in fileNameCheck:
            if i in dir:
                self._type = i.split("_")[1]
                self._meshtype = i.split("_")[1]


        #if "_LOW.mb" in dir:
        #    self._type = "LOW"
        #self._meshtype = "HI"

    def setCurrentType(self, dir):
        self._currenttype=dir.split("/")[6]

    def setNum(self, name):
        
        if re.search("([\d]+$)+?", name.split(":")[0]):
            self._num = int(re.search("([\d]+$)+?", name.split(":")[0]).group() )
        else:
            self._num=""
        
#     def setType(self, value):  #low hi proxy 
#         listName ={}
#         listType ={}
#         types={}
#
#         lowList = filter(lambda x : "_LOW.mb" in x , glob.glob("%s/*" %value ))
#         self.setLowDir(lowList)
#
#         map(lambda x : listType.update( {x:"LOW"} ) , lowList )
#         hiList = filter(lambda x : "_LOW.mb" not in x , glob.glob("%s/*" %value ))
#         self.setHiDir(hiList)
#
#         map(lambda x : listType.update( {x:"HI"} ) , hiList )                       
#         self._typeNames= listType

    def __repr__( self ):  
        return self._name

# if __name__ == "__main__":
#     node = Node()