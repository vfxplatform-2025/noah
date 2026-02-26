# Noah 네임스페이스 중복 문제 해결 문서

## 문제 상황
Noah 패키지에서 Alembic 파일을 임포트할 때 네임스페이스 불일치 문제가 발생했습니다.

### 증상
- 빈 씬에서 Alembic 임포트 시에도 네임스페이스에 숫자가 붙음
- Root 오브젝트: `c0099mc_e200_extra_fish_c:geo` (정상)
- 하위 오브젝트: `c0099mc_e200_extra_fish_c1:hair`, `c0099mc_e200_extra_fish_c1:fin` 등 (문제)

### 예시
```
빈 씬에서 임포트 결과:
├─ c0099mc_e200_extra_fish_c:geo         ✓ (정상)
├─ c0099mc_e200_extra_fish_c1:hair       ✗ (숫자 추가됨)
├─ c0099mc_e200_extra_fish_c1:fin        ✗ (숫자 추가됨)
└─ c0099mc_e200_extra_fish_c1:mouth      ✗ (숫자 추가됨)
```

## 문제 원인

### 1. 네임스페이스 사전 생성 문제
Noah 코드가 Alembic 임포트 전에 네임스페이스를 미리 생성하고 있었습니다:

1. **utilScript.py** (420-424줄):
   ```python
   # 네임스페이스가 없을 때만 생성
   elif ":" in item:
       namespace = item.split(':')[0]
       if not cmds.namespace(exists=namespace):
           cmds.namespace(add=namespace)
   ```

2. **alembicScript.py** (구버전):
   ```python
   # Ensure namespace exists before import
   namespace = item.split(":")[0]
   if not cmds.namespace(exists=namespace):
       cmds.namespace(add=namespace)
   ```

### 2. Maya의 자동 충돌 처리
- 빈 네임스페이스가 이미 존재하면, Maya가 Alembic 임포트 시 내부 충돌을 감지
- 일부 오브젝트에 자동으로 숫자를 붙여서 새 네임스페이스 생성 (예: `c0099mc_e200_extra_fish_c1`)

## 해결 방법

### 1. utilScript.py 수정
네임스페이스 사전 생성 코드를 주석 처리:

```python
# 네임스페이스가 없을 때만 생성 - 제거 (Maya가 임포트 시 자동 생성하도록)
# elif ":" in item:
#     namespace = item.split(':')[0]
#     if not cmds.namespace(exists=namespace):
#         cmds.namespace(add=namespace)
```

### 2. alembicScript.py 수정
네임스페이스 사전 생성 제거:

```python
if ":" in item:
    # Extract namespace but DON'T create it - let Maya handle it during import
    namespace = item.split(":")[0]
    print("DEBUG: Will import with namespace: %s" % namespace)
    
    # Only check for existing objects, don't create namespace
    if cmds.namespace(exists=namespace):
        existing_objects = cmds.ls(namespace + ":*")
        print("DEBUG: Namespace %s already exists with %d objects" % (namespace, len(existing_objects)))
```

### 3. 임포트 옵션 수정
Maya의 수동 임포트와 동일한 옵션 사용:

```python
returnList = cmds.file("%s" % itemDir, namespace="%s" % namespace, i=True, pr=True, ra=True,
                       mergeNamespacesOnClash=False, type="Alembic", ignoreVersion=True,
                       importTimeRange="combine", rnn=True)
```

## 영향 범위

### 수정이 적용되는 데이터 타입
- **모든 Alembic 기반 타입**: alembicAni, alembicCloth, alembicFx, alembicHair 등
- **I/O 관련 데이터**: ioScript.py 사용 데이터

### 독자적 처리를 하는 데이터 타입
- **Maya 파일**: mayaScript.py (reference는 root namespace `:` 사용)
- **Model/Rig**: modelScript.py, rigScript.py (개별 수정됨)
- **USD**: usdScript.py (독자적 네임스페이스 처리)

## 테스트 결과

### 수정 전
```
DEBUG: Namespaces before import: ['UI', 'c0099mc_e200_extra_fish_c', 'shared']
DEBUG: Namespaces after import: ['UI', 'c0099mc_e200_extra_fish_c', 'c0099mc_e200_extra_fish_c1', 'shared']
```

### 수정 후 (예상)
```
DEBUG: Namespaces before import: ['UI', 'shared']
DEBUG: Namespaces after import: ['UI', 'shared', 'c0099mc_e200_extra_fish_c']
```

## 주의사항

1. **Maya 버전 호환성**: Maya가 자동으로 네임스페이스를 처리하도록 하므로 Maya 버전에 따라 동작이 약간 다를 수 있습니다.

2. **Cancel 시 넘버링**: 중복 오브젝트가 있을 때 Cancel을 선택하면 utilScript.nameSpaceCheck()에서 수동으로 넘버링된 네임스페이스를 생성합니다.

3. **배포 경로**:
   - 개발: `/storage/.NAS5/rocky9_core/TD/users/chulho/packages/noah/1.9.0/`
   - 프로덕션: `/storage/.NAS5/core/Linux/APPZ/packages/noah/1.9.0/`

## 수정 이력

- **2024-01-08**: 네임스페이스 중복 문제 해결
  - utilScript.py: 네임스페이스 사전 생성 코드 주석 처리
  - alembicScript.py: 네임스페이스 사전 생성 제거, 임포트 옵션 수정

## 추가 개선 사항

향후 개선이 필요한 부분:
1. 네임스페이스 관리자 클래스 구현으로 중앙 관리
2. 각 스크립트별 독자적 처리 통합
3. 네임스페이스 충돌 처리 옵션 확장 (merge, prefix 추가 등)