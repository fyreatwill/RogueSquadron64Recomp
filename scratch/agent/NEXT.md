# NEXT: G1c phase 2 — name the BUMPFAST=2 bad2 mismatch, then split the 10.7 ns push/shadow/call remainder
HYPOTHESIS-ID: g1c-bump-push-split
Context (s7028): net bridge cost per DPC_END bump at dd6 is 15.7 ns once the 9.0 ns AQ=3 offset (ROGUESQ_G1E_AQ_NULL=1) is taken out.
That splits as checks 1.7, counter atomics 3.3, and push/shadow/call 10.7. BUMPFAST=2 (plain per-task counters) gave CHECK bad2=1 of 11702 flushes, so it is not exact.
G5i/owner items: nothing to run (CURRENT-TRUTH items 1-14); check that first.
Step 1, exactness (must come first, same unit). In rs64_bf2_flush on a bad2, log one [s7028-bad2] line with: the pending vs reference
bytes/cmds/fwd/g1e, pthread_self vs the gfx thread id latched in rs64_dpc_defer_begin, and g_defer_active. Also record, in
rsp_dpc_submit_impl, a thread-id mismatch counter for bf2 bumps (a bump from another thread while task_on==2).
Hypotheses: H-thread (a second thread calls rsp_dpc_submit_impl or a flush reader: the fix is to key bf2 on the gfx thread id);
H-path (an early return between the s_fwd add and the task add other than oob, so fwd != task: the fix is to undo at that return).
The log line tells them apart: a thread mismatch means H-thread, fwd_bytes != task_bytes on the gfx thread means H-path.
Step 2, remainder split, same build: ROGUESQ_G1E_BUMPFAST_SH=tog3 on top of BUMPFAST=2, with arms (a) as is, (b) g_s4272_shadow.reserve()
at defer_begin from the last task's size, (c) no shadow insert when the range is extended in place. Arm (c) is a diagnostic only, because
S4272 is a correctness shadow: check what reads it before (c) runs. Analysis: extend tools/s7028_bump_push_split.py to read the arm per row.
Discriminator: if (b) or (c) cut net ns/bump by >=40% of 10.7, H-shadow; otherwise the remainder is call overhead plus the range push (H-call).
Then the next lever is RT64's ~3 ns/B parse (lib, out of this unit) or ucode self. The whole bridge is ~1.4 ms of a ~13.8 ms task,
so after this unit stop micro-trimming the bridge unless it pays >=0.3 ms/task.
Recipe: scratch/s7028/run.zsh (arm.zsh copy), L1 dd6 21:9 WIDEWIN cap 10240, AQ=3 AQ_NULL S7026_SUB SPIN_NS=300000, 290 s; then a 150 s CHECK run.
