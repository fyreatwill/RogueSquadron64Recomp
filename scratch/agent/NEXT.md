# NEXT: name the WIDEWIN frame cost (G5e side edge, s7009)
HYPOTHESIS-ID: dd-wide-window
Context: s7009 landed ROGUESQ_DD_WIDEWIN (tools/apply_s7009_widewin.py, opt-in). Same-run tog at 21:9 dd4 L4 cuts side-third hard edges
(N128 18.4->14.6 / 16.1->8.3; N96 21.2->12.7 / 17.7->5.8) with 0 crashes, but captured fps falls ~60 -> ~50 in wide seconds. N96 (96x85) costs the
same as N128 (128x64): cost follows the kept-cell area (8192 vs 4096), not the shape. Owner bar (G1c): no frame-time regression beyond baseline.
First fold the queued holds: SOAK-RESULTS lines s7009_widewin_L4/L1/L15 (pass = crash=0 and wide17>0). A crash there outranks this unit.
Hypotheses for the cost (one build already has every lever; add only a cost instrument if G1B lacks it):
 H-guest: streamTerrainGridCellsByDistance + buildGridCellMeshForFace host time on the game thread doubles (cells x2).
 H-rsp: LLE F5 ucode host ms per gfx task doubles (tris x2); check ROGUESQ_UCODE_CAP fires too (cap reached = lost terrain AND cost).
 H-rdp: RT64 GPU/present wait grows.
Discriminator, ONE run: scratch/s7009/arm.zsh 4 4 c1 "ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=tog ROGUESQ_G1B=1 ROGUESQ_G3E_TRACE=..." 120 60 (check what
ROGUESQ_G1B logs first: grep G1B src/main/*.cpp src/rsp/*.cpp); split per-frame gfx-task host ms, guest frame ms and present wait by tog parity
(mach second parity, 24e6 ticks). The term that rises ~20% in on seconds names the cost. Cheap arm in the same unit if H-guest: time the two guest
functions with mach_absolute_time in a fixup (trace site 19 per call).
Fix candidates by outcome: H-rsp -> cull cells whose box is outside the side FOV wedge before submit (the window box is wider than the frustum near
the eye); H-guest -> same cull earlier, in stream; any -> cap the area at the cost budget (pool cap via ROGUESQ_DD_WIDEWIN_AREA) and re-score.
Then owner sheet at 16:9 too (same arm with ASP=16:9 CW=960) and ask the owner to judge. Delete raws after scoring (disk ~21 GB).
