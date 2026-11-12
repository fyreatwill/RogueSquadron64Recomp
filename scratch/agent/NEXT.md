# NEXT: s7207 follow-up — the 4:3 interlaced field screen presents twice per image with the s7206 fix
HYPOTHESIS-ID: interlaced-still-present
Context: s7207 showed the s7206 fix gives 60 distinct images/s on the 16:9 fullscreen stills (H-motion) and leaves 4:3 Elite Rogues
fidelity equal. But on the 4:3 windowed Elite Rogues screen (VI width 1024, fb 512 at 790000, origin 790400) f1 presents in back-to-back
pairs: ring Q intervals < 4 ms 1010 (f0 3), ~102 presents/s for ~48 distinct images/s (scratch/s7207/ring_ER1.txt). At 16:9 fullscreen
the duplicate shows as a skip=1 row instead (ring_f1.txt: B51E00 skip=0 60/s + fb=000000 skip=1 60/s).
Hypotheses:
 H-twopath: for one VI both the early present (now matching via the corrected fbAddress) and the VI-change / threadPresent path present
   the same fb; at 16:9 the second is superseded because the queue already moved, at 4:3 it is not.
 H-field: one present per field-scissor workload (the game issues 2 workloads per image on this screen: W fbs 790000,620000,...).
 H-window: windowed (4:3, 849x788) vs fullscreen supersede logic differs (drawable availability), independent of the fix.
Discriminator, ONE build (current; add a cheap per-present source tag to the Q row if it does not already say which path presented —
check lib/rt64 rt64_state.cpp early-present + threadPresent first, then submodule-patches/export.sh + commit):
 run scratch/s7207/er43.zsh WITHOUT ROGUESQ_G5B_FRAME* (ring only, no 12 GB stream) for ER0/ER1, plus ER1 at ASPECT=4:3 FULLSCREEN=1.
 Per pair of < 4 ms presents: which paths, same wl/fb or different, which VI.
Outcomes: two paths same wl -> H-twopath (dedupe on wl/fb per VI); different wl per field -> H-field (present once per VI); fullscreen
4:3 arm shows no pairs -> H-window. Fix = default on with =0 restoring s7206, prove 60/s distinct kept on the 16:9 boot stills
(scratch/s7207/boot.zsh + tools/s7207_distinct_by_vi.py) and pairs -> ~0 at 4:3.
