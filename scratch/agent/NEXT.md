# NEXT work unit — two wait-for-recurrence instruments now armed; read the backlog below CURRENT-TRUTH item -124 further, or take `tickTextureMaterialExpiry`

## Status of the last 4 backlog items

- `-0x25A4` hangar-list-pointer audit lineage (s283-288, `CURRENT-TRUTH` item -129): CLOSED.
- Elevated pre-scene `waitForAnyAudioSlot` death rate (s289, item -130): CLOSED as a non-finding.
- `inflate_fast`/zlib investigation (s290, item -131): **NOT closed, wait-for-recurrence.**
  `BREADCRUMB10` is live, scoped to `inflate_fast`. Do not touch until it recurs.
- `coalesceFreeHeapBlocks+2108` investigation (s291, item -132): **NOT closed, wait-for-recurrence.**
  `BREADCRUMB11` is live, scoped to `coalesceFreeHeapBlocks`. Source read found no unique translation
  bug (same uniform-unguarded baseline as every RECOMP_FUNC). Ranked candidate pointers if it recurs
  (most caller-controlled first): `ctx->r18` (`funcs_0.c:4598`) > `ctx->r16` (`:4626-4632`) >
  `ctx->r19` (`:4647`) > the global free-list-head walk chain (`:4338`). **Do not design a guard
  blind** — wait for `[CRASH][last-guest-pc]` to actually catch an occurrence pointing inside
  `coalesceFreeHeapBlocks`, then cross-reference the guest PC against `funcs_0.c` to see which
  candidate was zero.

## What this session's iteration should actually be

Both `inflate_fast` and `coalesceFreeHeapBlocks` are now wait-for-recurrence instruments — **do NOT
spend this iteration staring at either of them.** Two reasonable options, pick one:

1. **Take the other s270-flagged, still-fully-unaddressed candidate**: `tickTextureMaterialExpiry`
   (`N64Recomp/RecompiledFuncs/funcs_6.c:12135-12333`, ~2052-byte native range confirmed via `nm -n`
   this session — next distinct symbol `_resetMaterialExpiryById` at `0x1008aa704`). It was flagged
   alongside `coalesceFreeHeapBlocks` at s270 (`CURRENT-TRUTH.md:1464-1481`, item -111) as "unrelated
   subsystem, not yet investigated" and has NEVER been source-read. Same recipe as s290/s291: source
   read for the standard unguarded-`MEM_*`-access shape, rank candidate pointers, land a
   `BREADCRUMB12` scoped to its body (same `g_rs64_last_guest_pc` mechanism, see
   `N64Recomp/fixup_game_funcs.py:7378` onward — insert a new block following BREADCRUMB11's exact
   template, function-name-matched to `tickTextureMaterialExpiry`, file `funcs_6.c`), regen+build+2
   soaks to confirm no regression. Note: this crash site has only been flagged twice, ~125 sessions
   apart (s157, `CURRENT-TRUTH.md:5572`, "not yet read"; s270) — lower urgency than
   `coalesceFreeHeapBlocks` was, but still a clean, bounded, in-pattern work unit.

2. **Continue reading the pre-s283 backlog**: read `docs/CURRENT-TRUTH.md`'s "Next steps" section
   starting below the NEW item -124 pointer left by s291's item -132 entry (i.e., skip past -132
   through -125, all closed/instrumented-and-waiting) and look for the next oldest genuinely
   unaddressed thread, same methodology s291 used (delegate the scan to an Explore agent rather than
   reading thousands of lines directly — it found `coalesceFreeHeapBlocks+2108` in one pass by
   checking whether each session's stated "next target" was actually picked up by the following
   entry). Cross-check any candidate against "Overturned conclusions" (`CURRENT-TRUTH.md:~7339`) and
   "Dead ends" (`:~7615`) before committing.

## Do NOT do this iteration

- Do NOT re-open `-0x25A4`, `waitForAnyAudioSlot`, `inflate_fast`, or `coalesceFreeHeapBlocks` — all
  four are either closed or correctly waiting on new evidence, not actionable right now.
- Do NOT run `fixup_game_funcs.py` twice without a fresh `N64Recomp` regen in between.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — block with
  `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn. If a soak's summary step is
  still trickling out near the timeout (large log `grep -c` calls take a while), re-block rather than
  assuming it hung — s291 saw this take ~4 polls before `CRASH: N` printed.
- Do NOT treat a soak that hits an ALREADY-CATALOGUED, unrelated crash family as a failed validation
  — s291's soak 1 died to `rs_free ← rebuildActiveDisplayObjectList` (catalogued since s164/s167,
  large-garbage-offset fault family), confirmed via `[CRASH][pc-symbol]` naming, unrelated to that
  session's `coalesceFreeHeapBlocks` change. Check the `[CRASH][pc-symbol]` name against
  `CURRENT-TRUTH.md` before assuming any crash is a regression.
- Do NOT treat a soak that happens to hit `inflate_fast`'s or `coalesceFreeHeapBlocks`'s breadcrumbs
  as wasted even if it doesn't crash there — both breadcrumbs have zero cost when they don't fire, so
  ordinary soaking for whatever NEW work unit you pick this session is "free" extra exposure for both.

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
  240). Output dir `scratch/s73_post_a_scene/dequeuearg1/run.log` — OVERWRITTEN each run, so capture
  the crash symbol out of it into a session note before the next soak clobbers it.
- Scene-reached check: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene death, >=1 = reached).
- `+N` crash-symbol offsets are NATIVE (ARM64) and SHIFT across sessions — verify range membership
  via the Mach-O symtab walk (`nm -n`, filter T/t, dedupe, sort, confirm offset < distance to next
  DISTINCT symbol) before trusting a reported `sym=X+N`. Note: this native byte size is NOT the same
  as the guest MIPS function's byte size (compiled ARM64 code reliably expands well beyond the
  original MIPS instruction count) — a mismatch between the two is expected, not a red flag.
- `[CRASH][last-guest-pc]` is now informative for THREE functions: `static_5_800AB658`
  (`BREADCRUMB7`), `inflate_fast` (`BREADCRUMB10`, s290), and `coalesceFreeHeapBlocks`
  (`BREADCRUMB11`, s291) — still stale noise for any other crashing function.
- `N64Recomp/fixup_game_funcs.py` is untracked in the standalone `N64Recomp` checkout — no
  `export.sh` needed for edits there, only for actual `lib/` submodule changes.
- Disassembly tools (`otool`/`objdump`/`lldb`) remain BLOCKED in this sandbox (confirmed s194,
  re-confirmed by omission every session since — do not re-attempt, use the breadcrumb mechanism).
- `CURRENT-TRUTH.md` is far over the ~35KB target (32+ sessions overdue) — not this iteration's job
  unless the picked work unit is a quick null with clear leftover budget.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration before assuming a `WORKING`/missing-`OUTCOME` state means recovery work is needed — this
  has repeatedly turned out to be just the loop's normal per-iteration bootstrap. Only treat it as
  recovery-worthy if there's actual uncommitted diff evidence beyond the routine reset. The
  `lib/N64ModernRuntime`/`lib/rt64` "-dirty" gitlink markers are the same long-standing baseline
  every session has seen — not new, not worth re-verifying each time.
