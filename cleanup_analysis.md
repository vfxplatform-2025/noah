# Hair Export Cleanup Analysis

## Current Situation
Based on Maya command port analysis, we have:
- **Group**: Clean hair data from copy/paste operation
- **Reference**: `c0082ma_e200_kite:c0078ma_e200_romi_daily:root` with reference data that needs cleanup

## Reference Structure
The reference contains 4 main children:
1. `c0082ma_e200_kite:c0078ma_e200_romi_daily:geo`
2. `c0082ma_e200_kite:c0078ma_e200_romi_daily:hair` ✓ (needed)
3. `c0082ma_e200_kite:c0078ma_e200_romi_daily:rig`
4. `c0082ma_e200_kite:c0078ma_e200_romi_daily:dmm_GRP` ❌ (unwanted)

## Objects to DELETE from Reference:

### 1. Unwanted Geometry Objects
- `*:body_all` - Character body mesh
- `*:teeth` - Teeth geometry 
- `*:HairGeoGrp` - Hair geometry group (redundant)
- `*:dmm_GRP` - DMM simulation group

### 2. Rig Objects (to HIDE, not delete)
- `*:rig` - Character rig controls

### 3. Selection Sets (to DELETE)
All objectSets with these namespace prefixes:
- `*c0082ma_e200_kite*`
- `*c0078ma_e200_romi_daily*`
- Area sets: `eyeBrowArea`, `eyeBrowLineArea`, `eyeLidArea`, etc.

### 4. Controller Sets (to DELETE)
All sets starting with `pasted__*` (from copy/paste operation):
- Animation controller sets
- Hair controller sets
- Constraint sets

## Final Goal
Transform reference structure to match group structure:
- Keep only hair-related geometry and systems
- Remove body, teeth, and other unwanted objects
- Hide rig but don't delete (for animation reference)
- Remove all selection sets
- Rename root to `{asset_name}_hair` format

## Implementation
The cleanup script should:
1. Import reference to make it editable
2. Delete unwanted objects by pattern matching
3. Delete all namespace-related sets
4. Hide rig objects
5. Rename root group
6. Clean up shaders (keep only hair/eyebrow)