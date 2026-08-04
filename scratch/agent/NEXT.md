# NEXT work unit — trace why RSP task #40 never arrives after task #39's clean exit

(Written s307. See docs/CURRENT-TRUTH.md item -168 for the full write-up and `PORTING-STATE` Session 307
for full detail.)

## Note: this session may be a MAINTENANCE iteration instead

`docs/CURRENT-TRUTH.md` is now 60,540 bytes — over the Step-0 60,000-byte trigger. If Step 0 fires,
compact CURRENT-TRUTH first (see tools/agent/ITERATION.md's Maintenance section) and treat this file as
the work unit for whichever session picks up M5 audio next, not necessarily this one.

## Context

s307 re-reversed `setDisplayMode`'s gate-byte site (`0x8008EB40`) a 3rd time (1st: s303, black-box,
re-reverted. 2nd: s307 itself, with s306's 3 gate-consumer entry/exit tags live). The soak reproduced
the same deterministic hang a 3rd time (VI stuck at width 320, exactly 39 RSP tasks, no crash, 600s
window, never reaches title) — but this time with localization data: `update3DAudioFrame`,
`tickAllActiveSongs`, and `tickAudioSequencerFrame` all completed 20 clean entry/exit pairs (`n=0..19`)
before the freeze. **None of the 3 previously-suspected functions hangs internally.**

Cross-referencing the RSP task log (`[runner] task #N exit=1`, emitted from
`src/main/main.cpp:485`, the shared factor5_ucode task runner that dispatches BOTH graphics DL tasks and
audio ucode tasks through one path — this explains why a graphics-side counter and an audio-tick counter
freeze together): task #39 is the last one ever logged; task #40 never arrives, for the rest of the
600s window. The audio-tick freeze (stuck at `n=19`, 20th iteration never starts) and the RSP-task freeze
(stuck at task #39) land at the same point in the log, both followed by pure scheduler churn
(`[sched-queue]`/`[sched-check]`/`[sched-runnext]` lines cycling with no new work item ever appearing).
The VI/present thread does NOT freeze — `update_screen #N` and `vi-fs-decision #N` keep climbing (past
`#36000` by 600s) — it just perpetually skips presentation because `rdpFs` (RSP task-dispatch count)
never advances past 39.

**Revised hypothesis**: a shared upstream resource — most likely something in the coop-scheduler
thread-wakeup chain, or a producer thread that's supposed to feed the next RSP task (audio or graphics)
into the queue — stops delivering work after a fixed small count. This is NOT explained by a bug inside
any of the 3 audio-gate-consumer functions; they're cleared as suspects. s307 reverted the fixup change
same session (one-site-per-session discipline) — baseline is back to s306's validated state
(`initMusyXEngine`'s dead-code site alone reversed, both `setDisplayMode` and `reapplyDisplayMode`
force-zeroed).

## The work unit

**Step 1 — source-read, no build/soak yet.** Using s307's saved log
(`scratch/s73_post_a_scene/step307reach/run.log` — do NOT re-soak yet, this log already has everything
needed for a first pass), work out what's supposed to happen right after `[runner] task #39 exit=1`:
- What guest code is expected to submit the next task (audio ucode task or graphics DL task — check
  whether task #40 would have been audio or graphics by looking at the alternating `dl_ptr` pattern in
  the last several `[runner]` lines: `0x80720318`/`0x80720108` alternate — is task #40 expected to keep
  that alternation, and does either address correspond to an audio-side or graphics-side DL buffer?).
- Read `src/main/main.cpp` around the `[runner]` line (currently ~line 485) upward to find what enqueues
  a task into this runner and what would need to happen (thread wakeup, semaphore, message queue) for a
  40th one to be dispatched. Cross-reference against the `[sched-queue]`/`[sched-check]`/`[sched-runnext]`
  churn visible after task #39 in the log — is the scheduler stuck cycling between the SAME small set of
  threads forever (a real wedge, e.g. a thread that never yields what it's supposed to) or does it
  eventually queue a new thread that then does nothing (a different, more specific stall)?
- Identify the guest function whose 20th call would have produced the next audio ucode task (probably
  something musyxSynthFrame calls downstream of the 3 already-cleared gate-consumer functions, or a
  separate producer entirely) and read what it does that could block.

**Step 2 — form 2-4 concrete hypotheses** about the specific blocking condition (e.g.: "thread X is
waiting on a semaphore that thread Y is supposed to post, but Y's post site is unreached because gate=1
changes control flow inside a 4th function not yet examined", or "the RSP task queue has a fixed-size
ring buffer whose consumer stopped draining"), and design the ONE diagnostic tag that discriminates
between them — do not add a diagnostic without first knowing what each possible reading would prove (the
iron-rule-8 discipline that's kept this thread converging session over session).

**Step 3 — if a new diagnostic is warranted**, batch it into `fixup_game_funcs.py` alongside a fresh
`setDisplayMode` reversal (this will be the 3rd such reversal attempt with new instrumentation, expect
the same hang — that's fine, it's a controlled, reproducible experiment now, not a surprise), soak with
`scratch/s73_post_a_scene/run_step307reach.sh` (or a copy — s307's recipe carries everything needed) and
read the result. Revert the fixup same session per the established discipline once the soak completes.

## Expected discriminating outcomes

Depends on what Step 1's source-read finds — write the actual hypothesis table into a revised NEXT.md
before building anything, per the iteration contract's "before building anything" rule.

## Environment notes (carried forward, all still valid)

- Regen order: `fixup_game_funcs.py` edit → clear `N64Recomp/RecompiledFuncs/*.c` (python3 glob-delete;
  plain `rm`/`find -delete` are blocked in this sandbox) → `N64Recomp/build/N64Recomp
  rogue_squadron.toml` (cwd = `N64Recomp` checkout) → `python3 fixup_game_funcs.py` (run exactly once,
  refuses a 2nd run via its own SENTINEL check) → `DEVELOPER_DIR=/Applications/Xcode.app/Contents/
  Developer cmake --build build -j8` (cwd = this repo root). `make_elf.py` not needed unless
  source/symbol mapping changed (it didn't in s307).
- `N64Recomp/fixup_game_funcs.py` is NOT git-tracked in that checkout — durable record is this project's
  own `PORTING-STATE.md`/`CURRENT-TRUTH.md` plus the physical file on disk.
- Soak driver template: `scratch/s73_post_a_scene/run_step307reach.sh` (s307's recipe, identical env to
  s306's `run_step5reach1.sh` — copy either, don't hand-roll a new script; only the fixup-script edit
  changes between sessions).
- **Waiting on a soak**: launch via Bash with `run_in_background: true`, then use `TaskOutput` with
  `block: true` and a generous `timeout` (up to 480000ms) to wait for completion — do NOT foreground-
  poll with a bare `sleep` loop (blocked in this harness) or hand-rolled `pgrep` polling loops.
- **One game run at a time** — confirm `pgrep -f "build/RogueSquadron64Recomp"` is empty before
  launching (NOTE: `pgrep -f "\./RogueSquadron64Recomp"` false-positives on unrelated processes whose
  command line happens to contain that path string, e.g. `tail -f .../loop.log` on a path under this
  repo — matched a stray `tail -f` in s307, cost a few minutes of investigation; use the more specific
  `build/RogueSquadron64Recomp` pattern instead).
- `[phase]` line count is a fast triage signal: 2 lines total stuck at width 320 (s303's/s307's
  signature) means this specific hang; many lines advancing through 640→1024 means normal progress.
  `[runner] task #N` stopping permanently mid-run (grep the log for the highest N reached, confirm no
  higher N appears later) is now the more precise signal for this specific hang than the phase-line count
  alone.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug as s303-307 — still the active
investigation thread. s303 = iteration 1 (black-box reversal, hung). s304 = iteration 2 (source-read,
refuted 2 hypotheses). s305 = mandated MAINTENANCE, does not count. s306 = iteration 3 (reachability
settled, prior conclusion overturned — a genuine discriminating result, resetting the no-progress
counter per iron rule 8). s307 = iteration 4 — ALSO produced a discriminating result (localized the hang
away from the 3 gate-consumer functions to the shared RSP-task/audio-tick freeze point), so this again
does not trigger the "3 iterations, no result" stop condition — real information keeps landing each
session on this thread. The work unit above (source-read what should produce task #40) is the next
genuinely new probe, not a repeat.
