# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4884 sign-extended the 90 `ctx->rN = 0x80000000u` substitution sites. First: read scratch/agent/soak_results/s4884/summary.txt (16 runs; s4883 baseline 1/16 crashes) and fold the number into CURRENT-TRUTH/PORTING-STATE. If any crash has si_addr = rdram_base + 0x1_0000_0000-ish, repeat the audit for other zero-extended register writers (grep `ctx->r[0-9]+ = U32(` / `= 0x[0-9a-f]{8}u;` outside funcs).
Then resume M5 contract boundary (step 12) in docs/M5-AUDIO-PLAN.md.
