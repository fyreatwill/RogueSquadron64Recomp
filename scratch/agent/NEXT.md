# NEXT (s7257): fold s7251_dd6r_ac and s7250_slowhost (rerun starts at wwd)
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7256): ww holds 60/s in L4 t=77-97 on AC, three runs (13.16, 12.64, 12.37 ms). Queue: s7250_slowhost (ww kept via ok_ww; runs wwd, stack,
stackd), s7251_dd6r_ac (both SOAK_NEEDS_IDLE=180, VOID_OK_AFTER=110: a human void after t=110 keeps the arm, look for 'latevoid=' in arms.log).
Check loop.log 'soak phase:' lines first; every arms.log line carries clk= (must be ~1.0, DUTY arms ~1.4).
1. s7251_dd6r_ac: scratch/s7251/arms.log + soak log tail. Control: dd6rd flat 30 in t=77-97. Control passes + dd6r 60 ->
   farthest-view line holds 60 on AC: correct CURRENT-TRUTH + tell owner. dd6r 30 on AC -> dd6 radius cost real; next OFFMAPCULL K=0.6.
2. s7250_slowhost: wwd flat 30 = control; stackd 60 vs 30 decides 'stack holds 60 on a slow host'.
3. Score any latevoid arm with tools/s7230_headroom.py (window must be complete: log t reaches >=97).
4. If none ran again: take the next offline G-ladder item (not another loop/harness tweak, not another re-fold).
