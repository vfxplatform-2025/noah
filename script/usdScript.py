# -*- coding:utf-8 -*-
'''
Created on Dec 17, 2025

USD Export Script for Noah Pipeline
Based on alembicScript.py

@author: m83
'''

import os
import re
import configparser
import maya.cmds as cmds
import maya.mel as mel
import json
from . import utilScript
import imp
imp.reload(utilScript)
from script import convert_byte_to_string
import set_usd_metadata
import usd_export

def get_usd_export_options(start_frame, end_frame, step=1, default_prim="", euler_filter=False):
    """
    Get USD export options string for Maya USD export
    Used by both local and farm exports for consistency
    
    Args:
        start_frame: Start frame for animation export
        end_frame: End frame for animation export
        step: Frame step/stride
        default_prim: Default primitive name
        euler_filter: Whether to apply euler filter to animation (default: False)
    
    Returns:
        String of USD export options
    """
    options = []
    
    # Basic export options
    options.append(";exportUVs=1")  # Note: starts with semicolon
    options.append("exportSkels=none")
    options.append("exportSkin=none")
    options.append("exportBlendShapes=0")  # Changed to 0 (disabled)
    options.append("exportDisplayColor=1")
    options.append(";exportColorSets=1")  # Double semicolon in working version
    options.append("exportComponentTags=1")
    options.append("defaultMeshScheme=catmullClark")
    
    # Animation options
    options.append("animation=1")
    options.append("eulerFilter={}".format(1 if euler_filter else 0))  # Default to 0
    options.append("staticSingleSample=0")
    options.append("startTime={}".format(int(start_frame)))
    options.append("endTime={}".format(int(end_frame)))
    options.append("frameStride={}".format(step))
    options.append("frameSample=0.0")
    
    # USD format options
    options.append("defaultUSDFormat=usdc")
    options.append("rootPrim=")
    options.append("rootPrimType=scope")  # Changed to scope
    options.append("defaultPrim={}".format(default_prim))
    
    # Material options
    options.append("exportMaterials=1")  # Changed to 1 (enabled)
    options.append("shadingMode=useRegistry")
    options.append("convertMaterialsTo=[rendermanForMaya]")  # Changed to rendermanForMaya
    options.append("exportAssignedMaterials=1")
    options.append("exportRelativeTextures=automatic")
    
    # Transform and visibility options
    options.append("exportInstances=1")
    options.append("exportVisibility=1")
    options.append("mergeTransformAndShape=1")
    options.append("includeEmptyTransforms=1")
    options.append("stripNamespaces=0")
    options.append("worldspace=0")
    options.append("exportStagesAsRefs=1")
    options.append("excludeExportTypes=[]")
    options.append("legacyMaterialScope=0")
    
    # History options
    options.append("history=1")  # Enable history export
    
    return ";".join(options)

def all_ref_list():
    """Get all reference objects matching pattern"""
    pattern = r"^(\w+)\d+:\1$"
    objects = cmds.ls(long=True)
    matched_objects = []

    for obj in objects:
        short_name = obj.split('|')[-1]
        if re.match(pattern, short_name):
            matched_objects.append(short_name)

    return matched_objects

def usdAllLoadSet(lodType="Default"):
    """Select all USD cache objects - similar to alembicAllLoadSet"""
    print(">>> USD ALL LOAD SET FUNCTION CALLED <<<")
    print("File: {}".format(__file__))
    print("Function: usdAllLoadSet()")
    print("lodType: {}".format(lodType))
    
    cmds.select(cl=True)

    usdDic = {}

    # usdCache_SET, usdCache_lod_SET
    if lodType != "Default":
        cmds.ls("*:usdCache_%s_SET" % lodType) and cmds.select("*:usdCache_%s_SET" %lodType)
    else:
        usd_all_list = all_ref_list()
        cmds.select(usd_all_list)
        # cmds.ls("*:usdCache_SET") and cmds.select("*:usdCache_SET")

    allUsdSet = cmds.ls(sl=1)
    for i in list(set(allUsdSet)):
        usdDic[i]={"step":"1", "type":"base"}

    # usdCache_step_SET
    cmds.select(cl=True)
    cmds.ls("*:usdCache_step_SET") and cmds.select("*:usdCache_step_SET")

    allUsdStepSet = cmds.ls(sl=1)
    for i in list(set(allUsdStepSet)):
        usdDic[i] = {"step": "0.1", "type":"merge"}

    # usdCache_numberPlate_SET
    cmds.select(cl=True)
    cmds.ls('*:usdCache_numberPlate_SET') and cmds.select('*:usdCache_numberPlate_SET')

    allUsdnumberPlateSet = cmds.ls(sl=1)
    if allUsdnumberPlateSet:
        for i in list(set(allUsdnumberPlateSet)):
            usdDic[i] = {"step": "1", "type":"merge"}

    if usdDic:
        cmds.select(cl=True)

    return usdDic

def usdSceneSetLoad():
    """Load USD Scene SET - similar to alembicSceneSetLoad"""
    print(">>> USD SCENE SET LOAD FUNCTION CALLED <<<")
    print("File: {}".format(__file__))
    print("Function: usdSceneSetLoad()")
    
    cmds.select(cl=True)

    usdDic = {}

    # scene_SET
    for i in cmds.ls("*:scene_SET"):
        cmds.select(i)
        setGrp = cmds.ls(sl=1)[0]
        cmds.select(i.split(":")[0]+":usdCache_SET")
        setUsdGrp = cmds.ls(sl=1)[0]
        refName = cmds.referenceQuery( setGrp, referenceNode=True )
        usdDic[i]={"step":"1", "type":"scene,{},{}".format(refName,setUsdGrp)}

    if usdDic:
        cmds.select(cl=True)

    return usdDic

def usdLoadMesh():
    """Load selected USD mesh objects - similar to alembicLoadMesh"""
    print(">>> USD LOAD MESH FUNCTION CALLED <<<")
    print("File: {}".format(__file__))
    print("Function: usdLoadMesh()")
    
    selected = cmds.ls(sl=1)
    print("Selected objects: {}".format(selected))
    
    usdDic = {}
    for i in selected:
        usdDic[i] = {"step": "1", "type":"base"}

    print('usdDic result: {}'.format(usdDic))
    return usdDic

def scale_checker(item):
    """Check uniform scale of the item"""
    non_uniform_scales = set()
    children = cmds.listRelatives(item, allDescendents=True, type='transform') or []

    for child in children:
        if cmds.nodeType(child) == 'transform':
            scaleX = round(cmds.getAttr(child + '.scaleX'), 3)
            scaleY = round(cmds.getAttr(child + '.scaleY'), 3)
            scaleZ = round(cmds.getAttr(child + '.scaleZ'), 3)

            if scaleX == scaleY == scaleZ != 1:
                non_uniform_scales.add(scaleX)
            if len(non_uniform_scales) > 1:
                return None

    return non_uniform_scales.pop() if non_uniform_scales else 1

def usdExport(fileList, itemdir, item, num, step_num, frameType="FrameRange", typeV="", hiddenV=[]):
    """Export USD files directly from Maya"""
    # Check USD plugin
    try:
        utilScript.pluginChecks('mayaUsdPlugin')
        print("DEBUG: Maya USD Plugin loaded successfully")
    except Exception as plugin_error:
        print(f"WARNING: Maya USD Plugin check failed: {str(plugin_error)}")
        print("Proceeding without plugin check...")
    
    print(">>>> USD option <<<", fileList, itemdir, item, num, step_num, frameType, typeV, hiddenV)
    
    # frame info - get current timeline settings like Alembic
    startF = 0.0
    endF = 0.0
    if frameType == "FrameRange":
        # Get current Maya timeline range (without hardcoded min=1)
        timelineStart = cmds.playbackOptions(q=1, min=1)
        timelineEnd = cmds.playbackOptions(q=1, max=1)
        startF = timelineStart - num
        endF = timelineEnd + num
        print(f"DEBUG: Timeline range: {timelineStart}-{timelineEnd}, Export range with handle: {startF}-{endF}")
    if frameType == "CurrentFrame":
        startF = cmds.currentTime(q=1)
        endF = cmds.currentTime(q=1)
        print(f"DEBUG: Current frame: {startF}")

    fileinfo = {}
    cmds.refresh(su=1)

    # Check scale
    scale = scale_checker(item)
    if scale is None:
        scale = 1.0

    # Create directory path and file info (similar to alembicExport)
    fileinfo = {}
    
    if ":" in item:
        assetName = re.search("[\w]*[\D](?=([\d]+)?:)", item).group()

        if "out_cur_Grp" in item:
            itemName = item.split(":")[0]  # org
            assetName = item.split(":")[1]  # org
        else:
            if not "geo_Grp" in item:
                assetName = item.split(":")[1]  # org
            itemName = item.split(":")[0] # asset name
            
        fileName = item.replace(":", "_")
        itemNewDir = "%s/%s" % (itemdir, itemName)
        fileinfo[ "%s:%s" %(itemName,assetName,) ] = "%s/%s.usd" %(itemNewDir, fileName)
        print('assetName1 :', assetName)
        print('itemName1 :', itemName)
        print('fileName1 :', fileName)
        print('itemNewDir1 :', itemNewDir)
    else:
        fileName = item
        itemNewDir = itemdir
        fileinfo[ item ] = "%s/%s.usd" %(itemNewDir, fileName)
        print('assetName2 :', item)
        print('itemNewDir2 :', itemNewDir)

    if not os.path.isdir(itemNewDir):
        try:
            os.makedirs(itemNewDir)
            print(f"DEBUG: Created directory: {itemNewDir}")
        except Exception as dir_error:
            print(f"ERROR: Failed to create directory {itemNewDir}: {str(dir_error)}")
            return fileinfo
    
    # USD Export path
    usdPath = "{}/{}.usd".format(itemNewDir, fileName)
    print(f"DEBUG: USD Export path: {usdPath}")
    
    # Hide objects if specified
    if hiddenV:
        cmds.hide(hiddenV)

    # Export USD using Maya USD plugin
    try:
        # Get full path of item and ensure it exists
        if not cmds.objExists(item):
            print(f"USD Export Error: Object '{item}' does not exist")
            return fileinfo
            
        itemFullPath = cmds.ls(item, l=1)[0]
        print(f"DEBUG: Exporting object: {item} -> {itemFullPath}")
        
        # USD Export options
        usdOptions = {
            'file': usdPath,
            'frameRange': (startF, endF),
            'frameStride': step_num,
            'selection': True,
            'exportUVs': True,
            'exportSkels': True,
            'exportSkin': True,
            'exportBlendShapes': True,
            'exportDisplayColor': True,
            'exportInstances': True,
            'exportVisibility': True,
            'mergeTransformAndShape': True,
            'stripNamespaces': False,
            'worldspace': True
        }
        
        # Select the item for export
        cmds.select(itemFullPath)
        print(f"DEBUG: Selected objects: {cmds.ls(sl=True)}")
        
        # Build USD export command using common options
        try:
            # Get defaultPrim name from selected item - matching the successful export
            if ":" in item:
                # Match successful format: c0082ma_e200_kite:root
                defaultPrimName = item.replace(":geo", ":root").replace(":geo_Grp", ":root")
            else:
                defaultPrimName = f"{item}:root"
            
            # Use centralized USD export options
            usdOptions = get_usd_export_options(
                start_frame=startF,
                end_frame=endF,
                step=step_num,
                default_prim=defaultPrimName,
                euler_filter=False  # Updated to match new options (eulerFilter=0)
            )
            
            # Build complete USD export command
            usdExportCmd = 'file -force -options "{}" -typ "USD Export" -pr -es "{}"'.format(usdOptions, usdPath)
            
            print("USD Export Command (Working Options):", usdExportCmd)
            print(f"DEBUG: DefaultPrim set to: {defaultPrimName}")
            result = mel.eval(usdExportCmd)
            print("USD Export MEL result:", result)
            print("USD Export completed with working options: {}".format(usdPath))
            
        except Exception as production_error:
            print(f"Production options USD export failed: {str(production_error)}")
            # Fallback to simplest possible export
            simple_cmd = 'file -force -typ "USD Export" -es "{}"'.format(usdPath)
            print(f"Trying simplest export: {simple_cmd}")
            result = mel.eval(simple_cmd)
            print("Simple USD export succeeded:", result)
        
        # Add successful export to fileinfo
        if os.path.exists(usdPath):
            print(f"DEBUG: USD file created successfully: {usdPath}")
            try:
                set_usd_metadata.run_set_usd_metadata(usdPath, scale, assetName if ":" in item else item)
            except Exception as meta_error:
                print("USD metadata setting failed:", str(meta_error))
        else:
            print(f"WARNING: USD file was not created: {usdPath}")
        
    except Exception as e:
        print("USD Export Error:", str(e))
        # Fallback: Convert from Alembic if USD direct export fails - DISABLED FOR NOW
        """
        print("Falling back to Alembic -> USD conversion...")
        
        # First export to Alembic
        abcPath = usdPath.replace('.usd', '.abc')
        try:
            # Ensure object exists for fallback
            if not cmds.objExists(item):
                print(f"Fallback export failed: Object '{item}' does not exist")
                return fileinfo
                
            itemFullPath = cmds.ls(item, l=1)[0]
            print(f"DEBUG: Fallback exporting: {item} -> {itemFullPath}")
            
            mel.eval(
                'AbcExport -j "-frameRange %d %d -uvWrite -writeUVSets -eulerFilter -writeVisibility -step %s -worldSpace -dataFormat ogawa -root %s -file %s" ' 
                % (startF, endF, step_num, itemFullPath, abcPath))
            
            # Then convert to USD
            if os.path.exists(abcPath):
                usd_export.UsdExporter(itemNewDir, fileName, scale)
                print(f"USD conversion completed via fallback: {usdPath}")
                
                # Check if USD file was created by fallback
                if os.path.exists(usdPath):
                    print(f"DEBUG: USD file created via fallback: {usdPath}")
                    # Clean up temporary Alembic file after successful USD conversion
                    try:
                        os.remove(abcPath)
                        print(f"DEBUG: Cleaned up temporary Alembic file: {abcPath}")
                    except Exception as cleanup_error:
                        print(f"WARNING: Failed to clean up Alembic file {abcPath}: {str(cleanup_error)}")
                else:
                    print(f"WARNING: USD file not created by fallback: {usdPath}")
        except Exception as fallback_error:
            print("Fallback export also failed:", str(fallback_error))
        """
        # Show error popup when USD export fails
        cmds.confirmDialog(
            title='USD Export Failed',
            message=f'USD Export failed for: {item}\n\nError: {str(e)}',
            button=['OK'],
            defaultButton='OK',
            icon='critical'
        )
    
    # Show hidden objects
    if hiddenV:
        cmds.showHidden(hiddenV)

    cmds.select(cl=1)
    cmds.refresh(su=0)
    
    print(f"DEBUG: Returning fileinfo: {fileinfo}")
    return fileinfo

# Import
def usdImport(itemInfo, type, rootType, itemNum=None, lod="None"):
    """Import USD files - similar to alembicImport"""
    print("=" * 60)
    print("USD IMPORT FUNCTION STARTED")
    print("File: {}".format(__file__))
    print("Function: usdImport()")
    print("Parameters:")
    print("  - itemInfo: {}".format(itemInfo))
    print("  - type: {}".format(type))
    print("  - rootType: {}".format(rootType))
    print("  - itemNum: {}".format(itemNum))
    print("  - lod: {}".format(lod))
    print("=" * 60)
    
    print("Checking Maya USD Plugin...")
    utilScript.pluginChecks('mayaUsdPlugin')
    print("Maya USD Plugin check completed")
    
    # Process each item in the dictionary (same pattern as alembicImport)
    baseItemList = []
    mergeObjectSpaceItemList = []
    mergeWorldSpaceItemList = []

    for i in itemInfo:
        if "_mergeObjectSpace" in i:
            mergeObjectSpaceItemList.append(i)
        elif "_mergeWorldSpace" in i:
            mergeWorldSpaceItemList.append(i)
        else:
            baseItemList.append(i)
            
    print("USD Import processing {} items:".format(len(itemInfo)))
    print("  - Base items: {}".format(baseItemList))
    print("  - Merge ObjectSpace items: {}".format(mergeObjectSpaceItemList))
    print("  - Merge WorldSpace items: {}".format(mergeWorldSpaceItemList))
    
    # Import base items and merge object space items
    writeItemName = ""
    for baseItem in baseItemList:
        writeItemName = usdImportFile(baseItem, itemInfo[baseItem], rootType, type, lod)
    for mergeObjectSpaceItem in mergeObjectSpaceItemList:
        writeItemName = usdImportFile(mergeObjectSpaceItem, itemInfo[mergeObjectSpaceItem], rootType, type, lod)
    
    print("=" * 60)
    print("USD IMPORT FUNCTION COMPLETED")
    print("=" * 60)
    
    return writeItemName

def usdImportFile(item, itemDir, rootType, type, lod="None"):
    """Import individual USD file - similar to alembicImportFile"""
    print("USD Import File: {} from {}".format(item, itemDir))
    
    # Parse item info
    print("Parsing item info...")
    itemSplit = item.split(":")
    if len(itemSplit) > 1:
        assetName = itemSplit[0]
        itemType = itemSplit[1]
        print("  Parsed - assetName: {}, itemType: {}".format(assetName, itemType))
    else:
        assetName = item
        itemType = ""
        print("  Parsed - assetName: {}, itemType: (empty)".format(assetName))
    
    # Build USD file path
    print("Building USD file path...")
    
    # Check if itemDir is already a complete file path or just a directory
    if itemDir.endswith('.usd'):
        # itemDir is already a complete file path
        usdFilePath = itemDir
        print("  Using provided file path: {}".format(usdFilePath))
    else:
        # itemDir is a directory, build file path
        usdFileName = "{}.usd".format(item.replace(":", "_"))
        usdFilePath = "{}/{}".format(itemDir, usdFileName)
        print("  Built file path: {}".format(usdFilePath))
    
    print("  Final USD path: {}".format(usdFilePath))
    
    print("Checking if USD file exists...")
    if not os.path.isfile(usdFilePath):
        print("ERROR: USD file not found: {}".format(usdFilePath))
        return ""
    
    print("SUCCESS: USD file found: {}".format(usdFilePath))
    
    try:
        # Method 1: Simple USD import then apply namespace manually (RELIABLE METHOD)
        print("Attempting USD import with manual namespace application...")
        
        # Extract base namespace - should be 'c0082ma_e200_kite'
        if ":" in item:
            namespace = assetName  # Use the asset name part
        else:
            # For USD items, the namespace is typically the asset base name
            # c0082ma_e200_kite_root -> c0082ma_e200_kite
            # c0082ma_e200_kite_geo -> c0082ma_e200_kite
            import re
            # Match pattern like: c0082ma_e200_kite (letters_numbers_letters)
            match = re.match(r"([a-zA-Z]+\d+[a-zA-Z]+_[a-zA-Z]+\d+_[a-zA-Z]+)", item)
            if match:
                namespace = match.group(1)
            else:
                # Fallback: assume first 3 parts separated by underscore
                parts = item.split('_')
                if len(parts) >= 3:
                    namespace = '_'.join(parts[:3])  # c0082ma_e200_kite
                else:
                    namespace = item.split('_')[0]
        
        print("Using namespace: {}".format(namespace))
        
        # Get scene objects before import to identify new objects
        objects_before = set(cmds.ls(transforms=True))
        
        # Simple USD import without namespace (then apply manually)
        usdImportCmd = 'file -import -type "USD Import" -ignoreVersion -mergeNamespacesOnClash false -options "primPath=/;excludePrimvar=0;excludeDisplayColor=0;readAnimData=1;useAsAnimationCache=1" "{}"'.format(usdFilePath)
        
        print("USD Import Command (Simple then Manual Namespace):", usdImportCmd)
        mel.eval(usdImportCmd)
        
        # Get newly imported objects
        objects_after = set(cmds.ls(transforms=True))
        new_objects = list(objects_after - objects_before)
        
        if new_objects:
            print("Found {} newly imported objects:".format(len(new_objects)))
            for obj in new_objects:
                print("  - Original: '{}'".format(obj))
            
            # DEBUG: Check all transforms to see what was actually imported
            all_transforms = cmds.ls(transforms=True)
            print("\nDEBUG: All transforms in scene:")
            for t in all_transforms[-10:]:  # Show last 10
                print("  - Transform: '{}'".format(t))
            
            # Apply namespace and format conversion to new objects
            renamed_objects = []
            for obj in new_objects:
                try:
                    print("\nProcessing object: '{}'".format(obj))
                    
                    # Convert to namespace format using base namespace
                    # c0082ma_e200_kite_root -> c0082ma_e200_kite:root
                    # c0082ma_e200_kite_geo -> c0082ma_e200_kite:geo
                    
                    # Use the determined namespace as base
                    base_namespace = namespace  # This should be 'c0082ma_e200_kite'
                    
                    # Check if object name starts with the namespace
                    if obj.startswith(base_namespace + '_'):
                        # Remove the base namespace and underscore, keep the rest
                        object_part = obj[len(base_namespace) + 1:]  # +1 for underscore
                        final_name = "{}:{}".format(base_namespace, object_part)
                        print("  - Base namespace: '{}'".format(base_namespace))
                        print("  - Object part: '{}'".format(object_part))
                        print("  - Final name: '{}'".format(final_name))
                    else:
                        # If doesn't follow expected pattern, keep original
                        final_name = obj
                        print("  - Doesn't match namespace pattern, keeping: '{}'".format(final_name))
                    
                    # Ensure namespace exists in Maya first
                    if ':' in final_name:
                        ns_part = final_name.split(':')[0]
                        if not cmds.namespace(exists=ns_part):
                            try:
                                cmds.namespace(add=ns_part)
                                print("  - Created namespace: '{}'".format(ns_part))
                            except Exception as ns_error:
                                print("  - Could not create namespace '{}': {}".format(ns_part, str(ns_error)))
                    
                    # Rename to final format
                    if obj != final_name:
                        try:
                            result = cmds.rename(obj, final_name)
                            renamed_objects.append(result)  # Use the actual returned name
                            print("  - Successfully renamed: '{}' -> '{}' (actual: '{}')".format(obj, final_name, result))
                        except Exception as rename_error:
                            print("  - Rename failed '{}' -> '{}': {}".format(obj, final_name, str(rename_error)))
                            renamed_objects.append(obj)  # Keep original if rename fails
                    else:
                        renamed_objects.append(obj)
                        print("  - No rename needed: '{}'".format(obj))
                    
                except Exception as overall_error:
                    print("  - Processing failed for '{}': {}".format(obj, str(overall_error)))
                    renamed_objects.append(obj)  # Keep original name if processing fails
            
            print("\nSuccessfully processed {} USD objects:".format(len(renamed_objects)))
            for obj in renamed_objects:
                print("  Final: '{}'".format(obj))
                
            # DEBUG: Verify objects exist in scene and check actual names
            print("\nDEBUG: Verifying final objects exist:")
            for obj in renamed_objects:
                exists = cmds.objExists(obj)
                print("  - '{}' exists: {}".format(obj, exists))
            
            # DEBUG: Check Maya namespaces and actual object names
            print("\nDEBUG: Maya namespace information:")
            all_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True)
            print("  - All namespaces in scene: {}".format(all_namespaces))
            
            # Check if our namespace exists
            target_namespace = namespace
            if target_namespace in all_namespaces:
                print("  - Target namespace '{}' exists in Maya".format(target_namespace))
                objects_in_ns = cmds.namespaceInfo(target_namespace, listNamespace=True)
                print("  - Objects in '{}' namespace: {}".format(target_namespace, objects_in_ns[:10] if objects_in_ns else []))
            else:
                print("  - WARNING: Target namespace '{}' NOT found in Maya".format(target_namespace))
            
            # DEBUG: Check actual object names in scene
            print("\nDEBUG: Checking actual scene objects:")
            all_transforms = cmds.ls(transforms=True)
            usd_objects = [obj for obj in all_transforms if 'c0082ma_e200_kite' in obj]
            print("  - USD-related objects found ({} total):".format(len(usd_objects)))
            for obj in usd_objects[:10]:  # Show first 10
                print("    - '{}'".format(obj))
            
            print("Base USD : {}".format(item))
        else:
            print("No objects found after USD import, trying alternative...")
            raise Exception("USD import failed, no objects imported")
            
    except Exception as traditional_error:
        print("Traditional import failed: {}".format(str(traditional_error)))
        
        # FALLBACK: Stage method (commented previous working method)
        """
        # Method 2: Stage approach (PREVIOUS WORKING METHOD - COMMENTED)
        try:
            # Check import type from Opt2 parameter
            if type == "import":
                # Force traditional import method
                print("USD import type: traditional import (from Opt2)")
                raise Exception("Using traditional import as requested")
            else:
                # Default: use stage method (type == "stage" or other)
                print("USD import type: stage method (default)")
            
            # Method 1: Try mayaUsd stage approach first
            print("Attempting USD import using mayaUsd stage approach...")
            try:
                from mayaUsd import lib as mayaUsdLib
                
                # Check if USD stage exists, create if not
                stage_shapes = cmds.ls(type='mayaUsdProxyShape')
                
                if not stage_shapes:
                    # Create a new USD stage
                    print("Creating new USD stage...")
                    stage_transform = cmds.createNode('transform', name='stage1')
                    stage_node = cmds.createNode('mayaUsdProxyShape', name='stageShape1', parent=stage_transform)
                    
                    # Set the file path directly
                    cmds.setAttr('{}.filePath'.format(stage_node), usdFilePath, type='string')
                    
                    print("Created USD stage with file: {}".format(usdFilePath))
                else:
                    # Use existing stage
                    stage_node = stage_shapes[0]
                    print("Using existing USD stage: {}".format(stage_node))
                    
                    # Try to get the stage and add USD file as sublayer
                    try:
                        prim = mayaUsdLib.GetPrim(stage_node)
                        stage = prim.GetStage()
                        
                        if stage:
                            root_layer = stage.GetRootLayer()
                            
                            # Check if USD path already exists in sublayers
                            if usdFilePath not in root_layer.subLayerPaths:
                                print("Adding USD file as sublayer: {}".format(usdFilePath))
                                root_layer.subLayerPaths.append(usdFilePath)
                                print("USD file loaded as sublayer successfully")
                                
                                # CRITICAL: Use refreshSystemLock for proper animation update
                                stage_transform = cmds.listRelatives(stage_node, parent=True)[0]
                                stage_full_path = "|{}|{}".format(stage_transform, stage_node)
                                layer_id = root_layer.identifier
                                
                                print("Applying refreshSystemLock for animation...")
                                print("Stage path: {}, Layer ID: {}".format(stage_full_path, layer_id))
                                
                                try:
                                    # Use the exact pattern from Maya USD documentation
                                    mel.eval('mayaUsdLayerEditor("{}", edit=True, refreshSystemLock=("{}", 1));'.format(layer_id, stage_full_path))
                                    print("refreshSystemLock applied successfully")
                                    
                                    # Additional: Force time refresh for animation
                                    current_time = cmds.currentTime(q=True)
                                    cmds.currentTime(current_time + 0.01)
                                    cmds.currentTime(current_time)
                                    print("Time refresh completed")
                                    
                                except Exception as refresh_error:
                                    print("refreshSystemLock failed: {}".format(str(refresh_error)))
                            else:
                                print("USD file already loaded in stage: {}".format(usdFilePath))
                                
                            # Print stage info
                            print("Stage sublayers: {}".format(list(root_layer.subLayerPaths)))
                        else:
                            print("Could not get USD stage, trying direct file path assignment...")
                            cmds.setAttr('{}.filePath'.format(stage_node), usdFilePath, type='string')
                            
                    except Exception as stage_error:
                        print("Stage sublayer approach failed: {}".format(str(stage_error)))
                        print("Trying direct file path assignment...")
                        cmds.setAttr('{}.filePath'.format(stage_node), usdFilePath, type='string')
                
                # Refresh the viewport
                cmds.refresh()
                print("USD import completed successfully via stage approach")
                print("Base USD : {}".format(item))
                
            except ImportError:
                print("mayaUsd module not available, trying fallback import method...")
                raise Exception("mayaUsd not available")
        except Exception as stage_error:
            print("Stage approach also failed: {}".format(str(stage_error)))
        """
        
        # Alternative fallback: Raw import without any processing
        try:
            print("Attempting raw USD import as final fallback...")
            
            # Very simple USD import command
            usdImportCmd = 'file -import -type "USD Import" "{}"'.format(usdFilePath)
            
            print("USD Import Command (Raw):", usdImportCmd)
            mel.eval(usdImportCmd)
            
            # Just report what was imported without modification
            all_objects = cmds.ls(transforms=True)
            usd_related = [obj for obj in all_objects if any(part in obj for part in [assetName, 'root', 'geo']) if assetName]
            
            if usd_related:
                print("Found USD-related objects:", usd_related)
                print("Base USD : {}".format(item))
            else:
                print("No recognizable USD objects found")
                
        except Exception as final_error:
            print("All USD import methods failed:", str(final_error))
            import traceback
            traceback.print_exc()
    
    return item