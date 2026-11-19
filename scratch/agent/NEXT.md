# NEXT (s7627)
HYPOTHESIS-ID: g6-upstream-features

G6c step 3d: do stand-in display-list calls produce RDP pixels? s7626 proved the CPU side end to end (walk visits and converts
them, prebuilt-DL queue 0x80116400 gets them, beginFrameDLChunk reads 100%) and showed every earlier pixel test sat in a window
with ~0 stand-in draws (docs/G6C-STANDINS-PLAN.md "Step 3c result").
1. Fold soak s7626_standins_pixels if the loop ran it (scratch/agent/SOAK-RESULTS.md, scratch/s7626_soak). If not run yet (owner on
   the machine), run it in-session when idle >= 300 s: `zsh scratch/agent/soak_queue/s7626_standins_pixels.sh` (moves nothing;
   delete the queued copy after an in-session run). ~5 min, L1 dd4, dumps at 10/16 s after the first submit.
2. ALSO add a real-object positive control so the scorer is fed a frame known to hold an object: ROGUESQ_STANDINS_CTL=frame skips
   addNpcToVisibilityBucket for REAL spawned objects (not ours) on odd submit calls in window 1 (hook at the game's own callers is
   overkill: a host flag checked in a tiny apply script at 0x80057C8C entry returning v0=0 when set and inst not in our region).
   Scorer must find flicker excess in that arm, or the pixel chain itself is blind.
Outcomes:
- P (PULL=3) excess > 0 and N excess > 0 -> stand-ins draw; step 3 proof (frames early vs pop) on L1+L4 at dd2/dd4, then 300 s holds.
- P > 0, N = 0 -> depth: occlusion by terrain (legit) vs far clip / fog: compare P at D=20 (inside object far) vs D=3.
- P = 0 with window draws > 0 and the real-object control > 0 -> lost in the RSP/RDP path: dump the F5 DL for a stand-in matrix
  address (matrix ptrs recorded in s_q_ours_mtx) and check the G_MTX + G_DL commands reach the ucode.
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; check idle (owner was active at 20:15).
