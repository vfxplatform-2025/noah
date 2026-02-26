# -*- coding:utf-8 -*-
import maya.cmds as cmds
import re
import os
from . import nkCam_PZexport

def find2DPZ(item):
    print("---------------------------------------------------")
    print('>>>>>> find2DPZ_start!!! <<<<<<<<')
    mb_path = cmds.file(sn=1, q=1)
    # / show / SHOME2 / seq / TST / TST_0010 / ani / wip / scenes / TST_0010_ani_v01_w01.mb
    basename = os.path.basename(mb_path)
    basic_name = basename.split('.')[0]
    split_mb = mb_path.split('/')[0:8]
    json_path = '/'.join(split_mb)+'/data/json'
    nodes = cmds.listRelatives(item, allDescendents=True, type='camera')
    cam_name = []

    if nodes != None:
        cam_name.extend([node for node in nodes if cmds.nodeType(node) == 'camera'])
        print("---------------------------------------------------")
        print('>>>> Cam Find!!!! <<<<')
    else:
        print("---------------------------------------------------")
        print('>>>> This is not Cam & find2DPZ exit....<<<<')
        return

    if len(cam_name) == 1:


        for cam in cam_name:

            zoom_parm = '{}.zoom'.format(cam)
            zoom_value = cmds.getAttr(zoom_parm)
            zoom_enableKey = cmds.keyframe(zoom_parm, query=True)

            panx_parm = '{}.horizontalPan'.format(cam)
            panx_value = cmds.getAttr(panx_parm)
            panx_enableKey = cmds.keyframe(panx_parm, query=True)

            pany_parm = '{}.verticalPan'.format(cam)
            pany_value = cmds.getAttr(pany_parm)
            pany_enableKey = cmds.keyframe(pany_parm, query=True)

        file_path = os.path.join(json_path, '{}_Use2DPZ.txt'.format(basic_name))

        if zoom_value == 1 and panx_value == 0 and pany_value == 0:
            print("---------------------------------------------------")
            print('>>>> 2DPZ value is all default & find2DPZ exit... <<<<')
            return

        elif zoom_enableKey != None or panx_enableKey != None or pany_enableKey != None:
            print("---------------------------------------------------")
            print('>>>> 2DPZ parm has key!!! & run find2DPZ!!! <<<<')

            if os.path.isdir(json_path):
                pass
            else:
                try:
                    os.makedirs(json_path)
                except:
                    pass

            with open(file_path, 'w') as file:
                file.write('Zoom: {}\n'.format(zoom_value))
                file.write('PanX: {}\n'.format(panx_value))
                file.write('PanY: {}\n'.format(pany_value))

            nkCam_PZexport.nkCam_exportJson(json_path, basic_name, item)

        else:
            print("---------------------------------------------------")
            print('>>>> 2DPZ do not have key!!! & find2DPZ exit...  <<<<')
            pass
            return
            #if os.path.isdir(json_path):
            #    pass
            #else:
            #    try:
            #        os.makedirs(json_path)
            #    except:
            #        pass

            #with open(file_path, 'w') as file:
            #    file.write('Zoom: {}\n'.format(zoom_value))
            #    file.write('PanX: {}\n'.format(panx_value))
            #    file.write('PanY: {}\n'.format(pany_value))
    else:
        print("---------------------------------------------------")
        print("서치된 카메라가 1개 이상입니다.")
        return


