# NEXT work unit

## s335 closed the mainGameLoop-upstream hypothesis with a source proof — start here

s335 (`HYPOTHESIS-ID m5-audio-destub-mainGameLoop-upstream-stall`, 3rd/final of 3 iterations,
CURRENT-TRUTH item -192, full detail `PORTING-STATE` Session 335) read `cutsceneDispatchSlotsByFlag`'s
body (`funcs_27.c`, function starts 113839) before adding any new diagnostic, per NEXT.md's own
prescribed step 1 — and the read alone answered the open question, so no new soak was needed.

**Finding**: the `runVideoFrameTick` call textually inside `cutsceneDispatchSlotsByFlag`
(`funcs_27.c:118121`) is **unreachable dead code** — it sits after an unconditional `return;`
(`funcs_27.c:117878`) with no incoming label/goto/jump-table reference from anywhere in the tree. It's
a duplicate of `static_6_800A9ABC`'s body (`funcs_43.c:20718`), which `N64Recomp` appears to have
appended into `cutsceneDispatchSlotsByFlag`'s address range without a real function boundary between
them. The genuine call to `static_6_800A9ABC` lives at `funcs_27.c:107076` (`jal 0x800A9ABC`), inside
`cinematicLoopBody` (`funcs_27.c:106842`) — a *different* function from `cutsceneDispatchSlotsByFlag`,
though both are called from `cinematicLoopBody`:
- `static_6_800A9ABC` call site: `funcs_27.c:107079` — fires **once** in s334's log
  (`[static6-800a9abc-entry]`, n=1).
- `cutsceneDispatchSlotsByFlag` call site: `funcs_27.c:107938` — fires **1152+ times** in the SAME
  s334 log (`[cutscenedispatch-entry]`).

Both counters were read directly from `scratch/s73_post_a_scene/s334_maingameloop/run.log` (already on
disk, not re-run — "capture once, analyze many"). `cutsceneDispatchSlotsByFlag`'s climbing count was
always a red herring for the `runVideoFrameTick`-reachability question — it's a real, live,
continuously-invoked function, just one whose apparent call to `runVideoFrameTick` can never execute.

## New question: why does cinematicLoopBody call one callee once and the other 1152+ times?

`cinematicLoopBody` (`funcs_27.c:106842`) contains BOTH call sites, ~860 source lines apart:
- `funcs_27.c:107079` → `static_6_800A9ABC` (fires once, per s334)
- `funcs_27.c:107938` → `cutsceneDispatchSlotsByFlag` (fires 1152+ times, per s334)

Neither individual call is wrapped in a loop (s335 checked this for the `runVideoFrameTick`-adjacent
code but did NOT fully trace `cinematicLoopBody`'s own control flow around either call site or find
`cinematicLoopBody`'s own caller(s)). Two live possibilities, not yet distinguished:

1. **`cinematicLoopBody` itself is invoked once by ITS caller, but loops internally** such that the
   860-line span from 107079 to 107938 is skipped on iterations 2+ (a state-machine `goto` bypassing
   the `static_6_800A9ABC` call after the first pass), while the `cutsceneDispatchSlotsByFlag` call
   keeps being reached every iteration. This would make `cinematicLoopBody` itself the thing now
   driving the game after `mainGameLoop` parks (a live self-looping caller `mainGameLoop` doesn't own).
2. **`cinematicLoopBody` is invoked repeatedly by an outer caller** (not itself looping), and each
   invocation takes a DIFFERENT path through its body — reaching the `static_6_800A9ABC` call only on
   the very first invocation (e.g. gated by a one-shot init flag) but reaching the
   `cutsceneDispatchSlotsByFlag` call on every invocation. This would put the real "what's still
   alive" driver one level further out, in whatever calls `cinematicLoopBody`.

## The work unit

1. Read `cinematicLoopBody`'s full body (`funcs_27.c:106842` onward — find its end via
   `grep -n "^RECOMP_FUNC"` for the next function after it) to determine:
   - Is there a loop (goto-based state machine) wrapping BOTH call sites, or just one, or neither?
   - What guards the `static_6_800A9ABC` call at `funcs_27.c:107079` — a one-shot flag, an argument,
     something else? (Mirror s335's method: find the nearest enclosing `if`/label, trace what feeds
     its condition.)
2. Grep `cinematicLoopBody`'s own call site(s) in the tree (`grep -rn "cinematicLoopBody(rdram, ctx)"`)
   to find its caller(s) and whether IT is what's being invoked repeatedly (candidate: something in the
   scene/cutscene dispatch machinery, possibly a VI-retrace callback or thread separate from
   `mainGameLoop`, similar to how audio's `gfx_thread`/`task_thread`/`vi_thread` are independent OS
   threads per s330's finding).
3. This may resolve by pure source-read again (no new soak) — if it does, close the hypothesis the
   same way s335 did. If the source alone can't distinguish the two possibilities above, THEN design a
   diagnostic: an entry/exit counter at `cinematicLoopBody`'s own top plus a marker at whichever gate
   is found guarding the `static_6_800A9ABC` call, armed together in one soak (reuse
   `ROGUESQ_LOG_MAINGAMELOOP_REACH` if it's a natural fit, or open a new var — always use
   `lambda m: (...)` for `re.subn` replacements per s333's caught bug).
4. If a new soak IS needed: same setup as s329/s332/s333/s334 (gate narrowed to reverse
   `reapplyDisplayMode`'s site only, `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`,
   `HOLD_S=600`). Revert to the full force-zero baseline (`audio gate patched x2`) and rebuild clean
   before ending, per every prior session's convention.
5. Whichever hypothesis wins, close it in the same iteration and update CURRENT-TRUTH item -192 /
   add a new item.

## Environment notes (carried forward — see s327-335 for full detail)

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
- **Existing logs are reusable evidence** — s335 answered a whole hypothesis by re-grepping s334's log
  instead of re-running the soak. Check `scratch/s73_post_a_scene/<recent label>/run.log` for a
  relevant counter before spending a new build-run cycle.
- Output redirection quirks this session: bare `python3 script.py > file 2>&1` as a single Bash call
  gets flagged "Contains simple_expansion" or requires approval in compound form — safest pattern is
  `cd <dir>` as its own standalone Bash call (no compound `cd x && ...`), then the redirected command
  as a separate call with an absolute output path inside an allowed working directory.
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` — allowlisted
  verbatim.

HYPOTHESIS-ID: m5-audio-destub-cinematicloopbody-divergent-callees (1st iteration — pivoted from
`m5-audio-destub-mainGameLoop-upstream-stall`, closed s335 with a source-level proof).
