# -*- encoding: utf-8 -*-

import maya.cmds as cmds
import os
import re
import json
from script import convert_byte_to_string

def checkOffset(item):
    print("---------------------------------------------------")
    print('>>>> checkoffset start!!!! <<<<')

    mb_path = cmds.file(sn=1, q=1)
    # / show / SHOME2 / seq / TST / TST_0010 / ani / wip / scenes / TST_0010_ani_v01_w01.mb
    basename = os.path.basename(mb_path)
    json_basic_name = basename.split('.')[0]
    split_mb = mb_path.split('/')[0:8]
    json_path = '/'.join(split_mb)+'/data/json'
    cam_list = []
    geo_name = str(item)

    nodes = cmds.listRelatives(geo_name, allDescendents=True, type='camera')

    if nodes != None:

        # 카메라 노드의 이름을 가져와서 리스트에 추가
        cam_list.extend([node for node in nodes if cmds.nodeType(node) == 'camera'])

    else:
        print("---------------------------------------------------")
        print('>>>> This object is not cam & checkOffset exit... <<<<')
        return

    hoffset = 'offsetX'
    voffset = 'offsetY'
    key_dict = []
    no_key_dict = []

    object_pattern = re.compile(r'{}.*->imagePlaneShape.*'.format(cam_list[0]))

    object_name = None
    for obj_name in cmds.ls(type='imagePlane'):
        match = object_pattern.match(obj_name)
        if match:
            object_name = match.group()
            break

    if object_name is None:
        print("---------------------------------------------------")
        print('>>>> imagePlane parm NOT Found & checkOffset exit... <<<<')
        return

    # 객체의 모든 키프레임을 얻음
    hkeyframes = cmds.keyframe(object_name, attribute=hoffset, query=True)
    vkeyframes = cmds.keyframe(object_name, attribute=voffset, query=True)

    if os.path.isdir(json_path):
        pass
    else:
        try:
            os.makedirs(json_path)
        except:
            pass

    if hkeyframes != None and vkeyframes != None:


        hdict = {}
        vdict = {}

        if len(hkeyframes) != 0:
            # 각 키프레임에 대한 파라미터 값을 얻음
            for frame in hkeyframes:
                cmds.currentTime(frame)
                hoffset_value = cmds.getAttr('{}.{}'.format(object_name, hoffset))
                hdict[frame] = hoffset_value
                print(('Frame:', frame, 'Value:', hoffset_value))
        else:
            print(("{0}에 키가 없습니다.".format(hoffset)))

        if len(vkeyframes) != 0:
            # 각 키프레임에 대한 파라미터 값을 얻음
            for frame in vkeyframes:
                cmds.currentTime(frame)
                voffset_value = cmds.getAttr('{}.{}'.format(object_name, voffset))
                vdict[frame] = voffset_value
                print(('Frame:', frame, 'Value:', voffset_value))
        else:
            print(("{0}에 키가 없습니다.".format(voffset)))

        key_dict.append(hdict)
        key_dict.append(vdict)
        key_dict = convert_byte_to_string.convert_byte_to_string(key_dict)
        with open(json_path+'/{0}_Key.json'.format(json_basic_name),'w') as f:
            json.dump(key_dict, f, indent=4)

        json_nonkeyname = json_path + '/{0}_NonKey.json'.format(json_basic_name)
        print(json_nonkeyname)
        if os.path.isfile(json_nonkeyname):
            os.remove(json_nonkeyname)
            print('>>>>>>>>> _NonKey.json Remove Done!!! <<<<<<<<')

        else:
            pass



    else:
        x_parm = cmds.getAttr('{}.{}'.format(object_name, hoffset))
        y_parm = cmds.getAttr('{}.{}'.format(object_name, voffset))

        if x_parm != 0 and y_parm != 0:

            single_xdict = {'x':x_parm}
            single_ydict = {'y':y_parm}

            no_key_dict.append(single_xdict)
            no_key_dict.append(single_ydict)
            no_key_dict = convert_byte_to_string.convert_byte_to_string(no_key_dict)
            with open(json_path+'/{0}_NonKey.json'.format(json_basic_name),'w') as f:
                json.dump(no_key_dict, f, indent=4)

            json_keyname = json_path + '/{0}_Key.json'.format(json_basic_name)
            print(json_keyname)
            if os.path.isfile(json_keyname):
                os.remove(json_keyname)
                print('>>>>>>>>> _Key.json Remove Done!!! <<<<<<<<')

            else:
                pass

        else:
            pass
