# NEXT: G1e — qualify ROGUESQ_RDP_ASYNC=1 + ROGUESQ_RDP_NODRAIN=1 and measure game fps at dd4
HYPOTHESIS-ID: g1e-gfx-overlap

s6708: the task-end tail is State::fullSync's fb-pair render (1.7 ms CPU encode + 1.3 ms GPU wait). NODRAIN lets send_dl
return without waiting: lvl5 FPS60 dd2 Gfx 8.88 -> 4.54 ms/task, 57.8 -> 59.9 tasks/s (same run, 3 arms), frames sane.
Opt-in, single run.

## Hypotheses
- H-free: no-drain is safe and the Gfx thread stops binding at dd4 too -> game fps at dd4 FPS60 rises from 44-50 (s6704)
  toward 60, or the binder moves to the game thread (G1B sd_cpu / game-thread busy).
- H-race: running the guest ahead of RT64 shows up as render defects (texture garbage, missing fb effects, stale frames)
  or crashes: RT64 reads RDRAM textures / writes fb back while the guest changes it.
- H-worker: at dd4 the worker itself (>16 ms fullSync+ranges per task) binds -> pend_jobs grows, update_screen drains long.

## Work unit
1. Fold the queued soaks (SOAK-RESULTS: s6708_nodrain_lvl1_dd1, s6708_nodrain_lvl10_dd4): crash/stall verdict, [g1e-aq]
   as=3 tasks/s + total ms, g1b tasks/s, fbd sheet per level (reuse the s6708 sheet snippet in PORTING-STATE s6708 / make
   it a tool if used twice).
2. One same-run run lvl5 dd4 FPS60, ASYNC_TOGGLE=10 + NODRAIN=2 (copy scratch/agent/s6708_nd.zsh, dd=4): per arm tasks/s,
   Gfx ms/task, pend_jobs, update_screen drain wait (add a g1b field if missing, in the SAME build as any other field).
   Game fps = distinct fb hashes/s if the G1B instrument gives it; otherwise tasks/s.
3. If clean and faster at dd4: write the one-line opt-in command into docs/OWNER-OPT-INS.md (ROGUESQ_RDP_ASYNC=1
   ROGUESQ_RDP_NODRAIN=1 with FPS60) and ask the owner to judge feel. Default stays off until the owner says.
