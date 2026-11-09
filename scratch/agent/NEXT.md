# NEXT: G1c phase 2 — cut the gfx-side per-cell cost (the binding term above dd4)
HYPOTHESIS-ID: g1c-gfx-percell
Context: s7020/s7021 at L1 dd6 21:9 WIDEWIN: +2048 cells = gfx thread +1.72 ms/frame (ucode self 0.70 over L_1F98/pre/L_1090/L_162C/L_16B8/L_1298/L_1740;
DPC submit 0.68 = bridge self 0.24 + RT64 submit_rdp_range 0.23 + record_submit 0.16) and game +0.91. s7022-s7025 closed the game-side stream walk
(clamp drift = our create hook, fixed s7025). G5i/owner items: nothing to run (CURRENT-TRUTH items 1-14), check them first.
Step 1 (boring first, same build): dd6 cap 10240 fps with the s7025 fix vs cap 8192 same run (tog3 caps, scratch/s7024/run3.zsh S6-style arm, G1E_TL timer)
 to re-baseline the cells-cost line after s7025.
Hypotheses for the DPC submit share (0.68 ms per 2048 cells):
 H-percall: per-submit fixed cost (bridge + submit_rdp_range called once per small RDP range): predicts submit count scales with cells and ns/submit is flat;
   fix = batch adjacent ranges into one submit.
 H-perbyte: cost scales with RDP command bytes: predicts ns/byte flat, submit count irrelevant; fix lives in RT64 parsing, not batching.
 H-sync: submits wait on a lock/queue (RDP_ASYNC off path): predicts wait time inside submit, rising with cells.
Discriminator, ONE build, ONE run: per frame submit count, bytes, ticks in bridge/RT64 submit/lock wait, bucketed by cap phase (tog3 8192/10240).
Outcome: ns/submit flat with count rising -> H-percall (try a same-run batching tog arm); ns/byte flat -> H-perbyte; wait share -> H-sync.
