# NEXT: G1 - s5877: fold s5876_timer soak ([tmr] lines)
Hypotheses: (a) legit ground-impact fuse - player dives into terrain under held input; dt~1/60 and timer starts at the 0x800A566C-scale const, the object has been below terrain for real. (b) our dt (f6) wild or timer init zero/garbage -> premature expiry. (c) y/terrain wrong (terrain query 0x80067D90 returns too-high value), so craft "hits" ground it should not.
Measure: grep '\[tmr\]' scratch/agent/m6/s5876_timer/run.log. dt~0.016-0.05 and timer counting down from a sane value => not (b). Then compare terrain vs y trajectory just before the first [bit1] (c): if y is monotonically descending in flight that is (a); if y snaps below terrain in one frame, suspect (c) - add a per-frame y/terrain log near 0x800B10F4 for the player only.
Control: [tmr] must print for 0x80137DBC and [bit1]/[m47] a0=1 must fire in same run.
HYPOTHESIS-ID: g1-mission-progression
