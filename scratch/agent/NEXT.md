# NEXT: G1c - fold tblwatch arms s6043_dd1w (retail control) / s6043_dd2w
HYPOTHESIS-ID: g1c-draw-distance
s6042 result: gate fixed H1 (dd15s/dd2s now reach mission, t=84-87). Both then die IN-mission (~t=98 s) with the player in a death/respawn churn (s5897 lives=1216) and terrain table 0x80136DC4==0, window x0=0x7F7F0017 (poison high half, low half 23 = real x0), a0=-128 d=128. dd2s: SIGBUS deterministic (same si_addr in 2 attempts) in streamTerrainGridCellsByDistance+10880; dd15s: abort (signal 6, no [CRASH] bt context read yet).
H1: tbl nonzero->0 transition also happens in retail dd1 and is survived there (then dd2 differs via stale window words). H2: transition is dd-specific (clamp/knob left state). H3: transition is retail-benign only because function is not called with tbl==0 in dd1.
Discriminator: grep '\[tblwatch\]' in m6/g1_lvl1g1cdd1w/run.log vs cdd2w; compare window words at the transition and whether crash follows. Positive control: first tblwatch line (prev FFFFFFFF -> initial) must print in both arms.
Next: if retail also zeroes tbl, name the writer (watch 0x80136DC4 write PC) and guard the stream fn on tbl==0 as retail-equivalent; then dd3s result, levels 5/10.
