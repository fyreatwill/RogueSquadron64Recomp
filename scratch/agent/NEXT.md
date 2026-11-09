# NEXT: WIDEWIN edge/cost trade by pool area cap, one same-run 3-phase toggle (G5e side edge, s7011)
HYPOTHESIS-ID: dd-wide-window
Context: s7010 put the WIDEWIN cost in the gfx ucode (+3.6 ms/task at cap 8192 = 128x64). s7011: the game already frustum-culls cells (a wedge cull
removes nothing) and the LOD tiers do not move cost (LODMUL 0.25/4 inside the ~1 ms parity noise). The cost is the on-screen side-band cells, so the
only lever left is how many: the area cap the s7009 window placement spends (src: apply_s7009_widewin.py, `cap` loop; site 17 logs ww,w,d,cap).
Hypotheses:
 H-linear: rsp cost and side-edge gain both scale with area, so a middle cap (6144 = 96x64) gives about half of each; owner picks a point.
 H-knee: most of the side-edge gain comes from the first extra columns (the side face is 18-22 cells deep), so cap 6144 keeps most of the hard80 gain
   at about half the cost -> make 6144 the WIDEWIN default.
 H-flat-cost: cost does not drop until the cap is near 4096 (for example a per-task fixed cost from crossing 64 cols) -> report that WIDEWIN is all-or-nothing.
Build ONE change: ROGUESQ_DD_WIDEWIN_CAP=<a,b,c> (default unset = 8192), and with WIDEWIN=tog3 the cap cycles a/b/c on (mach/24e6) % 3 seconds; print a
[s7010-clk] anchor; extend tools/g5e_cost_by_parity.py with --phases 3 (phase = (mach/24e6) % 3). Use CULL=1 (CULL_SPIKE=tog shares the parity).
Runs (one at a time): (1) NOCAP=1 ASP=21:9 zsh scratch/s7011/arm.zsh 4 4 k1 "ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=tog3 ROGUESQ_DD_WIDEWIN_CAP=4096,6144,8192
 ROGUESQ_G1B=1 ROGUESQ_G1E_TL=$PWD/scratch/s7012/tl_k1.bin" with CULL=1 -> rsp per phase; positive control: phase 8192 vs 4096 must reproduce ~+3.6 ms.
 (2) CW=1260 CH=540 capture run of the same env -> tools/g5e_edge_score.py per third and phase (needs the same 3-phase key), sheet for the owner.
Outcomes: rsp(6144)-rsp(4096) ~ half of 8192's and edge gain ~ half -> H-linear; edge gain at 6144 >= 75% of 8192's with <= 60% of cost -> H-knee;
rsp(6144) ~ rsp(8192) -> H-flat-cost. Delete raws after scoring (disk ~19 GB free).
