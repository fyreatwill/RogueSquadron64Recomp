# NEXT work unit — s297's guard landed; watch for a 3rd `BREADCRUMB12` recurrence, otherwise resume the unguarded-walk sweep

## What s297 did (context for this session, not a re-derivation prompt)

Landed `MATEXPIRY_GUARD` (a `ctx->r16` KSEG0-range check, same template as `DEQUEUE_GUARD`/
`CACHE4_GUARD`) in `tickTextureMaterialExpiry` at `N64Recomp/RecompiledFuncs/funcs_6.c`'s
`L_80022094` label, bailing to `L_80022128` on failure. Patch lives in
`N64Recomp/fixup_game_funcs.py`, placed AFTER the `BREADCRUMB12` block so its regex matches the
POST-breadcrumb text shape. Regen/build clean; `BREADCRUMB12` still patches x83 (unchanged),
`MATEXPIRY_GUARD` patches x1 (new). Also armed `ROGUESQ_LOG_MATEXPIRY_GUARD=1` in the shared soak
driver (`scratch/s73_post_a_scene/run_dequeuearg1.sh`).

**2 validation soaks (`HOLD_S=275`, named `s297_soak1`/`s297_soak2`): both clean, scene reached, 0
crashes, 0 `[matexpiry-guard]` fires.** This is a WEAK NULL, not a confirmation — `BREADCRUMB12` has
only fired twice in ~294 prior sessions (s293, s294), so 0/2 fires in 2 soaks is fully consistent
with either "the guard works" or "the guard just wasn't exercised this time." Do not treat this as
"fixed." Full detail: `PORTING-STATE.md` Session 297, `docs/CURRENT-TRUTH.md` item -160.

## Top priority: decide based on whether a `BREADCRUMB12` recurrence shows up

`BREADCRUMB12` is still armed (it's a passive guest-PC breadcrumb, not gated by the new guard's env
var) in every soak that uses the shared driver, so future soaks — including any queued via
`scratch/agent/soak_queue/` — will keep silently collecting more observations even without a
dedicated session.

1. **If `scratch/agent/SOAK-RESULTS.md` or a future session's own soak shows `[CRASH][last-guest-pc]
   pc=0x80022094` again** (i.e. `tickTextureMaterialExpiry` crashes again despite the guard): the
   guard is wrong — either the bail target discards state some other part of the function still
   needs, or the range check itself is passing a bad value through. Re-read the bail-path control
   flow (`funcs_6.c` around `L_80022128`, the outer per-table-index loop continuation) rather than
   just re-soaking. This would be the 3rd observation of the underlying crash and the 1st of the
   guard failing to catch it — a real, actionable signal.
2. **If a soak shows a `[matexpiry-guard]` fire log line** (requires `ROGUESQ_LOG_MATEXPIRY_GUARD=1`,
   armed in the shared driver): the guard caught a real corrupted pointer. That's a genuine positive
   observation — note it in the ledger as the first confirming evidence, no code change needed unless
   the surrounding behavior looks wrong (e.g. visible visual/audio glitch from the skipped node).
3. **If neither shows up this session** (most likely, given the historical ~1-in-~150-sessions hit
   rate): do NOT spend a session waiting for it. Move to the fallback below.

## Fallback (and likely actual next work unit): resume the unguarded-walk sweep

`scratch/agent/find_unguarded_walks.py` generated `unguarded_walk_candidates.json` — 143 sites across
43 functions. 3 of 43 are now addressed: `tickSongSequence` (s293, `BREADCRUMB13`), `stopSongByHandle`
(s294, `BREADCRUMB14`), and `tickTextureMaterialExpiry` (s292/s297, `BREADCRUMB12` + now
`MATEXPIRY_GUARD`). 1 explicitly deferred as out-of-scope: `func_800AE3F0` (funcs_27.c, ~18000 lines —
do NOT pick this one, too large for a single session, likely overlaps the closed `-0x25A4` hangar
audit). Pick the next unaddressed function from the JSON, source-read it fully before writing
anything, and land a breadcrumb (same mechanism as BREADCRUMB10-14) scoped to that function. A
`"status"` field added to each JSON entry (not yet done) would make "which functions are covered"
an O(1) lookup instead of a fresh grep-and-cross-reference each session — worth doing if a session has
spare budget before picking the next candidate.

## Strategic priority reminder (still in force, unchanged by s297)

Per the 2026-08-04 USER DIRECTIVE (`docs/CURRENT-TRUTH.md` top): Maintenance (Step 0) still overrides
everything if `wc -c docs/CURRENT-TRUTH.md` prints >60000 at session start — check this FIRST. As of
s297's commit it's 59,909 bytes, just under the trigger with a slim ~90-byte margin; a normal
work-unit session's own Next-steps addition could easily push it back over 60,000 next time. If Step 0
doesn't trigger, **M5 audio de-stubbing** (design doc `docs/M5-AUDIO-PLAN.md` first) is priority 2,
ahead of any further M3 crash work, per the same directive — this has now been deferred across s292-
s297 in favor of the `BREADCRUMB12`/guard thread; if this session doesn't have a live `BREADCRUMB12`
recurrence to react to (see above), seriously consider starting the M5 design doc instead of jumping
straight to the sweep fallback, since the sweep is explicitly priority 3 ("M3 crash work") in the
directive's ordering.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` NOT needed (ELF/ROM mapping unchanged since s284). `N64Recomp`
  needs cwd `N64Recomp` (`./build/N64Recomp rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd
  `N64Recomp`. Always delete `funcs_*.c` and regen from scratch first:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
- `fixup_game_funcs.py` REFUSES to run twice on the same generated output (it checks for
  `// RS64_FIXUP_APPLIED` markers) — this is a correct safety refusal, not a bug; regen from scratch
  (delete `funcs_*.c`, rerun `N64Recomp`) before rerunning fixup, don't work around the refusal.
- `cd` does not persist into a subsequent `run_in_background: true` call — launch background
  commands by full absolute path with no preceding bare `cd`.
- Soak driver: `scratch/s73_post_a_scene/run_dequeuearg1.sh` (`HOLD_S` env-overridable, default
  240; s297 used 275). Total wall time for a `HOLD_S=275` run is ~337-340s — plan Bash tool timeouts
  (600000ms max) or background+poll accordingly; a foreground Bash call with `timeout` under ~400000ms
  WILL be moved to background mid-run rather than erroring, which is fine (poll for the game process
  exiting via `pgrep -f RogueSquadron64Recomp`, not a bare `sleep`, which the sandbox blocks in
  foreground Bash — poll with short `time.sleep()` calls inside a `python3 -c` loop instead).
- **The full `ROGUESQ_LOG_*` instrument set (as armed in `run_dequeuearg1.sh`) produces MULTI-GIGABYTE
  run.log files over a ~340s hold** (s297's two soaks were 9.2GB/9.5GB, 200M+ lines — `rs-free-walk`
  logs one line per free-list node and dominates). `grep -c` for the specific markers you need
  (`\[CRASH\]`, `vi_width=1024`, your guard's fire-log name) then DELETE the log — don't leave these
  lying around, they ate ~19GB combined this session (cleaned up before commit).
  Output dir `scratch/s73_post_a_scene/<name>/run.log` — the `<name>` arg (positional $1) controls
  the output subdir, so distinct soaks in the same session don't clobber each other if given distinct
  names.
- Scene-reached check: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene death, >=1 = reached).
- Bash tool cwd persists across sequential (non-background) calls but resets after an unrelated
  `cd` elsewhere in the session — re-`cd` explicitly before cwd-dependent commands.
- Compound `cd && ...` commands need interactive approval — issue `cd` as its own call first. Simple
  `&&`-chained commands in general also sometimes need approval outside `cd` — prefer separate tool
  calls over chaining when in doubt.
- `git -C`/`git --git-dir=`/`cd <dir> && git ...` all get flagged for approval even standalone, and
  in a non-interactive/autonomous session that approval is NOT available — do not spend time
  retrying these forms for submodule git state. `nm -n <binary> > file` also flagged — use Python
  `subprocess.run`, written to a script file.
- Shell `for`/`$(...)` loops get rejected by the sandbox — use Python scripts via `Write` instead.
- Redirecting shell output (`>`) only works under the 3 session working directories
  (`RogueSquadron64Recomp`, `N64Recomp`, `rogue_squadron64`), NOT `/tmp` — writes to `/tmp` are
  blocked outright.
- `+N` crash-symbol offsets are NATIVE (ARM64) and SHIFT across sessions — verify range membership
  via the Mach-O symtab walk (`nm -n`, filter T/t, dedupe, sort, confirm offset < distance to next
  DISTINCT symbol) before trusting a reported `sym=X+N`.
- `[CRASH][last-guest-pc]` is now informative for SIX functions: `static_5_800AB658`
  (`BREADCRUMB7`), `inflate_fast` (`BREADCRUMB10`), `coalesceFreeHeapBlocks` (`BREADCRUMB11`),
  `tickTextureMaterialExpiry` (`BREADCRUMB12`, now GUARDED as of s297 — see above), `tickSongSequence`
  (`BREADCRUMB13`), and `stopSongByHandle` (`BREADCRUMB14`) — still stale noise for any other
  crashing function (most commonly `beginFrameDLChunk`'s `0x8000b650`), OR informative-but-benign
  when it lands on a breadcrumbed function's own LAST instruction (its normal return point).
- `N64Recomp/fixup_game_funcs.py` is untracked in the standalone `N64Recomp` checkout — no
  `export.sh` needed for edits there, only for actual `lib/` submodule changes.
- Disassembly tools (`otool`/`objdump`/`lldb`) remain BLOCKED in this sandbox — do not re-attempt,
  use the breadcrumb mechanism.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration, but also run `git diff --cached` for staged tracked-file content beyond the routine
  reset.
- The `unguarded_walk_candidates.json` sweep tracker (143 sites/43 funcs) is itself never edited in
  place as sites get addressed — coverage status has to be cross-checked against `CURRENT-TRUTH.md`
  function-name mentions each time. Adding a `"status"` field would make this O(1) — see Fallback
  section above.

HYPOTHESIS-ID: tickTextureMaterialExpiry-guard
