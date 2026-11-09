# NEXT: G1c phase 2 — split the remaining ~22 ns/bump on the s7027 fast path (push vs counter atomics vs timing offset)
HYPOTHESIS-ID: g1c-bump-push-split
Context (s7027): ROGUESQ_G1E_BUMPFAST=1 (exact) skips every per-bump check on 54% of DPC_END bumps; bridge self 24.4 -> 22.4 ns/bump only.
What is left on a fast bump (src/rsp/dpc_bridge.cpp rsp_dpc_submit_impl, label rs64_bf_push): DPCWIN static check, base/last_end logic,
s_fwd_bytes/s_fwd_submits (seq_cst fetch_add), oob check, g_task_rdp_bytes / rs64_g1e_rdp_bytes / g_task_rdp_cmds / g_cumulative_op_count
(atomics), the Rs64BfScope guard dtor, then the push: BATCH extend of g_deferred_ranges.back() + g_s4272_shadow.insert(8 bytes).
G5i/owner items: nothing to run (CURRENT-TRUTH items 1-14); check first.
Hypotheses: H-atomics (the ~7 atomic RMWs, ~2-3 ns each, carry >=40% of the 22 ns); H-shadow (the 8-byte vector insert / range extend
carries >=40%); H-offset (AQ=3's per-timed-call clock read cost is scaled x16 into ns/bump: a null-timed call reads >=5 ns/bump).
Unit, ONE build: (1) ROGUESQ_G1E_AQ_NULL=1: every 16th call also times an empty noinline call with the same clock pair, reported as a
ring column (= the offset to subtract). (2) ROGUESQ_G1E_BUMPFAST=2 (fast path + counters): move the per-bump atomics to plain
thread-local per-task accumulators flushed once at rs64_dpc_defer_end (the gfx thread is the only writer; check every reader of
g_task_rdp_bytes/g_task_rdp_cmds/rs64_g1e_rdp_bytes/g_cumulative_op_count is per-task or end-of-task first), and make s_fwd_* relaxed.
(3) BUMPFAST tog3 = 3-way same-run split on xor8 seconds: off / =1 / =2. Exactness: BUMPFAST_CHECK must stay bad 0 ctl 4, and the
end-of-task counter totals must equal the atomic path's (compare per-task in CHECK mode).
Discriminator: tools/s7027_bumpfast_split.py extended to 3 arms + null column: ns/bump off / fast / fast+counters, minus the null offset.
If H-atomics wins, land =2 (exact) and ask whether to default on; if H-shadow, look at reserving g_s4272_shadow per task (capacity from
the last task) or dropping the 8-byte shadow when the range is extended in place; if H-offset, the real bridge cost is smaller than s7026
said and G1c per-cell headroom must come from RT64's ~3 ns/B parse (lib, out of this unit) or the ucode self.
Recipe: scratch/s7027/run.zsh pattern (arm.zsh copy), L1 dd6 21:9 WIDEWIN cap 10240, AQ=3 S7026_SUB SPIN_NS=300000, 290 s hold; then a
150 s CHECK run.
