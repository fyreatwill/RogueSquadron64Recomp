# NEXT: G1e — split the fixed ~3.3 ms task-end RT64 cost (fullSync) in the async+stream arm
HYPOTHESIS-ID: g1e-gfx-overlap

s6707: streaming the deferred RDP list every 16 kB (ROGUESQ_RDP_STREAM_KB, on whenever ROGUESQ_RDP_ASYNC=1) worked mechanically
(last job 150 -> 7.7 kB, RT64 calls 8.9k -> 0.6k/task, 0 drop-after-stream) but the worker's last job still takes 3.29 ms and
drain 3.33 ms. The tail is a FIXED cost triggered by the final range (the task's FULL_SYNC -> RT64 State::fullSync), not parsing.

## Hypotheses (State::fullSync segments, rt64_state.cpp:1881; S4267 phase names in rt64_render_context.cpp:170)
- H-fsflush: State::flush / submitFramebufferPair (fsFlush, fsSubmitFb) dominate -> CPU-side draw-call building; could run
  incrementally (submit fb pairs as they close mid-task) now that the worker sees the stream.
- H-fsupload/render: fsUpload / fsRender / fsRspPipe dominate -> GPU command encoding + uploads; move to the present thread or
  overlap with the next task (only the dp_complete ordering needs the drain).
- H-fswait: a wait (texwait/fbwait/ddwait/pipeline) dominates -> the worker blocks on the GPU / prior workload; pipelining
  (don't wait for the workload) is the lever.

## Work unit (no rebuild needed)
1. Copy scratch/agent/s6707_stream.zsh to s6708_fs.zsh; XENV_EXTRA: ROGUESQ_RDP_ASYNC=1 (constant, drop both toggles),
   add ROGUESQ_S4267=1. Plus a second arm ROGUESQ_RDP_ASYNC=0 with S4267=1 (sequential runs, compare per-task segment ms only,
   not frame rates — segment costs are per-call, not scene-phase sensitive at t>=140 averages; label cross-run).
2. Fold [s4267] lines: per second, segment sum / fullSync n => ms per fullSync for fsFlush..fsAdvance; positive control =
   segments sum ~= fullSync total (phase 4) and fullSync ms ~= last_ms 3.3 from [g1e-aq].
3. Whichever segment owns >=2 ms selects the lever; implement it in the same session if bounded (patches under lib/rt64 ->
   ./submodule-patches/export.sh + commit).
