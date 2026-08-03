# NEXT work unit — land `BREADCRUMB8` on `emitAllocatedDLCommand` (the oldest
# untried backlog candidate, garbage-offset fault shape, single observation
# from s271), regen, soak-verify.

## Where the investigation stands (s274)

s274 landed `BREADCRUMB7` on `static_5_800AB658` per s273's plan: 0/2 this session
(its first), no informative hit. Soak 1 ran the ENTIRE 240s hold plus grace window
crash-free — the deepest soak this whole investigation has recorded (driver had to
SIGKILL the still-alive process). Soak 2 died pre-scene to the pre-catalogued
`waitForAnyAudioSlot` boot crash class (unusable, no scene reached). This is the
first session since s270 where neither soak caught a genuinely new, not-yet-
catalogued crash site — the backlog of untried candidates did NOT grow this session.

Current armed-breadcrumb tally, all weak-to-zero signal:
- `BREADCRUMB5`/`reserveAndEmitDLEntry`: 0/4 combined (s272+s273), never informative.
- `BREADCRUMB6`/`buildPositionAndCallTransformHelper`: 0/2 (s273), never informative.
- `BREADCRUMB7`/`static_5_800AB658`: 0/2 (s274), never informative.

None is at the formal 3-strikes limit (rule 8 counts consecutive sessions on the
SAME sub-hypothesis), but re-soaking any of them a 3rd time with zero signal is
lower information value than trying a candidate that already has a real,
symrange-confirmed observation and simply hasn't been breadcrumbed yet.

## The next work unit

1. **Land `BREADCRUMB8` on `emitAllocatedDLCommand`** (symrange-confirmed real
   crash from s271: `emitAllocatedDLCommand+6608`, garbage-offset fault shape —
   `si_addr` = RDRAM base + `0xd2095209`, NOT the exact-`0x80000000` family — single
   observation, never chased). First: confirm which `funcs_N.c` it lives in via
   `grep -rn "RECOMP_FUNC void emitAllocatedDLCommand" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c`
   (do this BEFORE editing `fixup_game_funcs.py` — do not assume `funcs_3.c` just
   because nearby DL-code functions live there). Same mechanism as `BREADCRUMB`-
   `BREADCRUMB7`: in `N64Recomp/fixup_game_funcs.py`, add a block scoped to the
   correct `p.name`, matching
   `RECOMP_FUNC void emitAllocatedDLCommand\(uint8_t\* rdram, recomp_context\* ctx\) \{\n`,
   reusing the shared `g_rs64_last_guest_pc` global (no `main.cpp` change). Check
   whether this function already carries earlier hand-written guards further up the
   file (like `reserveAndEmitDLEntry` did) — if so, confirm their comment style
   doesn't collide with the blanket `// 0x...: ` breadcrumb regex before assuming
   no conflict.

2. **Regen in the mandated order, exactly once**: delete `funcs_*.c` first
   (`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`),
   then `python3 tools/make_elf.py` (cwd `rogue_squadron64`), then
   `./build/N64Recomp rogue_squadron.toml` (cwd `N64Recomp`), then ONE
   `fixup_game_funcs.py` pass with output saved to a log file (cwd `N64Recomp`) —
   grep the SAVED LOG for multiplicities, never re-run the script to re-inspect.
   Confirm `BREADCRUMB8` patched exactly once, and that `BREADCRUMB5`/`BREADCRUMB6`/
   `BREADCRUMB7`/`CACHE3_GUARD`/`CACHE4_GUARD` are all still at their documented
   counts (`BREADCRUMB5` x224, `BREADCRUMB6` x305, `BREADCRUMB7` x2643, `CACHE3_GUARD`
   x1, `CACHE4_GUARD` x1). Build
   (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`
   from repo root), expect 0 errors, same pre-existing warnings.

3. **Soak twice** (budget rule 8): `env HOLD_S=240 zsh scratch/s73_post_a_scene/run_dequeuearg1.sh s275_soak1`
   then `s275_soak2` — launch each `run_in_background: true` from an absolute
   path, then `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME
   turn (cross-turn waiting does not work under the Stop hook).

4. **If `emitAllocatedDLCommand` crashes and `last-guest-pc` is informative** (grep
   the reported guest PC in the relevant `funcs_N.c`, confirm it's inside this
   function via the nearest-preceding `RECOMP_FUNC` line): read ~20 surrounding
   lines. This crash's fault shape (garbage `si_addr`, not exact `0x80000000`) is
   the SAME shape as `static_5_800AB658+49104`'s — worth comparing the two idioms
   side by side if both get localized, they may share a root cause distinct from
   the cached-free-list-head family. Do not force the familiar `CACHE*_GUARD`
   deref-side/write-side shape onto this without reading the actual code first.

5. **If `buildPositionAndCallTransformHelper` (`BREADCRUMB6`), `reserveAndEmitDLEntry`
   (`BREADCRUMB5`), or `static_5_800AB658` (`BREADCRUMB7`) recur instead**: localize
   via `last-guest-pc` the same way `BREADCRUMB3`/`BREADCRUMB4` were localized — grep
   the guest PC in the owning `funcs_N.c` (`funcs_15.c`, `funcs_3.c`, `funcs_40.c`
   respectively). Any of these would be a first-ever informative hit for
   `BREADCRUMB6`/`BREADCRUMB7` or the first in 3 sessions for `BREADCRUMB5` — treat
   as high value.

6. **If `inflate_fast`/zlib recurs**: see s272's writeup (`PORTING-STATE` Session
   272) — not localizable via the simple breadcrumb-grep approach yet (system
   library, not a guest function).

7. **If a completely different crash lands** (has happened most sessions until
   s274 broke the streak): note it, symrange-verify if plausible, don't chase it
   this iteration unless clearly highest-information-value (budget rule 8).

8. **If both soaks run fully clean with zero crashes** (s274's soak 1 shows this is
   now a real possibility, not just a theoretical one): this would be the first
   session with a 2/2 clean pair since this investigation began chasing this crash
   family. Note it explicitly in the session writeup as a possible signal that
   crash frequency is decreasing (more breadcrumbs happen to also touch guarded
   idioms, or genuine reduction in remaining unguarded sites) — but label it
   single-observation, do not conclude the investigation is near done from one
   session's clean pair.

## Do NOT do this iteration

- Do NOT run `fixup_game_funcs.py` twice in a row without deleting and
  regenerating `funcs_*.c` in between — silently duplicates every patch. Delete
  -> `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` ONCE, save output to
  a log file, grep the SAVED LOG (never re-run the script) to check
  multiplicities -> build.
- Do NOT spend a 3rd consecutive session re-soaking `BREADCRUMB5`,
  `BREADCRUMB6`, or `BREADCRUMB7` without a new angle — none is formally at the
  3-strikes limit yet, but all three have weak-to-zero signal, and
  `emitAllocatedDLCommand` is a higher-information-value untried candidate.
- Do NOT re-touch `DEQUEUE_GUARD`'s range-check bound — refuted (s267).
- Do NOT conflate the `0x80000000`-exact-fault family (or its `+0x10`
  `processSceneNode`-`+0x30`, `emitAllocatedDLCommand`-garbage-offset,
  `inflate_fast`-`+3`, or `static_5_800AB658`-garbage-offset variants) with item
  -49's KSEG0-zero-extension bug (`0x80630062`) — confirmed distinct multiple
  sessions running.
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
  for its summary.

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
  Mach-O symtab walk (inline python, see s273/s274's approach: parse LC_SYMTAB,
  sort `(n_value, name)` pairs, find the exact-name entry, check the reported
  crash offset is less than the distance to the next symbol). System-library
  crashes (like `inflate_fast`) resolve via the OS's own dyld symbol table and
  don't need/support the same check.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the crashing
  function is ITSELF breadcrumbed. Always grep the reported guest PC's hex
  label in the relevant `funcs_N.c` and find its enclosing `RECOMP_FUNC`
  before trusting it. `0x8000b650` specifically is a recurring stale value
  belonging to `beginFrameDLChunk` (`funcs_3.c`), seen in s272/s273/s274 for
  crashes that happen elsewhere — do not treat it as informative unless the
  crashing symbol IS `beginFrameDLChunk`.
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
- `CURRENT-TRUTH.md` is far over the ~35KB target — now 15+ consecutive
  sessions overdue for a pruning pass. Still not this iteration's job unless
  the localization work above is a quick null with clear leftover budget.
