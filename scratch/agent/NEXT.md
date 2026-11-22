# NEXT (s7813)
HYPOTHESIS-ID: generated-host-callee-class
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Closed siblings (do not redo): gcc C-patches s7809, host overrides s7810, fixup hunks = class GR s7558 (gated), recomp.h helpers s7812
(tools/s7812_recomp_h_census.py, sweep row S7812_RECOMP_H).
Unit: the last sibling = every NON-helper, NON-RECOMP_FUNC callee the generated C calls (s7812 count: 680 distinct callees in
../N64Recomp/RecompiledFuncs, 325 not rs64-prefixed: fprintf 2633, getenv 2290, fabsf 248, do_break 230, switch_error 177, sqrtf 113,
memcpy 84, os*_recomp (RecvMesg 53, SendMesg 44, CreateMesgQueue 28, YieldThread 22, GetTime 14, StartThread 12), yield_self_1ms 30,
__builtin_trap 29, cop0_status_write 13, ...). BORING FIRST: grep PORTING-STATE for an existing callee census (s7392-s7406 BB-BP
closed thread/mesg/timer contracts; s7415 abs/sqrt emission) and only table what is not already rowed.
Method: extend s7812_recomp_h_census.py (or a sibling tool) with a callee table: class = diag (only reached under a default-off
gate / log), guest-visible libc (fabsf/sqrtf/memcpy/memset: map to s7415 or a new test row), runtime contract (os*_recomp: map to the
BB-BP sessions), trap/yield (map to GR verdicts). Unrowed guest-visible callee -> OPEN (RED).
Hypotheses: H-all-rowed (0 OPEN), H-orphan (>=1 guest-visible callee with no evidence -> write its differential), H-hollow (classifier
misses a call shape: distinct-callee count must equal the regex enumeration's count).
Controls: planted guest-visible callee with no row -> OPEN; planted diag-gated callee -> diag; missing session -> OPEN.
