#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Alembic 파일 구조 분석 스크립트
네임스페이스 중복 문제 원인 파악용
"""

import maya.cmds as cmds
import maya.mel as mel

def analyze_alembic_structure(abc_file):
    """Alembic 파일의 내부 구조를 분석"""
    print("\n=== ALEMBIC FILE STRUCTURE ANALYSIS ===")
    print("File: %s" % abc_file)
    
    # 1. AbcImport -h 명령으로 계층 구조 확인
    try:
        hierarchy_cmd = 'AbcImport -h "%s"' % abc_file
        print("\n1. Hierarchy structure:")
        mel.eval(hierarchy_cmd)
    except:
        print("Failed to get hierarchy")
    
    # 2. 임시로 임포트하여 구조 확인
    temp_namespace = "TEMP_ABC_TEST"
    
    # 기존 temp namespace 삭제
    if cmds.namespace(exists=temp_namespace):
        cmds.namespace(rm=temp_namespace, deleteNamespaceContent=True)
    
    # 네임스페이스 없이 임포트
    print("\n2. Import without namespace:")
    cmds.AbcImport(abc_file, mode='import')
    
    # 임포트된 최상위 노드 확인
    top_nodes = cmds.ls(assemblies=True)
    print("Top level nodes: %s" % top_nodes)
    
    # 네임스페이스 확인
    all_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
    print("All namespaces: %s" % all_namespaces)
    
    # 3. 네임스페이스와 함께 임포트
    print("\n3. Import with namespace:")
    cmds.namespace(add=temp_namespace)
    cmds.file(abc_file, i=True, namespace=temp_namespace, 
              mergeNamespacesOnClash=False, type="Alembic")
    
    # 새로 추가된 네임스페이스 확인
    new_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
    print("Namespaces after import: %s" % new_namespaces)
    
    # 계층 구조 출력
    print("\n4. Object hierarchy:")
    temp_objects = cmds.ls(temp_namespace + ":*", long=True)
    for obj in sorted(temp_objects)[:20]:  # 처음 20개만
        print("  %s" % obj)
    
    # 정리
    if cmds.namespace(exists=temp_namespace):
        cmds.namespace(rm=temp_namespace, deleteNamespaceContent=True)

# 사용 예시:
# analyze_alembic_structure("/path/to/your/alembic.abc")