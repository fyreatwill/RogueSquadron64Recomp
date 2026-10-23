# NEXT: fold s6016_g1b_scanfix (G1b post-fix arm)
HYPOTHESIS-ID: g1b-frame-pacing
s6015 sampler (6 samples, all with sd_wall 102-193ms; positive control passed): Gfx thread ~93% in send_dl -> factor5_ucode -> rsp_dpc_submit, ~80% of ALL gfx samples at dpc_bridge.cpp:2748 (linear scan of g_s4272_sh per deferred range, O(n^2)) + the s4285 per-flush shadow word-compare diag. RT64 processRDPLists itself is only ~3% => H-rsp/H-host/H-shader/H-log not the cause; our own bridge scan is.
s6016 fix: hash index for the scan (first-match preserved), s4285 diag gated behind ROGUESQ_S4285=1.
Fold: compare SOAK-RESULTS s6016_g1b_scanfix [g1b] slow-second fraction vs s6014_g1b_loud (17.6%). Expect sharp drop. If slow seconds remain, re-sample (tools in s6015 recipe) and read the new top frame. Also check rendering unchanged (soak rc=0, no new crash).
