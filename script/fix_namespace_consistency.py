#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
네임스페이스 일관성 수정 스크립트
임포트 후 root와 하위 오브젝트의 네임스페이스를 통일
"""

import maya.cmds as cmds
import re

def fix_namespace_consistency(target_namespace, fix_numbered=True):
    """
    주어진 네임스페이스와 숫자가 붙은 변형들을 통일
    
    Args:
        target_namespace: 목표 네임스페이스 (예: "c0099mc_e200_extra_fish_c")
        fix_numbered: True면 숫자가 붙은 네임스페이스도 병합
    """
    print("\n=== FIXING NAMESPACE CONSISTENCY ===")
    print("Target namespace: %s" % target_namespace)
    
    # 1. 현재 네임스페이스 상태 확인
    all_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
    
    # 숫자가 붙은 네임스페이스 찾기
    pattern = "^%s\\d+$" % re.escape(target_namespace)
    numbered_namespaces = [ns for ns in all_namespaces if re.match(pattern, ns)]
    
    if not numbered_namespaces:
        print("No numbered namespaces found for: %s" % target_namespace)
        return
    
    print("Found numbered namespaces: %s" % numbered_namespaces)
    
    # 2. 목표 네임스페이스가 없으면 생성
    if not cmds.namespace(exists=target_namespace):
        cmds.namespace(add=target_namespace)
        print("Created target namespace: %s" % target_namespace)
    
    # 3. 숫자가 붙은 네임스페이스의 오브젝트를 목표로 이동
    for ns in numbered_namespaces:
        print("\nProcessing namespace: %s" % ns)
        
        # 해당 네임스페이스의 모든 오브젝트 찾기
        objects = cmds.ls("%s:*" % ns, long=True)
        print("Found %d objects" % len(objects))
        
        # 각 오브젝트를 새 네임스페이스로 이동
        for obj in objects:
            if cmds.objExists(obj):
                # 오브젝트 이름에서 네임스페이스 부분만 변경
                obj_short = obj.split("|")[-1]
                if ":" in obj_short:
                    obj_name = obj_short.split(":", 1)[1]
                    new_name = "%s:%s" % (target_namespace, obj_name)
                    
                    # 이미 존재하는지 확인
                    if not cmds.objExists(new_name):
                        try:
                            cmds.rename(obj, new_name)
                            print("Renamed: %s -> %s" % (obj_short, new_name))
                        except Exception as e:
                            print("Failed to rename %s: %s" % (obj, str(e)))
        
        # 빈 네임스페이스 제거
        try:
            if cmds.namespaceInfo(ns, listNamespace=True) == []:
                cmds.namespace(rm=ns)
                print("Removed empty namespace: %s" % ns)
        except:
            print("Could not remove namespace: %s" % ns)
    
    print("\n=== NAMESPACE FIX COMPLETED ===")
    
    # 최종 상태 확인
    final_objects = cmds.ls("%s:*" % target_namespace)
    print("Total objects in %s: %d" % (target_namespace, len(final_objects)))
    
    return True


# Alembic 임포트 직후 호출하는 함수
def post_import_namespace_fix(namespace):
    """Alembic 임포트 직후 네임스페이스 일관성 수정"""
    # 약간의 지연 후 실행 (임포트 완료 대기)
    cmds.evalDeferred(lambda: fix_namespace_consistency(namespace), lowestPriority=True)