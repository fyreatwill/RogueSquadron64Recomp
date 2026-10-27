# NEXT: does processGridCellByDistance (0x80048BAC) / updateActiveGridCellState (0x80047368) take a radius that scales the processed cell set?
HYPOTHESIS-ID: g1c-dd8-limit
Known (s6482): row+2 insert writers are generic list push/unlink (object-bound, single-source); no distance gate there.
H-radius2: processGridCellByDistance uses a radius constant/table -> scale by DRAW_DISTANCE, check [exitlog] pass count + terrain fraction dd1 vs lever.
H-object-bound-all: no radius anywhere in grid code -> close L-radius, pivot to L-lod / fog (G1c levers).
Work: read funcs_10.c for those two functions (N64Recomp/RecompiledFuncs), name the radius, one-site env lever, measure.
