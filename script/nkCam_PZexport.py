import json
import maya.cmds as cmds
import os
from script import convert_byte_to_string

def nkCam_exportJson(savePath, baseName, selCam):
    print(">>> ready to nkCam_exportJson <<<")
    save_path = savePath
    save_name = baseName + "_nkCam.json"
    selCam = selCam
    print("save path", save_path)
    print("save_name", save_name)
    print("selCam", selCam)

# def nkCam_exportJson():
#     save_path = "/show/NORYANG/seq/HUR/HUR_0140/ani/wip/data/json"
#     save_name = "HUR_0140_ani_v03_w08" + "_nkCam.json"
#     selCam = "HUR_0140_cam"

    panX_key = cmds.keyframe(selCam, attribute="horizontalPan", query=True)
    panY_key = cmds.keyframe(selCam, attribute="verticalPan", query=True)
    zoom_key = cmds.keyframe(selCam, attribute="zoom", query=True)

    panX_dict = {}
    panY_dict = {}
    zoom_dict = {}

    for i in panX_key:
        panX_attr = cmds.getAttr('{}.{}'.format(selCam, "horizontalPan"), time=i)
        panX_dict[i] = panX_attr

    for i in panY_key:
        panY_attr = cmds.getAttr('{}.{}'.format(selCam, "verticalPan"), time=i)
        panY_dict[i] = panY_attr

    for i in zoom_key:
        zoom_attr = cmds.getAttr('{}.{}'.format(selCam, "zoom"), time=i)
        zoom_dict[i] = zoom_attr

    panZoom_dict = {"panX": panX_dict, "panY": panY_dict, "zoom": zoom_dict}

    json_path = os.path.join(save_path, save_name)

    with open(json_path, 'w') as json_file:
        panZoom_dict = convert_byte_to_string.convert_byte_to_string(panZoom_dict)
        json.dump(panZoom_dict, json_file, indent=4)
        print(">>> nkCam_exportJson Done!! <<<")


