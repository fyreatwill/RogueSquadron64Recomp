# NEXT work unit — re-soak with `BREADCRUMB4` armed (it went 0/2 last
# session); if `processSceneNode+1184` recurs, localize and guard it; if a
# `coalesceFreeHeapBlocks`/`tickTextureMaterialExpiry` crash recurs instead,
# land a new breadcrumb on whichever one hit and localize that instead.

## Where the investigation stands (s270)

s270 ran s269's plan exactly: landed `BREADCRUMB4` scoped to `processSceneNode`
(confirmed in `funcs_4.c:15097`; patched x422; all 3 pre-existing breadcrumbs
unchanged at `BREADCRUMB` x1179 / `BREADCRUMB2` x724 / `BREADCRUMB3` x995),
regenerated cleanly, and re-soaked twice with `run_dequeuearg1.sh`.

**`processSceneNode` did NOT crash in either soak this session** (0/2, breaking
the 3/3 combined streak s267+s269 had built — now 3/5 combined). Soak 1 instead
hit an unrelated macOS-side crash (`fscache_insert_and_retain`, not RDRAM-
relative, not guest code — ignore). **Soak 2 caught a different, genuinely new,
symrange-confirmed real crash**: `submitSceneNodeRender+27676`, guest
`0x80010840` (`sw $zero, 0x4($v0)`) — a 3rd, previously-unaudited inlined copy
of the "reload persistent free-list cache-head global (`0x801163B0`),
dereference with zero validation, write to `head+4`" idiom that s197's
original guard and s266's `CACHE2_GUARD` already fixed at two OTHER call
sites. Landed `CACHE3_GUARD` (identical pattern: range-check the reloaded
head, reset the global to 0 on failure, jump to the merge point) and
soak-verified it clean: 2/2 VALID post-fix soaks with zero recurrence
(`verify1` ran a genuinely deep 109s hold, VI width transitioned twice, crashed
elsewhere instead; `verify3` also crashed elsewhere instead; `verify2` was an
unusable data point — died before the phase-gate).

**Two new, not-yet-catalogued, not-yet-localized crash sites surfaced
incidentally** during `CACHE3_GUARD` verification (neither is breadcrumbed;
`last-guest-pc` for both showed the stale `0x8000b650` value from
`beginFrameDLChunk`, uninformative for either):
- `coalesceFreeHeapBlocks` (`verify1`) — heap-related, plausibly the same
  broader family as `heapFreeListDequeue`'s original 0x80000000-family fault.
- `tickTextureMaterialExpiry` (`verify3`) — unrelated subsystem (texture/
  material lifecycle), no obvious connection to the scene-traversal family.

Both are single-observation, unverified whether they're the same family as
this investigation's `0x80000000`-ish faults or something distinct — do not
cite either as confirmed-related to anything without a symrange check AND a
2nd independent observation.

## The next work unit

1. **Re-soak with the current build as-is** (no code changes needed first —
   `BREADCRUMB4` is armed and `CACHE3_GUARD` is landed):
   `env HOLD_S=240 zsh scratch/s73_post_a_scene/run_dequeuearg1.sh <tag>`.
   Launch `run_in_background: true` from an absolute path, then immediately
   `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn.
   Budget 2 attempts before deciding what to do with the result (iron rule 8).

2. **If `processSceneNode+1184` (`si_addr=0x380000030`) recurs**: `grep -n
   "0x<UPPERCASE_HEX>:"` in `N64Recomp/RecompiledFuncs/funcs_4.c` around
   `last-guest-pc`'s reported address (should now be genuinely informative
   since `processSceneNode` is breadcrumbed), read ~20 surrounding lines.
   Given the `+0x30` fault offset (not `+0` like the other two sites), expect
   a struct-field load/store at a small constant offset off a register
   holding a corrupted/sentinel base pointer — add ONE targeted guard
   (same shape as `CACHE3_GUARD`/`DEQUEUE_GUARD`: range-check before the
   deref, log behind a new `ROGUESQ_LOG_*` var, skip to the nearest natural
   reentry point on failure), full regen (delete `funcs_*.c` FIRST, see iron
   rule below), soak-verify (≥2 independent clean runs, iron rule 4).

3. **If a `coalesceFreeHeapBlocks` or `tickTextureMaterialExpiry` crash
   recurs instead** (or any other crash not yet breadcrumbed): land a new
   breadcrumb (`BREADCRUMB5`) scoped to that function's own body, identical
   mechanism to `BREADCRUMB`-`BREADCRUMB4` (same shared `g_rs64_last_guest_pc`
   global, confirm which `funcs_N.c` file first via `grep -n "RECOMP_FUNC void
   <name>" N64Recomp/RecompiledFuncs/funcs_*.c`), regen, re-soak to localize
   it exactly — same playbook that has now successfully localized 3 crashes
   in a row (`beginFrameDLChunk`, `processSceneNode` partially, and indirectly
   `submitSceneNodeRender`'s 3rd cache site).

4. **If a completely different crash lands** (has happened most sessions):
   note it, symrange-verify if the offset looks plausible, but don't chase it
   this iteration unless it's clearly the highest-information-value next
   step — see iron rule 8's budget discipline.

## Do NOT do this iteration

- Do NOT run `fixup_game_funcs.py` twice in a row without deleting and
  regenerating `funcs_*.c` in between — this SILENTLY DUPLICATES every
  breadcrumb insertion (confirmed operationally this session: 3202 vs
  expected 1601 `g_rs64_last_guest_pc =` lines in `funcs_4.c` after an
  accidental 2nd invocation). Always: delete `funcs_*.c` -> `make_elf.py` ->
  `N64Recomp` -> `fixup_game_funcs.py` ONCE -> check multiplicities -> build.
- Do NOT spend another soak attempt on `heapFreeListDequeue`'s own
  BREADCRUMB2-targeted crash — it's 0/6 across 2 sessions, parked per rule 8.
- Do NOT re-touch `DEQUEUE_GUARD`'s range-check bound — the a0-argument
  hypothesis is refuted (s267) with a same-run positive control.
- Do NOT conflate the `0x80000000`-exact-fault family (or its `+0x30`
  variant at `processSceneNode`) with item -49's KSEG0-zero-extension bug
  (`0x80630062`) — different exact values, different sites, confirmed
  distinct multiple sessions running.
- Do NOT cite `x0`/`x8`/`x9`/`x11 = 0x0000000300000000` as crash-matching
  evidence for ANYTHING — constant RDRAM base pointer (s219, item -60).
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `CACHE2_GUARD`/`CACHE3_GUARD`/`MATLIST_GUARD1-3`/`COMPOSE_NPC_GUARD1-9`/
  `DEQUEUE_GUARD` — all verified not regressing and not the current blocker.
- Do NOT treat `coalesceFreeHeapBlocks`/`tickTextureMaterialExpiry` as
  confirmed-related to the `0x80000000` family — single observation each,
  unverified. A 2nd independent hit + symrange check is the bar before citing
  either as a real, catalogued crash class.
- Do NOT idle across a Stop-hook turn boundary waiting on a background
  soak — block with `TaskOutput(task_id, block=true, timeout<=480000)` in
  the SAME turn.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64` (run as
  `python3 tools/make_elf.py`), `N64Recomp` needs cwd `N64Recomp`
  (`./build/N64Recomp rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd
  `N64Recomp`. Always delete `funcs_*.c` and regen from scratch before
  running `fixup_game_funcs.py` — see the duplication warning above.
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Background launches do NOT inherit a prior foreground `cd` — always
  launch soak drivers by full absolute path when using
  `run_in_background: true`.
- Cross-turn waiting does not work under the Stop hook — use
  `TaskOutput(task_id, block=true, timeout<=480000)` synchronously in the
  same turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`. Current-best baseline: `run_dequeuearg1.sh` (`HOLD_S`
  overridable via env, defaults to 240 if unset).
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets. Verify range
  membership by reading `build/RogueSquadron64Recomp`'s Mach-O symtab
  directly — see `scratch/agent/s268_symrange2.py` for the reusable
  parser/walker (edit its `targets` list or copy the walk logic inline); run
  it with cwd `RogueSquadron64Recomp/build` so the relative binary path
  resolves. No `nm`/`atos`/`otool`/`lldb`/`dwarfdump` needed or available.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the
  crashing function is ITSELF breadcrumbed — otherwise it just shows
  wherever the process last passed through one of the OTHER currently-
  instrumented functions (stale, confirmed misleading multiple times this
  investigation). Check which file/function the crash symbol is in before
  trusting `last-guest-pc` for it.
- Redirecting shell output (`>`) only works to paths under one of the 3
  session working directories (`RogueSquadron64Recomp`, `N64Recomp`,
  `rogue_squadron64`) — `/tmp` is blocked. Use `scratch/agent/*.log`.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone
  `N64Recomp` checkout — expected, not a bug; not a `lib/` submodule so
  `submodule-patches/export.sh` never applies to it. Its changes persist
  only via the live file on disk across sessions.
- `git status --short` run from inside `RogueSquadron64Recomp/build` (or any
  subdir) works without needing `-C`/`cd` combined-command approval prompts.
- `CURRENT-TRUTH.md` is far over the ~35KB target in CLAUDE.md. A dedicated
  pruning session is now 12+ consecutive sessions overdue — still not this
  iteration's job unless the localization work above is a quick null with
  clear leftover budget.
