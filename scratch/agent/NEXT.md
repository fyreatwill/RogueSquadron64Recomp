# NEXT (s7294): fold s7294_169_dd8_levels — does the landed dd8 px8 auto hold 300 s on L1/L5/L10/L12 at 16:9?
HYPOTHESIS-ID: g1c-window-bind
State (s7293): main.cpp [s7293] dd>=8 + WIDEWIN + FB_WIDTH<=796 -> POOLX_MAX=8 + WIDEWIN_R=128 (L4 16:9: 11406 cells/call vs 6902,
60/s 11.9 ms, 2 runs). Unit: fold scratch/agent/soak_queue/s7294_169_dd8_levels.sh (if still queued/voided run it in-session, ~32 min).
Outcomes:
  - H-hold: all arms alive, 0 crash, 60/s beyond route, [s7293] line, L12 [s7287] widewin_r=48, ctl dips -> dd8 qualified at 16:9;
    next = look sheet dd6 vs dd8 same camera (tools/g1c_dd_arm_sheet.py style, L1+L4), then 21:9 dd8 px8 cost arm.
  - H-level-cost: one level flat-30 / <55 beyond route -> add a level rule (RLEVEL <lvl>:88 at dd8, re-run that level as fix arm).
  - H-crash: any crash -> backtrace + name the writer (heap/pool at 16384 cells; site 18 pool-out counter).
Positive control: ctl arm (L12 STACK=0+DUTY=1.4) must show a dip.
