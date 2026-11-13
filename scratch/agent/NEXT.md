# NEXT (s7288): fold s7288_169_dd6_levels — does R=88 at 16:9 dd6 dip on other heavy levels?
HYPOTHESIS-ID: g1c-169-dd6-r88-levels
State: s7287 selected H-R88 on L12 16:9 dd6 (2 runs) and landed ROGUESQ_DD_WIDEWIN_RLEVEL (auto 12:48 at dd>=6), verified
same-session (auto 60.0/s 10.94 ms vs RLEVEL=none flat 30 t=77-84). R=88 at 16:9 dd6 is qualified on L4 and now L12 only.
Unit: fold scratch/agent/soak_queue/s7288_169_dd6_levels.sh (L1/L9/L13 16:9 dd6 auto + ctl L13 STACK=0+DUTY 1.4). If the loop
voided it (rc=2) or it is still queued, run it in-session: `zsh scratch/agent/soak_queue/s7288_169_dd6_levels.sh` (~17 min, idle host, AC).
Control: ctl must show a flat-30 run; otherwise the null on l1/l9/l13 is void.
Outcomes:
  - H-L12-only: l1/l9/l13 0 flat runs beyond route -> R88 auto is fine elsewhere at 16:9; close the thread, next G1c phase-2 step
    is widening the window (s7286: area cap / 64-deep FWDWIN binds from dd4).
  - H-dense-levels: some level dips -> add it to the RLEVEL auto list in main.cpp [s7258], fix arm _RLEVEL=<lvl>:48 same run.
  - H-host: control also clean -> host faster than DUTY 1.4 exposes; raise DUTY and re-run.
