import os
import sys
import re
from pathlib import Path
from pxr import Usd, UsdGeom, Sdf
import maya.cmds as cmds
import set_usd_metadata
import json

class UsdExporter():
    def __init__(self, itemNewDir, fileName, scale=None):
        self.itemNewDir = itemNewDir
        print(self.itemNewDir, '<<<<<<<<<<<<<<<<')
        # lookdev :   /show/ORV/assets/aircraft/  test  /model/wip/data/alembic/test_model_v04
        # animation : /show/ORV/  seq /   TST  /TST_0100/ ani /wip/data/alembic/TST_0100_ani_v01_w02/test3
        self.fileName = fileName
        print(self.fileName, '<<<<<<<<<<<<<<<<<<')
        # ani : test3_high_grp
        self.prefix = self.fileName.split('_')[0]
        self.scale = scale
        print(self.scale, '<<<<<<<<<<<<<<<<<<<<')
        self.usd_itemNewDir = self.itemNewDir.replace(f"{os.sep}data/alembic{os.sep}", f"{os.sep}usd{os.sep}")
        # /show/ORV/seq/TST/TST_0020/ani/wip/usd/TST_0020_ani_v006/ddangDogChungmuroA1
        # /show/ORV/seq/TST/TST_0100/ani/wip/usd/TST_0100_ani_v02_w01/test3
        # /show/ORV/assets/aircraft/  test  /model/wip/usd/    test_model_v01
        self.usd_path = f"{self.usd_itemNewDir}/{self.fileName}.usd"
        self.abc_path = f"{self.itemNewDir}/{self.fileName}.abc"
        self.claen_ref_path = None

        self.abc_to_usd()
        # self.link_usd()

        if self.scale is not None:
            self.scale_meta(self.usd_itemNewDir, self.scale, self.fileName)

        if self.itemNewDir.split('/')[6] == 'ani':
            name = f"{self.fileName.split('_')[0]}:{'_'.join(self.fileName.split('_')[1:])}"
            if cmds.referenceQuery(name, isNodeReferenced=True):
                ref_path = cmds.referenceQuery(name, filename=True)
                self.clean_ref_path = ref_path.split('{')[0]
                # /show/ORV/assets/aircraft/test        /rig  /pub/ddangDogChungmuroA_rig_v005.mb
                # /show/ORV/assets/aircraft/twoWayTunnel/model/wip/scenes/twoWayTunnel_model_v002_w012_pub.mb
                # /show/ORV/assets/aircraft/twoWayTunnel/model/pub/twoWayTunnel_model_v002/twoWayTunnel_model_v002.mb
            # self.lookdev_usd_path = Path(self.clean_ref_path).parents[2]/'lookdev/pub/lookdev.usda'
            self.lookdev_usd_path = '/'.join(self.clean_ref_path.split('/')[:6])+'/lookdev/pub/lookdev.usda'
            self.assign_usd_path = '/'.join(self.clean_ref_path.split('/')[:6])+'/lookdev/pub/assign.usda'
            self.material_usd_path = '/'.join(self.clean_ref_path.split('/')[:6]) + '/lookdev/pub/material.usda'
            # /show/ORV/assets/aircraft/twoWayTunnel/model/lookdev/pub/lookdev.usda
            if os.path.isfile(str(self.lookdev_usd_path)):
                self.make_wrapper_lookdev_usd(self.assign_usd_path, self.material_usd_path, self.usd_itemNewDir, self.prefix+'_')
            else:
                print(f'{self.lookdev_usd_path} 파일이 존재하지 않습니다.')
            self.make_ani_usd(str(Path(self.usd_itemNewDir).parent), 'ani.usda')

    def make_ani_usd(self, pub_root_dir, output_name):
        version_dir = Path(pub_root_dir)
        print(f'version_dir: {version_dir}')
        output_path = Path(pub_root_dir) / output_name
        print(f'output_path: {output_path}')

        sublayer_paths = []
        merged_doc_dict = {}

        # 각 usda 경로 수집 및 메타데이터 추출
        for asset in os.listdir(version_dir):
            usda_path = version_dir / asset / f"{asset}.usda"
            if not usda_path.exists():
                print(f"[WARN] Missing: {usda_path}")
                continue

            sublayer_paths.append(str(usda_path.relative_to(pub_root_dir)))

            layer = Sdf.Layer.FindOrOpen(str(usda_path))
            if not layer:
                print(f"[WARN] Failed to open: {usda_path}")
                continue

            doc_meta = layer.documentation or layer.comment or ""
            try:
                doc_data = json.loads(doc_meta)
                if isinstance(doc_data, dict):
                    merged_doc_dict.update(doc_data)
            except json.JSONDecodeError:
                print(f"[WARN] Invalid doc metadata in: {usda_path}")

        # 새 ani.usda Layer 생성
        top_layer = Sdf.Layer.CreateNew(str(output_path))
        top_layer.subLayerPaths = sublayer_paths

        # 병합된 doc 메타데이터 저장
        top_layer.documentation = json.dumps(merged_doc_dict, indent=4)
        top_layer.Save()
        print(f"[OK] Created merged ani.usda: {output_path}")

    def abc_to_usd(self):
        if os.path.exists(self.usd_itemNewDir):
            os.system(
                f"/core/Linux/ENV/usdcat.sh {self.abc_path} {self.usd_path}")
            self.set_double_sided_all(self.usd_path)
        else:
            try:
                os.makedirs(self.usd_itemNewDir)
                os.system(
                    f"/core/Linux/ENV/usdcat.sh {self.abc_path} {self.usd_path}")
                self.set_double_sided_all(self.usd_path)
            except OSError:
                print(">>> USD EXPORT FAILED <<<")

    def set_double_sided_all(self, stage_path):
        stage = Usd.Stage.Open(stage_path)
        for prim in stage.Traverse():
            if prim.GetTypeName() == "Mesh":
                mesh = UsdGeom.Mesh(prim)
                mesh.CreateDoubleSidedAttr(True)
        stage.GetRootLayer().Save()

    def scale_meta(self, path, scale, fileName):
        set_usd_metadata.run_set_usd_metadata(f'{path}/{fileName}.usd', scale, f'{fileName.split("_")[0]}')

    def make_wrapper_lookdev_usd(self, assign_path, material_path, save_path, prefix=None):
        assign_path = Path(assign_path)
        material_path = Path(material_path)
        save_path = Path(save_path)

        if not assign_path.exists():
            print(f"[ERROR] assign.usda not found: {assign_path}")
            return
        if not material_path.exists():
            print(f"[ERROR] material.usda not found: {material_path}")
            return

        # assign.usda에서 over "high_grp" 이하 추출
        content = assign_path.read_text()
        match = re.search(r'over\s+"high_grp".*', content, re.DOTALL)
        if not match:
            print(f"[ERROR] 'over \"high_grp\"' not found in {assign_path}")
            return
        extracted_content = match.group(0)

        # 새로운 wrapper_lookdev.usda 구성
        new_usda_lines = [
            '#usda 1.0',
            '(\n    defaultPrim = "' + prefix + 'high_grp"\n    subLayers = [',
            f'        @{material_path}@,',
            f'        @{assign_path}@',
            '    ]\n)',
            '',
            extracted_content
        ]

        new_content = '\n'.join(new_usda_lines)

        # prefix 적용 (materials 블록 제외)
        pattern = re.compile(r'(\bover\s+\")([^\"]+)(\")')
        lines = new_content.split('\n')
        updated_lines = []
        in_materials_block = False
        materials_brace_depth = 0

        for line in lines:
            stripped = line.lstrip()

            if re.match(r'over\s+"materials"', stripped):
                in_materials_block = True
                materials_brace_depth = 0

            if in_materials_block:
                materials_brace_depth += line.count('{') - line.count('}')
                if materials_brace_depth < 0:
                    in_materials_block = False

            def repl(m):
                name = m.group(2)
                if in_materials_block or 'MTL' in name or name.startswith(prefix):
                    return m.group(0)
                return f'{m.group(1)}{prefix}{name}{m.group(3)}'

            updated_lines.append(pattern.sub(repl, line))

        final_output = '\n'.join(updated_lines)

        # 파일 저장
        new_path = save_path / "wrapper_assign.usda"
        new_path.write_text(final_output)
        print(f"[OK] Created: {new_path}")

        # 상위 wrapper 생성
        self.create_sublayer_wrapper(
            str(new_path),  # wrapper_lookdev.usda
            self.usd_path,  # geo.usd
            str(save_path / f"{self.prefix}.usda"),  # 최종 wrapper
            self.material_usd_path,  # 추가됨 ✅
            self.assign_usd_path  # 추가됨 ✅
        )

    def create_sublayer_wrapper(self, wrapper_usd_path, geo_usd_path, output_path, material_usd_path=None,
                                assign_usd_path=None):
        wrapper_usd_path = Path(wrapper_usd_path)
        geo_usd_path = Path(geo_usd_path)
        output_path = Path(output_path)

        # material / assign은 선택적
        material_usd_path = Path(material_usd_path) if material_usd_path else None
        assign_usd_path = Path(assign_usd_path) if assign_usd_path else None

        # 레이어 열기
        wrapper_layer = Sdf.Layer.FindOrOpen(str(wrapper_usd_path))
        geo_layer = Sdf.Layer.FindOrOpen(str(geo_usd_path))

        if not wrapper_layer or not geo_layer:
            raise RuntimeError("One or more source layers could not be opened.")

        # 새 상위 Layer 생성
        top_layer = Sdf.Layer.CreateNew(str(output_path))

        # 메타데이터 복사
        top_layer.startTimeCode = geo_layer.startTimeCode
        top_layer.endTimeCode = geo_layer.endTimeCode
        top_layer.timeCodesPerSecond = geo_layer.timeCodesPerSecond
        top_layer.framesPerSecond = geo_layer.framesPerSecond
        top_layer.defaultPrim = geo_layer.defaultPrim
        top_layer.documentation = geo_layer.documentation

        # ✅ subLayerPaths 순서 지정
        sublayers = [wrapper_usd_path.name]
        if material_usd_path and material_usd_path.exists():
            sublayers.append(material_usd_path.name)
        if assign_usd_path and assign_usd_path.exists():
            sublayers.append(assign_usd_path.name)
        sublayers.append(geo_usd_path.name)

        top_layer.subLayerPaths = sublayers
        top_layer.Save()

        print("[OK] Created:", output_path)
        print("  subLayers:")
        for s in sublayers:
            print(f"   - {s}")
