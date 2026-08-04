# NEXT work unit — read the backlog below CURRENT-TRUTH item -124 fresh (unreviewed since before s283)

## Status of the last 3 backlog items (all closed or instrumented-and-waiting)

- `-0x25A4` hangar-list-pointer audit lineage (s283-288, `CURRENT-TRUTH` item -129): CLOSED.
- Elevated pre-scene `waitForAnyAudioSlot` death rate (s289, item -130): CLOSED as a non-finding.
- `inflate_fast`/zlib investigation (s290, item -131): **NOT closed, but not actionable right now
  either.** Full source read found no unique translation bug. The single s272 crash observation
  (`si_addr=0x380000003`) was re-framed as the SAME "near-exact-`0x80000000`, small positive offset"
  null-pointer signature this investigation has guarded ~15 times elsewhere — i.e., a familiar bug
  shape, not a novel zlib bug — but there's still only 1 observation ever, with no way to force it to
  recur on demand. `BREADCRUMB10` (`fixup_game_funcs.py`, `g_rs64_last_guest_pc`, same mechanism as
  `BREADCRUMB`-`BREADCRUMB9`) is now live and scoped to `inflate_fast`'s body — the next time this
  crash fires (in ANY soak, not a dedicated one), `[CRASH][last-guest-pc]` will for the first time
  point at the actual faulting `inflate_fast` instruction instead of the stale `beginFrameDLChunk`
  value s272/s273 both saw. **Do not design a guard blind** — wait for the breadcrumb to actually
  catch an occurrence, then read the guest PC it reports (grep `funcs_7.c` for that address) to see
  which register/access it corresponds to, cross-reference against the 4 candidate pointers below,
  and land a guard only once you know which one was zero. Full detail: `PORTING-STATE` Session 290,
  `CURRENT-TRUTH` item -131.

  **Candidate zero-valued pointers, if/when it recurs** (ranked by how directly caller-controlled they
  are, most first): `tl`/`td` (Huffman table bases, loaded by `inflate_blocks` from `$s1+0x14`/`+0x18`
  with no range check, `funcs_7.c:12344`/`:12347`) > `p`/`q` (input/output byte pointers inside the
  copy loop, `ctx->r12`/`ctx->r11`) > `z`/`s` (the z_streamp and blocks-state "self" pointers, less
  likely to ever be zero since they're the same struct on every call).

## What this session's iteration should actually be

Since `inflate_fast` is now a wait-for-recurrence instrument (not a task with concrete next actions),
**do NOT spend this iteration staring at it**. Instead:

1. Read `docs/CURRENT-TRUTH.md`'s "Next steps, in order of expected value" section starting right
   AFTER item -124 (i.e., skip past the entire `-0x25A4`/`waitForAnyAudioSlot`/`inflate_fast` trilogy,
   items -125 through -131, which are all now either closed or instrumented-and-waiting) and read
   what's queued below that — this has not been reviewed fresh since before s283 (over 7 sessions),
   so treat its stated priority ordering as possibly stale, not gospel. `grep -n "^-1[0-9][0-9]\." or
   "^-9[0-9]\."` (or similar) to find the next few numbered items quickly rather than reading
   thousands of lines linearly.
2. Cross-check whatever item you find against the "Overturned conclusions" section
   (`CURRENT-TRUTH.md:7339`) and the "Dead ends" section (`:7615`) before committing to it — some
   older backlog items may already be superseded without their own "Next steps" entry having been
   updated to say so.
3. Pick ONE work unit from there per the normal rules (2-4 hypotheses, discriminating measurement,
   batch instrumentation).

## Do NOT do this iteration

- Do NOT re-open `-0x25A4`, `waitForAnyAudioSlot`, or attempt to guess-guard `inflate_fast` blind —
  all three are either closed or correctly waiting on new evidence, not actionable right now.
- Do NOT run `fixup_game_funcs.py` twice without a fresh `N64Recomp` regen in between.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — block with
  `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn.
- Do NOT treat a soak that happens to hit `inflate_fast`'s new breadcrumb as a wasted run even if it
  doesn't crash there — the breadcrumb has zero cost when it doesn't fire, so ordinary soaking for
  whatever NEW work unit you pick this session is "free" extra exposure for `inflate_fast` too.

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
  in a non-interactive/autonomous session that approval is NOT available (confirmed s289/s290: both
  forms blocked outright, no prompt resolvable) — do not spend time retrying these forms for
  submodule git state; treat the dirty-submodule baseline as already-established fact from prior
  sessions' direct confirmations (s279, s280, s282, s284, s285) instead of re-attempting to verify
  it each session. `nm -n <binary> > file` also flagged — use Python `subprocess.run`.
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
- `[CRASH][last-guest-pc]` is now informative for TWO functions: `static_5_800AB658` (`BREADCRUMB7`)
  and, as of s290, `inflate_fast` (`BREADCRUMB10`) — still stale noise for any other crashing
  function.
- `N64Recomp/fixup_game_funcs.py` is untracked in the standalone `N64Recomp` checkout — no
  `export.sh` needed for edits there, only for actual `lib/` submodule changes.
- `CURRENT-TRUTH.md` is far over the ~35KB target (31+ sessions overdue) — not this iteration's job
  unless the picked work unit is a quick null with clear leftover budget.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration before assuming a `WORKING`/missing-`OUTCOME` state means recovery work is needed — this
  has repeatedly turned out to be just the loop's normal per-iteration bootstrap, not an interrupted
  session. Only treat it as recovery-worthy if there's actual uncommitted diff evidence (e.g.
  `git status`/`git diff` on `fixup_game_funcs.py` or other tracked work files) beyond the routine
  `STATUS`/`OUTCOME` reset. The `lib/N64ModernRuntime`/`lib/rt64` "-dirty" gitlink markers are the
  same long-standing baseline every session has seen — not new, not worth re-verifying each time.
