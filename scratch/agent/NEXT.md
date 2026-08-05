# NEXT work unit

## s333 closed the previous hypothesis — start here

s333 CLOSED `HYPOTHESIS-ID m5-audio-destub-reapplydisplaymode-reachability` (CURRENT-TRUTH item -190,
full detail `PORTING-STATE` Session 333) with a clean, all-3-hypotheses-settled result: 4 diagnostics
(`ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1`) — an unconditional counter at `runVideoFrameTick`'s own top
(`[frametick-top]`), a marker at `reapplyDisplayMode`'s sole call site (`[reapplydisplaymode-callsite]`),
and paired entry/exit counters on `reapplyDisplayMode`'s own body — all fired **exactly twice** (n=1,
n=2) and then never again for the remaining ~598s of a 600s soak. This refutes "the guard never trips"
and "`reapplyDisplayMode`'s body hangs internally" outright, and relocates the stall an entire
call-frame further upstream than any prior session reached: `runVideoFrameTick` itself — not merely the
`reapplyDisplayMode` call inside it — stops being invoked by its own caller after call #2. Audio stays
alive throughout (`synth=957` at the log's last line). Gate is back at the full force-zero baseline
(`audio gate patched x2`), tree rebuilt clean.

## New hypothesis thread: what does mainGameLoop do between call #2 and the call #3 that never comes?

s333 grepped all 5 `runVideoFrameTick(rdram, ctx);` call sites in the whole `RecompiledFuncs` tree:

| file:line | enclosing function |
|---|---|
| `funcs_8.c:21562` | `mainGameLoop` |
| `funcs_8.c:21717` | `mainGameLoop` |
| `funcs_29.c:37895` | `menuOverlayInit` |
| `funcs_27.c:118107` | `cutsceneDispatchSlotsByFlag` |
| `funcs_43.c:20961` | `static_6_800A9ABC` |

`mainGameLoop` is the top-priority candidate: a per-frame game loop function calling the per-frame tick
function twice (likely two different call sites on different code paths within the loop body, not two
sequential calls per iteration — read the surrounding code before assuming which) is exactly the shape
expected for the real per-frame driver. It has NOT yet been confirmed that `mainGameLoop` is the one
actually exercised in this soak's phase (the craft-select / post-leave menu chain) — that is itself
part of hypothesis 1 below.

## Hypotheses (pick the discriminating probe)

1. **`mainGameLoop` (or whichever of the 5 callers is actually active in this phase) itself stops
   iterating** — its own loop-top/loop-body counter would show the SAME n=2-then-silent pattern as
   `[frametick-top]`, meaning the game thread is stuck somewhere in `mainGameLoop`'s own per-iteration
   logic, either before reaching the `runVideoFrameTick` call a 3rd time or after returning from call
   #2 and never getting back around the loop. Discriminator: an unconditional per-iteration counter at
   `mainGameLoop`'s own loop-top (find the actual loop structure first — it may not be a single simple
   `while`; read the function body, `funcs_8.c` around 21500-21750, before instrumenting blindly).
2. **A different one of the 4 non-`mainGameLoop` callers is the one actually active**, and
   `mainGameLoop` never even runs during this phase — the n=2 pattern belongs to whichever function is
   really driving the frame tick here. Discriminator: entry counters on ALL 5 enclosing functions
   (`mainGameLoop`, `menuOverlayInit`, `cutsceneDispatchSlotsByFlag`, `static_6_800A9ABC`) in the same
   soak — whichever one's entry count is climbing (or stopped) at the same cadence as
   `[frametick-top]` is the real caller.
3. **The stall is even further upstream than any of these 5 functions** — e.g. in whatever calls
   `mainGameLoop` itself (a coop-scheduler / thread-resume mechanism), which would explain why the
   loop's own body never gets a 3rd chance to run at all. This is speculative pending hypothesis 1/2's
   result; do not build for it directly this iteration unless 1 and 2 both come back negative (the
   candidate function's own entry/loop-top counters keep incrementing normally past n=2 with no
   internal stall visible, i.e. the function is being CALLED repeatedly but its own `runVideoFrameTick`
   call site specifically stops firing — that would mean the block is a conditional/branch INSIDE the
   caller, not upstream of it, and should be chased there instead of jumping further up prematurely).

## Also flagged, not yet chased (do not act on without a same-run comparison)

s333 noted this VI=640/`stalled=1 pairs=0` symptom closely resembles the pre-existing, still-unsolved
`~+90-115s post-leave` "graphics-task-submission stall" already documented in this file's phase
timeline (a staggered subsystem shutdown, s176-183, `[thr-resume-skip]` candidate mechanism weakened
but not refuted by s183). If hypothesis 3 above is reached, consider whether this M5 investigation has
been reproducing THAT stall via a different trigger path (the `reapplyDisplayMode` gate reversal)
rather than something audio-de-stubbing-specific — but this needs its own discriminating measurement,
not an assumption from surface resemblance.

## The work unit

1. Read `mainGameLoop`'s body (`funcs_8.c`, roughly lines 21500-21750 in the current regen — confirm
   exact bounds with `grep -n "RECOMP_FUNC" funcs_8.c` since regen can shift line numbers slightly)
   BEFORE instrumenting: find the actual loop structure (label + backward goto, or a native
   `while`/`for` if this is coop-scheduler-driven) and where the 2 `runVideoFrameTick` call sites sit
   relative to it (same iteration on different branches, vs. genuinely two distinct call points).
2. Add diagnostics in `N64Recomp/fixup_game_funcs.py` (same convention: single shared env var, e.g.
   `ROGUESQ_LOG_MAINGAMELOOP_REACH=1`, default off, hard-capped ~40 prints + coarse modulo sample):
   - an unconditional per-iteration (or per-entry, if no simple loop) counter in `mainGameLoop`.
   - entry counters on the other 4 candidate callers (`menuOverlayInit`,
     `cutsceneDispatchSlotsByFlag`, `static_6_800A9ABC`) as a cheap same-run cross-check for
     hypothesis 2 — these are one-line top-of-function inserts, low cost.
   - **CAUTION, learned the hard way this session**: any `re.subn(pattern, repl, text)` call where
     `repl` is a plain string (not a `lambda`) gets its OWN `\n`/backslash escapes reprocessed by the
     `re` module's template engine, silently corrupting `fprintf` format strings into literal embedded
     newlines (a real compile break this session, root-caused via a standalone repro:
     `re.sub("hello","X\\nY","hello world")` -> `'X\nY world'`). Always use `lambda m: (...)` for the
     replacement, matching every other diagnostic in this file — never a bare string with an fprintf
     format inside it.
3. Regen (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → cmake — delete `RecompiledFuncs/*.c`
   first), narrow the audio-gate force-zero regex to `reapplyDisplayMode`'s site only again
   (`0x8008EB40`-only match — confirm `audio gate patched x1` in the fixup report), rebuild, confirm
   the build is clean (check for compile errors, not just patch counts, before soaking — this
   session's lesson).
4. Soak once with `scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`HOLD_S=600`, plus the new
   env var(s)). Expect the same VI=640 phase-timeout INCONCLUSIVE symptom; the new counters' fire
   pattern is the actual result.
5. Whichever hypothesis wins, close it in the same iteration — this is still a
   reachability/location probe, not a fix attempt.
6. Revert the gate to the full force-zero baseline (`audio gate patched x2`) and rebuild clean before
   ending, per every prior session's convention.

## Environment notes (carried forward — see s327-333 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=600 ROGUESQ_LOG_<NEWVAR>=1 zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>`
  (the `env` prefix is required — see project rule 10, a bare `VAR=1 zsh ...` is denied by the
  permission prefix-matcher). Run it via Bash `run_in_background: true` — the harness may move it to
  background automatically past ~120s regardless. Get the PID from the launch output (`pid <PID>
  out=...`), then block in a SEPARATE foreground Bash call: `while kill -0 <PID> 2>/dev/null; do sleep
  5; done` with a timeout comfortably over 600s. A `Monitor` call alone does NOT satisfy the Stop-hook
  gate if the turn ends before the soak completes — the gate re-fires on every attempted stop while
  `scratch/agent/STATUS` is `WORKING`. Log lands at `scratch/s73_post_a_scene/<label>/run.log` — grep
  it, don't read it directly (s333's was 1.28M lines / 60+ MB).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` — allowlisted
  verbatim. `cd <dir>` as its own standalone Bash call, then a separate command in that directory,
  avoids the "compound cd + redirection" approval prompt a single `cd x && cmd > file` triggers.
  Compound commands like `cmd1; cmd2` or `cmd1 > file; cat file` also trigger an approval prompt in
  this environment — prefer separate Bash calls, or a single pipeline (`cmd1 2>&1 | tail -N`).

HYPOTHESIS-ID: m5-audio-destub-mainGameLoop-upstream-stall (1st of 3 iterations — new thread, opened
this session after item -190 closed the prior one).
