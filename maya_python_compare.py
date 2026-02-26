#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maya Python command comparison
"""

import socket
import time

def send_maya_python_command(command, host='localhost', port=4434):
    """Send Python command to Maya via command port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # Format as Python command
        python_cmd = 'python("{}");'.format(command.replace('"', '\\"').replace('\n', '\\n'))
        sock.send(python_cmd.encode('utf-8'))
        
        # Receive response
        sock.settimeout(5)
        response = ""
        try:
            data = sock.recv(8192)
            if data:
                response = data.decode('utf-8')
        except socket.timeout:
            response = "Response timeout"
        
        sock.close()
        return response.strip()
    except Exception as e:
        return "Error: " + str(e)

print("=== Maya Python Hair Structure Comparison ===")

# Step 1: Check if objects exist
print("\n1. Checking if objects exist:")
check_cmd = "import maya.cmds as cmds\\ngroup_exists = cmds.objExists('group')\\nref_exists = cmds.objExists('c0082ma_e200_kite:c0078ma_e200_romi_daily:root')\\nprint('group exists:', group_exists)\\nprint('reference exists:', ref_exists)"

result = send_maya_python_command(check_cmd)
print(result)

# Step 2: Get children info
print("\n2. Getting children info:")
children_cmd = "import maya.cmds as cmds\\nif cmds.objExists('group'):\\n    group_children = cmds.listRelatives('group', children=True) or []\\n    print('Group children count:', len(group_children))\\n    for i, child in enumerate(group_children[:5]):\\n        print('  ', i, child)\\nelse:\\n    print('Group not found')\\nif cmds.objExists('c0082ma_e200_kite:c0078ma_e200_romi_daily:root'):\\n    ref_children = cmds.listRelatives('c0082ma_e200_kite:c0078ma_e200_romi_daily:root', children=True) or []\\n    print('Reference children count:', len(ref_children))\\n    for i, child in enumerate(ref_children[:5]):\\n        print('  ', i, child)\\nelse:\\n    print('Reference not found')"

result = send_maya_python_command(children_cmd)
print(result)

print("\n=== Comparison Complete ===")