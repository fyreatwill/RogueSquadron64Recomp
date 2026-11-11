# NEXT: off vs NEARK=1.6 wall-loss replication in the same runs (owner recipe), then the opt-in closes on the owner's look
HYPOTHESIS-ID: fps60-wall-confirm
Context (s7119): at NEARLIFT=1 NEARK=1.6 the camera does not hop (H-smooth vs retail, same run m). But off vs k1.6 *losses* in the same run were
never powered: s7116 was off vs k1.0, s7118 k1.0 vs k1.6, and run m (tog1, k1.6) had only 3 off losses (steady 3/1, z -1.0).
Hypotheses: H-fix (k1.6 removes >=75% of off-arm steady losses), H-partial (25-75%), H-none (<25%; s7118 k1.0->1.6 gain was route luck).
Runs: one game at a time, 3 runs n, o, p:
  sed 's/_m\./_n./g; s/ 6 4 m / 6 4 n /' scratch/s7115/cmd_m.txt > scratch/s7115/cmd_n.txt ; zsh scratch/s7115/cmd_n.txt > scratch/s7115/arm_n.log 2>&1
  (same for o, p; check the screen is unlocked first: /usr/sbin/ioreg -n Root -d1 | grep -c '"CGSSessionScreenIsLocked"=Yes' must print 0).
  NOTE: a waiter using `pgrep -f cmd_m.txt` matches itself; wait on the background task notification instead.
Per run: python3 tools/s7107_losscan.py tris_X.bin X.csv > losscan_X.txt; python3 tools/s7118_edge.py 0.1 tris_X.bin losscan_X.txt push_X.txt
  (pool with run m); python3 tools/s7119_hop.py --edge 0.1 push_X.txt (hop replication; pre-registered H-smooth rule). Delete X.raw after
  analysis unless a sheet is needed.
Positive control: the s7118_edge off-arm must show >= 10 pooled steady losses (else the runs hugged walls too little: add a run). The hop control is
  --inject T:1.0 (+3 on >0.25).
Outcomes: H-fix -> close item 26 on the owner's look (OWNER-OPT-INS already says so), next ladder item; H-partial/H-none -> table the residual
  dmin bands (s7117 tickjoin) for k1.6 losses.
