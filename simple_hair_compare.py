#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple hair structure comparison
"""

import socket
import time

def send_maya_command(command, host='localhost', port=4434):
    """Send command to Maya via command port with timeout"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        sock.connect((host, port))
        
        # Send command
        sock.send(command.encode('utf-8'))
        
        # Receive response with timeout
        sock.settimeout(5)  # 5 seconds for response
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

print("=== Simple Hair Structure Comparison ===")

# Step 1: Check if both objects exist
print("\n1. Checking if objects exist:")
check_cmd = '''
import maya.cmds as cmds
group_exists = cmds.objExists('group')
ref_exists = cmds.objExists('c0082ma_e200_kite:c0078ma_e200_romi_daily:root')
print("group exists:", group_exists)
print("reference exists:", ref_exists)
'''

result = send_maya_command(check_cmd)
print(result)

# Step 2: Get basic info about both
print("\n2. Getting basic structure info:")
info_cmd = '''
import maya.cmds as cmds

if cmds.objExists('group'):
    group_children = cmds.listRelatives('group', children=True) or []
    print("Group children count:", len(group_children))
    print("Group children:", [child for child in group_children[:5]])  # First 5 only
else:
    print("Group not found")

if cmds.objExists('c0082ma_e200_kite:c0078ma_e200_romi_daily:root'):
    ref_children = cmds.listRelatives('c0082ma_e200_kite:c0078ma_e200_romi_daily:root', children=True) or []
    print("Reference children count:", len(ref_children))
    print("Reference children:", [child for child in ref_children[:5]])  # First 5 only
else:
    print("Reference not found")
'''

result = send_maya_command(info_cmd)
print(result)

# Step 3: Look for problematic nodes in reference
print("\n3. Checking for problematic nodes in reference:")
problem_cmd = '''
import maya.cmds as cmds

ref_root = 'c0082ma_e200_kite:c0078ma_e200_romi_daily:root'

if cmds.objExists(ref_root):
    # Check for specific unwanted objects
    unwanted = ['body_all', 'teeth', 'HairGeoGrp', 'dmm_GRP']
    
    for item in unwanted:
        # Look for the object with any namespace
        search_patterns = [
            '*:' + item,
            '*:*:' + item,  # nested namespace
            item  # no namespace
        ]
        
        for pattern in search_patterns:
            found = cmds.ls(pattern)
            if found:
                print("Found unwanted object:", pattern, "->", found)
                break
    
    # Check for sets
    all_sets = cmds.ls(type='objectSet')
    namespace_sets = []
    for s in all_sets:
        if 'c0082ma_e200_kite' in s or 'c0078ma_e200_romi_daily' in s:
            namespace_sets.append(s)
    
    if namespace_sets:
        print("Found namespace sets:", len(namespace_sets))
        print("Sample sets:", namespace_sets[:3])  # First 3 only
    else:
        print("No namespace sets found")
        
else:
    print("Reference root not found")
'''

result = send_maya_command(problem_cmd)
print(result)

print("\n=== Comparison Complete ===")