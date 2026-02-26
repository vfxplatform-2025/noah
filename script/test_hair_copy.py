#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for hair export with namespace objects
"""

import maya.cmds as cmds
import maya.mel as mel
import tempfile
import os
import subprocess

def test_copy_paste_between_sessions():
    """
    Test if we can copy objects with namespace and paste in another Maya session
    """
    
    # Method 1: Using Maya's clipboard file
    # Maya stores clipboard data in a temporary file
    clipboard_file = os.path.join(tempfile.gettempdir(), "maya_clipboard.ma")
    
    # Select hair objects
    selected = cmds.ls(sl=True)
    if not selected:
        print("No objects selected")
        return False
        
    print("Selected objects:", selected)
    
    # Export selection to temp file
    temp_export = os.path.join(tempfile.gettempdir(), "hair_export_temp.ma")
    
    try:
        # Export selected as Maya ASCII
        cmds.file(temp_export, force=True, options="v=0;", typ="mayaAscii", pr=True, es=True)
        print("Exported to:", temp_export)
        
        # Launch standalone Maya and import
        maya_py_code = '''
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

# Import the file
cmds.file("{}", i=True, type="mayaAscii", ignoreVersion=True, mergeNamespacesOnClash=0, namespace="hair_import", pr=True)
print("Import successful")

# List imported objects
imported = cmds.ls("hair_import:*", type="transform")
print("Imported objects:", imported)
'''.format(temp_export)
        
        # Save code to temp file
        py_file = os.path.join(tempfile.gettempdir(), "test_import.py")
        with open(py_file, 'w') as f:
            f.write(maya_py_code)
            
        # Run mayapy
        mayapy_path = os.path.join(os.environ.get('MAYA_LOCATION', '/usr/autodesk/maya'), 'bin', 'mayapy')
        if os.path.exists(mayapy_path):
            result = subprocess.check_output([mayapy_path, py_file])
            print("Mayapy result:", result)
            return True
        else:
            print("mayapy not found at:", mayapy_path)
            
    except Exception as e:
        print("Error:", str(e))
        return False
        
    return True


def export_hair_with_namespace():
    """
    Export hair objects preserving namespace
    """
    selected = cmds.ls(sl=True)
    hair_objects = []
    
    # Filter objects with 'hair' in name
    for obj in selected:
        if 'hair' in obj.lower():
            hair_objects.append(obj)
            
    if not hair_objects:
        cmds.warning("No hair objects found in selection")
        return None
        
    print("Hair objects found:", hair_objects)
    
    # Create export data
    export_data = {
        'objects': hair_objects,
        'namespaces': {},
        'connections': []
    }
    
    # Get namespace info
    for obj in hair_objects:
        if ':' in obj:
            namespace = obj.split(':')[0]
            export_data['namespaces'][namespace] = True
            
    return export_data


if __name__ == "__main__":
    # Test the functionality
    test_copy_paste_between_sessions()