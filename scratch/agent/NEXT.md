# NEXT: G5i owner-recipe arm - hangar re-entry pans at FULLSCREEN and dd2 (s6995 fix not yet run there)
HYPOTHESIS-ID: g5i-hangar-reentry
Context: s6995 keyed the s6907 aim release on the raw view reaching the craft; A/B ran windowed dd4 16:9 only. The owner
plays ROGUESQ_FULLSCREEN=1 with dd2 or dd4. CURRENT-TRUTH item 1 lists "not yet run: fullscreen, dd2".
Hypotheses:
- H-holds: re-entry long/double-press scrolls stay <=5 deg off axis at fullscreen dd2 and dd4, same as first entry.
- H-size: fullscreen (other window size / RESMULT / present cadence) changes the pan timing so the release fires early again.
- H-dd: dd2 heap/arena layout moves something the aim reads (state 0x800CC3E4, cursor 0x800CD6E8) on re-entry.
Unit, one build (current), arms back to back (one game at a time, check screen unlocked first):
  env AP2="$(cat scratch/s6995/route_long.txt)" zsh scratch/s6995/arm.zsh fs4 "ROGUESQ_FULLSCREEN=1"
  env AP2="$(cat scratch/s6995/route_long.txt)" zsh scratch/s6995/arm.zsh fs2 "ROGUESQ_FULLSCREEN=1 ROGUESQ_DRAW_DISTANCE=2"
  control: same with ROGUESQ_G5G_RELMODE=time (old clock) must show the 20-30 deg off-axis re-entry frames (positive control).
  score: python3 tools/g5i_pan_metric.py scratch/s6995/<arm>.g5g.txt  (first entry vs re-entry max off-axis deg)
Check arm.zsh's DRAW_DISTANCE=4 is overridden by the later env (it is inserted after; confirm run.log echoes multiplier 2).
Discriminating outcome: fixed arms <=5 deg on both entries with the time-mode control >20 deg -> H-holds, update owner sheet;
any fixed arm >10 deg on re-entry -> H-size or H-dd by which arm fails.
