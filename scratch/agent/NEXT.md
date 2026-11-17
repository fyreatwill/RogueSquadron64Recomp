# NEXT (s7514)
HYPOTHESIS-ID: timer-count-shape-vs-hardware

First: fold s7513_fj_levels from SOAK-RESULTS if it ran (score 0 -> FJ CLOSED 6 levels in CURRENT-TRUTH item 20; score 1 -> a gated arm
sent a stick count outside the 85/70 octagon: read scratch/s7513_fj_levels/out.txt; 3 -> the l4off ctl did not print on=0; 4 -> an arm
never polled input). The stick gate needs the OWNER's feel verdict (OWNER-OPT-INS row); do not retune 85/70 without one.

Work unit: class FK, CP0 Count / osGetTime / osSetTimer shape vs hardware. Live wrappers: osGetTime 14 callers, osSetTimer 1, osGetCount
0 (ultramodern timer.cpp:250-270, librecomp ultra_translation.cpp:12 note on the game dividing osGetTime deltas). Hardware: Count ticks
at 46.875 MHz (CPU 93.75 MHz / 2), osGetTime = 64-bit __osCurrentTime + (Count - __osBaseCounter), wraps Count at 2^32 (~91.6 s).
Hypotheses: H-canon (every guest-visible time value advances at 46875 ticks/ms of wall time, monotone, consistent with the VI count:
1 VI = 781,250 ticks at 60 Hz NTSC... check: 46.875e6/60 = 781,250) / H-dead (differences only at boot or in unused high bits) / H-live
(a live reader sees a different rate, a non-monotone step, or a 32-bit wrap that retail would not produce at that uptime; or osSetTimer
fires at a different count than retail for the same interval) -> fix to the hardware rule.
Measurement: one census env (ROGUESQ_LOG_TIME_SHAPE=1: every osGetTime return with host ns + VI ordinal, every osSetTimer arm/fire with
countdown/interval and host ns), 2 arms (L4 dd1, L15 dd8 21:9) via tools/g1e_owner_quiet_arms.zsh (command shape as s7512), offline
tools/s7514_time_shape.py: ticks per host ms, ticks per VI, monotonicity, timer fire error vs interval; synthetic + mutant controls and
an in-run ctl (ROGUESQ_TIME_SHAPE_CTL=<n>: one census record skewed, screen untouched).
