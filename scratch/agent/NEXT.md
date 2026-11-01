# NEXT: G1e — stream deferred RDP ranges to the async worker during the task
HYPOTHESIS-ID: g1e-gfx-overlap

s6706 ([g1e-aq], lvl5 FPS60 dd2 toggle): async worker busy 4.2 ms/task, of which 3.5 ms is the LAST job (~120 kB) = the
defer layer's final commit at rs64_dpc_defer_end (main.cpp:6658), which only exists after the ucode exits. Mid-task, only
ring-lap wrap flushes (dpc_bridge.cpp ~5241, s4273) release ranges, one 8-byte range per submit call (~9.5k calls/task).
Producer side costs ~0.9 ms (copy 0.35 + mutex/merge).

## Hypotheses
- H-stream: feeding the deferred list to the worker every ~16 kB while the RSP runs moves most of the 3.5 ms tail into the RSP
  phase. Expect wk_tail < 1 ms, drain < 1 ms, total down ~2.5 ms vs as=0 in the same run.
- H-dep-late: bytes in the ring are rewritten after bump but before the periodic flush (s4272 latewrite says 0 diffs at commit
  time, so unlikely); render check catches it (fbd frames both arms).
- H-producer-bound: the extra flushes add mutex/copy cost that cancels the gain (copy column grows past ~1.5 ms).

## Work unit (ONE build, ONE run)
1. dpc_bridge.cpp defer path (~6429): when rs64_rdp_async_on and deferred bytes since the last flush >= ROGUESQ_RDP_STREAM_KB
   (default 16, 0 = off), submit the pending deferred ranges merged (same code as defer_end's merge loop; factor it into a
   helper) and clear them + the s4272 shadow entries already consumed. Keep sync mode byte-identical.
   Also consider merging contiguous ranges in the wrap flush (it submits unmerged).
2. `zsh scratch/agent/s6706_aq.zsh astog 5 2` with a new tag (copy to s6707_stream.zsh), fold `python3 tools/g1e_aq.py <dir>`
   and `env AS=1 python3 tools/g1e_gfxbusy.py <dir>`; contact sheet of fbd frames from both arms.
3. If total drops >=2 ms with sane frames: qualify lvl1/5/10 dd2 FPS60 300 s (queue as soaks), then offer ROGUESQ_RDP_ASYNC in
   docs/OWNER-OPT-INS.md.
