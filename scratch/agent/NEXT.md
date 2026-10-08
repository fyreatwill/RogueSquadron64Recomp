# Next work unit: private audio DMEM so run_task does not take g_lle_task_mutex (s4250)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4249 confirmed: gfx holds the mutex 15-870 ms per DL, audio <1 ms; audio starves (180 -> 22 tasks/3 s at t>=22).
Hypotheses: (h1) audio ucode state is fully contained in `dmem[]`/IMEM-like globals that can be redirected per thread (thread_local pointer or a swap-in audio copy), so audio runs concurrently with gfx; (h2) the recompiled ucode and dma helpers reference the global `dmem` symbol directly (hundreds of sites), so redirect needs a macro/alias change in generated code (fixup scripts); (h3) audio and gfx share more than dmem (vector regs, flags, rsp.cpp statics) so a private dmem alone races.
Step 1 (survey, no build): grep how `dmem` is declared/used (rsp.hpp, factor5_ucode/*.c, rsp.cpp dma helpers, rs64 runner) and what other globals run_task touches; count sites. Decide thread_local-dmem feasibility.
Step 2: implement the least-invasive route (e.g. `thread_local uint8_t* dmem_ptr` or per-task audio DMEM swap), put generated-code edits in tools/fixup_*.py, edit under lib/ => export.sh + commit.
Discriminator: rerun s4245_rates.sh with ROGUESQ_S4245=1; audio lockwait ~0 and audio tasks stay ~180/3 s through t=18-28 while gfx holds stay long. Positive control: [s4249-sum] gfx holds still show the long DLs in the same run; audio task count in t>=22 windows (was 22-111/3 s).
