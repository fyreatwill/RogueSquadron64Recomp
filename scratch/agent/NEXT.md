# NEXT: G1e — why the async RDP consumer saves only ~1.2 ms/task
HYPOTHESIS-ID: g1e-gfx-overlap

s6705 landed ROGUESQ_RDP_ASYNC=1 (src/main/rt64_render_context.cpp ultramodern::rdpq). Same-run toggle (lvl5 FPS60 dd2):
sd 11.70 -> 10.46 ms, 49.3 -> 54.9 tasks/s, frames sane, 0 crash. s6704 put RT64 at ~46% of send_dl (~5 ms), so most of it
still does not overlap.

## Hypotheses
- H-endload: most RT64 time lands in the last range(s) of the task (the fullSync after the RSP finishes: framebuffer
  resolve/workload submit), so it runs after the RSP is done. Expect drain wait ~= RT64 busy in the tail, and worker idle
  for most of the RSP phase.
- H-worker: the worker is busy for the whole task (RT64 >= RSP), so send_dl = RT64 time. Expect worker busy ~= sd_ms; the
  lever is RT64 itself (TMEM hash, loadBlock, decodeTriangles, ProfilingTimer leftovers).
- H-producer: copy/merge/mutex cost on the Gfx thread eats the gain. Expect RSP wall in async > RSP-only wall in sync.

## Work unit (ONE build, ONE run)
1. In rdpq, accumulate per task (Gfx thread, cheap clock): t_rsp = send_dl start -> drain() entry, t_drain = drain wait,
   worker busy ms (worker-side sum, atomic), bytes and jobs, and the size and busy time of the LAST job. Print one [g1e-aq]
   line per [g1b] second (averages) from events.cpp g1b::tick, or from rdpq on its own second boundary.
2. Rerun `zsh scratch/agent/s6705_async.zsh astog 5 2` (300 s) and fold with `env AS=1 python3 tools/g1e_gfxbusy.py`.
3. Decide: H-endload -> split the fullSync work (let dp_complete fire after RT64 has the workload queued, or pipeline the
   next task's RSP against this task's tail: risky, needs RDRAM-visibility analysis). H-worker -> profile RT64 on the worker
   (sample(1) the "RS64 RDP async" thread). H-producer -> drop the copy where the ring does not lap.
4. If the gain then reaches >=2 ms, qualify lvl1/5/10 dd2 FPS60 300 s, and offer ROGUESQ_RDP_ASYNC to the owner in
   docs/OWNER-OPT-INS.md.
