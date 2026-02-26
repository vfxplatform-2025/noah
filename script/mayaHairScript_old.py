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

    #pluginCheck()
    utilScript.pluginChecks(fileType)

    fileinfo = {}

    cmds.refresh(su=1)
    if frameType == "FrameRange":
        startF = cmds.playbackOptions(min=1, q=1)
        endF = cmds.playbackOptions(max=1, q=1)
    if frameType == "CurrentFrame":
        startF = cmds.currentTime(q=1)
        endF = cmds.currentTime(q=1)

    # Hair Export Workflow
    print("=== Hair Export Workflow Started ===")
    print("Selected items:", itemList)
    
    # Filter hair objects
    hair_objects = []
    for item in itemList:
        if ':hair' in item or 'hair' in item.lower():
            hair_objects.append(item)
            
    if not hair_objects:
        cmds.warning("No hair objects found in selection (looking for ':hair' pattern)")
        return fileinfo
    
    print("Hair objects found:", hair_objects)
    
    # Export hair objects to temporary file
    import tempfile
    import os
    import subprocess
    
    temp_hair_file = os.path.join(tempfile.gettempdir(), "hair_export_temp.ma")
    
    # Clean unknown nodes and plugins before export
    print("Cleaning scene before export...")
    
    # Method 1: Use Maya's deleteUnusedBrush2 and MLdeleteUnused
    try:
        mel.eval('MLdeleteUnused;')
        print("Ran MLdeleteUnused")
    except:
        print("Warning: Could not run MLdeleteUnused")
    
    # Method 2: Clean unknown nodes
    try:
        unknown_nodes = cmds.ls(type="unknown")
        if unknown_nodes:
            print("Found {} unknown nodes: {}".format(len(unknown_nodes), unknown_nodes))
            for node in unknown_nodes:
                try:
                    if cmds.objExists(node):
                        cmds.lockNode(node, lock=False)
                        cmds.delete(node)
                        print("Deleted unknown node:", node)
                except:
                    print("Could not delete unknown node:", node)
        else:
            print("No unknown nodes found")
    except Exception as e:
        print("Warning: Error checking unknown nodes:", str(e))
    
    # Method 3: Clean unknown plugins
    try:
        # List all unknown plugins first
        unknown_plugins = cmds.unknownPlugin(q=True, list=True)
        if unknown_plugins:
            print("Found unknown plugins:", unknown_plugins)
            for plugin in unknown_plugins:
                try:
                    cmds.unknownPlugin(plugin, remove=True)
                    print("Removed unknown plugin:", plugin)
                except:
                    print("Could not remove unknown plugin:", plugin)
        else:
            print("No unknown plugins found")
    except Exception as e:
        print("Warning: Could not process unknown plugins:", str(e))
    
    # Method 4: Set file export options to ignore unknown data
    try:
        mel.eval('optionVar -iv "fileOptionsStripEnable" 1;')
        mel.eval('optionVar -iv "fileOptionsStripLevel" 1;')
        print("Set file options to strip unknown data")
    except Exception as e:
        print("Warning: Could not set strip options:", str(e))
    
    # Select only hair objects
    cmds.select(hair_objects, r=True)
    
    print("Exporting hair objects for standalone processing...")
    
    # Step 1: Simple export of selected hair objects
    export_success = False
    
    # Try export as Maya Binary first
    try:
        temp_hair_file_mb = temp_hair_file.replace('.ma', '.mb')
        cmds.file(temp_hair_file_mb, force=True, options="v=0;", typ="mayaBinary", pr=True, es=True)
        temp_hair_file = temp_hair_file_mb
        print("Exported hair objects as Maya Binary to:", temp_hair_file)
        export_success = True
    except Exception as e:
        print("Maya Binary export failed:", str(e))
        try:
            # Fallback to ASCII
            cmds.file(temp_hair_file, force=True, options="v=0;", typ="mayaAscii", pr=True, es=True)
            print("Exported hair objects as Maya ASCII to:", temp_hair_file)
            export_success = True
        except Exception as e2:
            print("Maya ASCII export also failed:", str(e2))
    
    if not export_success:
        raise Exception("Export failed. Please check if objects are accessible.")
    
    # Extract asset name from namespace (e.g., c0078ma_e200_romi_daily:hair -> romi_daily)
    namespace = hair_objects[0].split(':')[0] if ':' in hair_objects[0] else ""
    # Extract asset name from namespace pattern
    asset_name = ""
    if namespace:
        # Pattern: c0078ma_e200_romi_daily -> romi_daily
        parts = namespace.split('_')
        if len(parts) >= 4:
            asset_name = '_'.join(parts[2:])  # Get romi_daily from c0078ma_e200_romi_daily
        else:
            asset_name = namespace
    
    # Create standalone Maya script
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

# Step 1: Create new scene
try:
    cmds.file(new=True, force=True)
    print("Step 1: Created new scene")
except Exception as e:
    print("Step 1 ERROR:", str(e))
    import sys
    sys.exit(1)

# Step 2: Import the hair file  
try:
    file_type = "mayaBinary" if "{temp_file}".endswith(".mb") else "mayaAscii"
    print("Step 2: Importing file:", "{temp_file}", "as", file_type)
    cmds.file("{temp_file}", i=True, type=file_type, ignoreVersion=True, preserveReferences=False)
    print("Step 2: Successfully imported hair objects from temp file")
except Exception as e:
    print("Step 2 ERROR (continuing anyway):", str(e))

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
        delete_namespace + ':geo',  # Contains all body accessories
        delete_namespace + ':dmm_GRP',
        # Specific body accessories
        delete_namespace + ':pants*',
        delete_namespace + ':bracelet*',
        delete_namespace + ':watch*',
        delete_namespace + ':necklace*',
        delete_namespace + ':ring*',
        delete_namespace + ':glass*',
        delete_namespace + ':body_geo_grp*'
    ]
    
    print("Deleting unwanted objects...")
    for pattern in unwanted_patterns:
        # Handle wildcard patterns
        if '*' in pattern:
            found_objects = cmds.ls(pattern)
            for obj in found_objects:
                if cmds.objExists(obj):
                    try:
                        cmds.delete(obj)
                        print("Deleted (pattern):", obj)
                    except Exception as e:
                        print("Could not delete:", obj, str(e))
        else:
            # Handle exact matches
            if cmds.objExists(pattern):
                try:
                    cmds.delete(pattern)
                    print("Deleted:", pattern)
                except Exception as e:
                    print("Could not delete:", pattern, str(e))

# Step 6: Delete all selection sets with namespace
print("Cleaning up selection sets...")
all_sets = cmds.ls(type='objectSet')
for set_node in all_sets:
    if set_node in ['defaultObjectSet', 'defaultLightSet', 'initialShadingGroup', 'initialParticleSE']:
        continue
    # Delete sets with nested namespace, target namespace, or unwanted prefixes
    if ((nested_namespace and nested_namespace.replace(':','') in set_node) or
        (target_namespace and target_namespace in set_node) or 
        'pasted__' in set_node or 
        'c0082ma_e200_kite' in set_node or
        set_node.startswith('Default') or 'Filter' in set_node):
        try:
            cmds.delete(set_node)
            print("Deleted set:", set_node)
        except:
            pass

# Step 7: Hide rig (don't delete)
if delete_namespace:
    rig_pattern = delete_namespace + ':rig'
    if cmds.objExists(rig_pattern):
        try:
            cmds.hide(rig_pattern)
            print("Hidden rig:", rig_pattern)
        except:
            pass

# Step 8: Find and rename root group
top_level_transforms = cmds.ls(assemblies=True)
for transform in top_level_transforms:
    if target_namespace and target_namespace in transform:
        new_name = "{{asset_name}}_hair"
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

# Step 10: Save final file
try:
    output_file = "{output_dir}/{asset_name}_hair.{ext}"
    cmds.file(rename=output_file)
    cmds.file(save=True, type="mayaAscii" if "{ext}" == "ma" else "mayaBinary", force=True)
    print("Saved cleaned hair file to:", output_file)
    
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
    script_content = standalone_script.format(
        temp_file=temp_hair_file,
        output_dir=itemdir,
        asset_name=asset_name,
        ext=mayaExt
    )
    
    # Save script to temp file with timestamp for debugging
    import time
    timestamp = str(int(time.time()))
    script_file = os.path.join(tempfile.gettempdir(), "process_hair_standalone_{}.py".format(timestamp))
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # Run standalone Maya
    export_success = False
    mayapy_path = os.path.join(os.environ.get('MAYA_LOCATION', '/usr/autodesk/maya'), 'bin', 'mayapy')
    if os.path.exists(mayapy_path):
        try:
            print("Running standalone Maya...")
            result = subprocess.check_output([mayapy_path, script_file], stderr=subprocess.STDOUT)
            print("Standalone output:", result)
            
            # Add to file info for step 10 (task json recording)
            output_filename = "{}_hair.{}".format(asset_name, mayaExt)
            output_filepath = os.path.join(itemdir, output_filename)
            fileinfo[asset_name + "_hair"] = output_filepath
            
            print("Hair export completed successfully!")
            print("Output file:", output_filepath)
            export_success = True
            
        except subprocess.CalledProcessError as e:
            print("Error running standalone Maya:", e)
            print("Output:", e.output)
            print("Debug script saved at:", script_file)
    else:
        print("mayapy not found at:", mayapy_path)
        
    # Clean up temp files (but keep script for debugging if error occurred)
    try:
        os.remove(temp_hair_file)
        if export_success:  # Only remove script if successful
            os.remove(script_file)
            print("Cleaned up temporary files")
        else:
            print("Kept script file for debugging:", script_file)
    except:
        pass
    
    print("=== Hair Export Workflow Completed ===")
    cmds.refresh(su=0)
    return fileinfo

    # Original code for regular items (not used for hair export)
    for item in itemList:
        extType = mayaExt
        fileinfotmp, itemNewDir, fileName = takeScript.takeItem(item, itemdir, extType, "", "mayaHair")
        fileinfo.update(fileinfotmp)
        print (fileinfo)

        if "/pub/" in itemNewDir:
            fileinfo[item] = itemNewDir
        else:
            #fileinfo[item] = "%s/%s.%s" % (itemNewDir, item, mayaExt)
            fileinfo[item] = "%s/%s.%s" % (itemNewDir, fileName, mayaExt)

            if mayaExt == "mb":
                mayaType = "mayaBinary"
            if mayaExt == "ma":
                mayaType = "mayaAscii"

            cmds.select(item, r=True)
            #cmds.file("%s/%s.%s" % (itemNewDir, item, mayaExt), force=1, options="v=0;", typ=mayaType, pr=1, es=1)
            cmds.file("%s/%s.%s" % (itemNewDir, fileName, mayaExt), force=1, options="v=0;", typ=mayaType, pr=1, es=1)

            # alembic
            if mayaAlembic:
                mel.eval(
                    'AbcExport -j "-frameRange %d %d -uvWrite -writeUVSets -eulerFilter -worldSpace -dataFormat ogawa -root %s -file %s/%s.abc" ' \
                    % ((startF), (endF), cmds.ls(sl=1)[0], itemNewDir, fileName))

    cmds.select(cl=1)
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