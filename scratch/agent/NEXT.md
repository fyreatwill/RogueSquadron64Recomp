# NEXT work unit — identify which scheduler thread drives the audio tick, and whether it's silent-but-scheduled or dropped

(Written s309. See docs/CURRENT-TRUTH.md item -169 for the summary and `PORTING-STATE` Session 309 for
the full write-up.)

## Context — s309 overturned s307's "lockstep" framing

s307 claimed the RSP-task freeze (stuck at task #39) and the audio-tick freeze (stuck at tick #19) were
the same event, driven by one shared upstream resource. s309 (pure source-read, no soak) found this is
**wrong**: `src/main/main.cpp:485`'s `[runner]` print lives inside `factor5_gfx_runner`, which
`get_rsp_microcode` (line 581) returns **only** for `M_GFXTASK`. `M_AUDTASK` dispatch is a fully separate
branch of that switch (lines 594-626) with its own counter, `[audtask-dispatch]` (line 620) — no shared
runner between the two task types.

Re-reading s307's saved log (`scratch/s73_post_a_scene/step307reach/run.log`, still the correct log to
use — do NOT re-soak yet) with that fact in hand: audio ticks (`[audtask-dispatch]`/`[reach-allsongs-*]`/
`[reach-audioseq-*]`) permanently stop at tick `n=19`, **log line 3013**. RSP graphics tasks then keep
dispatching cleanly for **18 more tasks** (#22 through #39, ending line 4943) — a real, non-trivial
stretch: 1550 `[sched-queue]`/`[sched-check]`/`[sched-runnext]` lines in that window, cycling the *same 7
distinct thread pointers* that were active before the audio stall (diffed the `popped_thr=`/`self_thr=`
sets in `[1857,3013)` vs `[3013,4943)` — identical, plus one incidental new thread). The scheduler does
NOT go fully silent until *after* task #39 (line 4958 onward: 0 further `[sched-*]` lines in the
remaining 2467 log lines) — a real, separate, later full-scheduler wedge.

**Two distinct problems, not one:**
- **(A) Audio-tick-producer stall** at tick 19→20, while the rest of the scheduler keeps running fine.
  This is the M5-relevant one — the thing actually blocking gate-byte reversal validation.
- **(B) Full cooperative-scheduler wedge**, later, coincident with RSP task #39. Possibly the same class
  of bug as the already-documented "post-leave graphics-task-submission stall" (much later game phase,
  `docs/CURRENT-TRUTH.md`'s Current-truth timeline) but that's an untested hypothesis, not a finding —
  don't conflate the two without evidence. **Parked, not this session's target.**

One dead-end already eliminated: an initial thread-set diff across the *whole* log (not scoped to
steady-state) showed thread `0x30010d3d0` present pre-3013 and absent post-3013 — looked like "the audio
thread stopped being scheduled," but it last appears at line 174, hundreds of lines before the *first*
RSP task even starts (line 775). It's an early-boot thread, unrelated. Scoping the diff to steady-state
ticking (`[1857,3013)`) showed no thread disappears at all when audio stops — so the simple "audio
thread's own scheduler entry vanishes" theory (call it H1-simple) doesn't hold *in the trivial form*; the
audio-driving thread (whichever of the 7 it is) is very plausibly still being scheduled after tick #19,
just not reaching the print. This needs a dedicated instrument to settle — the existing log cannot
identify *which* of the 7 thread pointers is the audio producer, so it cannot show what that specific
thread is doing after tick #19.

## The work unit

**Step 1 — form the hypothesis table before building anything** (do this first, revise below if a
different source-read surfaces a better split):

| # | Hypothesis | Discriminating signal |
|---|---|---|
| H1 | The thread that runs `viRetraceHandlerThread`/`musyxSynthFrame` stops being woken at all (its wakeup source — a VI-retrace event, message queue, or semaphore post — stops firing) after the 20th tick. | That thread's pointer stops appearing in `[sched-queue]` (never re-queued) after tick #19, while still being visible in `sched-check` as a "head" comparison target maybe, but never popped/run again. |
| H2 | The thread keeps running on schedule, but a **control-flow gate inside `viRetraceHandlerThread` itself** (a loop-iteration counter, a different condition than the 3 already-cleared gate-consumer functions) stops it from reaching `musyxSynthFrame`/the tick chain after the 20th call — the thread does other work or spins harmlessly. | A new counter placed at `viRetraceHandlerThread`'s own loop-top (not inside `musyxSynthFrame`) keeps incrementing past 20 even though the tick-chain prints stop. |
| H3 | The thread reaches `musyxSynthFrame` on schedule but blocks *inside* it, before reaching `update3DAudioFrame`/`tickAllActiveSongs`/`tickAudioSequencerFrame` (a wait/semaphore/mutex not yet examined, upstream of the 3 already-cleared functions). | The new loop-top counter (from H2's instrument) also freezes at the same call as the tick-chain — i.e., the *thread itself* stalls, but inside `musyxSynthFrame`, not before it. |
| H4 | The 20-tick cap is a real, intentional guest-side limit (e.g., an audio-task ring/queue of fixed depth 20 whose consumer never drains) — not a "stall" at all but a full queue with no reaper. | A queue/ring depth or occupancy counter (if one exists in the audio task submission path) reads exactly 20/20 (full) at the freeze point, in a positive-controlled way (show it draining below 20 during the first 20 ticks). |

**Step 2 — design ONE diagnostic that discriminates all four**, batched into a single build+soak (per
CLAUDE.md's "one build carrying every counter you will want" rule — do not spend a build-run cycle per
counter):
- A print at `viRetraceHandlerThread`'s own loop top (thread-identifying: include `std::this_thread`'s
  id or the raw host thread pointer if accessible from the recompiled-function context — check how
  `[sched-queue]`'s `thr=0x...` value is obtained in `lib/N64ModernRuntime/ultramodern/src/scheduling.cpp`
  or `threads.cpp` and reuse the same accessor) — this settles H1 vs H2/H3 (does the loop itself keep
  ticking past 20, and does its thread pointer match one of the 7 already seen in `[sched-*]`), and
  distinguish H2 from H3.
- If a queue/ring depth for `M_AUDTASK` submission exists (grep `librecomp/src/sp.cpp` /
  `mesgqueue.cpp` for the audio task queue), a same-run occupancy counter — settles H4 independent of
  the others (a positive control: show occupancy varying 0-19 during the healthy first 20 ticks, then
  pinned at a cap afterward, vs. never hitting the cap).

**Step 3 — batch into `fixup_game_funcs.py`/the relevant `lib/` source (with `export.sh` + commit in the
same session if `lib/` is touched, per the hard rule), soak with a copy of
`scratch/s73_post_a_scene/run_step307reach.sh`, read the result, and update the hypothesis table.**
Revert the fixup-script diagnostic same session once read, per the established one-site-per-session
discipline — the `lib/`-side instrument (if any) can stay if it's inert/no-op by default.

## Expected discriminating outcomes

- H1 confirmed alone → look at whatever's supposed to re-queue that thread (a VI-retrace producer or
  message-queue post that itself might be starved — possibly still tracing back to problem (B)'s later
  full wedge, i.e., maybe the SAME wakeup-chain component fails twice, once partially (just this thread)
  then totally (everything) 18 tasks later — this would be a genuine, evidenced link between (A) and (B),
  not an assumed one).
- H2 confirmed alone → the newly-changed gate is inside `viRetraceHandlerThread`'s own body, distinct
  from the 3 already-cleared functions; source-read that function next.
- H3 confirmed alone → something inside `musyxSynthFrame` upstream of the 3 cleared functions blocks;
  source-read `musyxSynthFrame`'s own body (not just its 3 known callees) next.
- H4 confirmed alone → this isn't a stall, it's a full unreaped queue; find the consumer side and why it
  stopped draining (likely converges back toward H1/H3's territory, or opens a genuinely new 5th
  hypothesis about the queue reaper itself).
- More than one could be true; the point of the batched diagnostic is to not have to guess which before
  building.

## Environment notes (carried forward, all still valid)

- Regen order: `fixup_game_funcs.py` edit → clear `N64Recomp/RecompiledFuncs/*.c` (python3 glob-delete;
  plain `rm`/`find -delete` are blocked in this sandbox) → `N64Recomp/build/N64Recomp
  rogue_squadron.toml` (cwd = `N64Recomp` checkout) → `python3 fixup_game_funcs.py` (run exactly once,
  refuses a 2nd run via its own SENTINEL check) → `DEVELOPER_DIR=/Applications/Xcode.app/Contents/
  Developer cmake --build build -j8` (cwd = this repo root). `make_elf.py` not needed unless
  source/symbol mapping changed.
- If the diagnostic requires touching `lib/N64ModernRuntime` (e.g. to expose a thread-identifying
  accessor from `scheduling.cpp`/`threads.cpp` to the recompiled-function context), run
  `./submodule-patches/export.sh` and commit the refreshed patches in the SAME session — required by the
  hard rule, not optional.
- `N64Recomp/fixup_game_funcs.py` is NOT git-tracked in that checkout — durable record is this project's
  own `PORTING-STATE.md`/`CURRENT-TRUTH.md` plus the physical file on disk.
- Soak driver template: `scratch/s73_post_a_scene/run_step307reach.sh` (s307's recipe) — copy it, don't
  hand-roll a new script; only the fixup-script/lib-side edit changes between sessions.
- **Waiting on a soak**: launch via Bash with `run_in_background: true`, then use `TaskOutput` with
  `block: true` and a generous `timeout` (up to 480000ms) — do NOT foreground-poll with a bare `sleep`
  loop or hand-rolled `pgrep` polling.
- **One game run at a time** — confirm `pgrep -f "build/RogueSquadron64Recomp"` is empty before
  launching (the more specific pattern avoids the s307 false-positive on `tail -f` commands whose path
  string happens to contain the binary name).
- `scratch/s73_post_a_scene/step307reach/run.log` is the log this session (s309) re-analyzed — it already
  has everything needed for the thread-set diffing described above if a future session wants to re-verify
  before building; no need to re-derive the 7-thread-pointer sets from scratch, they're recorded here and
  in PORTING-STATE Session 309.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug, s303-309 — still the active
investigation thread, now correctly split into problem (A) audio-tick-stall and (B) full-scheduler-wedge
sub-threads with (A) as the live target. s306/s307 each produced discriminating results (resetting the
iron-rule-8 no-progress counter); s309 is ALSO a discriminating result (overturns s307's own
interpretation via source-read, no soak needed) — does not trigger the "3 iterations, no result" stop
condition. The next session should treat itself as continuing the same slug but should aim to actually
run the Step 2/3 batched soak above, since 2 sessions in a row (s307, s309) have now landed results
without a new soak.
