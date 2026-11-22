# NEXT (s7799)
HYPOTHESIS-ID: g6c-standins-dd2-handoff
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. 11 s7797 stand-in re-holds are still queued (L2,3,6,7,8,9,13,14,16,17,18; L0/L11 folded s7798). Fold every verdict
landed (pass = alive=1/1 crash_arms=0 stall_arms=0, `s7797 Lx standins_on_line=1 spawns>0` in the log). Any crash/stall outranks the unit.

Unit: G6c stand-in -> real handoff at dd2. s7672 measured it at dd4 only (HOLD fix: 0 blinks, control blinks). At dd2 the stand-in far
window is smaller, so stand-ins sit nearer the spawn ring; s7798's frame diff cannot see a handoff gap (angrylion replays our stream).
Recipe scratch/s7672/run.zsh <outdir> <level> [1|0|odd] builds E="ROGUESQ_STANDINS=1+ROGUESQ_STANDINS_LOG=1+ROGUESQ_S7672_HOLD=$H"
and runs g1e_owner_quiet_arms (dd4 via that harness). Add dd2: append `+ROGUESQ_DRAW_DISTANCE=2` via an optional 4th arg DD (tool change,
default unchanged), confirm `[standins] on mode=on dd=2.00` in the arm log, else void.
  zsh scratch/s7672/run.zsh scratch/s7799 4 odd 2      # L4, odd held / even = same-run control
  zsh scratch/s7672/run.zsh scratch/s7799b 1 odd 2     # L1
  python3 tools/s7672_handoff_score.py <arm logs>      # rc 1 if a held group blinks
Hypotheses: H-clean (held odd: blink>1 = 0, overlap 0; even control blinks -> positive control), H-gap-dd2 (held blinks at dd2: the
real object's first accept lands after the 900-frame cap, or stand-ins die by their own far test before spawn at the smaller window),
H-none (handoffs=0 at dd2: stand-ins never on screen at the spawn moment -> report si_before_spawn distribution; then nothing to hand off).
Control must fire (even group blink>1 > 0) or a 0 is void. One game at a time; SOAK_NEEDS_IDLE not needed (no keys beyond harness).
If H-clean: G6c dd2 closed on both lines (render + handoff); take the next item-3c ladder rung.
