# NEXT: widen the dd>1 terrain window past 64 columns (G5e side edge, s7008)
HYPOTHESIS-ID: dd-wide-window
Context: s7008 showed the 21:9 (and 16:9) side/corner edge at dd4 is the 64x64 terrain window's side face, 18-22 cells deep, on ~98% of calls;
K retuning cannot help (tools/g5e_window_geom.py). The only lever is more columns across the view.
Step 1 (offline, this unit's first half): read binPolygonIntoTerrainGrid, streamTerrainGridCellsByDistance, buildGridCellMeshForFace in
/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c (base sites 0x800425D4 0x8004271C 0x80042A48 0x80042A50 0x80042CF0
0x80042D20 0x80042D48 0x80043530 0x80043688; slot store 0x80043020 (row<<8)+4*col) and funcs_18.c 0x8007667C. Write down for each table: element
size, index formula (row = z or x?), which axis is the 64 limit, and who reads it. Decide whether the window axis to widen is fixed (z rows vs x cols)
or must follow the heading (then widen both to 128 and keep the area cap).
Step 2: apply_s7009_widewin.py (registered in RS64_REPLAY list in tools/fixup_game_funcs_vendored.py after apply_s6901): when dd>1 and
ROGUESQ_DD_WIDEWIN=1|tog, redirect the tables to a CPU-only buffer (host static or the spill arena >=0x80800000; these are not read by the RSP)
with stride 128, change the index shifts, and let apply_s6901 place w,d up to 128 (cap still honoured). Live tree patched in place + cmake build.
Hypotheses for the test: H-fix (side edge gone, side-third hard80 drops toward dd1 floor, no crash) / H-budget (pool/cap 2048 or tier cap 600 limits
the kept cells, so the wider box fills only partially: [gridlog] kept==cap) / H-cost (VI or frame time drops, G1b instrument).
Test: env CULL=1 ASP=21:9 CW=1260 CH=540 zsh scratch/s7008/arm.zsh 4 4 x1 "ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=tog ROGUESQ_G3E_TRACE=$PWD/scratch/s7008/trace_x1.txt" 120 60
score g5e_edge_score.py raw 4 2600 50 24e6 per third + g5e_window_geom.py (adapt to 128); positive control = trace shows w>64 in on seconds.
Then 300 s hold L4/L1/L15 at 21:9 dd4 for crashes; owner sheet 16:9 + 21:9. Delete raws after scoring (disk ~22 GB).
