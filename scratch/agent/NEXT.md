Single next work unit: fold the s5584_plume_title_hold soak verdict from SOAK-RESULTS.md (N=4 LLE-trio boots held 120 s past first title). Control: each titled run has an ALIVE_AT_+120 line with first!=last origin. Crash -> backtrace in run*.game (main.cpp:10190 handler), name the writer of the si_addr=0x58 deref, fix root cause. 0/4 crash with alive120=4/4 -> plume thread closed (<1/16 over 40 boots); then ask the human for direction (BLOCKED.md).
Do NOT re-run M6 holds (closed) or the renaming sweep (exhausted s5530).
HYPOTHESIS-ID: plume-title-extended-hold
