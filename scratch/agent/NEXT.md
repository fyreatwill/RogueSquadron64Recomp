# NEXT work unit

## s336 closed the divergent-callee-count question with a source proof — start here

s336 (`HYPOTHESIS-ID m5-audio-destub-cinematicloopbody-divergent-callees`, 2nd of up to 3 iterations,
CURRENT-TRUTH item -193, full detail `PORTING-STATE` Session 336) read `cinematicLoopBody`'s full body
(`funcs_27.c:106842`–`108530`) before touching any instrumentation, per NEXT.md's own prescribed step
1 — and the read alone answered the open question, so no new soak was needed (same pattern as s335).

**Finding**: `cinematicLoopBody` contains its own internal per-frame `goto`-loop — an unconditional
`j L_800A6024` at `funcs_27.c:108258` lands back at `funcs_27.c:107269` (`L_800A6024`), a point AFTER
the `static_6_800A9ABC` setup call (`107079`) but BEFORE the `cutsceneDispatchSlotsByFlag` call
(`107938`). Every loop pass calls `cutsceneDispatchSlotsByFlag` and `submitGfxFrame` (`108253`) and
jumps straight back to the top; `static_6_800A9ABC`, sitting before the loop's entry point, never
re-fires. This is exactly hypothesis 1 from s335's NEXT.md (self-looping function), confirmed, and
refutes hypothesis 2 (repeated invocation by an outer caller). `cinematicLoopBody`'s own two call
sites (`funcs_44.c:4825`, `funcs_27.c:156405` — duplicate overlay copies of the same wrapper,
`static_6_800AE518`) are plain non-looping tail calls with fixed args, consistent with "invoked once
to start a cutscene, then this internal loop pumps every frame until its own exit condition fires."

## New question: is the loop's exit gate audio-related at all, or was this thread mis-filed under M5?

The loop's only exit (`funcs_27.c:107342`, `goto L_800A64BC`) is gated by `static_6_800AF550`
(`funcs_44.c:6187`) returning nonzero. Read it in full: it compares an accumulated float against two
threshold constants (`0x800A5D70`/`0x800A5D74`) and force-exits after a 7-iteration debounce. Traced
its `a2` input (`$f20`, set at the loop's top from the PRECEDING call's return) back through
`static_6_800AF360` (`funcs_44.c:5792`) to `timeSnapshotFiller` — a real OS-clock delta-time snapshot
call. **Three function-levels deep, zero audio-subsystem references anywhere in the chain traced so
far.** This is source-level evidence — not yet proven at runtime — that the `reapplyDisplayMode`
VI=640 stall this whole s327-336 arc has been chasing under the "M5 audio de-stubbing" strategic
priority may have nothing to do with audio: it may be a plain cutscene-duration timer that never gets
satisfied (a long/legitimate cutscene, or a duration-table bug), independent of the audio-gate work.

## The work unit

1. **Instrument `static_6_800AF550` and correlate with the loop's own iteration counter, in ONE soak**
   (batch every counter — iron rule "batch instrumentation"):
   - Entry/return counter on `static_6_800AF550` itself: log its return value (`ctx->r2` at the two
     `jr $ra` sites, `funcs_44.c:6268` returns via fallthrough=1/exit, `6325` (`L_800AF604`)
     returns=0/continue) each call, modulo-sampled like prior sessions' vars.
   - Log the `a2` argument (`ctx->r6`, the delta-time float bits) at entry — reinterpret as float when
     analyzing offline.
   - Log the debounce counter (struct-offset `0x938` off the pointer loaded from global `0x800B0934`)
     and whether it's advancing or stuck.
   - Reuse `ROGUESQ_LOG_MAINGAMELOOP_REACH`-style var naming or open a new one
     (`ROGUESQ_LOG_CUTSCENETIMER_REACH=1`) — whichever is a natural fit once you look at how the
     existing macro is wired in `fixup_game_funcs.py`. Always use `lambda m: (...)` for `re.subn`
     replacements (s333's caught bug — a plain string substitution double-escapes).
2. Same soak setup as s329/s332/s333/s334/s335: gate narrowed to reverse `reapplyDisplayMode`'s site
   only, `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, `env HOLD_S=600 <VARS> zsh
   scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (the `env` prefix is required — see project
   rule 10). Positive control: confirm the new counter(s) actually fire at least once early in the run
   before trusting a "stuck" reading late in the run (iron rule 1).
3. **Discriminating outcomes**:
   - If `a2`/delta-time is consistently near-zero across the 1152+ loop iterations → the timer truly
     isn't advancing, which reopens the audio-relevance question (what's holding
     `timeSnapshotFiller`'s snapshot still — possibly an OS-timer service normally driven by an
     interrupt/thread the audio stub also short-circuits; investigate that specific mechanism next).
   - If `a2`/delta-time IS advancing normally but the debounce counter or threshold comparison never
     triggers exit → this is a plain gameplay/duration-table bug, unrelated to M5 — recommend
     re-filing this thread out of the "M5 audio de-stubbing" strategic priority (item 2) into M3-class
     crash/hang idiom work (item 3), or its own tracked item, at the next iteration boundary. This is a
     judgment call worth surfacing to the user rather than silently reclassifying.
   - If the debounce counter DOES reach 7 and `static_6_800AF550` DOES return nonzero at some point
     during the 600s soak, but `cutsceneDispatchSlotsByFlag`'s count still climbs past that point →
     something else is wrong (the loop isn't actually exiting on the gate signal as read) — treat as a
     new open question, don't force-fit it into either bucket above.
4. Whichever outcome, close it in the same iteration (update CURRENT-TRUTH item -193 / add a new item)
   — this is the 3rd iteration on `HYPOTHESIS-ID m5-audio-destub-cinematicloopbody-divergent-callees`
   if run next, which is the iron-rule-8 budget ceiling: if this iteration doesn't produce a
   discriminating result, STOP experimenting on this thread and go BLOCKED or pivot explicitly.
5. Revert to the full force-zero baseline (`audio gate patched x2`) and rebuild clean before ending,
   per every prior session's convention.

## Environment notes (carried forward — see s327-336 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=600 <VARS> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (the `env` prefix
  is required — see project rule 10, a bare `VAR=1 zsh ...` is denied by the permission
  prefix-matcher). Run it via Bash `run_in_background: true`. Get the PID from the launch output
  (`pid <PID> out=...`), then block in a SEPARATE foreground Bash call:
  `while kill -0 <PID> 2>/dev/null; do sleep 5; done` with a timeout comfortably over 600s. Log lands
  at `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly (past logs have run
  tens of MB / over a million lines).
- **Existing logs are reusable evidence** — s335 and s336 both answered open questions by re-reading
  source or re-grepping already-captured logs instead of re-running a soak. Check
  `scratch/s73_post_a_scene/<recent label>/run.log` for a relevant counter before spending a new
  build-run cycle — but note s334's existing log did NOT arm any `static_6_800AF550`-adjacent counter,
  so THIS question does need a new soak.
- Output redirection quirks this session: bare `python3 script.py > file 2>&1` as a single Bash call
  gets flagged "Contains simple_expansion" or requires approval in compound form — safest pattern is
  `cd <dir>` as its own standalone Bash call (no compound `cd x && ...`), then the redirected command
  as a separate call with an absolute output path inside an allowed working directory.
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` — allowlisted
  verbatim.
- Multi-directory `cd a && git ...` or `cd a && <cmd>` compound Bash calls get flagged for approval
  this session — use `git -C <path> ...` instead, or a standalone `cd` as its own call.
- Scratch files outside the three allowed working directories (e.g. `/tmp/...`) are blocked by the
  sandbox — write throwaway analysis scripts under `scratch/` in this repo instead.

HYPOTHESIS-ID: m5-audio-destub-cinematicloopbody-divergent-callees (2nd iteration — same thread as
s335's pivot, closed its own divergent-callee-count question this session, opened a new sub-question
about whether the exit-gate's timer is audio-dependent).
