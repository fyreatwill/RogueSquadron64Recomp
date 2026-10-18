# Next work unit: fold s5446_plume_scratchfb_guard soak verdict, then mission endurance
HYPOTHESIS-ID: m6-title-boot-plume-sigsegv
- Read SOAK-RESULTS.md for s5446_plume_scratchfb_guard (title boots; any [CRASH]/si_addr=0x58 = guard incomplete, read the crash-handler backtrace in the log).
- Clean = weak evidence only (p~0.29 at 1/7). Optionally add a one-shot stderr breadcrumb in the new guard branch to prove it fires (positive control for the mechanism).
- Then resume M6: keyed mission endurance / results-screen recipe (start=pause defect noted in s5444).
