# NEXT (s7256): fold s7251_dd6r_ac and s7250_slowhost
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7255): s7248 2nd runs folded (off 9.79, ww 12.64 ms in t=77-97, both 60/s on AC: two-run). s7248_fixed_fps_b is in soak_queue/hold
(stackb only; restore by moving it back if a stack replication is wanted). Queue now: s7250_slowhost, s7251_dd6r_ac (both SOAK_NEEDS_IDLE=180).
Check loop.log 'soak phase:' lines first; every arms.log line carries clk= (must be ~1.0, DUTY arms ~1.4).
1. s7251_dd6r_ac: scratch/s7251/arms.log + soak log tail. Control: dd6rd flat 30 in t=77-97. Control passes + dd6r 60 ->
   farthest-view line holds 60 on AC: correct CURRENT-TRUTH + tell owner. dd6r 30 on AC -> dd6 radius cost real; next OFFMAPCULL K=0.6.
2. s7250_slowhost: wwd flat 30 = control; stackd 60 vs 30 decides 'stack holds 60 on a slow host'.
3. A voided arm whose void time is after t=97 still has a clean window: score it with tools/s7230_headroom.py.
4. If none ran again: take the next offline G-ladder item (not another loop/harness tweak, not another re-fold).
