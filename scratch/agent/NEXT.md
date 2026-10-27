# NEXT: fold s6463_dd4_lvl10_retry, s6463_dd1_lvl10_ctl, s6462_dd6_lvl5 (G1c phase 2)
HYPOTHESIS-ID: g1c-dd4-limits
Hypotheses: H-route-flake (dd1 control also fails lvl10 route -> not dd), H-dd4-menu (dd1 passes, dd4 fails again -> dd4 breaks level-select path; look at m6/g1_lvl10s6463_dd4 keys/run.log), H-probe-race (SIGBUS in rs64_probe_audio_dma_write recurs -> capture lldb/ASan, name writer of probe->ranges).
Steps: tail scratch/agent/SOAK-RESULTS.md for s6463_* and s6462_dd6_lvl5; summary files in scratch/agent/m6/g1_lvl10s6463_*; grep 'multiplier'. If all clean, contact sheet dd1 vs dd6 same camera for owner, then try dd8 (needs clamp raise in apply_s6036 patch).
