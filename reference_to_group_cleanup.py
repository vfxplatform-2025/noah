#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to convert reference hair data to match group (copy/paste) structure
This script should be integrated into mayaHairScript.py
"""

import maya.cmds as cmds
import maya.mel as mel

def convert_reference_to_editable_hair(hair_objects):
    """
    Convert reference hair objects to editable structure matching copy/paste result
    
    Args:
        hair_objects (list): List of hair object names with namespace
        
    Returns:
        list: List of converted editable hair objects
    """
    
    print("=== Converting Reference Hair to Editable Structure ===")
    
    # Extract namespace from hair objects
    namespace = ""
    if hair_objects and ':' in hair_objects[0]:
        namespace = hair_objects[0].split(':')[0]
        print("Detected namespace:", namespace)
    
    # Step 1: Import the reference to make it editable
    try:
        # Find all reference files related to the namespace
        ref_files = cmds.file(query=True, reference=True)
        for ref_file in ref_files:
            ref_namespace = cmds.file(ref_file, query=True, namespace=True)
            if namespace in ref_namespace:
                print("Importing reference file:", ref_file)
                cmds.file(ref_file, importReference=True)
                break
    except Exception as e:
        print("Warning: Could not import reference automatically:", str(e))
        print("Proceeding with existing objects...")
    
    # Step 2: Delete unwanted objects
    unwanted_patterns = [
        namespace + ':body_all',
        namespace + ':teeth', 
        namespace + ':HairGeoGrp',
        namespace + ':dmm_GRP'
    ]
    
    print("Deleting unwanted objects...")
    for pattern in unwanted_patterns:
        if cmds.objExists(pattern):
            try:
                cmds.delete(pattern)
                print("Deleted:", pattern)
            except Exception as e:
                print("Could not delete {}:".format(pattern), str(e))
        else:
            # Try wildcard pattern
            found_objects = cmds.ls(pattern.replace(namespace + ':', '*:'))
            for obj in found_objects:
                if cmds.objExists(obj):
                    try:
                        cmds.delete(obj)
                        print("Deleted:", obj)
                    except Exception as e:
                        print("Could not delete {}:".format(obj), str(e))
    
    # Step 3: Delete all selection sets with namespace
    print("Cleaning up selection sets...")
    all_sets = cmds.ls(type='objectSet')
    deleted_sets = []
    
    for set_node in all_sets:
        # Skip default Maya sets
        if set_node in ['defaultObjectSet', 'defaultLightSet', 'initialShadingGroup', 'initialParticleSE']:
            continue
            
        # Delete sets with our namespace or pasted__ prefix
        if (namespace in set_node or 
            'pasted__' in set_node or
            set_node.startswith('Default') or  # Default Maya filter sets
            'Filter' in set_node):
            try:
                cmds.delete(set_node)
                deleted_sets.append(set_node)
            except:
                pass
    
    print("Deleted {} selection sets".format(len(deleted_sets)))
    
    # Step 4: Delete specific area sets
    area_patterns = [
        'eyeBrowArea', 'eyeBrowLineArea', 'eyeLidArea', 'eyeLidMainArea', 
        'eyeLidOuterArea', 'eyeLidOuterAreaLeft', 'lipArea', 'lipFalloffArea', 
        'lipMainArea'
    ]
    
    for area in area_patterns:
        # Check both with namespace and without
        for pattern in [namespace + ':' + area, area]:
            if cmds.objExists(pattern):
                try:
                    cmds.delete(pattern)
                    print("Deleted area set:", pattern)
                except:
                    pass
    
    # Step 5: Hide rig (don't delete, just hide)
    rig_patterns = [namespace + ':rig', 'rig']
    for rig_pattern in rig_patterns:
        if cmds.objExists(rig_pattern):
            try:
                cmds.hide(rig_pattern)
                print("Hidden rig:", rig_pattern)
                break
            except:
                pass
    
    # Step 6: Clean up namespaces if possible
    try:
        # Remove empty namespaces
        all_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        for ns in all_namespaces:
            if ns not in ['UI', 'shared'] and namespace in ns:
                try:
                    # Move objects to root namespace
                    objects_in_ns = cmds.namespaceInfo(ns, listOnlyDependencyNodes=True)
                    if objects_in_ns:
                        for obj in objects_in_ns:
                            if cmds.objExists(obj):
                                try:
                                    # Remove namespace from object name
                                    new_name = obj.split(':')[-1]
                                    if not cmds.objExists(new_name):
                                        cmds.rename(obj, new_name)
                                        print("Renamed {} to {}".format(obj, new_name))
                                except:
                                    pass
                    
                    # Try to remove namespace
                    cmds.namespace(removeNamespace=ns, mergeNamespaceWithRoot=True)
                    print("Removed namespace:", ns)
                except Exception as e:
                    print("Could not remove namespace {}:".format(ns), str(e))
    except Exception as e:
        print("Warning during namespace cleanup:", str(e))
    
    # Step 7: Find the hair objects after cleanup
    # Look for hair objects that should now be without namespace
    cleaned_hair_objects = []
    for hair_obj in hair_objects:
        # Try original name
        if cmds.objExists(hair_obj):
            cleaned_hair_objects.append(hair_obj)
        else:
            # Try without namespace
            no_ns_name = hair_obj.split(':')[-1]
            if cmds.objExists(no_ns_name):
                cleaned_hair_objects.append(no_ns_name)
            else:
                # Search for hair objects
                found_hair = cmds.ls('*hair*', type='transform')
                cleaned_hair_objects.extend(found_hair)
                break
    
    if not cleaned_hair_objects:
        # Last resort: find any remaining hair-related objects
        cleaned_hair_objects = cmds.ls('*hair*', type='transform')
    
    print("Converted hair objects:", cleaned_hair_objects)
    print("=== Reference to Group Conversion Complete ===")
    
    return cleaned_hair_objects


def test_conversion():
    """Test function to be run in Maya"""
    # Test with current scene objects
    test_objects = ['c0082ma_e200_kite:c0078ma_e200_romi_daily:hair']
    result = convert_reference_to_editable_hair(test_objects)
    print("Test result:", result)


if __name__ == "__main__":
    # This can be run standalone for testing
    print("Use this script by importing and calling convert_reference_to_editable_hair(hair_objects)")