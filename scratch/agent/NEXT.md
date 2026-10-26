# Fold s6262 FPS60+dd2 combo soaks, then G1d widescreen+FPS60 pairing
HYPOTHESIS-ID: g1-optin-combos
Read s6262_fps60_dd2_l1 / _l5 lines in SOAK-RESULTS.md (want alive_at_end=1, crashlines=0, vi_stalls30s=0; rc=0 alone is not a pass). If clean, update docs/OWNER-OPT-INS.md and queue ASPECT=16:9 (+OSMEM_MB=12) + FPS60 lvl1 hold. If a crash: backtrace it (this is a side-effect crash, fix the root cause). G1d title defect B stays parked.
