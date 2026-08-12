# BLOCKED — s671 E9-alignment discriminating run cannot complete inside this
interactive session

## What I need
A way to let the s671 item -421 discriminating run (`e9_aligned` vs naive
`e9_a`/`e9_b`) actually finish — it needs ~1400-2400s of real wall-clock time
per NEXT.md's own estimate, and this interactive session's Stop-hook gate
re-fires on every attempt to end a turn, well before that much real time can
elapse through normal check-in cycles. I need either:
- a human to just let the already-running attempt finish and hand me (or the
  next iteration) the resulting log, or
- confirmation that it's fine to add a soak_queue/ recipe for this
  specific one-shot run despite NEXT.md's prior guidance that it's
  "NOT soak-queueable" (the queue's 600s hard cap would truncate it before
  reaching sec2 — same reasoning as -422), or
- guidance on the correct pattern for waiting out a long external process in
  this harness when the project's own Stop-hook gate requires the work unit
  to be finished before the turn can end.

## What I already tried
1. Built the instrument: added `e9_aligned` counting (inline-data-aware
   stride, respecting MoveMem/TriGen/Tri/TexrectGen/SetOtherMode_*_EX
   advances) to the existing `ROGUESQ_LOG_DL_SYNC2` walker in
   `src/main/main.cpp` (`[dl-sync-probe2]` fprintf, ~line 857-929), and wired
   `ROGUESQ_LOG_DL_SYNC2=1` into `scratch/agent/s670_postsec2_pulse_freeroll.sh`'s
   `GAME_EXTRA_ENV_BASE` so it fires alongside the existing naive
   `ROGUESQ_LOG_DL_SYNC` counters on the same tasks. Rebuilt cleanly (no
   regen needed — pure runtime C++).
2. Launched the freeroll script (`BUDGET_S=2400`, matching NEXT.md's
   in-session-only guidance) as a background Bash task and armed a Monitor
   with an until-loop on the script's PID.
3. The Stop-hook gate fired on every attempt to end the turn while the run
   was still in progress, regardless of the background task/Monitor —
   evidence: `date` between successive checks moved forward only ~10-60s
   per round-trip even though the underlying game process kept running and
   producing new log lines in real time (verified: attempt 1 reached
   hangar-sel at +215s, then went recovery-silent and rerolled to attempt 2
   at +268s — genuine progress, just slower than the hook re-fire rate).
4. Tried a foreground blocking wait (`sleep`, and a `sleep`+`ps` check loop)
   — both explicitly blocked by the sandbox, which redirected me to use
   Monitor/background instead (which I had already done, and which does not
   synchronously block the Stop-hook check).
5. After 6 consecutive Stop-hook blocks with no way to force the needed
   wall-clock time to elapse synchronously within the turn, stopping here
   per the hook's own instruction rather than continuing to retry the same
   approach.

## Evidence this is a real block, not a precedent citation
This iteration's own transcript: 6 rounds of Stop-hook feedback, each
showing the background process (`pid=24977`, tag
`s670_postsec2_pulse_2_20260811205418` as of the last check) still alive and
making incremental real progress (new `[s670] attempt N ...` log lines each
round), while `date` advanced only tens of seconds per round — i.e., the
turn-based check-in cadence cannot outrun the ~1400-2400s the experiment
itself needs.

## What would refute this
If a future iteration (or a human) can demonstrate a way to hold this
session's turn open — via a tool call that genuinely blocks until an
external background process/Monitor event fires, rather than one that gets
rejected by the sandbox or returns instantly — then the "cannot complete
inside this interactive session" claim is refuted and the run should be
retried in-session as originally planned.

## State left behind
- `src/main/main.cpp` and `scratch/agent/s670_postsec2_pulse_freeroll.sh`
  changes are complete, built, and correct (per NEXT.md's plan) — committing
  them now.
- The background freeroll process may still be running on the machine
  (`pid=24977` at last check, log at
  `scratch/agent/s671_e9align_freeroll_out.log`,
  `scratch/s73_post_a_scene/s670_postsec2_pulse_2_20260811205418/run.log`)
  but is not guaranteed to survive session end.
- NEXT.md is unchanged — the plan is still correct, it just needs a session
  (or human-supervised run) that can actually let it finish. Do not redo the
  instrumentation; just re-run
  `env BUDGET_S=2400 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh` and
  wait for it to finish (or check whether the already-running attempt from
  this session left a usable `run.log` with a syncs>0/recovery-active
  post-sec2 stretch).
