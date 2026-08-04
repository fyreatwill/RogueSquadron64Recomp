# NEXT work unit — land the tickTextureMaterialExpiry guard (fully specified, no investigation needed)

## Note: s295 was a MAINTENANCE iteration (Step 0), not a pivot away from this work unit

`docs/CURRENT-TRUTH.md` was compacted 562,666→120,975 bytes (7,959→1,267 lines) and its
triple-colliding Next-steps numbering was fixed into one sequence. The item describing this work
unit's origin (`tickTextureMaterialExpiry` crossing the two-observation confirmation bar) is now
`-159` in `CURRENT-TRUTH.md` (was `-135`) — same content, renumbered only. Nothing below this note
changed; the guard work is still the fully-specified next unit, do it next.

## Top priority: land and validate the `ctx->r16` guard in `tickTextureMaterialExpiry`

`tickTextureMaterialExpiry`'s crash (`BREADCRUMB12`, armed s292) has now fired at the **identical
guest PC** in two independent sessions: s293's soak 2 and s294's soak 1, both `[CRASH][last-guest-pc]
pc=0x80022094`. This crosses the two-independent-observations confirmation bar. This is no longer a
"wait for recurrence" item — it's ready to guard.

**Site**: `N64Recomp/RecompiledFuncs/funcs_6.c:12207` — `lhu $v1, 0x8($s0)`
(`ctx->r3 = MEM_HU(ctx->r16, 0X8)` or equivalent in the generated C; check the exact current line
number after the next regen, since native/guest-side line numbers can drift slightly between
sessions — grep for `0x80022094` to relocate it if the line shifted). This is a 2-byte unsigned read
of offset `0x8` off `ctx->r16`, the walked list-node pointer.

**Fix template**: same KSEG0-range check every other guard in this project uses (reject if
`ctx->r16 < 0x80000000u || ctx->r16 >= 0x80800000u`, or whatever the established bound constant is in
`fixup_game_funcs.py` — grep for `DEQUEUE_GUARD` or `CACHE4_GUARD` for the exact boilerplate to copy).
On failure, bail to whatever the function's existing null/empty-list handling does one node earlier —
read `funcs_6.c:12135-12332` (the function s292 already fully read) to find the correct bail target;
do NOT invent a new control-flow path.

**Do this session, in order**:
1. Re-read `funcs_6.c:12135-12332` (or wherever the function currently lives after regen) to confirm
   the guard site and bail target are still accurate — the s292 read is the source of truth, but
   confirm line numbers before writing the patch.
2. Add the guard to `N64Recomp/fixup_game_funcs.py`, same file/pattern as `CACHE4_GUARD`/
   `DEQUEUE_GUARD`. Check the ordering gotcha documented in `CURRENT-TRUTH.md` (~line 1520-1533):
   since `tickTextureMaterialExpiry` IS breadcrumbed (`BREADCRUMB12`), a new guard block whose file
   position precedes the breadcrumb regex must match the PRE-breadcrumb shape (no
   `g_rs64_last_guest_pc` lines) or it silently matches zero times.
3. Regen (delete `funcs_*.c`, `N64Recomp`, `fixup_game_funcs.py`), confirm the patch report shows
   the new guard `x1` and `BREADCRUMB12` still patches its prior count (83) unchanged.
4. Build clean, confirm no new warnings beyond the 46-warning baseline.
5. **2 validation soaks** (iron rule 4, `HOLD_S=275`, `scratch/s73_post_a_scene/run_dequeuearg1.sh`).
   Discriminating outcome: if the guard fires (a fire-log entry, if one is wired up — check whether
   this guard family logs fires the way `DEQUEUE_GUARD`/`CACHE_GUARD` do) AND the run stays clean past
   where the crash previously happened, that's real evidence the guard works. If 0/2 fires (crash
   didn't recur at all, ~consistent with its historical ~rare hit rate), that's a weak null — do not
   over-claim "fixed," just note it's unconfirmed-but-not-refuted, same honest framing s270/s271 used
   for their 0-fire soaks.
6. If a 3rd soak in a row shows the OLD crash symbol still firing at the SAME guest PC even with the
   guard installed, the guard is wrong (bail target or range check is broken) — do not just re-soak
   hoping it clears; go back and re-read the bail-path control flow.

## Fallback if the guard proves harder than expected (budget rule 8: 3 strikes)

If 3 consecutive attempts at the guard (wrong bail target, patch doesn't match, etc.) don't converge,
stop and fall back to the sweep instead: resume `unguarded_walk_candidates.json` (`scratch/agent/
find_unguarded_walks.py` generated it, 143 sites/43 funcs). 2 of 43 functions are now addressed
(`tickSongSequence` s293, `stopSongByHandle` s294), 1 explicitly deferred as out-of-scope
(`func_800AE3F0`, funcs_27.c, ~18000 lines — do NOT pick this one, it's too large for a single
session and likely overlaps the closed `-0x25A4` hangar audit). Pick the next untouched function by
the same recipe: source-read, check for a translation bug (there won't be one, same baseline every
time), land a breadcrumb if a guard can't be validated blind.

## Status of all armed breadcrumbs (as of s294)

- `BREADCRUMB10`/`inflate_fast`: 0 recurrences since s290. Still wait-for-recurrence.
- `BREADCRUMB11`/`coalesceFreeHeapBlocks`: 0 recurrences since s291. Still wait-for-recurrence.
- `BREADCRUMB12`/`tickTextureMaterialExpiry`: **2 recurrences (s293, s294), SAME guest PC
  `0x80022094` both times — confirmed, ready to guard (see above).**
- `BREADCRUMB13`/`tickSongSequence`: 0 recurrences since s293. Still wait-for-recurrence.
- `BREADCRUMB14`/`stopSongByHandle`: 0 recurrences since s294 (this session). Still
  wait-for-recurrence.

## Do NOT do this iteration

- Do NOT re-open `-0x25A4`, `waitForAnyAudioSlot`, `inflate_fast`, `coalesceFreeHeapBlocks`,
  `tickSongSequence`, or `stopSongByHandle` unless one of them gets its OWN 2nd recurrence at a
  matching guest PC (same bar `tickTextureMaterialExpiry` just crossed).
- Do NOT pick `func_800AE3F0` from the sweep (~18000 lines, out of single-session scope, likely
  overlaps the closed `-0x25A4` hangar audit — already checked and rejected s294).
- Do NOT run `fixup_game_funcs.py` twice without a fresh `N64Recomp` regen in between.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — the background bash
  task auto-notifies on completion; do not call `ScheduleWakeup` for it (that tool is for `/loop`
  dynamic-pacing mode, not for waiting on a task the harness already tracks) and do not end the turn
  with unfinished exit-contract steps just because a soak is still running — the Stop hook will
  reject it. If a soak is genuinely still running when you'd otherwise stop, keep working (write up
  what's done so far, prep the next command) rather than ending the turn.
- Do NOT treat a soak that hits an ALREADY-CATALOGUED, unrelated crash family as a failed validation
  — check the `[CRASH][pc-symbol]` name against `CURRENT-TRUTH.md` before assuming any crash is a
  regression. `__pthread_kill+8`/SIGABRT is one such already-catalogued unrelated class (s265).
- Do NOT commit staged work you did not verify — always run `git diff --cached` first even if it
  looks like routine bootstrap noise.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` NOT needed (ELF/ROM mapping unchanged since s284). `N64Recomp`
  needs cwd `N64Recomp` (`./build/N64Recomp rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd
  `N64Recomp`. Always delete `funcs_*.c` and regen from scratch first:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
- `cd` does not persist into a subsequent `run_in_background: true` call — launch background
  commands by full absolute path with no preceding bare `cd`.
- Bash tool cwd persists across sequential (non-background) calls but resets after an unrelated
  `cd` elsewhere in the session — re-`cd` explicitly before cwd-dependent commands.
- Compound `cd && ...` commands need interactive approval — issue `cd` as its own call first. Simple
  `&&`-chained commands in general (e.g. `grep ... && python3 ...`) also sometimes need approval even
  outside `cd` — prefer separate tool calls over chaining when in doubt.
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
  given distinct names (s294 used `s294_soak1`/`s294_soak2`).
- Scene-reached check: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene death, >=1 = reached).
- `+N` crash-symbol offsets are NATIVE (ARM64) and SHIFT across sessions — verify range membership
  via the Mach-O symtab walk (`nm -n`, filter T/t, dedupe, sort, confirm offset < distance to next
  DISTINCT symbol) before trusting a reported `sym=X+N`.
- `[CRASH][last-guest-pc]` is now informative for SIX functions: `static_5_800AB658`
  (`BREADCRUMB7`), `inflate_fast` (`BREADCRUMB10`), `coalesceFreeHeapBlocks` (`BREADCRUMB11`),
  `tickTextureMaterialExpiry` (`BREADCRUMB12`, now CONFIRMED with 2 matching data points — see
  above), `tickSongSequence` (`BREADCRUMB13`), and `stopSongByHandle` (`BREADCRUMB14`, s294) —
  still stale noise for any other crashing function (most commonly `beginFrameDLChunk`'s
  `0x8000b650`), OR informative-but-benign when it lands on a breadcrumbed function's own LAST
  instruction (its normal return point — confirms the function ran to completion, not a fault
  inside it; s265 established this for `submitSceneNodeRender`, s294 reconfirmed it for
  `tickTextureMaterialExpiry`).
- `N64Recomp/fixup_game_funcs.py` is untracked in the standalone `N64Recomp` checkout — no
  `export.sh` needed for edits there, only for actual `lib/` submodule changes.
- Disassembly tools (`otool`/`objdump`/`lldb`) remain BLOCKED in this sandbox — do not re-attempt,
  use the breadcrumb mechanism.
- `CURRENT-TRUTH.md` is far over the ~35KB target (35+ sessions overdue) — not this iteration's
  job unless the picked work unit is a quick null with clear leftover budget. Given `CURRENT-TRUTH.md`
  is now ~8000 lines and growing every session, a future session with spare budget should seriously
  consider a compression pass (migrate durable material to `PROJECT-OVERVIEW.md`, prune superseded
  detail) rather than deferring again — this note has now carried forward unaddressed for over 30
  sessions.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration, but also run `git diff --cached` for staged tracked-file content beyond the routine
  reset.
- The `unguarded_walk_candidates.json` sweep tracker (143 sites/43 funcs) is itself never edited in
  place as sites get addressed — coverage status has to be cross-checked against `CURRENT-TRUTH.md`
  function-name mentions each time, as this and the two prior sessions did. A future session with
  spare budget could add a `"status"` field to each JSON entry to make this lookup O(1) instead of
  a fresh grep-and-cross-reference every time — not urgent, but would save real time if the sweep
  continues for many more sessions.

HYPOTHESIS-ID: tickTextureMaterialExpiry-guard
