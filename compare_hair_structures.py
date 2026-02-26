#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compare hair structures between copy/paste group and reference export
"""

import socket
import sys

def send_maya_command(command, host='localhost', port=4434):
    """Send command to Maya via command port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # Send command
        sock.send(command.encode('utf-8'))
        
        # Receive response
        response = ""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data.decode('utf-8')
        
        sock.close()
        return response.strip()
    except Exception as e:
        return "Error: " + str(e)

# Step 1: Get children of both structures
print("=== Comparing Hair Structures ===")

# Get children of 'group' (copy/paste version)
cmd_group = '''
import maya.cmds as cmds
group_children = cmds.listRelatives('group', children=True, fullPath=True) or []
print("Group children count:", len(group_children))
for child in sorted(group_children):
    print("  -", child)
'''

print("\n1. Getting 'group' structure:")
result = send_maya_command(cmd_group)
print(result)

# Get children of reference version
cmd_ref = '''
import maya.cmds as cmds
ref_root = 'c0082ma_e200_kite:c0078ma_e200_romi_daily:root'
if cmds.objExists(ref_root):
    ref_children = cmds.listRelatives(ref_root, children=True, fullPath=True) or []
    print("Reference children count:", len(ref_children))
    for child in sorted(ref_children):
        print("  -", child)
else:
    print("Reference root not found")
'''

print("\n2. Getting reference structure:")
result = send_maya_command(cmd_ref)
print(result)

# Compare node types
cmd_compare_types = '''
import maya.cmds as cmds

def get_all_descendents(root):
    """Get all descendents with their types"""
    descendents = {}
    if not cmds.objExists(root):
        return descendents
        
    all_desc = cmds.listRelatives(root, allDescendents=True, fullPath=True) or []
    for node in all_desc:
        node_type = cmds.nodeType(node)
        short_name = node.split('|')[-1]
        descendents[short_name] = {
            'fullPath': node,
            'type': node_type,
            'parent': cmds.listRelatives(node, parent=True, fullPath=True)[0] if cmds.listRelatives(node, parent=True) else None
        }
    return descendents

# Get structures
group_desc = get_all_descendents('group')
ref_desc = get_all_descendents('c0082ma_e200_kite:c0078ma_e200_romi_daily:root')

# Find differences
group_names = set(group_desc.keys())
ref_names = set(ref_desc.keys())

only_in_ref = ref_names - group_names
only_in_group = group_names - ref_names

print("\\n=== Nodes only in reference (to be deleted) ===")
print("Count:", len(only_in_ref))
for node in sorted(only_in_ref):
    print(f"  - {node} ({ref_desc[node]['type']})")

print("\\n=== Nodes only in group ===")
print("Count:", len(only_in_group))
for node in sorted(only_in_group):
    print(f"  - {node} ({group_desc[node]['type']})")
'''

print("\n3. Comparing node structures:")
result = send_maya_command(cmd_compare_types)
print(result)

# Check for specific problematic nodes
cmd_check_specific = '''
import maya.cmds as cmds

ref_root = 'c0082ma_e200_kite:c0078ma_e200_romi_daily:root'

# Check for common problematic nodes in reference
problematic_patterns = [
    '*:body_all', '*:teeth', '*:HairGeoGrp', '*:dmm_GRP',
    '*:rig', '*:*_CON', '*:*_CON_0'
]

print("\\n=== Checking for problematic nodes in reference ===")
for pattern in problematic_patterns:
    nodes = cmds.ls(ref_root + '|' + pattern, recursive=True)
    if nodes:
        print(f"Found {pattern}:")
        for node in nodes:
            print(f"  - {node}")

# Check for sets
all_sets = cmds.ls(type='objectSet')
ref_sets = [s for s in all_sets if 'c0082ma_e200_kite' in s or 'c0078ma_e200_romi_daily' in s]
if ref_sets:
    print("\\n=== Reference related sets ===")
    for s in ref_sets:
        print(f"  - {s}")
'''

print("\n4. Checking for problematic nodes:")
result = send_maya_command(cmd_check_specific)
print(result)

print("\n=== Analysis Complete ===")