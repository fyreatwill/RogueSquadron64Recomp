# NEXT (s7255): fold the slow-host / AC soaks (s7250_slowhost, s7251_dd6r_ac, s7248_fixed_fps_b)
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7254): none of the three ran (owner active at the boundary). The loop now waits up to SOAK_IDLE_WAIT=1800 s for idle before the
next iteration, so check loop.log for 'soak phase:' lines first (did it wait / expire / run).
Every queued recipe uses g1e_owner_quiet_arms.zsh, so their arms.log lines carry clk=; check it is ~1.0 on every arm before reading timing.
1. s7251_dd6r_ac: scratch/s7251/arms.log (clk~1.0) + soak log tail. Control: dd6rd flat 30 in t=77-97. Control passes + dd6r 60 ->
   farthest-view line holds 60 on AC: correct CURRENT-TRUTH + tell owner. dd6r 30 on AC -> dd6 radius cost real; next OFFMAPCULL K=0.6.
2. s7250_slowhost: wwd flat 30 = control; stackd 60 vs 30 decides 'stack holds 60 on a slow host'.
3. s7248_fixed_fps_b: score scratch/s7248r/log_{offb,wwb,stackb}.txt.
4. If none ran again: if on battery, run `tools/s7253_clkprobe` once and record the LPM ratio; otherwise take the next offline
   G-ladder item (not another loop/harness tweak). Do not redo the battery audit, the clock gate or the idle wait.
