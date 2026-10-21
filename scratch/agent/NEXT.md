# NEXT: fold s5744_hpwatch_lvsel (queued; hp/lives lldb write-watch on level-select route, MISSION_RE=62BD00)
s5743 was void (gate quoting bug, fixed in s5739_hpwatch.sh). Read tail of scratch/agent/SOAK-RESULTS.md and scratch/agent/m6/s5744_hpwatch_lvsel/{keys.log,summary,lldb_att*.log}.
Hypotheses: (H1) a game routine reacting to autopilot held-stick writes kills the craft; (H2) mission 62BD00 has a terrain/enemy hazard; (H3) port defect in held-input path.
Discriminator: top frame/PC at hp->0 write (wp2) and lives decrement (wp3). Control: wp1 hit on 0x3470 AND a death ([snap] death#1) in the run, else void.
If it armed but no death: queue a 480 s re-run; if keys.log shows a different failure, fix the script (boring-first).
HYPOTHESIS-ID: g1-gameover-cause
