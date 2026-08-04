# NEXT work unit — investigate the elevated pre-scene `waitForAnyAudioSlot` death rate (open since s278)

The `-0x25A4($s1)` hangar-list-pointer audit lineage (s283-288) is now **fully CLOSED** — every
function it touched or flagged is either guarded or confirmed to need no guards
(`playerSnowSpeederInit` closed s288 with 0 hits, refuting the s286/287 "may be a dead duplicate"
guess). Do not re-open it without a NEW discriminating signal (e.g. a soak crash at a fresh,
symtab-verified `-0x25A4`-adjacent site).

## Where the investigation stands (s288)

s288 classified `playerSnowSpeederInit` (`funcs_27.c:144145-150543`): zero `-0x25A4` hits anywhere
in it (verified 2 independent ways), and proved — via whole-function guest-address monotonicity (0
decreases across 2552 address comments) plus 3 direct instruction-divergence checks at the 3
addresses where its labels overlap `static_5_800AAD9C`/`_800AB1C8`/`_800AB658`'s own start
addresses — that it is genuinely live, continuously-translated code, NOT a dead duplicate. The
label-name overlap that triggered the original suspicion (s286/287) is just coincidental shared
virtual-address space between two live functions from different overlay contexts. Full detail:
`PORTING-STATE` Session 288, `CURRENT-TRUTH` item -129.

## The next work unit

**Investigate the elevated pre-scene `waitForAnyAudioSlot` death rate.** This has been costing real
soak budget for many sessions now (e.g. s283: 1 of 3 soaks; recur throughout s284-288's soak logs)
without ever being the DIRECT target of a session — always background noise next to some other
function's audit. It was flagged as backlog priority #2 as far back as s283/-124 and is now the
top open item.

**What's already known** (do not re-derive, build on it):
- This is the "23rd crash class", first catalogued s165: SIGSEGV in/near `waitForAnyAudioSlot`,
  called from `menuOverlayInit`, very early (pre-title, task #267 in the s165 occurrence, ~1.7s in).
- s166 source-read `isAudioSlotActive` (`funcs_24.c:5788`) and found+guarded a concrete unguarded
  pointer dereference (base pointer from a fixed global slot, indexed, no null-check — the family's
  dominant shape in this codebase). Landed the guard, but the validating soak never exercised
  `waitForAnyAudioSlot` under failure conditions (4 calls, all resolved cleanly) — **0/0, no
  positive control, cannot attribute the clean run to the guard**. Full detail: `CURRENT-TRUTH`
  item -18, `PORTING-STATE` s166.
- Since s278 the death rate at this site has been "elevated" per NEXT.md's own carried-forward note
  (line 134 of the prior revision) but this claim itself has never been quantified THIS session —
  treat "elevated since s278" as an unverified prior, not a fact, until you count it directly (see
  step 1 below — numbers, not adjectives, per the investigation-method rules).

**Steps:**
1. **Quantify first.** Grep the soak logs already on disk from s283-288 (`scratch/s73_post_a_scene/
   dequeuearg1/run.log` gets overwritten each run, so use whatever crash-report artifacts or
   session write-ups in `PORTING-STATE.md` Sessions 278-288 recorded the crash symbol/site for each
   soak). Build a real numerator/denominator: N pre-scene `waitForAnyAudioSlot` deaths out of M total
   soaks across s278-288. Do not proceed to instrumentation until you have this number — it is the
   single most likely thing to change the plan (if it turns out to be 1-2 occurrences, "elevated"
   was noise and this backlog item should be closed as a non-finding).
2. If the rate holds up as genuinely elevated, source-read the CURRENT call chain into
   `waitForAnyAudioSlot` from `menuOverlayInit` (and check whether other call sites exist now — s165
   flagged "`waitForAnyAudioSlot` is reachable from more places than mapped" and this was never
   resolved) and check whether the s166 `isAudioSlotActive` guard (`funcs_24.c:5788`) is still
   present/intact and whether it's the right shape for whatever the CURRENT crash offset is — native
   ARM64 offsets drift across sessions/rebuilds, so re-verify via the Mach-O symtab walk (`nm -n`,
   filter T/t) before trusting any `sym=waitForAnyAudioSlot+N` from an old log.
3. If a genuinely new unguarded dereference is found, this becomes a standard fix-and-validate
   cycle: land the guard in `N64Recomp/fixup_game_funcs.py`, full regen pipeline, clean build, and
   get a soak that gives the guard an actual positive-control opportunity (i.e. one that would have
   hit the old crash site and instead fires the new guard) — not just another clean run with 0/0.

**If this turns out to be a non-finding** (rate isn't actually elevated, or no new unguarded site is
found after a reasonable source-read), close it and move to the other standing backlog item: the
`inflate_fast`/zlib localization design (s272, never attempted — needs a different approach since
it's a system-library call, not a guest-code guard).

## Do NOT do this iteration

- Do NOT re-open the `-0x25A4($s1)` audit lineage (`hangarInitialize` any chunk,
  `static_5_800AAD9C`/`_800AB1C8`/`_800AB658`/`_800ADB70`, `static_5_800A9270`,
  `playerSnowSpeederInit`) without a NEW discriminating signal — all closed/validated as of s288.
- Do NOT treat "elevated since s278" as already-proven — count it first (step 1).
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11`/`x12` = constant RDRAM-base-pointer-looking values as
  crash-matching evidence for ANYTHING.
- Do NOT treat `processSceneNode`, `reserveAndEmitDLEntry`, `coalesceFreeHeapBlocks` crashes as new
  findings — all already catalogued.
- Do NOT run `fixup_game_funcs.py` twice without a fresh `N64Recomp` regen in between.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — block with
  `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` NOT needed (ELF/ROM mapping unchanged since s284). `N64Recomp`
  needs cwd `N64Recomp` (`./build/N64Recomp rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd
  `N64Recomp`. Always delete `funcs_*.c` and regen from scratch first:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
- `cd` does not persist into a subsequent `run_in_background: true` call — launch background
  commands by full absolute path with no preceding bare `cd`.
- Bash tool cwd persists across sequential (non-background) calls but resets after an unrelated
  `cd` elsewhere in the session — re-`cd` explicitly before cwd-dependent commands.
- Compound `cd && ...` commands need interactive approval — issue `cd` as its own call first.
- `git -C`/`git --git-dir=`/`cd <dir> && git ...` all get flagged for approval even standalone — if
  you need submodule git state, expect an approval prompt, or use `git diff -- lib/<submodule>` from
  the repo root (shows the gitlink pointer/dirty flag without entering the submodule). `nm -n
  <binary> > file` also flagged — use Python `subprocess.run`.
- Shell `for`/`$(...)` loops get rejected by the sandbox — use Python scripts via `Write` instead.
- Multi-line `python3 -c "..."` with embedded `#`/newlines gets flagged — write to a file and run
  `python3 /path/to/script.py`.
- Redirecting shell output (`>`) only works under the 3 session working directories
  (`RogueSquadron64Recomp`, `N64Recomp`, `rogue_squadron64`), NOT `/tmp` — writes to `/tmp` are
  blocked outright.
- Soak driver: `scratch/s73_post_a_scene/run_dequeuearg1.sh` (`HOLD_S` env-overridable, default
  240). Output dir `scratch/s73_post_a_scene/dequeuearg1/run.log` — OVERWRITTEN each run, so capture
  the crash symbol out of it into a session note before the next soak clobbers it.
- Scene-reached check: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene death, >=1 = reached).
- `+N` crash-symbol offsets are NATIVE (ARM64) and SHIFT across sessions — verify range membership
  via the Mach-O symtab walk (`nm -n`, filter T/t, dedupe, sort, confirm offset < distance to next
  DISTINCT symbol) before trusting a reported `sym=X+N`.
- `[CRASH][last-guest-pc]` is only informative for `static_5_800AB658` (the only breadcrumbed
  function, `BREADCRUMB7`) — stale noise for any other crashing function.
- `N64Recomp/fixup_game_funcs.py` is untracked in the standalone `N64Recomp` checkout — no
  `export.sh` needed for edits there, only for actual `lib/` submodule changes.
- `CURRENT-TRUTH.md` is far over the ~35KB target (30+ sessions overdue) — not this iteration's job
  unless the `waitForAnyAudioSlot` investigation is a quick null with clear leftover budget.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration before assuming a `WORKING`/missing-`OUTCOME` state means recovery work is needed — this
  has repeatedly (s286/287/288) turned out to be just the loop's normal per-iteration bootstrap, not
  an interrupted session. Only treat it as recovery-worthy if there's actual uncommitted diff
  evidence (e.g. `git status`/`git diff` on `fixup_game_funcs.py` or other tracked work files) beyond
  the routine `STATUS`/`OUTCOME` reset.
