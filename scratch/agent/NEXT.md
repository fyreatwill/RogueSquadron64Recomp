# NEXT: G1c phase 2 — per-bump fast path in rsp_dpc_submit_impl (bridge ~21 ns x ~85k DPC_END bumps per gfx task)
HYPOTHESIS-ID: g1c-bump-fastpath
Context (s7026, two runs, spin control passed): at L1 dd6 21:9 WIDEWIN the bridge's own cost is ~21 ns per DPC_END bump, stable across caps and runs;
85k bumps/task = ~1.9 ms/task at every cap (+0.3 ms of the +1.3 ms per-cell delta). RT64 handoffs are already merged (7-8/task, ~3 ns/byte: a lib
parse cost, not this unit). The deferred push (`if (g_defer_active) {` ~line 7709 of src/rsp/dpc_bridge.cpp) sits behind ~1400 lines of per-bump
checks with 27 getenv statics. Extra cells add mostly 8-byte RDP commands (+14k bumps, +~100 KB).
G5i/owner items: nothing to run (CURRENT-TRUTH items 1-14); check first.
Unit: read rsp_dpc_submit_impl from entry to the defer push; list every per-bump block that runs on the owner path (no logging env) and what state it
writes (op6_head/0x27 pipe sync, wrap flush, spike scan, e9prov mark, shadows). Build ROGUESQ_G1E_BUMPFAST=1|tog (tog = odd xor8 seconds, same
[s7010-clk] anchor): when g_defer_active and no diagnostic env is set, skip straight to the push for bumps that cannot trigger any of those blocks
(decide by the first command word, e.g. not 0x27/0x29/0x3F/wrap). Exactness check: ROGUESQ_G1E_BUMPFAST_CHECK=1 compares g_deferred_ranges +
shadow bytes per task between paths (run 1 corrupts its copy = positive control, control must be 1, bad 0).
Hypotheses: H-checks (cost = the per-bump env/flag checks and branches; fast path cuts bridge self by >=50%); H-push (cost = the vector push/shadow
copy itself; fast path saves <20%); H-cache (cost = cache misses on the RDP bytes; neither changes it, ns/bump tracks bytes).
Discriminator: same-run tog, TRING + S7026_SUB columns (tools/s7026_submit_split.py extended with the bump arm): bridge self ns/bump per arm, and
fps/sd_wall per arm at cap 10240 (WIDEWIN=1 CAP=10240). Also log an RDP opcode histogram of the extra bumps (first byte per bump, by cap) in the same
build if WIDEWIN=tog3, to name the 8-byte commands per cell.
Recipe: scratch/s7026/run2.zsh pattern (arm.zsh copy), L1 dd6 21:9, 290 s hold.
