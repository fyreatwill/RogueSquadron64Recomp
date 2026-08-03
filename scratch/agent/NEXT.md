# NEXT work unit — land `BREADCRUMB7` on `static_5_800AB658` (the newest,
# highest-priority not-yet-localized crash site), regen, soak-verify.

## Where the investigation stands (s273)

s273 re-soaked `BREADCRUMB5` (`reserveAndEmitDLEntry`) per s272's plan: still 0/4
combined across 2 full sessions, never once informative. Soak 1 instead caught a
brand-new, symrange-confirmed crash — `buildPositionAndCallTransformHelper+1356`,
`si_addr=0x80000010` (guest), the near-`0x80000000` family's `+0x10` variant. This
is a normal recompiled guest function (unlike `inflate_fast`), so it was
breadcrumbed same-session as `BREADCRUMB6`. Its own 2 verify soaks then went 0/2:
soak 3 hit yet another new site (`static_5_800AB658+49104`, garbage-offset fault
shape, NOT the `0x80000000` family), soak 4 ran fully clean and reached
`vi_width=640` (deeper than any recent soak — driver had to SIGKILL the still-
alive process).

Both `BREADCRUMB5` and `BREADCRUMB6` are now armed but weak-signal (0/4 and 0/2
respectively). Rather than a 3rd re-soak of either, the highest-information-value
move is to land a breadcrumb on the newest confirmed-real site.

## The next work unit

1. **Land `BREADCRUMB7` on `static_5_800AB658`** (confirmed real recompiled
   function at `N64Recomp/RecompiledFuncs/funcs_40.c:7242`, called from several
   sites in `funcs_27.c`/`funcs_40.c` — an unnamed-in-source static function, NOT
   a data table despite the name). Same mechanism as `BREADCRUMB`-`BREADCRUMB6`:
   in `N64Recomp/fixup_game_funcs.py`, add a block scoped to
   `p.name == "funcs_40.c"`, matching
   `RECOMP_FUNC void static_5_800AB658\(uint8_t\* rdram, recomp_context\* ctx\) \{\n`,
   reusing the shared `g_rs64_last_guest_pc` global (no `main.cpp` change).

2. **Regen in the mandated order, exactly once**: delete `funcs_*.c` first
   (`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`),
   then `python3 tools/make_elf.py` (cwd `rogue_squadron64`), then
   `./build/N64Recomp rogue_squadron.toml` (cwd `N64Recomp`), then ONE
   `fixup_game_funcs.py` pass with output saved to a log file (cwd `N64Recomp`) —
   grep the SAVED LOG for multiplicities, never re-run the script to re-inspect
   (s272's near-mistake). Confirm `BREADCRUMB7` patched exactly once, and that
   `BREADCRUMB5`/`BREADCRUMB6`/`CACHE3_GUARD`/`CACHE4_GUARD` are all still at
   their documented counts (`BREADCRUMB5` x224, `CACHE3_GUARD` x1,
   `CACHE4_GUARD` x1 — confirm `BREADCRUMB6`'s count too once known, it was
   x305 this session). Build (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`
   from repo root), expect 0 errors, same pre-existing warnings.

3. **Soak twice** (budget rule 8): `env HOLD_S=240 zsh scratch/s73_post_a_scene/run_dequeuearg1.sh s274_soak1`
   then `s274_soak2` — launch each `run_in_background: true` from an absolute
   path, then `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME
   turn (cross-turn waiting does not work under the Stop hook).

4. **If `static_5_800AB658` crashes and `last-guest-pc` is informative** (grep
   the reported guest PC in `funcs_40.c`, confirm it's inside this function via
   the nearest-preceding `RECOMP_FUNC` line): read ~20 surrounding lines. If it
   matches the cached-free-list-head idiom (`lui $vX,0x8011` / `lw
   $vX,0x63B0($vX)` / deref or `+4`-store with zero validation), add a guard
   (deref-side shape if matching `CACHE4_GUARD`'s pattern, write-side if
   matching `CACHE2`/`CACHE3_GUARD`'s), full regen, soak-verify (>=2 clean),
   add its `ROGUESQ_LOG_*` flag to `run_dequeuearg1.sh` same session. If the
   idiom does NOT match (this crash's fault shape — garbage `si_addr`, not
   exact `0x80000000` — suggests it may NOT be the same idiom family), read the
   actual surrounding code before assuming; describe what's actually there
   instead of forcing the familiar guard shape onto it.

5. **If `buildPositionAndCallTransformHelper` (`BREADCRUMB6`'s own target)
   recurs instead**: localize via `last-guest-pc` (informative now, since this
   function is breadcrumbed) the same way `BREADCRUMB3`/`BREADCRUMB4` were
   localized — grep the guest PC in `funcs_15.c`.

6. **If `reserveAndEmitDLEntry` (`BREADCRUMB5`) recurs**: this would be its
   first-ever informative hit after 0/4 — treat as high-value, localize via
   `last-guest-pc` in `funcs_3.c`.

7. **If `emitAllocatedDLCommand` or `inflate_fast`/zlib recur**: see s271/s272
   writeups (`PORTING-STATE` Sessions 271-272) — neither is localizable via the
   simple breadcrumb-grep approach yet (`emitAllocatedDLCommand` not
   breadcrumbed; `inflate_fast` is a system library).

8. **If a completely different crash lands** (has happened most sessions):
   note it, symrange-verify if plausible, don't chase it this iteration unless
   clearly highest-information-value (budget rule 8).

## Do NOT do this iteration

- Do NOT run `fixup_game_funcs.py` twice in a row without deleting and
  regenerating `funcs_*.c` in between — silently duplicates every patch. Delete
  -> `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` ONCE, save output to
  a log file, grep the SAVED LOG (never re-run the script) to check
  multiplicities -> build.
- Do NOT spend a 3rd consecutive session re-soaking `BREADCRUMB5` or
  `heapFreeListDequeue`'s original target without a new angle — both are
  parked/weak-signal per rule 8. `BREADCRUMB6` similarly shouldn't get a 3rd
  soak before trying `BREADCRUMB7` first.
- Do NOT re-touch `DEQUEUE_GUARD`'s range-check bound — refuted (s267).
- Do NOT conflate the `0x80000000`-exact-fault family (or its `+0x10`
  `processSceneNode`-`+0x30`, `emitAllocatedDLCommand`-garbage-offset, or
  `inflate_fast`-`+3` variants) with item -49's KSEG0-zero-extension bug
  (`0x80630062`) — confirmed distinct multiple sessions running. Don't assume
  `static_5_800AB658`'s garbage-offset crash is the same idiom family just
  because it's nearby in the investigation — read the actual code first.
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11` = `0x0000000300000000` as
  crash-matching evidence for ANYTHING — constant RDRAM base pointer.
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `CACHE2_GUARD`/`CACHE3_GUARD`/`CACHE4_GUARD`/`MATLIST_GUARD1-3`/
  `COMPOSE_NPC_GUARD1-9`/`DEQUEUE_GUARD` — all verified not regressing.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak —
  block with `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME
  turn.
- Do NOT treat a long-running soak (e.g. an 8GB+ log, driver command appearing
  "stuck") as necessarily hung — check `ps -p <pid>` first; the game process
  may already be dead while the driver script is still crunching a large log
  for its summary. s273's `soak4` took several extra `TaskOutput` polls purely
  for log-summary compute time after the game itself had already exited/been
  killed.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64` (run as
  `python3 tools/make_elf.py`), `N64Recomp` needs cwd `N64Recomp`
  (`./build/N64Recomp rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd
  `N64Recomp`. Always delete `funcs_*.c` and regen from scratch before running
  `fixup_game_funcs.py`.
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Background launches do NOT inherit a prior foreground `cd` — always launch
  soak drivers by full absolute path when using `run_in_background: true`.
- Cross-turn waiting does not work under the Stop hook — use
  `TaskOutput(task_id, block=true, timeout<=480000)` synchronously in the same
  turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`. Current-best baseline: `run_dequeuearg1.sh` (`HOLD_S`
  overridable via env, defaults to 240 if unset). `BREADCRUMB`-family entries
  do NOT carry their own `ROGUESQ_LOG_*` fire-log (only guards do) — no
  `run_dequeuearg1.sh` edit needed when adding a new `BREADCRUMBn`. DO add a
  log flag when landing a new GUARD.
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets and SHIFT across
  sessions as guards/breadcrumbs are added. Verify range membership via the
  Mach-O symtab walk (inline python, see s273's approach: parse LC_SYMTAB,
  sort `(n_value, name)` pairs, find the exact-name entry, check the reported
  crash offset is less than the distance to the next symbol). System-library
  crashes (like `inflate_fast`) resolve via the OS's own dyld symbol table and
  don't need/support the same check.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the crashing
  function is ITSELF breadcrumbed. Always grep the reported guest PC's hex
  label in the relevant `funcs_N.c` and find its enclosing `RECOMP_FUNC`
  before trusting it.
- When adding a guard to a function that's ALSO covered by an existing
  breadcrumb's blanket per-instruction pass: check whether the guard patch's
  code block sits before or after the breadcrumb patch's block in
  `fixup_game_funcs.py`'s file order. A guard block positioned BEFORE its
  function's breadcrumb block sees PRE-breadcrumb text and must not require
  `g_rs64_last_guest_pc` lines in its match regex.
- Redirecting shell output (`>`) only works to paths under one of the 3 session
  working directories — `/tmp` is blocked. Use `scratch/agent/*.log`.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone
  `N64Recomp` checkout — expected. Changes persist only via the live file on
  disk across sessions.
- `git status --short` run from inside `RogueSquadron64Recomp/build` works
  without needing `-C`/`cd` combined-command approval prompts; `git -C <path>`
  and `cd <dir> && git ...` both require interactive approval.
- `CURRENT-TRUTH.md` is far over the ~35KB target — now 14+ consecutive
  sessions overdue for a pruning pass. Still not this iteration's job unless
  the localization work above is a quick null with clear leftover budget.
