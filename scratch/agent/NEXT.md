# NEXT: fold s6014_g1b_quiet / s6014_g1b_loud (G1b frame-pacing, arm comparison)
HYPOTHESIS-ID: g1b-frame-pacing
Finding so far (s6014): ~29% of seconds have gfx send_dl 130-210 ms/task, cpu~wall, VI still 60/s; host/QoS/log-volume do not co-vary.
Hypotheses: H-harness (our FB hash/dump/tricount/drawn/objbool/hudbit instrumentation causes it; quiet arm slow fraction ~0), H-rsp/RT64 (real send_dl cost, scene-driven; quiet arm still ~25%), H-shader (ruled out: cpu~wall).
Fold: m6 dirs g1_lvl1g1bquiet vs g1_lvl1g1bloud run.log. Compute slow-second fraction (sd_wall avg >50 ms) per arm. Positive controls: quiet-arm logB/s must be far below loud (~130 KB/s); loud arm slow fraction must be >15%. Caveat: ROGUESQ_LOG_OBJBOOL/HUDBIT=0 semantics unverified (grep found no source in src/tools) - judge by logB.
If quiet still slow: run lvl1 under `/usr/bin/sample <pid> 3` launched when a [g1b] line shows sd_wall avg>100, read the top frames of the Gfx thread (RT64 vs F5 LLE interpreter vs our hooks). If quiet fast: find which logger is guilty by bisecting FBH_V/TRI_V/DRAWN_V/FBD_EVERY_V in one batch of queued arms.
