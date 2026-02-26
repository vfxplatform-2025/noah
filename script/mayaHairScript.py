# -*- coding:utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel

from . import utilScript
import imp
imp.reload(utilScript)
from . import takeScript
imp.reload(takeScript)
from . import vdbScript
imp.reload(vdbScript)


def mayaHairExport(fileName, itemdir, itemList, fileType, mayaExt, mayaAlembic, frameType):  # Hair export function

    fileinfo = {}

    # Hair Export Workflow
    print("=== Hair Export Workflow Started ===")
    print("Selected items:", itemList)
    
    # Use itemList directly (no filtering needed)
    hair_objects = itemList
    
    if not hair_objects:
        cmds.warning("No objects found in selection")
        return fileinfo
    
    print("Hair objects to export:", hair_objects)
    
    import os
    import subprocess
    
    # Extract asset name from selected hair object name (선택한 데이터 이름)
    selected_hair_name = hair_objects[0]  
    if ':' in selected_hair_name:
        full_namespace = selected_hair_name.split(':')[0]  # c0078ma_e200_romi_daily
        # Extract only the character name part (after the last underscore of episode info)
        # c0078ma_e200_romi_daily -> romi_daily
        if '_e' in full_namespace:
            # Find the pattern like 'c0078ma_e200_' and remove it
            import re
            match = re.search(r'([a-z]\d+[a-z]+_e\d+_)(.*)', full_namespace)
            if match:
                asset_name = match.group(2)  # romi_daily
            else:
                asset_name = full_namespace
        else:
            asset_name = full_namespace
    else:
        asset_name = selected_hair_name
    
    print("Asset name:", asset_name)
    
    # Get current scene file path and create output directory
    current_scene = cmds.file(query=True, sceneName=True)
    if current_scene:
        scene_dir = os.path.dirname(current_scene)
        # wip 디렉토리에서 data/hair 디렉토리로 변경
        if '/wip/' in scene_dir:
            base_path = scene_dir.split('/wip/')[0]
            output_dir = os.path.join(base_path, 'wip', 'data', 'hair')
        else:
            # wip이 없으면 현재 디렉토리에 data/hair 추가
            output_dir = os.path.join(scene_dir, 'data', 'hair')
    else:
        # 씬이 저장되지 않은 경우에도 hair export는 고정 경로 사용
        # itemdir 대신 기본 hair 경로 사용
        output_dir = os.path.join(os.path.dirname(os.getcwd()), 'wip', 'data', 'hair')
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("Output directory:", output_dir)
    
    # Extract scene name from current scene file
    scene_basename = ""
    if current_scene:
        scene_basename = os.path.basename(current_scene)
        # Remove extension (.mb or .ma)
        scene_basename = os.path.splitext(scene_basename)[0]
        print("Scene name:", scene_basename)
    
    # Create final output file path with scene name and character name
    if scene_basename:
        # tpm2_214_260_2505_v32_w02_romi_daily_hair.mb
        output_filename = "{}_{}_hair.{}".format(scene_basename, asset_name, mayaExt)
    else:
        # Fallback to original naming if no scene name
        output_filename = "{}_hair.{}".format(asset_name, mayaExt)
    
    final_output_file = os.path.join(output_dir, output_filename)
    
    # Convert hair objects to root objects for export
    export_objects = []
    for hair_obj in hair_objects:
        if ':hair' in hair_obj:
            # c0078ma_e200_romi_daily:hair -> c0078ma_e200_romi_daily:root
            root_obj = hair_obj.replace(':hair', ':root')
            export_objects.append(root_obj)
        elif ':root' in hair_obj:
            # Already root, use as is
            export_objects.append(hair_obj)
        else:
            # No namespace or different format, use as is
            export_objects.append(hair_obj)
    
    print("Original objects:", hair_objects)
    print("Export objects (converted to root):", export_objects)
    
    # Select root objects and export
    cmds.select(export_objects)
    
    print("Exporting hair objects directly to final location...")
    print("Output file:", final_output_file)
    print("Selected objects for export:", cmds.ls(selection=True))
    
    # Export selected hair objects to final location
    export_success = False
    
    # Try export as Maya Binary first
    try:
        if mayaExt == "mb":
            cmds.file(final_output_file, force=True, options="v=0;", typ="mayaBinary", pr=True, es=True)
            print("Exported hair objects as Maya Binary to:", final_output_file)
        else:
            cmds.file(final_output_file, force=True, options="v=0;", typ="mayaAscii", pr=True, es=True)
            print("Exported hair objects as Maya ASCII to:", final_output_file)
        export_success = True
    except Exception as e:
        print("Export failed:", str(e))
        raise Exception("Export failed. Please check if objects are accessible.")
    
    if not export_success:
        raise Exception("Export failed. Please check if objects are accessible.")
    
    # Create standalone Maya script using string concatenation to avoid format issues
    standalone_script = '''
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel

# Disable VRay and other plugin warnings
try:
    import maya.utils
    maya.utils.MayaGUILogHandler()
except:
    pass

# Set batch mode to avoid UI-related issues
cmds.scriptEditorInfo(suppressWarnings=True, suppressInfo=True)

print("=== Standalone Maya Hair Processing ===")

# Variables
hair_file = "''' + final_output_file + '''"
asset_name = "''' + asset_name + '''"

# Step 1: Open the exported hair file directly
try:
    file_type = "mayaBinary" if hair_file.endswith(".mb") else "mayaAscii"
    print("Step 1: Opening hair file:", hair_file, "as", file_type)
    cmds.file(hair_file, open=True, force=True, type=file_type, ignoreVersion=True)
    print("Step 1: Successfully opened exported hair file")
except Exception as e:
    print("Step 1 ERROR:", str(e))
    import sys
    sys.exit(1)

# Step 3: Detect namespace structure
print("Step 3: Detecting namespace structure...")
try:
    all_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
    nested_namespace = None
    target_namespace = None

    print("Step 3: All namespaces found:", all_namespaces)

    # Look for nested namespace pattern (c0082ma_e200_kite:c0078ma_e200_romi_daily)
    for ns in all_namespaces:
        if ns not in ['UI', 'shared']:
            if 'c0082ma_e200_kite' in ns and 'c0078ma_e200_romi_daily' in ns:
                nested_namespace = ns
                target_namespace = 'c0078ma_e200_romi_daily'
                print("Step 3: Found nested namespace pattern")
            elif 'c0078ma_e200_romi_daily' in ns:
                target_namespace = ns
                print("Step 3: Found single namespace pattern")
            break

    print("Step 3: Nested namespace:", nested_namespace)
    print("Step 3: Target namespace:", target_namespace)
except Exception as e:
    print("Step 3 ERROR:", str(e))

# Step 4: Import reference to make it editable (if still referenced)
try:
    ref_files = cmds.file(query=True, reference=True)
    for ref_file in ref_files:
        ref_namespace = cmds.file(ref_file, query=True, namespace=True)
        if target_namespace and target_namespace in ref_namespace:
            print("Importing reference file:", ref_file)
            cmds.file(ref_file, importReference=True)
            break
except Exception as e:
    print("Warning: Could not import reference automatically:", str(e))

# Step 5: Delete unwanted objects (based on actual Maya port comparison)
delete_namespace = nested_namespace if nested_namespace else target_namespace

if delete_namespace:
    unwanted_patterns = [
        delete_namespace + ':body_geo_grp',
        delete_namespace + ':body_all',
        delete_namespace + ':Low_Geo_Grp',
        delete_namespace + ':eye',
        delete_namespace + ':hairtie',
        delete_namespace + ':teeth',
        delete_namespace + ':HairGeoGrp',
        delete_namespace + ':dmm_GRP'
    ]
    
    print("Deleting unwanted objects...")
    for pattern in unwanted_patterns:
        if cmds.objExists(pattern):
            try:
                cmds.delete(pattern)
                print("Deleted:", pattern)
            except Exception as e:
                print("Could not delete:", pattern, str(e))

# Step 6: Delete specific selection sets only
print("Cleaning up specific selection sets...")
if delete_namespace:
    specific_sets_to_delete = [
        delete_namespace + ':Sets',
        delete_namespace + ':AniControlSet',
        delete_namespace + ':bake_hairSet',
        delete_namespace + ':ControlSet',
        delete_namespace + ':FaceAllSet',
        delete_namespace + ':FaceControlSet',
        delete_namespace + ':geoSet',
        delete_namespace + ':set2',
        delete_namespace + ':smoSet2',
        # Additional face-related sets
        delete_namespace + ':FaceAreas',
        delete_namespace + ':eyeBrowArea',
        delete_namespace + ':eyeBrowLineArea',
        delete_namespace + ':eyeLidArea',
        delete_namespace + ':eyeLidMainArea',
        delete_namespace + ':eyeLidOuterArea',
        delete_namespace + ':eyeLidOuterAreaLeft',
        delete_namespace + ':lipArea',
        delete_namespace + ':lipFalloffArea',
        delete_namespace + ':lipMainArea'
    ]
    
    for set_name in specific_sets_to_delete:
        if cmds.objExists(set_name):
            try:
                cmds.delete(set_name)
                print("Deleted specific set:", set_name)
            except Exception as e:
                print("Could not delete set:", set_name, str(e))

# Step 7: Hide rig (don't delete)
if delete_namespace:
    # Try different rig naming patterns
    rig_patterns = [
        delete_namespace + ':rig',
        delete_namespace + ':RIG', 
        delete_namespace + ':Rig',
        delete_namespace + ':rig_GRP',
        delete_namespace + ':RIG_GRP'
    ]
    
    print("Looking for rig objects...")
    rig_found = False
    
    for rig_pattern in rig_patterns:
        if cmds.objExists(rig_pattern):
            try:
                # Unlock the rig object and visibility attribute
                cmds.lockNode(rig_pattern, lock=False)
                print("Unlocked rig node:", rig_pattern)
                
                # Unlock visibility attribute specifically
                visibility_attr = rig_pattern + ".v"
                if cmds.objExists(visibility_attr):
                    cmds.setAttr(visibility_attr, lock=False)
                    print("Unlocked visibility attribute:", visibility_attr)
                
                cmds.hide(rig_pattern)
                print("Hidden rig:", rig_pattern)
                rig_found = True
            except Exception as e:
                print("Could not hide rig:", rig_pattern, str(e))
    
    # If no standard rig pattern found, search for any rig-related objects
    if not rig_found:
        print("No standard rig pattern found, searching for rig-related objects...")
        all_objects = cmds.ls(delete_namespace + ':*', type='transform')
        for obj in all_objects:
            if 'rig' in obj.lower() or 'ctrl' in obj.lower() or 'control' in obj.lower():
                try:
                    # Unlock the rig object and visibility attribute
                    cmds.lockNode(obj, lock=False)
                    print("Unlocked rig node:", obj)
                    
                    # Unlock visibility attribute specifically
                    visibility_attr = obj + ".v"
                    if cmds.objExists(visibility_attr):
                        cmds.setAttr(visibility_attr, lock=False)
                        print("Unlocked visibility attribute:", visibility_attr)
                    
                    cmds.hide(obj)
                    print("Hidden rig object:", obj)
                    rig_found = True
                except:
                    pass
    
    if not rig_found:
        print("No rig objects found to hide")

# Step 7.5: Hide geo object as well
if delete_namespace:
    geo_pattern = delete_namespace + ':geo'
    if cmds.objExists(geo_pattern):
        try:
            # Unlock the geo object and visibility attribute
            cmds.lockNode(geo_pattern, lock=False)
            print("Unlocked geo node:", geo_pattern)
            
            # Unlock visibility attribute specifically
            visibility_attr = geo_pattern + ".v"
            if cmds.objExists(visibility_attr):
                cmds.setAttr(visibility_attr, lock=False)
                print("Unlocked visibility attribute:", visibility_attr)
            
            cmds.hide(geo_pattern)
            print("Hidden geo:", geo_pattern)
        except Exception as e:
            print("Could not hide geo:", geo_pattern, str(e))
    else:
        print("No geo object found to hide")

# Step 7.6: Set pfx_Vis attributes to 2 if they exist
print("=== Setting pfx_Vis attributes ===")
if delete_namespace:
    # Find all objects with .pfx_Vis attribute
    all_objects = cmds.ls(delete_namespace + ':*', type='transform')
    for obj in all_objects:
        pfx_vis_attr = obj + '.pfx_Vis'
        if cmds.objExists(pfx_vis_attr):
            try:
                cmds.setAttr(pfx_vis_attr, 2)
                print("Set pfx_Vis to 2 for:", obj)
            except Exception as e:
                print("Could not set pfx_Vis for:", obj, str(e))

# Step 8: Create group and rename for root and world_dummy
print("=== Creating and renaming groups ===")
target_objects = []

# Find root and world_dummy objects
if target_namespace:
    root_obj = target_namespace + ':root'
    world_dummy_obj = 'world_dummy'
    
    if cmds.objExists(root_obj):
        target_objects.append(root_obj)
        print("Found root object:", root_obj)
    
    if cmds.objExists(world_dummy_obj):
        target_objects.append(world_dummy_obj)
        print("Found world_dummy object:", world_dummy_obj)

# If we have target objects, group them and rename
if target_objects:
    try:
        # Create group with asset name
        group_name = asset_name + "_hair"
        new_group = cmds.group(target_objects, name=group_name)
        print("Created group", group_name, "containing:", target_objects)
    except Exception as e:
        print("Could not create group:", str(e))
        # Fallback: try to rename the first object found
        if target_objects:
            try:
                renamed = cmds.rename(target_objects[0], asset_name + "_hair")
                print("Fallback: Renamed", target_objects[0], "to", renamed)
            except Exception as e2:
                print("Fallback rename failed:", str(e2))
else:
    # If no specific objects found, try the old method
    print("No specific root/world_dummy found, trying top-level transforms...")
    top_level_transforms = cmds.ls(assemblies=True)
    for transform in top_level_transforms:
        if target_namespace and target_namespace in transform:
            new_name = asset_name + "_hair"
            try:
                cmds.rename(transform, new_name)
                print("Renamed root group to:", new_name)
                break
            except:
                print("Could not rename:", transform)

# Step 9: Clean up shaders using Maya's delete unused nodes
print("=== Cleaning up shaders with MLdeleteUnused ===")
try:
    mel.eval('MLdeleteUnused;')
    print("Cleaned up unused shaders and materials with MLdeleteUnused")
except Exception as e:
    print("Warning: Could not run MLdeleteUnused for shaders:", str(e))

# Step 9.5: Additional cleanup before save
print("=== Final cleanup before save ===")
try:
    # Clean unknown nodes again
    unknown_nodes = cmds.ls(type="unknown")
    if unknown_nodes:
        for node in unknown_nodes:
            try:
                if cmds.objExists(node):
                    cmds.lockNode(node, lock=False)
                    cmds.delete(node)
                    print("Deleted unknown node before save:", node)
            except:
                pass
    
    # Clean unknown plugins again
    unknown_plugins = cmds.unknownPlugin(q=True, list=True) or []
    for plugin in unknown_plugins:
        try:
            cmds.unknownPlugin(plugin, remove=True)
            print("Removed unknown plugin before save:", plugin)
        except:
            pass
    
    # Set strip options again
    mel.eval('optionVar -iv "fileOptionsStripEnable" 1;')
    mel.eval('optionVar -iv "fileOptionsStripLevel" 1;')
    
    # Run MLdeleteUnused one more time
    mel.eval('MLdeleteUnused;')
    print("Final cleanup completed")
except Exception as e:
    print("Warning during final cleanup:", str(e))

print("Hair cleanup completed")

# Step 10: Save the cleaned file (overwrite the original)
try:
    cmds.file(save=True, force=True)
    print("Saved cleaned hair file to:", hair_file)
    
    # Exit with success code
    import sys
    sys.exit(0)
except Exception as e:
    print("Error saving file:", str(e))
    # Still try to exit cleanly
    import sys
    sys.exit(1)
finally:
    try:
        maya.standalone.uninitialize()
        print("Standalone Maya session ended")
    except:
        pass
'''
    
    # Format the script with actual values
    print("Formatting script with values:")
    print("- hair_file:", final_output_file)
    print("- asset_name:", asset_name)
    
    # No need for format() since we use string concatenation
    script_content = standalone_script
    print("Script content ready")
    
    # Save script to temp file with timestamp for debugging
    import time
    import tempfile
    timestamp = str(int(time.time()))
    script_file = os.path.join(tempfile.gettempdir(), "process_hair_standalone_{}.py".format(timestamp))
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # Run standalone Maya
    cleanup_success = False
    mayapy_path = os.path.join(os.environ.get('MAYA_LOCATION', '/usr/autodesk/maya'), 'bin', 'mayapy')
    if os.path.exists(mayapy_path):
        try:
            print("Running standalone Maya to clean up hair file...")
            result = subprocess.check_output([mayapy_path, script_file], stderr=subprocess.STDOUT)
            print("Standalone output:", result)
            
            # Add to file info for task json recording
            # Use the same naming as the exported file (without extension)
            json_key = os.path.splitext(os.path.basename(final_output_file))[0]
            fileinfo[json_key] = final_output_file
            
            print("Hair export and cleanup completed successfully!")
            print("Final file:", final_output_file)
            cleanup_success = True
            
        except subprocess.CalledProcessError as e:
            print("Error running standalone Maya cleanup:", e)
            print("Output:", e.output)
            print("Debug script saved at:", script_file)
    else:
        print("mayapy not found at:", mayapy_path)
        
    # Clean up script file (but keep for debugging if error occurred)
    try:
        if cleanup_success:  # Only remove script if successful
            os.remove(script_file)
            print("Cleaned up script file")
        else:
            print("Kept script file for debugging:", script_file)
    except:
        pass
    
    print("=== Hair Export Workflow Completed ===")
    cmds.refresh(su=0)
    return fileinfo


def mayaHairImport(itemInfo, type, rootType, projName):
    mentalNode = cmds.ls(['mentalrayGlobals', 'mentalrayItemsList'])

    if mentalNode:
        cmds.delete(mentalNode)

    for i in itemInfo:
        print (i)
        # name = "%s1:output_SET" %i
        if "import" in type or "None" in type:
            writeItemName = mayaImportFile(i, itemInfo[i], rootType)

        elif "reference" in type:
            writeItemName = mayaReferenceFile(i, itemInfo[i], rootType)

    vdbScript.cloudVDB(projName)

    return writeItemName


def mayaImportFile(itemName, itemDir, rootType):
    # check oBject
    if ":" in itemName:
        name = itemName.split(":")[1]
    else:
        name = itemName

    if cmds.ls(name):
        cmds.confirmDialog(title='Message', message=" Delete \"%s \"!!   Please! File Check!" % name, button=['ok'])
        return

    mayaExt = itemDir.split(".")[-1]
    if mayaExt == "mb":
        mayaType = "mayaBinary"
    if mayaExt == "ma":
        mayaType = "mayaAscii"

    cmds.file("%s" % itemDir, i=True, type=mayaType, ignoreVersion=True, \
              mergeNamespacesOnClash=0, options="v=0", pr=True, loadReferenceDepth="all", returnNewNodes=1)

    writeItemName = setWirteItme(rootType, name, itemDir)
    return writeItemName


def mayaReferenceFile(itemName, itemDir, rootType):
    mayaExt = itemDir.split(".")[-1]
    if mayaExt == "mb":
        mayaType = "mayaBinary"
    if mayaExt == "ma":
        mayaType = "mayaAscii"

    if cmds.ls(itemName):
        cmds.file("%s" % itemDir,
                  loadReference="%s" % itemName,
                  type=mayaType, options="v=0;")

        #setWirteItme(rootType, itemName, itemDir)
        writeItemName = initMayaItemImportWrite(itemName, itemDir, rootType)
        return

    cmds.file("%s" % itemDir,
              r=1, gl=1, type=mayaType, ignoreVersion=1,
              namespace=":",
              mergeNamespacesOnClash=True, options="v=0;")

    #writeItemName = setWirteItme(rootType, itemName, itemDir)
    writeItemName = initMayaItemImportWrite(itemName, itemDir, rootType)
    return writeItemName


def setWirteItme(rootType, itemName, itemDir):

    writeItemName = initMayaItemImportWrite(itemName, itemDir, rootType)

    return writeItemName

# write
def initMayaItemImportWrite(itemName, itemDir, rootType):
    mayaObj = cmds.ls('%s' % itemName, r=1)[0]
    if not cmds.ls('%s.%s' % (mayaObj, rootType)):
        cmds.addAttr('%s' % mayaObj, ln=rootType, dt="string")

    cmds.setAttr('%s.%s' % (mayaObj, rootType), "%s,%s" % (itemName, itemDir), type="string")
    return '%s.%s' % (mayaObj, rootType)