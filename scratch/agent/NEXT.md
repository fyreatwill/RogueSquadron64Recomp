# NEXT (s5683): fold s5682_pd2 soak result
Run: `grep -h '\[pd2\]' scratch/agent/soak_results/s5682_pd2_*.log > /tmp/pd2.txt; python3 tools/pd2_corr.py /tmp/pd2.txt` (check t= spacing for poll rate and that pos std>0).
|corr|>0.9 on a diag pair -> ship integrator confirmed, altitude=+0x50 -> design altitude-hold autopilot for G1 flying. <0.3 with pos moving -> vel is not world velocity; oracle watch on +0x4C/50/54 writer PC. No rows -> mission origin never reached; check log for crash first.
HYPOTHESIS-ID: g1-mission-progression
s5682 result: +0xD0 constant, not velocity (refuted); pos x/z moves, y static in an input-free window. Change the pd2 gate to start logging when mission_t>=60 s / stick!=0 (budget 600 polls), rerun, correlate dpos with stick and +0xDC/E0.
