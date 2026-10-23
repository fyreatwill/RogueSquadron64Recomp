# NEXT: G1c - fold s6020_g1c_posB / posAB / r2B (tags g1_lvl1g1cposB / posAB / r2B)
HYPOTHESIS-ID: g1c-draw-distance
Levers: RAM floats 0x9DEAC/0x9DEB0 (physical) feeding the terrain footprint polygon. Check run.log `[g1c] ram 0x9DE98..` dump first (values must be sane, nonzero distance-like).
Bin: grep -a '^\[g1c\] state=\|^\[tricnt\]' run.log | awk by state, ONLY tasks with tri>=50 (menu/boot tasks swamp the mean). Control: posB/posAB scaled tri must be clearly < retail (>10%).
Pass -> r2B tri rise = L-radius; flat = L-budget; then fb-dump distant-terrain fraction, 1.5x/3x, ROGUESQ_DRAW_DISTANCE wrapper. Fail -> try 0x80130C50 FOV scale / sinf args at 0x800438D4, or the LOD table 0x9ECB0 control.
