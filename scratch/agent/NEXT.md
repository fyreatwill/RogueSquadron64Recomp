# NEXT work unit — land `BREADCRUMB9` on `tickWrappingTimerAccumulatorList` (the
# brand-new, symrange-confirmed crash site from s275, novel fault shape, single
# observation), regen, soak-verify.

## Where the investigation stands (s275)

s275 landed `BREADCRUMB8` on `emitAllocatedDLCommand` per s274's plan: 0/2 this
session (its first), no informative hit on its own target. Soak 1 died at
hold-iter 10 to a brand-new, symrange-confirmed crash
(`tickWrappingTimerAccumulatorList+868`, `funcs_11.c`) — a fault shape not seen
before in this investigation: `si_addr` guest `0x20000004`, which is
`0x80000004` with bit 31 cleared, distinct from both the exact-`0x80000000`
family and the large-garbage-offset family (`emitAllocatedDLCommand+6608`/
`static_5_800AB658+49104`). Soak 2 ran the entire 240s hold plus grace window
completely crash-free (`CRASH: 0`).

Current armed-breadcrumb tally, all weak-to-zero signal on their OWN targets:
- `BREADCRUMB5`/`reserveAndEmitDLEntry`: 0/4 combined (s272+s273), never informative.
- `BREADCRUMB6`/`buildPositionAndCallTransformHelper`: 0/2 (s273), never informative.
- `BREADCRUMB7`/`static_5_800AB658`: 0/2 (s274), never informative.
- `BREADCRUMB8`/`emitAllocatedDLCommand`: 0/2 (s275), never informative.

None is at the formal 3-strikes limit (rule 8 counts consecutive sessions on the
SAME sub-hypothesis), but `tickWrappingTimerAccumulatorList` is a higher-
information-value candidate: it has a real, symrange-confirmed observation from
THIS session and simply hasn't been breadcrumbed yet, unlike a 3rd blind re-soak
of an already-0/2-or-worse target.

## The next work unit

1. **Land `BREADCRUMB9` on `tickWrappingTimerAccumulatorList`** (symrange-confirmed
   real crash from s275: `tickWrappingTimerAccumulatorList+868`, novel fault shape
   — `si_addr` = RDRAM base + `0x20000004`, i.e. guest `0x80000004` with bit 31
   cleared, NOT the exact-`0x80000000` family and NOT the large-garbage-offset
   family — single observation, never chased). Already confirmed to live in
   `N64Recomp/RecompiledFuncs/funcs_11.c` (`grep -rln "RECOMP_FUNC void
   tickWrappingTimerAccumulatorList" N64Recomp/RecompiledFuncs/funcs_*.c` — do
   this again first to re-confirm, since `funcs_*.c` gets fully regenerated
   every session and file assignment is not guaranteed stable). Same mechanism
   as `BREADCRUMB`-`BREADCRUMB8`: in `N64Recomp/fixup_game_funcs.py`, add a
   block scoped to `p.name == "funcs_11.c"`, matching
   `RECOMP_FUNC void tickWrappingTimerAccumulatorList\(uint8_t\* rdram, recomp_context\* ctx\) \{\n`,
   reusing the shared `g_rs64_last_guest_pc` global (no `main.cpp` change).
   Check whether this function already carries earlier hand-written guards
   further up the file (like `reserveAndEmitDLEntry`/`emitAllocatedDLCommand`
   did) before assuming no conflict — grep `tickWrappingTimerAccumulatorList`
   in `fixup_game_funcs.py` first.

2. **Regen in the mandated order, exactly once**: delete `funcs_*.c` first
   (`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`),
   then `python3 tools/make_elf.py` (cwd `rogue_squadron64`), then
   `./build/N64Recomp rogue_squadron.toml` (cwd `N64Recomp`), then ONE
   `fixup_game_funcs.py` pass with output saved to a log file (cwd `N64Recomp`) —
   grep the SAVED LOG for multiplicities, never re-run the script to re-inspect.
   Confirm `BREADCRUMB9` patched exactly once, and that `BREADCRUMB5`/`BREADCRUMB6`/
   `BREADCRUMB7`/`BREADCRUMB8`/`CACHE3_GUARD`/`CACHE4_GUARD` are all still at their
   documented counts (`BREADCRUMB5` x224, `BREADCRUMB6` x305, `BREADCRUMB7` x2643,
   `BREADCRUMB8` x222, `CACHE3_GUARD` x1, `CACHE4_GUARD` x1). Build
   (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`
   from repo root), expect 0 errors, same pre-existing warnings.

3. **Soak twice** (budget rule 8): `env HOLD_S=240 zsh scratch/s73_post_a_scene/run_dequeuearg1.sh s276_soak1`
   then `s276_soak2` — launch each `run_in_background: true` from an absolute
   path, then `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME
   turn (cross-turn waiting does not work under the Stop hook).

4. **If `tickWrappingTimerAccumulatorList` crashes and `last-guest-pc` is
   informative** (grep the reported guest PC in `funcs_11.c`, confirm it's
   inside this function via the nearest-preceding `RECOMP_FUNC` line): read
   ~20 surrounding lines. This is a genuinely novel fault shape (bit-31-cleared
   guest address) — do not force the familiar `CACHE*_GUARD` deref-side/
   write-side shape or the large-garbage-offset framing onto it without reading
   the actual code first. Consider whether it resembles the KSEG0-zero-
   extension bug family (item -49, `0x80630062`) — NEXT.md's prior sessions
   flagged that family as confirmed DISTINCT from the `0x80000000`-exact family,
   but this address's bit-31-clear pattern has not been compared against it
   before; read that item's writeup before concluding either way.

5. **If `BREADCRUMB5`/`BREADCRUMB6`/`BREADCRUMB7`/`BREADCRUMB8` recur instead**:
   localize via `last-guest-pc` the same way `BREADCRUMB3`/`BREADCRUMB4` were
   localized — grep the guest PC in the owning `funcs_N.c` (`funcs_3.c`,
   `funcs_15.c`, `funcs_40.c`, `funcs_3.c` respectively). Any of these would be
   a first-ever informative hit — treat as high value.

6. **If `inflate_fast`/zlib recurs**: see s272's writeup (`PORTING-STATE` Session
   272) — not localizable via the simple breadcrumb-grep approach yet (system
   library, not a guest function).

7. **If a completely different crash lands**: note it, symrange-verify if
   plausible, don't chase it this iteration unless clearly highest-information-
   value (budget rule 8).

8. **If both soaks run fully clean with zero crashes**: this investigation has
   now recorded 3 fully-clean soaks across the last 2 sessions (s274 soak1,
   s275 soak2) but never a clean PAIR within one session. A 2/2 clean pair
   would be the first ever — note it explicitly, single-observation, do not
   conclude the investigation is near done from one session's clean pair.

## Do NOT do this iteration

- Do NOT run `fixup_game_funcs.py` twice in a row without deleting and
  regenerating `funcs_*.c` in between — silently duplicates every patch. Delete
  -> `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` ONCE, save output to
  a log file, grep the SAVED LOG (never re-run the script) to check
  multiplicities -> build.
- Do NOT spend a 3rd consecutive session re-soaking `BREADCRUMB5`,
  `BREADCRUMB6`, `BREADCRUMB7`, or `BREADCRUMB8` without a new angle — none is
  formally at the 3-strikes limit yet, but all four have weak-to-zero signal,
  and `tickWrappingTimerAccumulatorList` is a higher-information-value untried
  candidate.
- Do NOT re-touch `DEQUEUE_GUARD`'s range-check bound — refuted (s267).
- Do NOT conflate the `0x80000000`-exact-fault family (or its `+0x10`
  `processSceneNode`-`+0x30`, `emitAllocatedDLCommand`-garbage-offset,
  `inflate_fast`-`+3`, `static_5_800AB658`-garbage-offset, or
  `tickWrappingTimerAccumulatorList`-bit31-clear variants) with item -49's
  KSEG0-zero-extension bug (`0x80630062`) without actually reading that item's
  writeup first — the new bit-31-clear pattern is close enough in shape to
  warrant a careful read, not an assumption either way.
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11`/`x12` = `0x0000000300000000` or
  `0x0000000080000000` as crash-matching evidence for ANYTHING — constant
  RDRAM base pointer / constant register value seen across many unrelated
  crashes.
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
- Compound shell commands using `cd` combined with `&&`/output-redirection
  require interactive approval and get denied under the loop's automation —
  issue `cd <dir>` as its OWN Bash call first (cwd persists across calls in
  this tool), then run the next command as a separate call from that cwd.
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
  Mach-O symtab walk (inline python, see s273/s274/s275's approach: parse
  LC_SYMTAB, sort `(n_value, name)` pairs by DISTINCT address, find the
  exact-name entry, check the reported crash offset is less than the distance
  to the next DISTINCT address — duplicate symtab entries at the same address
  are common, dedupe by address before computing "next symbol" or the range
  check false-negatives). System-library crashes (like `inflate_fast`) resolve
  via the OS's own dyld symbol table and don't need/support the same check.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the crashing
  function is ITSELF breadcrumbed. Always grep the reported guest PC's hex
  label in the relevant `funcs_N.c` and find its enclosing `RECOMP_FUNC`
  before trusting it. `0x8000b650` specifically is a recurring stale value
  belonging to `beginFrameDLChunk` (`funcs_3.c`), seen in s272/s273/s274/s275
  for crashes that happen elsewhere — do not treat it as informative unless
  the crashing symbol IS `beginFrameDLChunk`.
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
- `CURRENT-TRUTH.md` is far over the ~35KB target — now 16+ consecutive
  sessions overdue for a pruning pass. Still not this iteration's job unless
  the localization work above is a quick null with clear leftover budget.
