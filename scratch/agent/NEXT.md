# NEXT work unit — all 4 s270-era backlog items now closed or armed; read the pre-s283 backlog below CURRENT-TRUTH item -124

## Status of the last 5 backlog items

- `-0x25A4` hangar-list-pointer audit lineage (s283-288, `CURRENT-TRUTH` item -129): CLOSED.
- Elevated pre-scene `waitForAnyAudioSlot` death rate (s289, item -130): CLOSED as a non-finding.
- `inflate_fast`/zlib investigation (s290, item -131): **NOT closed, wait-for-recurrence.**
  `BREADCRUMB10` is live, scoped to `inflate_fast`. Do not touch until it recurs.
- `coalesceFreeHeapBlocks+2108` investigation (s291, item -132): **NOT closed, wait-for-recurrence.**
  `BREADCRUMB11` is live, scoped to `coalesceFreeHeapBlocks`. Ranked candidates if it recurs (most
  caller-controlled first): `ctx->r18` (`funcs_0.c:4598`) > `ctx->r16` (`:4626-4632`) > `ctx->r19`
  (`:4647`) > global free-list-head walk chain (`:4338`).
- `tickTextureMaterialExpiry` investigation (s292, item -133): **NOT closed, wait-for-recurrence.**
  `BREADCRUMB12` is live, scoped to `tickTextureMaterialExpiry`. Only 1 candidate if it recurs (this
  function takes no caller-supplied pointers at all): `ctx->r16` (`funcs_6.c:12174`, the node pointer
  walked from the global slot table).

**All four of the s270-era "not yet investigated" candidates are now closed or armed
wait-for-recurrence instruments.** Do NOT spend this iteration on any of them unless
`[CRASH][last-guest-pc]` actually lands inside one during ordinary soaking for a DIFFERENT work unit
(free bonus signal, not a reason to go looking).

## Recovery note (read this before assuming a `WORKING`/no-`OUTCOME` state needs action)

s291's session did real, complete, validated work (source read, `BREADCRUMB11`, 2 clean soaks) but its
`git commit` never ran before the loop turn ended — the changes sat staged in the index across s292's
bootstrap. s292 caught this via `git status`/`git diff --cached` (staged changes beyond the routine
`STATUS`/`OUTCOME` reset — actual doc content matching a full session's work) and committed it
(`26e286c`) before starting its own work. If you see something similar — staged, coherent,
multi-file doc changes at session start that read like a finished session, not a partial fragment —
verify with `git diff --cached` and commit it before proceeding, rather than re-doing or discarding it.
This is different from the routine `scratch/agent/STATUS`=`WORKING`/`OUTCOME`-deleted bootstrap noise,
which is NOT recovery-worthy on its own (unstaged, no tracked-file content).

## What this session's iteration should actually be

Read `docs/CURRENT-TRUTH.md`'s "Next steps" section starting below item -124 (i.e., skip past -133
through -125, all closed/instrumented-and-waiting) and look for the next oldest genuinely unaddressed
thread. Same methodology s291 used successfully: **delegate the scan to an Explore agent** rather than
reading thousands of lines directly — it found `coalesceFreeHeapBlocks+2108` in one pass by checking
whether each session's stated "next target" was actually picked up by the following entry. Cross-check
any candidate against "Overturned conclusions" (`CURRENT-TRUTH.md:~7339`, line numbers have shifted
since s292's inserts — grep for the header) and "Dead ends" (`:~7615`, same caveat) before committing
to it.

This backlog has been pointed at repeatedly (s291, and now s292) without being read — treat picking
something from it as this session's actual job, not an afterthought.

## Do NOT do this iteration

- Do NOT re-open `-0x25A4`, `waitForAnyAudioSlot`, `inflate_fast`, `coalesceFreeHeapBlocks`, or
  `tickTextureMaterialExpiry` — all five are either closed or correctly waiting on new evidence, not
  actionable right now.
- Do NOT run `fixup_game_funcs.py` twice without a fresh `N64Recomp` regen in between.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — block with
  `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn. If a soak's summary step is
  still trickling out near the timeout (large log `grep -c` calls take a while), re-block rather than
  assuming it hung — s291 saw ~4 polls, s292 saw ~5 polls before `CRASH: N` printed. Check `ps aux` and
  incremental log growth between polls to confirm it's making progress, not stuck.
- Do NOT treat a soak that hits an ALREADY-CATALOGUED, unrelated crash family as a failed validation —
  s292's soak 1 died to `cvmsPoolAlloc+496` (an already-catalogued "RDRAM-base-relative near-
  `0x80000000`" fault family, first flagged ~line 1683), confirmed unrelated to that session's
  `tickTextureMaterialExpiry` change via `[CRASH][pc-symbol]` naming AND via `last-guest-pc` being the
  long-tracked stale `beginFrameDLChunk` value, not inside the new function's address range. Check the
  `[CRASH][pc-symbol]` name against `CURRENT-TRUTH.md` before assuming any crash is a regression.
- Do NOT treat a soak that happens to hit any of the 4 armed breadcrumbs' scoped functions as wasted
  even if it doesn't crash there — all 4 breadcrumbs have zero cost when they don't fire, so ordinary
  soaking for whatever NEW work unit you pick this session is "free" extra exposure for all of them.
- Do NOT commit staged work you did not verify — always run `git diff --cached` first (see Recovery
  note above) even if it looks like routine bootstrap noise.

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
- Scene-reached check: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene death, >=1 = reached). Note:
  the summary output printed by the driver script itself uses a different string ("phase width=1024
  reached after Ns") — the `grep -c "vi_width=1024"` check is meant to run against the raw
  `dequeuearg1/run.log`, not the driver's own stdout capture, which only logs the LAST phase line (can
  legitimately show `0` for an early-reached scene if VI width later transitioned away from 1024).
- `+N` crash-symbol offsets are NATIVE (ARM64) and SHIFT across sessions — verify range membership
  via the Mach-O symtab walk (`nm -n`, filter T/t, dedupe, sort, confirm offset < distance to next
  DISTINCT symbol) before trusting a reported `sym=X+N`. Note: this native byte size is NOT the same
  as the guest MIPS function's byte size (compiled ARM64 code reliably expands well beyond the
  original MIPS instruction count) — a mismatch between the two is expected, not a red flag.
- `[CRASH][last-guest-pc]` is now informative for FOUR functions: `static_5_800AB658`
  (`BREADCRUMB7`), `inflate_fast` (`BREADCRUMB10`, s290), `coalesceFreeHeapBlocks`
  (`BREADCRUMB11`, s291), and `tickTextureMaterialExpiry` (`BREADCRUMB12`, s292) — still stale noise
  for any other crashing function (most commonly `beginFrameDLChunk`'s `0x8000b650`).
- `N64Recomp/fixup_game_funcs.py` is untracked in the standalone `N64Recomp` checkout — no
  `export.sh` needed for edits there, only for actual `lib/` submodule changes.
- Disassembly tools (`otool`/`objdump`/`lldb`) remain BLOCKED in this sandbox (confirmed s194,
  re-confirmed by omission every session since — do not re-attempt, use the breadcrumb mechanism).
- `CURRENT-TRUTH.md` is far over the ~35KB target (33+ sessions overdue) — not this iteration's job
  unless the picked work unit is a quick null with clear leftover budget.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration before assuming a `WORKING`/missing-`OUTCOME` state means recovery work is needed —
  usually just the loop's normal per-iteration bootstrap. But DO check `git status`/`git diff --cached`
  for staged tracked-file content beyond that routine reset (see Recovery note above) — s292 found a
  genuine case of this from s291. The `lib/N64ModernRuntime`/`lib/rt64` "-dirty" gitlink markers are
  the same long-standing baseline every session has seen — not new, not worth re-verifying each time.
