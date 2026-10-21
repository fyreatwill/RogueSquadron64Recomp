# NEXT: read s5706_mask3 / s5706_mask5 soak results (scratch/agent/m6/<tag>/run.log). Control: `[lvsel] init a1(cursorMask)` == 0x8 (N=3) / 0x20 (N=5), NOT 0x4. If control fails, the hook is still mis-ordered - fix before concluding anything.
Then: tick ret==N? initMission name/gCurLevel for N vs 2; any crash/stall for N>2 (capture backtrace, name writer).
Note: fixup guard "PATCH: s5704 lvsel" not in text means regen applies the new _c0 only on fresh generate; generated file was patched in place.
HYPOTHESIS-ID: g1-level-select
