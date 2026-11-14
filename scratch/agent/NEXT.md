# NEXT (s7298): fold s7298_219_dd8_levels — does the dd8 px8 auto hold 300 s at 21:9 on L1/L5/L9/L10/L12?
HYPOTHESIS-ID: g1c-window-bind
State (s7297): main.cpp [s7293] dd8 auto (POOLX_MAX=8 + WIDEWIN_R=128) now applies at every aspect; L4 21:9 verified 60/s,
11620 vs 7313 cells/call (s7296 + s7297, 2 runs).
Unit: fold scratch/agent/soak_queue/s7298_219_dd8_levels.sh (if still queued/voided, run it in-session, ~32 min).
Outcomes:
  - H-hold: all arms alive, 0 crash, 60/s beyond route transients, [s7293] line in each non-ctl log, L12 [s7287] widewin_r=48,
    L9 CAPLEVEL 9:8192 still applies -> 21:9 dd8 qualified; update OWNER-OPT-INS.
  - H-level-cost: a level dips (flat 30 or >5 s <55/s beyond route) -> add a 21:9 level rule (RLEVEL/CAPLEVEL) for it, same-run A/B.
  - H-crash: an arm dies -> backtrace, root cause.
Positive control: ctl arm must dip (flat 30).
After: horizon-in-view dd6-vs-dd8 look sheet (ROGUESQ_POSE_LOCK or a later route second), then the game far cutoff 0x8009DEB4.
