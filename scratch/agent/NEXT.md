# NEXT: cut the WIDEWIN RSP cost by culling out-of-frustum cells (G5e side edge, s7010)
HYPOTHESIS-ID: dd-wide-window
Context: s7010 named the WIDEWIN cost: the gfx task (LLE F5 ucode) grows 13.3 -> 16.9 ms/frame (p90 16.3 -> 23.2) on wide seconds, crossing the ~14 ms
VI budget (P(>=2VI) 0.07 -> 0.61, fps 56 -> 37); guest run only +0.7 ms. Fold SOAK-RESULTS s7009_widewin_L4 first (pass = crash=0, wide17>0).
Hypotheses for the cull lever:
 H-offscreen: most of the extra 4096 cells are outside the horizontal frustum (s7008: footprint 140-290 cells wide but the box is pinned to the near
   footprint edge); culling them before mesh build/submit removes most of the +3.6 ms while keeping the side-edge gain.
 H-onscreen: the extra cells that cost are on screen (far side band), so a cull saves little and only an area cap (fewer far cells) trades edge for cost.
Discriminator, ONE build: in buildGridCellMeshForFace (or the stream loop) skip cells whose 2D box is outside the frustum wedge from site 13's bounds/eye
(site 11), behind ROGUESQ_DD_WIDEWIN_CULL=1|tog, counting culled vs kept per call (trace site 19). Run scratch/s7010/arm.zsh 4 4 c1 with
WIDEWIN=1 WIDEWIN_CULL=tog G1B=1 G1E_TL (NOCAP=1), score tools/g5e_cost_by_parity.py. Positive control: culled count > 0 and a CULL=all arm (cull
everything outside the 64 core) must show no side-edge gain. Then a capture run (CW=1260) for g5e_edge_score per third: cull-on must keep the
side hard80 gain of s7009 (16->8%) with no new holes. Outcomes: rsp on-off delta drops to <1 ms with edge kept -> H-offscreen, ship; delta stays ~3 ms
-> H-onscreen, try ROGUESQ_DD_WIDEWIN_N=96 + area cap and report the edge/cost trade to the owner.
Run from build/ via the arm script; delete raws after scoring (disk ~20 GB free).
