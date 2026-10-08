# Next work unit: confirm the lock holder and decouple audio from the gfx DMEM mutex (s4249)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4248: audio run_task wall time is ~98% lock wait on g_lle_task_mutex (src/main/main.cpp:4806); cpu 0.1-0.3 ms; DMA volume only 1.3x.
Hypotheses: (h1) gfx LLE runner holds the mutex for a whole DL (60-860 ms DLs at t18-26); (h2) another holder (rs64_run_lle_gfx setup, debug dumps) holds it; (h3) mutex fairness: audio starves though hold times are short.
Discriminator: log hold duration per holder (factor5_gfx_runner, rs64_run_lle_gfx, DmemGuard) with thread id, in one build; correlate with audio lockwait at the same t. Outcome h1 => hold ~= lockwait; h3 => short holds, many of them.
Positive control: baseline windows show holds ~ lockwait 3-10 ms.
Then plan: give audio ucode its own DMEM/IMEM (or snapshot-swap) so run_task need not take the gfx mutex.
