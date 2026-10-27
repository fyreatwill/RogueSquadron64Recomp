# NEXT: read ROM values at 0x8003A80C/0x8003A810 (flood-fill cutoff), 0x8003A7D8 (XZ range), 0x8003A7B8/7BC; one-site env lever scaling 0x8003A80C/10 by DRAW_DISTANCE
HYPOTHESIS-ID: g1c-dd8-limit
Known (s6482): inserts have no distance gate (two-source). Radius gates: processGridCellByDistance cutoffs 0x8003A80C/0x8003A810 (called by streamTerrainGridCellsByDistance funcs_9.c:13945), isPointXzWithinRangeOfRef 0x8003A7D4/7D8.
H-flood-cutoff: scaling 0x8003A80C/10 raises [exitlog] pass count + terrain fraction at dd1 -> bundle under DRAW_DISTANCE.
H-no-effect: no change -> cutoff not binding; pivot L-lod/fog.
Work: read the floats from rogue_squadron.z64 (or rdram at runtime), write an env lever patching them at boot (fixup script), run dd1 vs lever phase-gated, with positive control (cutoff x0 must collapse pass count).
