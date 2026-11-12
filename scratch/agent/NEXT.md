# NEXT (s7233): thin WIDEWIN's far cells (s7232: WW's extra tris are 42% zero-height + 58% tiny, +2% area, +5.75 ms)
HYPOTHESIS-ID: widewin-heavy-window-cost
Context: s7232 L4 t=77-97, 21:9 dd4: a4 (WW) - n4 = +2557 tri/task = tin +1490 / tout 0 / tzero +1066, dkpx +42 of 1990. The ucode
already culls off-screen; retail LOD is already coarsest past node 7 (s7011). So the only levers reduce input geometry for far WW cells.
Hypotheses:
  H-radius: the waste sits in the WW-only columns beyond some distance R -> a WW-only radius limit (draw the extra columns only within R
    cells of the eye) removes most tzero and cost with little kpx loss.
  H-thin: waste is spread across all WW distances -> need a coarser mesh (skip alternate vertices/rows) for WW cells past R.
  H-near: the extra tris are mostly in near WW cells (big but steep/sliver) -> neither helps; governor only.
Discriminator, ONE build: find where WIDEWIN extends the stream window (grep rs64_s7009 / WIDEWIN in src/main/upstream_compat.cpp and
tools/apply_s7009*.py), add ROGUESQ_DD_WIDEWIN_R=<cells> (cells outside the retail 64-column window and farther than R from the eye are
skipped) with _TOG=1 odd-second toggling (same [s7010-clk] parity as WIDEWIN=tog). Arms in one run: R=16, 24, 32 (tog each) at 21:9 dd4
L4 via tools/g1e_owner_quiet_arms.zsh (copy scratch/s7232/run.zsh, ROGUESQ_G1CF=1 G1B=1). Score: tools/s7232_tri_onscreen.py per parity
(extend with --parity from [s7010-clk]) for dtri/dtzero/dkpx and sd per toggle. Outcome: an R where sd falls >=3 ms with kpx loss <0.5% ->
H-radius, then owner sheet (side edge, s7009/s7052 refs); no R helps without large kpx loss -> H-thin; cost moves with nothing -> H-near.
Visual bar: keep the s7009 side-edge gain (docs/owner_sheet_s7009_widewin_219.png) and the L4 far-left shoreline (s7052).
