# Read per-phase `res=0x2C` route counts at VI 512 (dlwalk phase 6), then compare DROP=1 vs DROP=0 in-run

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4787: VI 512 is reached unattended on the default binary; the `[ovl-route] res=0x2C` logger now exists (positive control: 152 rows, n=8704 in title phase). Mission-phase count not yet measured (new-binary runs stalled in VI 640 under host load 14).
Work unit: read SOAK-RESULTS/soak_results for s4788_drop1_mission_2c (queued; same script as scratch/agent/s4788_drop1.sh). Check `uptime` load first; if load > 6 rerun later rather than trusting a stall. Extract: res=0x2C rows after the `vi_width=512` line (phase 6) vs title phase.
Competing: (A) phase 6 has many 0x2C routes => stopgap drops real mission content, the real-image splice matters; (B) phase 6 has ~0 routes while DL arrivals2c>0 => arrivals die before RSP routing, look upstream; (C) still stalls in VI 640 => stall is not load, bisect vs previous binary (counter-only diff).
Then: design an in-run toggle for DROP (not env-at-launch) so DROP=1/0 can be compared in the same phase.
Control: res=0x2C rows in title phase (fires already); VI 512 line present.
