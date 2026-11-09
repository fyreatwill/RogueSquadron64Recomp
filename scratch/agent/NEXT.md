# NEXT: G1c per-cell cost — phase-split profile at dd6 tog3 (name the blocks that grow with cells)
HYPOTHESIS-ID: g1c-dd-headroom
Context (s7020, same run, L1 21:9 WIDEWIN owner path dd6): cap 8192 = dd4 cost (59.2 fps, rsp 12.42, run 3.10); cap 10240 rsp +1.7, run +0.7
(52 fps). The dd multiplier costs ~0; the binding limit above dd4 is per-cell cost. G5i: fixed, owner look only — check CURRENT-TRUTH item 1 first.
Hypotheses for where the +1.7 ms rsp lives: H-ucode-xform (F5 ucode vertex transform/clip blocks scale with cell vertices), H-rdp-decode (RT64
RDP interpret/triangle decode inside the DPC_END submit, L_1198 incl), H-glue (bridge walks, closed at 0.2-0.45 ms total so expect small);
for the +0.7 ms run: H-stream (guest streamTerrainGridCellsByDistance / buildGridCellMeshForFace per cell).
Discriminator, ONE run: scratch/s7020/run.zsh recipe (dd6 tog3 CAP=8192,10240,10240) + xctrace Time Profiler 30 s at ~150 s (see s7014 k3
recipe in PORTING-STATE, grep "Run k3"). Split samples by cap phase using the sample timestamps + the [s7010-clk] anchor (extend
tools/xctrace_ucode_blocks.py with --anchor/--phases 3 if it lacks it), then per block / host function: self samples per second in p0 vs p1+p2.
The blocks whose delta sums to ~1.7 ms/frame name the path; positive control: total gfx-thread busy delta must match g5e_cost_by_parity rsp
delta on the same run (skip the xctrace window for the TL split, or report both). Then cut the biggest term (one change, same-run tog A/B).
