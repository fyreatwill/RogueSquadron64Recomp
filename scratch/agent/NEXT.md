# NEXT (s7232): are WIDEWIN's extra triangles on screen? (s7231: WIDEWIN = +4.5 ms/task in L4 t=77-97 at 21:9 dd4, flat 30/s)
HYPOTHESIS-ID: widewin-heavy-window-cost
Context: s7231 2x2 (L4 t=77-97, 21:9, owner path): dd4 13.96 ms/60, dd6 14.62/58.6, dd4+WW 18.47/30, dd6+WW 20.73/30. Cost tracks RDP
tri/task (1.80 ms per 1000, R2 0.60) plus a window residual (+1.3..+3.7 ms, biggest with WW). Cap 8192 (26% fewer streamed cells) saves
nothing; K0.45 saves ~1 ms.
Hypotheses for WW's +2k tri/task and residual:
  H-offscreen: WW cells submit triangles that land outside the 21:9 scissor (or entirely in the guard band): pure waste -> a host-side
    per-cell frustum test on the WW-only columns removes them with no visible change.
  H-onscreen: the extra triangles are the visible side terrain WW exists to draw -> only a budget/governor (trim WW columns when the last
    N tasks > ~15 ms) or a cheaper LOD for the outer WW columns can help; owner chooses look vs 60.
  H-clip: the residual is ucode clip/cull work on vertices whose triangles never reach the RDP (count by vertices loaded vs tris out).
Discriminator, ONE build: in the existing G1CF RDP stream walk (src/main/rt64_render_context.cpp ~line 2205, s_g1cf.tri) decode each
triangle's YH/YL and XL/XH/XM edge starts (fixed point s11.2 / s15.16) and count tri_in (bbox intersects the scissor), tri_out (bbox
fully outside), plus per gfx task the ucode's vertex-load count if a counter exists (grep ROGUESQ_ for vtx counters first). Print in [g1cf].
Positive control: at 4:3 dd1 tri_out must be ~0; a forced off-screen arm (ROGUESQ_DD_WIDEWIN=1 at 4:3 dd4, where the extra side cells are
off-screen by construction) must show tri_out > 0.
Run: same arms as s7231 run2/run3 (scratch/s7231/run2.zsh, run3.zsh) a4 vs n4 only, plus the 4:3 control. Score: tools/s7231_cost_decomp.py
(extend to tri_in/tri_out). Outcome: WW's extra tri mostly tri_out -> H-offscreen (build the cull); mostly tri_in -> H-onscreen (governor);
tri equal but residual large -> H-clip.
Visual bar: keep the s7009 side-edge gain (docs/owner_sheet_s7009_widewin_219.png) and the L4 far-left shoreline (s7052).
