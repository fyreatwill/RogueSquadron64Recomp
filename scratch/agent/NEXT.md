# NEXT work unit

## s334 narrowed the field to ONE active caller — start here

s334 (`HYPOTHESIS-ID m5-audio-destub-mainGameLoop-upstream-stall`, 2nd of 3 iterations, CURRENT-TRUTH
item -191, full detail `PORTING-STATE` Session 334) instrumented all 5 candidate `runVideoFrameTick`
callers (`mainGameLoop` x2 sites, `menuOverlayInit`, `cutsceneDispatchSlotsByFlag`,
`static_6_800A9ABC`) with entry counters, plus an unconditional per-iteration counter at
`mainGameLoop`'s own loop-top (label `L_8003E04C`, confirmed the single point every backward branch
in its goto/label state machine funnels through). Soaked 600s with the gate narrowed to reverse
`reapplyDisplayMode`'s site only (same setup s329/s332/s333 used, reproduces the VI=640
`stalled=1 pairs=0` INCONCLUSIVE symptom).

**Result, clean and discriminating**:
- `[maingameloop-entry]` / `[maingameloop-loop]`: BOTH fire exactly once (n=1), near the very start of
  the run (lines 694 / 5139, both before the VI 320->640 transition at line 5654). Never again for the
  remaining ~1.28M log lines. **Refutes hypothesis 1** — `mainGameLoop` does not keep iterating its own
  loop; it parks after exactly one pass.
- `[menuoverlayinit-entry]`: fires twice — n=1 early (line 5140, right after mainGameLoop's one loop
  pass) and n=2 right at the very end of the log (line 1283446, within ~2400 lines of the 600s cutoff).
  Not chased this session — flag if it recurs.
- `[static6-800a9abc-entry]`: fires once (line 78567, ~36s in). Not the active driver.
- `[cutscenedispatch-entry]`: fires continuously — n=1 at line 321596 (~147s into the run, well after
  the VI=640 transition and mainGameLoop's single pass), then climbs steadily (roughly one call per
  600-700 log lines) all the way to at least **n=1152** by the log's end (modulo-128 sampled past
  n=40). **Confirms hypothesis 2** — `cutsceneDispatchSlotsByFlag` (`funcs_27.c`), not `mainGameLoop`,
  is the actively-cycling caller during this stall.

## New question: does cutsceneDispatchSlotsByFlag's OWN runVideoFrameTick call site ever fire?

s334 did NOT arm `ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH` (the var gating `[frametick-top]` /
`[reapplydisplaymode-callsite]`, added s333) in the same run as the new `ROGUESQ_LOG_MAINGAMELOOP_REACH`
var — so there is no same-run correlation yet between `cutsceneDispatchSlotsByFlag`'s climbing entry
count (1152+) and whether `runVideoFrameTick` (and therefore `reapplyDisplayMode`) ever fires again
after s333's call #2. This is the discriminating probe for this iteration.

## Hypotheses (pick the discriminating probe)

1. **`cutsceneDispatchSlotsByFlag` reaches its own `runVideoFrameTick` call site
   (`funcs_27.c:118107`) on some/all of its 1152+ calls, and `[frametick-top]` keeps climbing past
   n=2 in lockstep.** This would mean the game thread IS still ticking frames throughout the stall via
   this caller, and the real block is somewhere else entirely — inside `runVideoFrameTick` itself past
   the `reapplyDisplayMode` call (worth re-reading with fresh eyes; s330's "no graphics-task call
   exists textually inside runVideoFrameTick" finding from item -188 would need reconciling with a
   still-climbing frametick count), or in the native `gfx_thread` producer downstream
   (`lib/rt64/src/hle/rt64_state.cpp:2945`).
2. **`[frametick-top]` stays frozen at n=2 (or close to it) while `[cutscenedispatch-entry]` keeps
   climbing into the hundreds/thousands.** This proves `cutsceneDispatchSlotsByFlag` is being called
   repeatedly but its OWN `runVideoFrameTick` call site specifically never fires (or fires only
   rarely/once more) — i.e. a conditional/branch INSIDE `cutsceneDispatchSlotsByFlag` gates the call,
   and that branch's condition is the real block. Discriminator: read `cutsceneDispatchSlotsByFlag`'s
   body (`funcs_27.c`, around line 113839 — confirm exact bounds with
   `grep -n "^RECOMP_FUNC" funcs_27.c` since regen can shift lines) BEFORE instrumenting further, find
   what gates its call to `runVideoFrameTick` at line 118107, and add a diagnostic AT that gate
   (not just the call site) to see what value the guard condition holds when it's not taken — this is
   the direct analogue of s333/s334's reachability-probe method, one level deeper.

## The work unit

1. Read `cutsceneDispatchSlotsByFlag`'s body (`funcs_27.c`, confirm bounds via
   `grep -n "^RECOMP_FUNC" funcs_27.c` — the s334 line 113839 may have shifted) BEFORE instrumenting:
   find the branch/condition that gates reaching its `runVideoFrameTick` call site
   (`... :118107`, confirm with `grep -n "runVideoFrameTick(rdram, ctx);" funcs_27.c`), and read what
   feeds that condition (a flag byte? an enum/state variable? a "slot" argument the function name
   suggests — `DispatchSlotsByFlag` implies it iterates something and calls per matching slot).
2. Add diagnostics in `N64Recomp/fixup_game_funcs.py` (same convention: reuse
   `ROGUESQ_LOG_MAINGAMELOOP_REACH=1` if it's a natural fit, or a new var if the investigation has
   genuinely moved on — default off, hard-capped ~40 prints + coarse modulo sample):
   - a counter or value-dump AT the gating condition inside `cutsceneDispatchSlotsByFlag`, not just
     its call site (which s333's `[reapplydisplaymode-callsite]`-style instrument already covers via
     `[frametick-top]` once armed).
   - **Always use `lambda m: (...)` for `re.subn` replacements, never a bare string with an `fprintf`
     format inside it** — a bare string gets its own `\n`/backslash escapes reprocessed by the `re`
     module's template engine and silently corrupts the format string (s333's real bug, repro'd
     standalone: `re.sub("hello","X\\nY","hello world")` -> `'X\nY world'`).
3. Regen (`make_elf.py` unchanged since s327, so skip it — delete `RecompiledFuncs/*.c`, run
   `N64Recomp`, `fixup_game_funcs.py`, then cmake build). Narrow the audio-gate store regex to
   `0x8008EB40`-only (leaves `setDisplayMode` force-zeroed, `reapplyDisplayMode` reversed — confirm
   `audio gate patched x1` in the fixup report). **Note the naming trap s334 caught**: the "X-only"
   convention names which site STAYS matched/force-zeroed, not which one is under test — to test
   `reapplyDisplayMode` the regex must match `0x8008EB40`, not `0x8008EC88`. Confirm the build is
   clean (0 `error:` lines, not just patch counts) before soaking.
4. Soak once with `scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`HOLD_S=600`), arming BOTH
   `ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1` AND `ROGUESQ_LOG_MAINGAMELOOP_REACH=1` (plus any new var)
   in the SAME run — this is the missing correlation s334 didn't have. Expect the same VI=640
   phase-timeout INCONCLUSIVE symptom; the counters' fire pattern is the actual result.
5. Whichever hypothesis wins, close it in the same iteration.
6. Revert the gate to the full force-zero baseline (`audio gate patched x2`) and rebuild clean before
   ending, per every prior session's convention.

## Environment notes (carried forward — see s327-334 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=600 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_MAINGAMELOOP_REACH=1 zsh
  scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (the `env` prefix is required — see project
  rule 10, a bare `VAR=1 zsh ...` is denied by the permission prefix-matcher). Run it via Bash
  `run_in_background: true`. Get the PID from the launch output (`pid <PID> out=...`), then block in a
  SEPARATE foreground Bash call: `while kill -0 <PID> 2>/dev/null; do sleep 5; done` with a timeout
  comfortably over 600s. Log lands at `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read
  it directly (s334's was 1,285,835 lines / tens of MB).
- Output redirection quirks this session: bare `python3 script.py > file 2>&1` as a single Bash call
  gets flagged "Contains simple_expansion" or requires approval in compound form — safest pattern is
  `cd <dir>` as its own standalone Bash call (no compound `cd x && ...`), then the redirected command
  as a separate call with an absolute output path inside an allowed working directory.
  `printf '...'` with embedded single-quotes/backticks/markdown is fragile under zsh's arithmetic
  expansion of `%d`/`%i`-looking substrings — prefer the Edit tool (Read the file first) for appending
  prose to PORTING-STATE.md/CURRENT-TRUTH.md rather than constructing it via Bash printf/heredoc.
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` — allowlisted
  verbatim.

HYPOTHESIS-ID: m5-audio-destub-mainGameLoop-upstream-stall (2nd of 3 iterations — narrowed from "which
caller is active" (answered: cutsceneDispatchSlotsByFlag) to "does that caller reach
runVideoFrameTick"). If this 3rd iteration doesn't produce a discriminating result, iron rule 8
requires a pivot preamble in the iteration after.
