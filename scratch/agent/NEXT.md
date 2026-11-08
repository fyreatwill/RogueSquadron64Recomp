# NEXT: G1e residual - dense levels 7/16/17 at 56-58.5 game fps (16:9 dd4)
HYPOTHESIS-ID: g1e-dense-level-cost
(G5i fixed s6995, awaits the owner's look; if the owner reports the hangar fish-eye again, reopen with slug g5i-hangar-reentry,
route scratch/s6995/arm.zsh + scratch/s6995/route_long.txt, metric tools/g5i_pan_metric.py, and add a fullscreen/dd2 arm.)
Hypotheses:
- H-rsp: gfx RSP task host-ms per frame scales with scene density on L16 -> misses co-vary with [g1b] RSP ms.
- H-guest: guest CPU (game thread) per frame exceeds the 16.7 ms budget on dense levels -> misses co-vary with guest cpu.
- H-dd: extended terrain at dd4 is the extra term -> L16 dd1 holds 60.0 where dd4 is 56.3.
Unit: offline join first (scratch/s6993s ring_L16 misses vs [g1b] sd_wall / guest cpu vs L10 control, no build), then one
build with L16 dd4 vs dd1 arms run back to back (tools/g1e_owner_quiet_arms.zsh, check `cur` = the flown level).
Discriminating outcome: which per-frame term exceeds budget on the miss frames and is absent on L10/dd1.
