# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4882: ctx-scan REFUTED a stack-resident ctx (0 hits in 2 crashes). Faulting value 0x80128d44 == (u32)(x1+0xD4), x1=0xffffffff80128c70: an address add done in unsigned 32-bit arithmetic (hypothesis A).
Do: grep tools/*.py, src/ and patches for a +0xD4 pointer add lacking S32/ADD32 reachable from spTaskSchedulerThread; symbolize lr in the crash handler to name the caller frame. Discriminator: a site found => fix/guard with ORIGIN; none found => the add is compiler-emitted from a generated MEM_BU(0xD4,...) in a callee (inspect funcs for 0XD4 near 80128C70 users).
Then pick the next M5 contract boundary (step 12) in docs/M5-AUDIO-PLAN.md.
