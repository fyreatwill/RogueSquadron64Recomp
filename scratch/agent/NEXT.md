# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

Name the writer of the zero-extended guest pointer (0x0000000080128d44) behind the intermittent spTaskSchedulerThread startup SIGSEGV (si_addr 0x400128d47; 2/5 with dedup off, 0/5 on; s4881).
Hypotheses: (A) a native scheduler helper/ctx-register write stores U32 without S32; (B) a host-side osRecvMesg/message write path yields an unsigned value into a ctx reg; (C) a stale/uninitialised ctx register on a racing thread start.
Discriminator: extend the crash handler to dump ctx->r1..r31 of the faulting thread's recomp_context (+ g_rs64_last_guest_pc) — the one register with upper 32 bits zero and low 32 == 0x80128d44 names the register; grep that register's last write in the scheduler patches. Positive control: the s4880 arm0 recipe (scratch/agent/soak_queue/done/s4880_dedup_crash_rate.sh) reproduces ~2/5.
Then pick the next M5 contract boundary (step 12) from docs/M5-AUDIO-PLAN.md.
