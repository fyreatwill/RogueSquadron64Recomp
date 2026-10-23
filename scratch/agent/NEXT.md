# NEXT: G1c - fold s6019_g1c_pos2 and s6018_g1c_r2 (tag g1_lvl1g1cpos2 / g1cr2b)
HYPOTHESIS-ID: g1c-draw-distance
Levers now scale rodata floats 0x3A4FC..0x3A50C (streamTerrainGridCellsByDistance). Check run.log `[g1c] rodata`/`scaled addrs` dump first (values must be sane distances, not 0.5).
Bin: `grep -a '^\[g1c\] state=\|^\[tricnt\]' run.log | awk` (see s6019 entry) by state. pos2 MUST give scaled tri < retail tri (control). If not, bisect addresses one at a time (ROGUESQ_DD_ADDRS=0x3A500 etc) in a single-run alt arm; also consider 0x80042B50 compares c.lt/c.le with $f2 from 0x3A4FC.
If control passes and r2 raises tris: LOD arm control next (ROGUESQ_DD_LOD=0.25), then 1.5/3x and ROGUESQ_DRAW_DISTANCE wrapper. fb-dump pairs for distant terrain fraction.
