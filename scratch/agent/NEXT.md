# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

Name the writer of the zero-extended guest pointer (0x80128d44) behind the spTaskSchedulerThread startup SIGSEGV (si_addr 0x400128d47).
State (s4882): crash handler has a [CRASH][ctx-scan] block; first scan (from sp) hits=0 because ctx is below sp. Source already widened to sp-0x2000 but NOT built.
Steps: check scratch/agent/soak_results/s4882/summary.txt (old-binary soak), then `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`, then `zsh scratch/agent/run_s4882_ctxscan.sh`, read `[CRASH][ctx-scan] ctx=... rN=` rows.
Hypotheses: (A) native scheduler helper stores U32 without S32; (B) host osRecvMesg/message path yields unsigned into a ctx reg; (C) stale/uninitialised ctx reg on racing thread start.
Discriminator: which rN (and the other ctx values) holds the zero-extended value; grep that register's last write. If hits=0 again, record the ctx pointer at spTaskSchedulerThread entry.
Then pick the next M5 contract boundary (step 12) in docs/M5-AUDIO-PLAN.md.
