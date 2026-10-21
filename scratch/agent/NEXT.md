# NEXT: G1 — name the caller of the 8 counter-1 sets (a2==1) and count its sources
s5810 showed updateDestructionDebrisNpc never carries a2==1 (0 class-1 spawns of 175). So the 8 `[ctr1] set` ids (0x18,19,2B,1D,1B,1C,29,2A) come from another caller.
Work unit: ONE build adding, in datItemSetObjectiveBooleanCount under ROGUESQ_LOG_HUDBIT, a glibc backtrace() (see s5793 patch pattern in funcs_16.c) for the first 8 a2==1 calls plus MIPS-side: the caller's $ra is lost because the recomp passes no ra, so also log the C backtrace symbols (recomp function names). Then statically count in that caller how many a2==1 sources the lv0 DAT supplies (>=21 needed). Run scratch/agent/g1_inv1.sh <tag> 400.
Outcomes: caller = datItem trigger/effect table with only 8 entries -> H-supply (level needs other action/other fail-win route); caller loops over >=21 entries but stops at 8 -> H-port-skip at that loop.
Positive control: the 8 known ids must each get a backtrace.
HYPOTHESIS-ID: g1-mission-progression
