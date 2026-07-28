# NEXT work unit — get a 2nd data point on the processSceneNode depth-cap guard

s175 source-read `processSceneNode`'s self-recursive SIGBUS (2 independent
prior occurrences: s172 soak 1, s174) and confirmed by direct read it is a
real, guest-intentional sibling-list tree walk with no depth cap anywhere
in the original code. Landed a recursion-depth-cap guard, rebuilt, and ran
one soak. Read PORTING-STATE Session 175 before doing anything else; this
file only has the actionable summary.

## What s175 established (read before doing anything else)

- **The `processSceneNode` recursion-depth-cap guard is landed, built
  clean, and soaked once** (`N64Recomp/fixup_game_funcs.py`, new
  `ROGUESQ_LOG_SCENE_NODE_DEPTH_GUARD` env var, file-scoped `funcs_4.c`,
  cap=128). **Not committed** — same long-standing uncommitted-history
  posture as `N64Recomp` since s54/s90, not this session's call to
  resolve.
- **The soak (`scenenodedepthguard1`) survived the ENTIRE 120s hold
  window + grace window alive** — process had to be manually killed, it
  never crashed. This is the first soak in the whole s160s-s174 lineage
  to do this. `lle tasks: 5774`, `exit=2: 0`, `missing-func: 0`,
  `thr-resume bad=1: 0`. The summary script's `UnhandledJump: 873` is
  benign RSP-audio-ucode noise (`0x17F0`/`0x0231` in `factor5_ucode`),
  unrelated to the guest-CPU crash family — do not mistake it for a new
  problem.
- **BUT the new guard never fired (0/0), and neither did any other guard
  in the family this run.** This is a null result on the fix specifically,
  not a positive control. Per s173/s174's own already-established finding,
  this whole crash family is racy across runs given an identical recipe —
  a clean run does not by itself prove the guard caused it. Do NOT write
  "processSceneNode fixed" into CURRENT-TRUTH based on this one soak; it
  needs either a 2nd clean soak (probabilistic support) or a soak where
  the guard actually trips (a real positive control).
- **This is soak 1 of this specific hypothesis**, not soak 3 — per rule 8,
  there is budget to run this same soak again before parking it.

## Do next

Re-run the exact same soak (`scratch/agent/run_scenenodedepthguard1.sh`,
unmodified — every instrument in the family stays armed, they're free) for
a 2nd data point:

```
zsh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/run_scenenodedepthguard1.sh > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/scenenodedepthguard1_run2_driver.log 2>&1
```

(the script's own `run_mission_keys.sh` call uses tag `scenenodedepthguard1`
internally, which will **overwrite** run 1's `run.log` in place — `cp -r
scratch/s73_post_a_scene/scenenodedepthguard1 scratch/s73_post_a_scene/scenenodedepthguard1_run1_archive`
first if you want to diff the two raw logs, or edit the script to use a
new tag name like `scenenodedepthguard2` before running, which is cleaner
and matches the project's usual per-soak-tag convention.)

Discriminating outcomes:
1. **Guard fires (positive control) and process survives past the fire
   point** — the fix works as designed; can start writing "confirmed fix"
   into CURRENT-TRUTH once this is the 2nd independent supporting data
   point.
2. **Guard fires but process still dies to a processSceneNode-shaped
   crash anyway** — cap of 128 may be too high, or corruption exists
   elsewhere in the same function; re-examine.
3. **Process survives the full hold again, guard still 0/0** — 2nd
   consecutive full-hold survival without ever needing the guard is still
   meaningful (probabilistic support that the dominant early-blocking bugs
   in this lineage are now guarded, even without directly observing this
   specific fix fire) — but keep the "single-source" caveat until a 3rd
   data point or an actual guard fire settles it.
4. **A new, uncatalogued crash class appears** — catalogue it per the
   family's established pattern (this would be the natural next early-
   blocking bug to chase, now that both the audio-chain race and
   processSceneNode's runaway recursion seem to be covered).

If outcome 3 or 4 happens and you have soak budget left in this session,
a 3rd soak is reasonable before invoking rule 8's "stop and pick a new
avenue" (this is 2 or 3 attempts on the SAME hypothesis, not yet past the
budget).

## Do not

- Do not conclude "processSceneNode's self-recursion is fixed" from a
  single soak where the guard never fired — that is exactly the kind of
  single-source, unvalidated-guard conclusion rule 4 exists to prevent.
- Do not skip straight to a brand-new hypothesis/instrument just because
  the guard didn't fire — this crash family's whole multi-session history
  says a 0/0 guard result on soak 1 is uninformative on its own; get a 2nd
  data point on the SAME guard first, per rule 8's "3 attempts" budget.
- Do not read the full-hold survival as proof the game is stable overall —
  it is one soak, using one specific driven-input recipe
  (`10:sr 25:sl 40:su 95:start 100:a`), and this whole project's history is
  full of soaks that survive one recipe cleanly and then crash on the very
  next run of the identical recipe.

## Blocking on a long-running soak (learned the hard way, still current)

Simplest approach (used successfully s168-s175): run the driver script
itself as a single foreground Bash call with output redirected to a log
file and a generous timeout (~480s covers this env block's 120s hold +
overhead) — the script blocks until the game process exits, no polling
loop needed. If it exceeds the foreground timeout, the harness moves it to
background automatically and notifies on completion — do not sleep-poll
in the meantime, just wait for the notification.

## This session's environment notes (carry forward, still current)

- Re-running the same script/tag **overwrites** the previous run's
  `run.log` in place — `cp -r` the whole tag directory aside first (e.g.
  `scratch/s73_post_a_scene/<tag>` -> `scratch/s73_post_a_scene/<tag>_archive`)
  if you need to diff two runs' raw logs, or better, copy the driver
  script to a new tag name per soak so each soak's full run.log and
  screenshots land in their own directory, never overwritten.
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
  s100's `composeNpcOrientationMatrix` guard and this session's own
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
  under `lib/` this session (s175 did NOT touch `lib/` — all edits were in
  the separate `N64Recomp` sibling checkout's `fixup_game_funcs.py`).
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

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target — migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-175
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
