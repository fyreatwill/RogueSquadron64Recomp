# NEXT (s5684): fold s5683_pd2 soak (input-gated per-poll ship pos/vel dump)
Run: `grep -h '\[pd2\]' scratch/agent/soak_results/s5683_pd2_*.log > /tmp/pd2.txt; python3 tools/pd2_corr.py /tmp/pd2.txt`.
Correlate dpos (x,y,z) with sx/sy and +0xDC/E0. Rows with pos y moving under stick_y -> altitude control found, design autopilot. No rows -> stick stayed 0 at mission origin; check autopilot keys.
HYPOTHESIS-ID: g1-mission-progression
