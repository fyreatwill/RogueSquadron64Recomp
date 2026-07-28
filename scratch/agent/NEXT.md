# NEXT work unit — characterize the graphics-task-submission stall's trigger condition

s176 got a 2nd consecutive full-hold crash-free soak (`scenenodedepthguard2`,
exact repeat of s175's recipe) — still 0/0 on every guard in the family,
including the new `processSceneNode` depth-cap guard from s175. Per rule 8,
the crash-family-guarding line of work is now provisionally parked (2/2
clean, a 3rd identical soak has low expected value). Read PORTING-STATE
Session 176 before doing anything else; this file only has the actionable
summary.

## What s176 established (read before doing anything else)

- **2nd consecutive full-hold crash-free soak.** `scenenodedepthguard2`
  (same recipe as s175's `scenenodedepthguard1`, only the tag renamed so
  both runs' logs/screenshots survive side by side). `CRASH: 0`,
  `lle tasks: 4775`, `missing-func: 0`, `thr-resume bad=1: 0`,
  `UnhandledJump: 0`. Every guard in the family, including
  `[scene-node-depth-guard]`, is 0/0 — confirmed by grepping the raw
  run.log for every guard tag, not just the summary counters.
- **New finding: the graphics-task-submission stall (s162's -14, CURRENT-TRUTH
  line ~1048) does not only strike post-leave during the mission-intro
  cutscene.** This session's 2 runs, same recipe, produced 2 structurally
  different stall onset points:
  - `scenenodedepthguard2` (run 2) froze **before** either scripted
    leave-key press (`hold_95`/`hold_100`) executed, still inside SELECT
    YOUR CRAFT — confirmed via `[vi-fs-decision]` (last real transition at
    counter #8079, then 300 straight `stalled=1 pairs=0`) and `[phase]`
    (last width transition still `vi_width=512 origin=0x006AB400`, no
    post-leave transition ever logged). Screenshots `hold_05.png` through
    `grace_01.png` are pixel-identical.
  - `scenenodedepthguard1` (run 1, s175) froze **after** leaving, mid
    cutscene (`vi_width=640 origin=0x006A2900`, s162's cutscene origin),
    much later in the run (stall onset near counter #14528 of ~16000).
  - Surface symptom is identical both times (`stalled=1 pairs=0`, RDP `fs`
    frozen, `[lle task]`/`[rs-malloc]` still running, process alive) — only
    the onset *point* in the state machine differs. This rules out "blocked
    on a function specific to the post-dive-shot code path" as the sole
    mechanism; a scene-state-independent trigger (tick count or resource
    count) is now at least as plausible.
- 4 total stall occurrences now on record: s160, s161 (both post-leave,
  per s162), and this session's 2 runs (one post-leave, one pre-leave).

## Do next

Instrument the stall's trigger condition, correlated against **wall-clock /
tick count**, not scene state — that's the variable that's actually
different between this session's 2 runs (run 2 stalled at wall ~75-80s /
`[vi-fs-decision]` counter ~8079; run 1 stalled at wall ~140s / counter
~14528).

1. Before writing any new instrument, grep the existing `[vi-fs-decision]`
   fields (`synth=`, `skSeen=`, `skNoTrig=`, `skPair0=`) for both runs at
   their respective stall-onset lines and look for a shared threshold value
   any of those counters cross right before `stalled=1` becomes permanent —
   this needs no rebuild, just re-reading logs already captured:
   - `scratch/s73_post_a_scene/scenenodedepthguard1/run.log`
   - `scratch/s73_post_a_scene/scenenodedepthguard2/run.log`
   Look specifically at the field values on the LAST `stalled=0` line in
   each run and see whether any one field (not `rdpFs`, which differs
   between runs) is close to a common value/threshold.
2. If no shared threshold jumps out from the existing logs, the
   discriminating instrument is probably on the *producer* side (whatever
   guest code is supposed to submit the next display list task) rather than
   the `[vi-fs-decision]` consumer/gate logic already instrumented — that
   producer has never been logged. Source-read the call site that should
   submit graphics tasks during the SELECT YOUR CRAFT idle loop (likely
   somewhere in the `runHangarSelectionFrame`/`runHangarMenuFromOverlay`
   family already characterized across s84-s101) and check whether it's
   still being called after the stall onset, or has itself stopped running.
3. Discriminating outcomes:
   - **The producer call stops being invoked at all** → points to a hang/
     early-return/infinite-loop-elsewhere in guest code upstream of DL
     submission (a logic bug, not a corruption race).
   - **The producer keeps being called but its output is rejected/ignored**
     → points back into the `[vi-fs-decision]` gate logic itself (a
     threshold or state-tracking bug in the RT64-side scheduler, not guest
     code).
   - **A shared tick/counter threshold explains both runs' onset** → gives
     a concrete reproduction recipe (drive the counter to that value
     directly) instead of waiting ~75-140s of wall-clock per attempt.

## Do not

- Do not re-run the identical `scenenodedepthguard1`/`2` recipe a 3rd time
  hoping for a positive control on the depth-cap guard — 2/2 clean is
  already a reasonable stopping point per rule 8, and the more
  information-rich next step is the stall characterization above.
- Do not assume the stall is "the same bug" across all 4 known occurrences
  just because the surface symptom matches — s176's own finding is that the
  onset *point* differs meaningfully; treat "one shared mechanism" as an
  unconfirmed hypothesis until a shared trigger is actually found.
- Do not conclude the crash family is fully closed — 2/2 clean soaks is
  probabilistic support, not proof, and this whole project's history is
  full of soaks that survive one recipe and then crash on the very next
  identical run.

## Blocking on a long-running soak (learned the hard way, still current)

Simplest approach: run the driver script itself as a single foreground Bash
call with output redirected to a log file and a generous timeout (~480s
covers this env block's 120s hold + overhead) — the script blocks until the
game process exits, no polling loop needed. If it exceeds the foreground
timeout, the harness moves it to background automatically and notifies on
completion — do not sleep-poll in the meantime, just wait for the
notification.

## This session's environment notes (carry forward, still current)

- Re-running the same script/tag **overwrites** the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak
  (e.g. `scenenodedepthguard2` from `scenenodedepthguard1`) so each soak's
  full run.log and screenshots land in their own directory, never
  overwritten. This is now the established convention going forward, not
  just a one-off workaround.
- Running `N64Recomp/build/N64Recomp` or any script under
  `RogueSquadron64Recomp/tools/agent/*.sh` / `scratch/agent/*.sh` directly
  gets denied even though the text matches an allowlisted prefix —
  prefix with `zsh` (already allowlisted).
- Compound `cd ... && zsh ... > file 2>&1` gets denied — call
  `zsh /absolute/path/to/script.sh > /absolute/path/to/log 2>&1` directly,
  no `cd`, the script `cd`s internally. Same for `cd ... && cmake ...` —
  use `cmake --build /absolute/path/to/build` instead of `cd`+relative.
  Same for chaining a 2nd command after any of these with `;` or `&&` —
  each Bash call should be a single command; run follow-ups as separate
  calls (including a trailing `echo` after a redirected command — that
  also counts as a 2nd operation and gets denied).
- Same for `python3 fixup_game_funcs.py` — it uses an absolute
  `pathlib.Path("/Users/.../N64Recomp/RecompiledFuncs")` internally, so it
  can be invoked as `python3 /absolute/path/to/fixup_game_funcs.py > log`
  with no `cd` at all, sidestepping the compound-cd-redirect denial
  entirely.
- **CRITICAL: `fixup_game_funcs.py` is non-idempotent** — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. Redirect to a log file on the ONE invocation, and grep
  the log for your new patch's report lines to confirm exactly x1 before
  moving on.
- If only `fixup_game_funcs.py`/a `lib/rt64` or `N64ModernRuntime` C++ file
  changed (not symbol files or the ELF), you don't need `make_elf.py` —
  for guest-code fixup changes: `N64Recomp` (via
  `zsh tools/agent/regen_n64recomp.sh`) then `fixup_game_funcs.py` once,
  then `cmake --build`. For pure host/runtime C++ changes: just
  `cmake --build`, no regen needed at all.
- Before writing ANY new patch to `fixup_game_funcs.py`, grep for the
  exact anchor text's uniqueness both within the target file and (if using
  a short/generic snippet) across the whole `RecompiledFuncs/` tree —
  s100's `composeNpcOrientationMatrix` guard and s175's own
  `processSceneNode` entry-anchor both needed widening from a 1-2 line
  match to a longer, uniquely-identifying one after a collision was found.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py` for Mach-O symbol reads (gives function
  sizes via symtab sort, NOT disassembly — it cannot map a crash's byte
  offset back to a source line; only a full source read can locate the
  actual fault site within a large function).
- Reading a `RECOMP_FUNC` body directly from
  `N64Recomp/RecompiledFuncs/funcs_*.c` (via `grep -n "RECOMP_FUNC void
  <name>"`) is far more reliable than trusting a `symbol_files/*.txt`
  comment.
- `git -C <path> ...` (with the `-C` flag) triggers an approval prompt even
  for read-only commands like `status`/`show` — plain `git <cmd>` from the
  correct cwd, or a separate `cd` call first, avoids it.
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns.
- Output redirection (`>`) from Bash is sandboxed to the session's allowed
  working directories — target `scratch/agent/`, never `/tmp`.
- `cmake --build` needs
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`; pass the
  build dir as an argument (`cmake --build /abs/path/to/build`) rather than
  `cd`-ing there, to avoid the compound-cd-redirect denial.
- `lib/N64ModernRuntime` and `lib/rt64` always show as "modified content"
  in the parent repo's `git status` — normal, long-standing state. Only run
  `submodule-patches/export.sh` + commit if you actually edit something
  under `lib/` this session (s175/s176 did NOT touch `lib/`).
- `/scratch/` is entirely gitignored in this repo except 3 force-tracked
  files: `scratch/agent/NEXT.md`, `OUTCOME`, `STATUS`. New soak
  scripts/logs under `scratch/agent/` or `scratch/s73_post_a_scene/` never
  need `git add` — they're intentionally untracked.
- A `grep -c "[pattern]"` across a very large run.log (millions of lines
  from a per-tick instrument like `[rs-malloc-walk]`) is fine and fast —
  no need to avoid grepping big log files, just don't `cat`/`Read` them
  wholesale.
- When a soak survives the full hold window, `run_mission_keys.sh`'s
  summary line `UnhandledJump: N` can be nonzero from totally benign RSP
  microcode fallback noise (`Unhandled jump target 0x17F0`/`0x0231` "in
  microcode factor5_ucode") — grep the actual matched lines before reading
  a nonzero count as a regression; it is NOT the same thing as a guest-CPU
  `UnhandledJumpTarget`.
- Screenshots (`hold_NN.png`, `grace_NN.png`, `craft_stable.png`) are
  genuinely useful for characterizing a "process alive but stuck" state —
  reading a handful of them directly (via the Read tool, not a subagent)
  is cheap and found this session's main new finding. Compare the SAME
  tick number across two runs, and compare a late-hold frame against the
  run's own `craft_stable.png`/early frames to spot exactly when a run
  visually froze, not just whether it eventually froze.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target — migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-176
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
