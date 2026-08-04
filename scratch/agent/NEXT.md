# NEXT work unit — tickSongSequence closed to armed; pick the sweep or campose8/9 next

## Status of the last 6 backlog items

- `-0x25A4` hangar-list-pointer audit lineage (s283-288, `CURRENT-TRUTH` item -129): CLOSED.
- Elevated pre-scene `waitForAnyAudioSlot` death rate (s289, item -130): CLOSED as a non-finding.
- `inflate_fast`/zlib investigation (s290, item -131): **NOT closed, wait-for-recurrence.**
  `BREADCRUMB10` is live, scoped to `inflate_fast`. Do not touch until it recurs.
- `coalesceFreeHeapBlocks+2108` investigation (s291, item -132): **NOT closed, wait-for-recurrence.**
  `BREADCRUMB11` is live, scoped to `coalesceFreeHeapBlocks`.
- `tickTextureMaterialExpiry` investigation (s292/s293, item -133/-134): **NOT closed,
  wait-for-recurrence, but now has ONE real data point.** `BREADCRUMB12` is live. s293's soak 2
  caught an actual recurrence: `[CRASH][last-guest-pc]=0x80022094`, confirmed inside
  `tickTextureMaterialExpiry`'s guest range at `funcs_6.c:12207` (`lhu $v1, 0x8($s0)`, dereferences
  `ctx->r16`, the walked list-node pointer — matches s292's #1-ranked candidate exactly). **This is
  1 observation, not the 2-independent-observations bar** — do NOT land a guard off this alone. If
  a 2nd recurrence lands at or near the same guest PC, that's the trigger to guard `ctx->r16` at
  that offset.
- `tickSongSequence` investigation (s293, item -134): **NOT closed, wait-for-recurrence.**
  `BREADCRUMB13` is live, scoped to `tickSongSequence`. Ranked candidates if it recurs: `ctx->r18`
  (`funcs_25.c:5018`, computed table-entry pointer) > `ctx->r16` (`funcs_25.c:5019/5039/5051/5071`,
  walked list-node pointer).

**All five of the s270-era-and-older "not yet investigated" single-function candidates are now
closed or armed wait-for-recurrence instruments.** Do NOT spend this iteration on any of them
unless `[CRASH][last-guest-pc]` lands inside one during ordinary soaking for a DIFFERENT work unit
(free bonus signal, not a reason to go looking) — except `tickTextureMaterialExpiry`, which DOES
warrant a look if `[CRASH][last-guest-pc]` fires again inside its range (see above: this would be
observation #2, crossing the confirmation bar).

## What this session's iteration should actually be

Two candidates surfaced by s293's Explore-agent backlog scan, both below `CURRENT-TRUTH` item
-124, neither in Overturned Conclusions or Dead Ends:

1. **The abandoned s249-251 project-wide unguarded-walk sweep.** `scratch/agent/find_unguarded_walks.py`
   generated `scratch/agent/unguarded_walk_candidates.json` — 143 sites across 43 functions,
   worked down to 139 by s251 (`CURRENT-TRUTH` item -92, line ~2509), then abandoned when the
   project pivoted to individual crash-lead chasing starting s253 (item -94). This is a
   **multi-session campaign**, not a single work unit — if picked, the right-sized first step is
   NOT "guard all 139," it's: read the JSON, pick the single highest-risk/most-caller-controlled
   site (or a small batch), source-read it the same way s289-293 did for single functions. Treat
   resuming the countdown as the actual deliverable, not finishing it in one session.
2. **The `campose8`/`campose9` soak discrepancy** (item -74, s233, `CURRENT-TRUTH` line ~3115) —
   a "silent vs. still-firing-with-no-new-content" difference between two display-list-payload
   staleness soaks, flagged as unexplained and never revisited after the s249 pivot. This one is
   narrower in scope than the sweep (a single open question about 2 specific old soak logs, not an
   open-ended campaign) — may be the better pick if this session wants a bounded null/positive
   result rather than opening a new multi-session thread. Read `PORTING-STATE` Session 233 for the
   original soak details before deciding whether the raw logs (`scratch/agent/campose8*`/`campose9*`
   if they still exist, or the soak driver that produced them) are even still available to compare.

Pick ONE. If neither pans out cleanly in one iteration, fall back to `unguarded_walk_candidates.json`
site #1 (whatever the JSON currently ranks first) as a concrete, boring, single-function default —
same recipe as `tickSongSequence`: source-read, determine caller-controlled vs. internally-derived
pointers, land a breadcrumb (BREADCRUMB14) if a guard can't be validated blind.

## Do NOT do this iteration

- Do NOT re-open `-0x25A4`, `waitForAnyAudioSlot`, `inflate_fast`, `coalesceFreeHeapBlocks`,
  `tickSongSequence`, or `tickTextureMaterialExpiry` (unless it gets a 2nd recurrence — see above).
- Do NOT run `fixup_game_funcs.py` twice without a fresh `N64Recomp` regen in between.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — block with
  `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn, re-block if still running.
  Check `ps aux` and log growth between polls to confirm progress, not a hang.
- Do NOT treat a soak that hits an ALREADY-CATALOGUED, unrelated crash family as a failed
  validation — check the `[CRASH][pc-symbol]` name against `CURRENT-TRUTH.md` before assuming any
  crash is a regression. s293's soak 2 hit `tickTextureMaterialExpiry` (a DIFFERENT, already-armed
  breadcrumb, not that session's own `tickSongSequence` change) and it was correctly treated as a
  bonus signal, not a regression.
- Do NOT treat a soak that happens to hit any of the 5 armed breadcrumbs' scoped functions as
  wasted even if it doesn't crash there — all 5 have zero cost when they don't fire.
- Do NOT commit staged work you did not verify — always run `git diff --cached` first even if it
  looks like routine bootstrap noise.
- Do NOT open the project-wide sweep (option 1 above) expecting to close it in one session — it is
  139 sites; treat any single-session progress on it as a partial contribution, not a completion.

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
- `git -C`/`git --git-dir=`/`cd <dir> && git ...` all get flagged for approval even standalone, and
  in a non-interactive/autonomous session that approval is NOT available — do not spend time
  retrying these forms for submodule git state; treat the dirty-submodule baseline as already-
  established fact from prior sessions instead of re-attempting to verify it each session. `nm -n
  <binary> > file` also flagged — use Python `subprocess.run`, written to a script file (embedded
  `#`/newlines in a multi-line `python3 -c` also get flagged).
- Shell `for`/`$(...)` loops get rejected by the sandbox — use Python scripts via `Write` instead.
- Redirecting shell output (`>`) only works under the 3 session working directories
  (`RogueSquadron64Recomp`, `N64Recomp`, `rogue_squadron64`), NOT `/tmp` — writes to `/tmp` are
  blocked outright.
- Soak driver: `scratch/s73_post_a_scene/run_dequeuearg1.sh` (`HOLD_S` env-overridable, default
  240). Output dir `scratch/s73_post_a_scene/<name>/run.log` — the `<name>` arg (positional $1)
  controls the output subdir, so distinct soaks in the same session don't clobber each other if
  given distinct names (s293 used `s293_soak1`/`s293_soak2`).
- Scene-reached check: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene death, >=1 = reached).
- `+N` crash-symbol offsets are NATIVE (ARM64) and SHIFT across sessions — verify range membership
  via the Mach-O symtab walk (`nm -n`, filter T/t, dedupe, sort, confirm offset < distance to next
  DISTINCT symbol) before trusting a reported `sym=X+N`.
- `[CRASH][last-guest-pc]` is now informative for FIVE functions: `static_5_800AB658`
  (`BREADCRUMB7`), `inflate_fast` (`BREADCRUMB10`), `coalesceFreeHeapBlocks` (`BREADCRUMB11`),
  `tickTextureMaterialExpiry` (`BREADCRUMB12`, now with 1 real data point — see above), and
  `tickSongSequence` (`BREADCRUMB13`, s293) — still stale noise for any other crashing function
  (most commonly `beginFrameDLChunk`'s `0x8000b650`).
- `N64Recomp/fixup_game_funcs.py` is untracked in the standalone `N64Recomp` checkout — no
  `export.sh` needed for edits there, only for actual `lib/` submodule changes.
- Disassembly tools (`otool`/`objdump`/`lldb`) remain BLOCKED in this sandbox — do not re-attempt,
  use the breadcrumb mechanism.
- `CURRENT-TRUTH.md` is far over the ~35KB target (34+ sessions overdue) — not this iteration's
  job unless the picked work unit is a quick null with clear leftover budget.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration, but also run `git diff --cached` for staged tracked-file content beyond the routine
  reset (s292 found a genuine case of this from s291; s293 found nothing to recover).
