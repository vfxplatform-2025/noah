#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기존 네임스페이스에 추가 임포트 테스트
"""

import maya.cmds as cmds

def test_import_with_existing_namespace():
    """기존 네임스페이스가 있을 때 임포트 동작 테스트"""
    
    # 1. 첫 번째 임포트 (xgGroom)
    print("\n=== First Import: xgGroom ===")
    namespace = "c0082ma_e200_kite"
    file_path1 = "/show/TPM2/seq/TPM/TPM_2543/ani/wip/data/alembic/tpm2_214_262_2543_v08/c0082ma_e200_kite/c0082ma_e200_kite_xgGroom.abc"
    
    print("Namespaces before first import:", cmds.namespaceInfo(listOnlyNamespaces=True))
    
    # mergeNamespacesOnClash=False로 임포트
    cmds.file(file_path1, namespace=namespace, i=True, pr=True, ra=True,
              mergeNamespacesOnClash=False, type="Alembic", ignoreVersion=True,
              importTimeRange="combine", rnn=True)
    
    print("Namespaces after first import:", cmds.namespaceInfo(listOnlyNamespaces=True))
    print("Objects in namespace:", cmds.ls(namespace + ":*"))
    
    # 2. 두 번째 임포트 (geo) - 같은 네임스페이스 사용
    print("\n=== Second Import: geo ===")
    file_path2 = "/show/TPM2/seq/TPM/TPM_2543/ani/wip/data/alembic/tpm2_214_262_2543_v08/c0082ma_e200_kite/c0082ma_e200_kite_geo.abc"
    
    print("Namespaces before second import:", cmds.namespaceInfo(listOnlyNamespaces=True))
    
    # 동일한 옵션으로 임포트
    cmds.file(file_path2, namespace=namespace, i=True, pr=True, ra=True,
              mergeNamespacesOnClash=False, type="Alembic", ignoreVersion=True,
              importTimeRange="combine", rnn=True)
    
    print("Namespaces after second import:", cmds.namespaceInfo(listOnlyNamespaces=True))
    
    # 모든 네임스페이스의 오브젝트 확인
    for ns in cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True):
        if namespace in ns:
            objects = cmds.ls(ns + ":*")
            if objects:
                print(f"\nObjects in {ns}:")
                for obj in objects[:5]:  # 처음 5개만 출력
                    print(f"  - {obj}")
                if len(objects) > 5:
                    print(f"  ... and {len(objects)-5} more")


def test_with_merge_option():
    """mergeNamespacesOnClash=True로 테스트"""
    print("\n\n=== TEST WITH mergeNamespacesOnClash=True ===")
    
    # 새 씬에서 테스트
    cmds.file(new=True, force=True)
    
    namespace = "c0082ma_e200_kite_test"
    file_path1 = "/show/TPM2/seq/TPM/TPM_2543/ani/wip/data/alembic/tpm2_214_262_2543_v08/c0082ma_e200_kite/c0082ma_e200_kite_xgGroom.abc"
    file_path2 = "/show/TPM2/seq/TPM/TPM_2543/ani/wip/data/alembic/tpm2_214_262_2543_v08/c0082ma_e200_kite/c0082ma_e200_kite_geo.abc"
    
    # 첫 번째 임포트
    print("\nFirst import with merge=True...")
    cmds.file(file_path1, namespace=namespace, i=True, pr=True, ra=True,
              mergeNamespacesOnClash=True, type="Alembic", ignoreVersion=True,
              importTimeRange="combine", rnn=True)
    
    print("After first import:", cmds.namespaceInfo(listOnlyNamespaces=True))
    
    # 두 번째 임포트
    print("\nSecond import with merge=True...")
    cmds.file(file_path2, namespace=namespace, i=True, pr=True, ra=True,
              mergeNamespacesOnClash=True, type="Alembic", ignoreVersion=True,
              importTimeRange="combine", rnn=True)
    
    print("After second import:", cmds.namespaceInfo(listOnlyNamespaces=True))
    
    # 결과 확인
    for ns in cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True):
        if namespace in ns:
            objects = cmds.ls(ns + ":*")
            if objects:
                print(f"\nObjects in {ns}: {len(objects)} total")


if __name__ == "__main__":
    # 새 씬에서 시작
    cmds.file(new=True, force=True)
    
    # 테스트 실행
    test_import_with_existing_namespace()
    test_with_merge_option()