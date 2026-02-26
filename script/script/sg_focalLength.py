# -*- encoding: utf-8 -*-

'''
import sys as exp
sys.path.append('/core/TD/users/jiho/jiho_python_script/h19_HDA/LOC_export.py')
'''


import re
import sys
import os
from datetime import datetime
sys.path.append('/core/TD/m83sg/handler')
from logHandler import LogM83
from sg_dataModule import SgData
import shotgun_api3 as sg
from subprocess import *
import ast
import glob
import shutil
import json
import maya.cmds as cmds

def sg_focalLength(item):
    # API 인증 정보 설정
    API_URL = "https://m83.shotgunstudio.com/"
    SCRIPT_NAME = "FK_Robot_standalone"
    SCRIPT_KEY = "sJpehuziaaja)3pjfpupklsvf"

    # ShotGrid API 객체 생성 및 프록시 설정
    shotgrid = sg.Shotgun(API_URL, SCRIPT_NAME, SCRIPT_KEY, http_proxy="192.168.10.14:3128")
    show = os.getenv('SHOW')
    seq = os.getenv('SEQ')
    shot = os.getenv('SHOT')
    shot_code = os.getenv('SHOT_CODE')

    cam_list = cmds.ls(item)
    if cam_list:
        new_lens = cmds.getAttr('{0}.focalLength'.format(cam_list[0]))
    else:
        print('=========================================')
        print('Unable to update local length to Shotgrid')
        print('{0} is NOT FOUND'.format(item))
        print('=========================================')
        pass

    # show = 'SHOME3'
    # seq = 'INT'
    # shot = '3506'
    # shot_code = 'INT_3506'


    # 프로젝트 필터 설정
    project_filter = [['name', 'is', show]]  # 프로젝트 FK 필터

    # 프로젝트 ID 찾기
    project = shotgrid.find_one("Project", project_filter, ['id'])
    if project:
        project_id = project['id']

        # shot 필터 설정: 이제 project_id가 사용 가능
        shot_filter = [['code', 'is', shot_code], ['project', 'is', {'type': 'Project', 'id': project_id}]]
        fields = ['sg_shot_type', 'sg_lens']

        # shot 정보 가져오기
        shot = shotgrid.find_one("Shot", shot_filter, fields)
        if shot:
            sg_shot_type = shot['sg_shot_type']
            sg_lens = shot['sg_lens']
            print('sg_shot_type :', sg_shot_type)
            print('sg_lens :', sg_lens)

            if sg_shot_type == 'f3d':
                shotgrid.update("Shot", shot['id'], {'sg_lens': str(new_lens)+' mm'})
            else:
                print('=========================================')
                print('Unable to update local length to Shotgrid')
                print('sg_shot_type is NOT \'f3d\'')
                print('=========================================')
                pass


        else:
            print("Shot not found.")
    else:
        print("Project not found.")

# if __name__=='__main__':
#     item = sys.argv[1]
