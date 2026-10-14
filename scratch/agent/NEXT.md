# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4883 closed the 0x400128d47 startup SIGSEGV (stale u32 probe, see CURRENT-TRUTH headline). One new crash seen 1/16: si_addr=0x380000004, last-guest-pc 0x80001b08, pc 0x101b40938 (scratch/agent/soak_results/s4883/run_1b.log).
Do: symbolize that pc with lldb (`image lookup -a`), check whether it is another stale/zero-extended probe (grep generated text for non-S32 constant bases), as an idiom-class audit: `rg 'MEM_[A-Z]+\(-?0X[0-9A-F]+, 0x[0-9a-f]{8}u\)' ../N64Recomp/RecompiledFuncs`.
Then resume M5 contract boundary (step 12) in docs/M5-AUDIO-PLAN.md.
