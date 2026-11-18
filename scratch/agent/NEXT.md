# NEXT (s7608)
HYPOTHESIS-ID: thread-keyed-state-census

Class UW closed s7607 (tools/s7607_uw_census.py, 0 open, controls 7/7, witness 2/2; ~Rs64Cf0Delay unwind fix).
Next idiom class TK: host state keyed by guest thread identity that OUTLIVES the thread. s7607 showed worker threads
are destroyed (and the destroyed thread unwinds out of a blocking stub, skipping its post-wait code). Workers are then
re-created with the SAME OSId and often the same OSThread struct. Any host table indexed by OSId / rogue_current_thread_id
/ OSThread address / UltraThreadContext* that is not reset on destroy carries the dead thread's state into the new one.
Examples seen in s7607: g_rs64_waittab[tid&63], g_s4259[tid], s7394fix::holder (tid), g1b slots, s4580::blk_pending,
s7545 thread list, thr_live set.
Enumerate: every host array/map/atomic indexed or compared by a thread id/pointer (grep rogue_current_thread_id,
->id, thread_self, this_thread(), UltraThreadContext*, & 63 index) in src + librecomp + ultramodern. Classify:
reset-on-destroy (osDestroyThread / cleanup_thread / osCreateThread re-init), keyed-by-generation (safe), diag-gated,
BAD (default-path decision reads a stale entry).
Contract: a default-path read of thread-keyed state either cannot see a previous incarnation's entry or the stale
entry is retail-equivalent (named reason).
Hypotheses: H-clean, H-bad-gated, H-bad-live.
Tool tools/s7608_tk_census.py --controls: (1) plant a tid-indexed default-path table with no reset -> OPEN; (2) drop a row
-> OPEN; (3) remove the reset in cleanup_thread for a rowed reset-on-destroy entry -> OPEN; (4) plant a stale-read
use of s7394fix::holder in a default path -> OPEN.
Second source: a runtime witness from an existing log with ROGUESQ_LOG_THREAD_RESUME (scratch/agent/loop.log.pre-s5016
has [thr-destroy]/[thr-create-id] rows): list the OSIds re-created after a destroy and check each rowed table's reset
fires between them, or a compiled witness that destroys and re-creates a thread id through the real tables.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
