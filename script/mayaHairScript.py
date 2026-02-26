# -*- coding:utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel
import os
import re
import time
import tempfile
import subprocess
from . import utilScript
import imp
imp.reload(utilScript)
from . import takeScript
imp.reload(takeScript)
from . import vdbScript
imp.reload(vdbScript)

def mayaHairExport(fileName, itemdir, itemList, fileType, mayaExt, mayaAlembic, frameType):
    fileinfo = {}
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print("=== Hair Export Workflow Started (per-character export) ===")
    print("Selected items:", itemList)

    hair_objects = list(itemList or [])
    if not hair_objects:
        cmds.warning("No objects found in selection")
        return fileinfo

    # ------------------------------------------------------------
    # 0) 선택을 namespace별로 그룹핑
    # ------------------------------------------------------------
    ns_to_items = {}
    for obj in hair_objects:
        ns = obj.split(":", 1)[0] if ":" in obj else ""
        ns_to_items.setdefault(ns, []).append(obj)

    print("Namespaces detected:", [k for k in ns_to_items.keys() if k])

    # ------------------------------------------------------------
    # 1) current scene / output dir 결정
    # ------------------------------------------------------------
    current_scene = cmds.file(query=True, sceneName=True) or ""
    scene_basename = os.path.splitext(os.path.basename(current_scene))[0] if current_scene else ""

    if current_scene:
        scene_dir = os.path.dirname(current_scene)
        if "/wip/" in scene_dir:
            base_path = scene_dir.split("/wip/")[0]
            output_dir = os.path.join(base_path, "wip", "data", "hair")
        else:
            output_dir = os.path.join(scene_dir, "data", "hair")
    else:
        output_dir = os.path.join(os.path.dirname(os.getcwd()), "wip", "data", "hair")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Output directory:", output_dir)
    if scene_basename:
        print("Scene name:", scene_basename)

    # ------------------------------------------------------------
    # 공통: ns에서 asset_name 추출
    #   ex) c0118ma_e200_sea_extra_man_9 -> sea_extra_man_9
    # ------------------------------------------------------------
    def _asset_name_from_namespace(ns_or_name):
        if not ns_or_name:
            return "nonamespace"
        s = ns_or_name
        if ":" in s:
            s = s.split(":", 1)[0]
        if "_e" in s:
            m = re.search(r"([a-z]\d+[a-z]+_e\d+_)(.*)", s)
            return m.group(2) if m else s
        return s

    # ------------------------------------------------------------
    # 공통: mayapy cleanup script 생성 함수
    #   - 파일 안에서 '*:root' 탐지
    #   - (추가) visibility breakConnection
    #   - (추가) 하드코딩 hide 목록 처리 (cleanup 맨 마지막)
    # ------------------------------------------------------------
    def _make_standalone_script(hair_file, asset_name):
        hair_file_esc = hair_file.replace("\\", "\\\\")
        asset_name_esc = asset_name.replace("\\", "\\\\")

        return r'''
import sys
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel

try:
    import maya.utils
    maya.utils.MayaGUILogHandler()
except:
    pass

cmds.scriptEditorInfo(suppressWarnings=True, suppressInfo=True)

hair_file = r"''' + hair_file_esc + r'''"
asset_name = r"''' + asset_name_esc + r'''"

print("=== Standalone Maya Hair Processing ===")
print("hair_file:", hair_file)
print("asset_name:", asset_name)

# Step 1: Open
try:
    file_type = "mayaBinary" if hair_file.lower().endswith(".mb") else "mayaAscii"
    cmds.file(hair_file, open=True, force=True, type=file_type, ignoreVersion=True)
    print("Opened file OK")
except Exception as e:
    print("OPEN ERROR:", e)
    sys.exit(1)

cleanup_ok = True

# ------------------------------------------------------------
# (A) Break ALL visibility connections
# ------------------------------------------------------------
def _break_all_visibility_connections():
    # "visibility" input connections 끊기
    # - transform 뿐 아니라 visibility 가진 노드면 다 처리
    nodes = cmds.ls() or []
    cut = 0
    for n in nodes:
        attr = n + ".visibility"
        if not cmds.objExists(attr):
            continue
        try:
            src = cmds.listConnections(attr, s=True, d=False, p=True) or []
            if not src:
                continue
            # breakConnection 대신 disconnectAttr로 정확히 끊기
            for sattr in src:
                try:
                    cmds.disconnectAttr(sattr, attr)
                    cut += 1
                except:
                    pass
        except:
            pass
    print("Break visibility connections:", cut)

_break_all_visibility_connections()

# Step 2: Find namespaces that actually have ':root'
roots = cmds.ls("*:root", type="transform") or []
root_namespaces = list({r.rsplit(":", 1)[0] for r in roots})

print("Roots found:", roots)
print("Root namespaces:", root_namespaces)

picked_ns = None
if root_namespaces:
    preferred = [ns for ns in root_namespaces if asset_name in ns]
    if preferred:
        preferred.sort(key=lambda x: (x.count(':'), len(x)), reverse=True)
        picked_ns = preferred[0]
    else:
        root_namespaces.sort(key=lambda x: (x.count(':'), len(x)), reverse=True)
        picked_ns = root_namespaces[0]

delete_namespace = picked_ns
target_namespace = picked_ns.split(":")[-1] if picked_ns else None
print("Picked delete_namespace:", delete_namespace)
print("Picked target_namespace:", target_namespace)

target_root = (target_namespace + ":root") if target_namespace else None
if not (target_root and cmds.objExists(target_root)):
    print("CRITICAL: target ':root' not found -> NOT saving")
    cleanup_ok = False

def _safe_delete(node):
    if not node or not cmds.objExists(node):
        return False
    try:
        cmds.lockNode(node, lock=False)
    except:
        pass
    try:
        cmds.delete(node)
        return True
    except:
        return False

def _safe_hide(node):
    if not node or not cmds.objExists(node):
        return False
    try:
        cmds.lockNode(node, lock=False)
    except:
        pass
    try:
        v = node + ".v"
        if cmds.objExists(v):
            try:
                cmds.setAttr(v, lock=False)
            except:
                pass
        cmds.hide(node)
        return True
    except:
        return False

# Step 3~: cleanup (namespace 확정된 경우만)
if cleanup_ok:
    ns_for_patterns = delete_namespace if delete_namespace else target_namespace

    unwanted = [
        ns_for_patterns + ':body_geo_grp',
        ns_for_patterns + ':body_all',
        ns_for_patterns + ':Low_Geo_Grp',
        ns_for_patterns + ':eye',
        ns_for_patterns + ':hairtie',
        ns_for_patterns + ':teeth',
        ns_for_patterns + ':HairGeoGrp',
        ns_for_patterns + ':dmm_GRP'
    ]
    for n in unwanted:
        if _safe_delete(n):
            print("Deleted:", n)

    sets_to_delete = [
        ns_for_patterns + ':Sets',
        ns_for_patterns + ':AniControlSet',
        ns_for_patterns + ':bake_hairSet',
        ns_for_patterns + ':ControlSet',
        ns_for_patterns + ':FaceAllSet',
        ns_for_patterns + ':FaceControlSet',
        ns_for_patterns + ':geoSet',
        ns_for_patterns + ':set2',
        ns_for_patterns + ':smoSet2',
        ns_for_patterns + ':FaceAreas',
        ns_for_patterns + ':eyeBrowArea',
        ns_for_patterns + ':eyeBrowLineArea',
        ns_for_patterns + ':eyeLidArea',
        ns_for_patterns + ':eyeLidMainArea',
        ns_for_patterns + ':eyeLidOuterArea',
        ns_for_patterns + ':eyeLidOuterAreaLeft',
        ns_for_patterns + ':lipArea',
        ns_for_patterns + ':lipFalloffArea',
        ns_for_patterns + ':lipMainArea'
    ]
    for s in sets_to_delete:
        if _safe_delete(s):
            print("Deleted set:", s)

    # hide rig + geo (기존 로직)
    rig_patterns = [
        ns_for_patterns + ':rig',
        ns_for_patterns + ':RIG',
        ns_for_patterns + ':Rig',
        ns_for_patterns + ':rig_GRP',
        ns_for_patterns + ':RIG_GRP'
    ]
    for r in rig_patterns:
        if _safe_hide(r):
            print("Hidden rig:", r)

    _safe_hide(ns_for_patterns + ':geo')

    # pfx_Vis
    for obj in (cmds.ls(ns_for_patterns + ':*', type='transform') or []):
        attr = obj + ".pfx_Vis"
        if cmds.objExists(attr):
            try:
                cmds.setAttr(attr, 2)
            except:
                pass

    # group root + world_dummy
    target_objects = []
    if target_root and cmds.objExists(target_root):
        target_objects.append(target_root)
    if cmds.objExists("world_dummy"):
        target_objects.append("world_dummy")

    if not target_objects:
        print("CRITICAL: no target objects to group -> NOT saving")
        cleanup_ok = False
    else:
        group_name = asset_name + "_hair"
        try:
            if cmds.objExists(group_name):
                try:
                    cmds.delete(group_name)
                except:
                    pass
            cmds.group(target_objects, name=group_name)
            print("Grouped into:", group_name)
        except Exception as e:
            print("CRITICAL: group failed:", e)
            cleanup_ok = False

# shader cleanup (non-critical)
try:
    mel.eval("MLdeleteUnused;")
except:
    pass

# unknown cleanup (best-effort)
try:
    for n in (cmds.ls(type="unknown") or []):
        try:
            cmds.lockNode(n, lock=False)
        except:
            pass
        try:
            cmds.delete(n)
        except:
            pass

    for p in (cmds.unknownPlugin(q=True, list=True) or []):
        try:
            cmds.unknownPlugin(p, remove=True)
        except:
            pass
except:
    pass

# ------------------------------------------------------------
# (B) FINAL: hard-coded hide AFTER all cleanup
#   - 네가 원하는 이름들 전부 hide
#   - namespace가 있는 경우: ns:* 를 우선
#   - 없는 경우도 대비해서 *:pattern 도 같이
# ------------------------------------------------------------
def _hide_matches(patterns, label):
    hits = []
    for pat in patterns:
        hits += (cmds.ls(pat, type="transform") or [])
    # 중복 제거
    uniq = []
    seen = set()
    for h in hits:
        if h in seen:
            continue
        seen.add(h)
        uniq.append(h)

    if not uniq:
        print("HIDE[%s]: no matches" % label)
        return

    for h in uniq:
        _safe_hide(h)
    print("HIDE[%s]: %d hidden" % (label, len(uniq)))

if cleanup_ok:
    ns = delete_namespace if delete_namespace else target_namespace

    # ns가 있으면 ns 기반을 먼저, 그래도 혹시 모를 케이스에 *: 도 같이
    # 1) :rig
    _hide_matches([ns + ":rig" if ns else "*:rig", "*:rig"], label="rig")

    # 2) :world_dummy (namespaced) + world_dummy(plain)
    _hide_matches([ns + ":world_dummy" if ns else "*:world_dummy", "*:world_dummy", "world_dummy"], label="world_dummy")

    # 3) others
    _hide_matches([ns + ":hair_model_grp" if ns else "*:hair_model_grp", "*:hair_model_grp"], label="hair_model_grp")
    _hide_matches([ns + ":wrapbaseGRP" if ns else "*:wrapbaseGRP", "*:wrapbaseGRP"], label="wrapbaseGRP")
    _hide_matches([ns + ":wrap_hair_GRP" if ns else "*:wrap_hair_GRP", "*:wrap_hair_GRP"], label="wrap_hair_GRP")
    _hide_matches([ns + ":hair_etc_GRP" if ns else "*:hair_etc_GRP", "*:hair_etc_GRP"], label="hair_etc_GRP")
    _hide_matches([ns + ":faceBase" if ns else "*:faceBase", "*:faceBase"], label="faceBase")
    _hide_matches([ns + ":eyebrowWrapBase" if ns else "*:eyebrowWrapBase", "*:eyebrowWrapBase"], label="eyebrowWrapBase")
    _hide_matches([ns + ":eyebrowWrap" if ns else "*:eyebrowWrap", "*:eyebrowWrap"], label="eyebrowWrap")

# SAVE only if cleanup_ok
try:
    if cleanup_ok:
        cmds.file(save=True, force=True)
        print("Saved cleaned file OK")
        sys.exit(0)
    else:
        print("Cleanup not OK -> NOT saving")
        sys.exit(2)
except Exception as e:
    print("SAVE ERROR:", e)
    sys.exit(1)
finally:
    try:
        maya.standalone.uninitialize()
    except:
        pass
'''

    # ------------------------------------------------------------
    # 2) mayapy 경로
    # ------------------------------------------------------------
    mayapy_path = os.path.join(os.environ.get("MAYA_LOCATION", "/usr/autodesk/maya"), "bin", "mayapy")
    if not os.path.exists(mayapy_path):
        print("[WARN] mayapy not found at:", mayapy_path)
        print("[WARN] cleanup 단계는 스킵됩니다. (export 파일은 생성됨)")
        mayapy_path = None

    # ------------------------------------------------------------
    # 3) namespace별로 export 루프
    # ------------------------------------------------------------
    for ns, items in ns_to_items.items():
        asset_name = _asset_name_from_namespace(ns or items[0])

        export_candidates = []
        if ns:
            export_candidates.append(ns + ":root")
            export_candidates.append(ns + ":hair")
        export_candidates.extend(items)

        export_targets = [x for x in export_candidates if cmds.objExists(x)]
        seen = set()
        export_targets = [x for x in export_targets if not (x in seen or seen.add(x))]

        if not export_targets:
            print("[WARN] No exportable targets for namespace:", ns, "items:", items)
            continue

        if scene_basename:
            output_filename = "{}_{}_hair.{}".format(scene_basename, asset_name, mayaExt)
        else:
            output_filename = "{}_hair.{}".format(asset_name, mayaExt)

        final_output_file = os.path.join(output_dir, output_filename)

        print("\n--- Export per character ---")
        print("namespace:", ns)
        print("asset_name:", asset_name)
        print("export_targets:", export_targets)
        print("output:", final_output_file)

        cmds.select(export_targets, replace=True)
        try:
            if mayaExt.lower() == "mb":
                cmds.file(final_output_file, force=True, options="v=0;", typ="mayaBinary", pr=True, es=True)
            else:
                cmds.file(final_output_file, force=True, options="v=0;", typ="mayaAscii", pr=True, es=True)
            print("Export OK:", final_output_file)
        except Exception as e:
            print("[ERROR] Export failed for ns:", ns, "err:", str(e))
            continue

        cleanup_success = False
        script_file = None

        if mayapy_path:
            script_content = _make_standalone_script(final_output_file, asset_name)
            timestamp = str(int(time.time()))
            script_file = os.path.join(
                tempfile.gettempdir(),
                "process_hair_standalone_{}_{}.py".format(asset_name, timestamp)
            )
            with open(script_file, "w") as f:
                f.write(script_content)

            try:
                out = subprocess.check_output([mayapy_path, script_file], stderr=subprocess.STDOUT)
                try:
                    print("Standalone output:\n", out.decode("utf-8", errors="ignore"))
                except:
                    print("Standalone output (raw):\n", out)
                cleanup_success = True
            except subprocess.CalledProcessError as e:
                print("[ERROR] Standalone cleanup failed:", e)
                try:
                    print("Output:\n", e.output.decode("utf-8", errors="ignore"))
                except:
                    print("Output (raw):\n", e.output)
                print("Debug script kept at:", script_file)
                cleanup_success = False
            except Exception as e:
                print("[ERROR] Unexpected standalone error:", str(e))
                print("Debug script kept at:", script_file)
                cleanup_success = False

        json_key = os.path.splitext(os.path.basename(final_output_file))[0]
        fileinfo[json_key] = final_output_file

        if script_file and cleanup_success:
            try:
                os.remove(script_file)
            except:
                pass

    print("\n=== Hair Export Workflow Completed ===")
    try:
        cmds.refresh(su=0)
    except:
        pass

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