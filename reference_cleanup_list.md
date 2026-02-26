# Reference Hair Data Cleanup List

## 레퍼런스 데이터를 Group 데이터처럼 깨끗하게 만들기 위한 삭제 목록

### 현재 구조 분석
- **Group (깨끗한 데이터)**: `c0078ma_e200_romi_daily:*` (단일 네임스페이스)
- **Reference (정리 필요)**: `c0082ma_e200_kite:c0078ma_e200_romi_daily:*` (중첩 네임스페이스)

---

## 삭제해야 할 데이터 목록

### 1. Body Geometry Groups (전체 삭제)
```
c0082ma_e200_kite:c0078ma_e200_romi_daily:geo
├── c0082ma_e200_kite:c0078ma_e200_romi_daily:body_geo_grp
├── c0082ma_e200_kite:c0078ma_e200_romi_daily:pants + pantsShape + pantsShapeOrig
├── c0082ma_e200_kite:c0078ma_e200_romi_daily:bracelet_grp (전체 bracelet 시리즈)
│   ├── bracelet_01~16 + Shapes + ShapeOrigs
├── c0082ma_e200_kite:c0078ma_e200_romi_daily:watch_grp
│   ├── watch_string + watchShapes
│   ├── glass + glassShape
│   ├── watch + watchShape
├── c0082ma_e200_kite:c0078ma_e200_romi_daily:necklace_grp
│   ├── ring + ringShape
```

### 2. DMM Simulation Group (전체 삭제)
```
c0082ma_e200_kite:c0078ma_e200_romi_daily:dmm_GRP
```

### 3. Rig Controls (숨김 처리, 삭제 안함)
```
c0082ma_e200_kite:c0078ma_e200_romi_daily:rig
```

### 4. 네임스페이스 정리
- 중첩 네임스페이스 `c0082ma_e200_kite:c0078ma_e200_romi_daily:*`를 
- 단일 네임스페이스 `c0078ma_e200_romi_daily:*`로 변경

### 5. Selection Sets 정리
- `pasted__*` 패턴의 모든 sets
- `c0082ma_e200_kite*` 네임스페이스 관련 sets
- `Default*Filter*` 시리즈 sets

---

## 보존해야 할 Hair 데이터

### Hair System 구조 (보존)
```
c0078ma_e200_romi_daily:hair/
├── c0078ma_e200_romi_daily:pfx_GRP
├── c0078ma_e200_romi_daily:bang_GMHHairSystem
├── c0078ma_e200_romi_daily:round_GMHHairSystem
├── c0078ma_e200_romi_daily:round_surfaceGrp
├── 모든 follicle, curve, stroke 객체들
```

### Head Geometry (보존 - Hair 관련)
```
c0078ma_e200_romi_daily:Head_Geo_Grp/
├── c0078ma_e200_romi_daily:head
├── c0078ma_e200_romi_daily:eyebrow + eyebrowShape
```

---

## 삭제 스크립트 패턴

### 패턴 매칭으로 삭제할 객체들:
1. `*:pants*`
2. `*:bracelet*`  
3. `*:watch*`
4. `*:necklace*`
5. `*:ring*`
6. `*:glass*`
7. `*:dmm_GRP*`
8. `*:body_geo_grp*`

### 예외 (삭제하지 않을 객체들):
- `*:hair*` (모든 hair 관련)
- `*:head*` (head geometry)
- `*:eyebrow*` (eyebrow geometry)
- `*:rig*` (숨김만 처리)

---

## 최종 목표 구조
Reference 데이터가 Group과 동일한 구조가 되도록:
```
c0078ma_e200_romi_daily:root/
├── c0078ma_e200_romi_daily:geo/
│   └── c0078ma_e200_romi_daily:Head_Geo_Grp/
│       ├── head
│       └── eyebrow
├── c0078ma_e200_romi_daily:hair/ (전체 hair system)
└── c0078ma_e200_romi_daily:rig (hidden)
```