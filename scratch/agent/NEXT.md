# NEXT: re-measure the s7016 gfx-host-glue walk costs with the de-biased xor8 split
HYPOTHESIS-ID: gfx-host-glue
Context: s7017 replaced the biased s7010 parity split with xor8 = (sec ^ sec>>3)&1 (rs64_tog_odd, default; anchor line carries split=xor8;
tools/g5e_cost_by_parity.py auto-reads it). A/A null +0.08 ms rsp, WIDEWIN=tog positive control +3.50 ms. s7016's GLUE_TOG=1 (skip walks on odd
seconds) and GLUE_TOG=2 (unfused two-pass walk) deltas were read through the biased split, so the glue walks' real rsp/run share is unknown.
Hypotheses: H-glue-big (walks cost >= 1 ms/frame of gfx-thread time: next trim the spike cull / pillar walk further), H-glue-small
(< 0.3 ms: glue trimming is done, the remaining gfx cost is ucode self + RT64 decode -> profile those), H-placement (walk cost lands in
dpc/rdp, not rsp: check which TL interval carries it).
Run (one script, both arms, same build): copy scratch/s7017/all.zsh; arms G2 = GLUE_TOG=1 GLUE_TIME=1, F2 = GLUE_TOG=2 GLUE_TIME=1, on
L1 21:9 dd4 MELT WIDEWIN=1 CULL=1 (ROGUESQ_G1E_TL each). Split each with g5e_cost_by_parity.py (+ --shift-ms 500 null). Reference null N2
= +0.08 ms (ring not kept; re-run an A/A arm GLUE_TOG=3 alongside if a fresh null is needed).
Accept: |shift-500| <= 0.2; report T/run/rsp deltas per arm and pick H-glue-big vs H-glue-small.
