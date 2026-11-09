# NEXT: G5f dd1 — why the W clamp raises small transients at dd1 (s6895: 306 vs 157, 8 of 8 bins)
HYPOTHESIS-ID: g5f-dd1-transients
Context: s7002 showed at dd4 L4 that lines under 60 px are real moving geometry and that dropping mixed-sign 40-200 px tris
adds sliver holes; W_SHEET_PX=200 stays. s6895 (old clamp rule, before the 200 px sheet rule) saw MORE small transients with
the clamp on at dd1 (T>=.003 306 vs 157) and never explained them. W_CLAMP is now default on at dd1 (s6906).
Hypotheses:
- H-sliver: clamped small tris (<20 px span, the bulk: ~3.5k per block) render with a slightly different footprint or
  texture than unclamped, flickering frame to frame -> tiny transients. Clamp on shows more 20-39 px lines than off.
- H-gone: the s6895 excess belonged to the first rule (drop over 20000 px area) and is absent under the current rule:
  on == off at the 20 px detector.
- H-real: transients are real motion; any on/off difference is phase noise (windows split both ways).
Discriminator, ONE run: LEVEL=4 dd1 16:9 FPS60, `ROGUESQ_W_CLAMP=tog ROGUESQ_W_SHEET_STATS=1`, capture 90 s only
(`zsh scratch/s7002/arm.zsh 4 1 c1 "ROGUESQ_W_CLAMP=tog ROGUESQ_W_SHEET_STATS=1" 120 90`; disk ~20 GB, 9 GB/min, no TRIS).
Score: scratch/s6906/g5f_lines c1.raw lines_c1.txt 40 20 50 (control >= 85%), python3 tools/g5f_short_buckets.py
lines_c1.txt; block 1 = clamp on. View 6 on-block and 6 off-block short lines (scratch/s6906/crop.py, phase 0.2-0.9),
flip diff (scratch/s6906/g5f_flip_diff). Delete the raw after scoring.
Outcomes: on > off in >= 8/10 windows and viewed on lines are slivers -> H-sliver (then try clamp only for span >= 20);
on ~= off -> H-gone, close the dd1 question; split windows -> H-real.
