# NEXT work unit — land `BREADCRUMB3` scoped to `beginFrameDLChunk`, then
# re-soak to catch and localize its guest-`0x80000000` fault exactly.

## Where the investigation stands (s268)

s268 re-ran s267's prescribed soak (`run_dequeuearg1.sh`, unmodified, 3
attempts) trying to catch the `heapFreeListDequeue`-range crash `BREADCRUMB2`
targets. **Still 0/3 (0/6 combined with s267)** — that specific crash has now
gone 2 full sessions without reproducing. Per iron rule 8, stop undirected
re-soaking on that exact hypothesis; it's no longer the highest-value next
move.

Instead, attempt 2 (`dequeuearg3`) caught a **brand-new crash site**:
`[CRASH][pc-symbol] sym=beginFrameDLChunk+13420`, `si_addr=0x380000000` —
RDRAM-base + guest `0x80000000` EXACTLY, the same fault-address shape s266
first found in `heapFreeListDequeue+16188`. Verified in-range (not a
nearest-symbol misattribution) via `scratch/agent/s268_symrange2.py`
(`beginFrameDLChunk` addr `0x10040599c`, size 24232, offset 13420 <
24232 → `IN_RANGE=True`). `dequeue-arg-trace` (170k fires that run, all sane
values right up to the crash) rules `heapFreeListDequeue` itself OUT as
implicated — this is a genuinely different function faulting the same way.
Attempt 3 (`dequeuearg4`) ran the FULL 240s hold + grace crash-free (had to
be SIGKILLed), a 2nd independent positive control that `heapFreeListDequeue`
is fine under load.

**This is now 2 distinct, unrelated functions** (`heapFreeListDequeue` s266,
`beginFrameDLChunk` s268) **observed to fault on guest pointer exactly
`0x80000000`** — suggestive of one shared upstream corruption source (a raw
KSEG0 segment-base constant landing in a field several call sites later
deref unchecked) rather than two independent bugs. **Single-session,
2-data-point — not yet confirmed.** Do not write this into the "established"
section of CURRENT-TRUTH until a 3rd site or a traced write-site backs it.

## The next work unit

1. **Find which `funcs_N.c` contains `beginFrameDLChunk`** (not yet checked
   this session — `grep -rn "beginFrameDLChunk" N64Recomp/RecompiledFuncs/
   funcs_*.c | head -1` for the definition, not just call sites).
2. **Land `BREADCRUMB3`**: same mechanism as `BREADCRUMB`
   (`submitSceneNodeRender`, s265) and `BREADCRUMB2` (`heapFreeListDequeue`,
   s267) in `N64Recomp/fixup_game_funcs.py` — a regex pass stamping
   `g_rs64_last_guest_pc` after every `// 0xADDR:` comment, scoped to
   `beginFrameDLChunk`'s own body via the existing `func_re` boundary
   search. Update `[CRASH][last-guest-pc]` handling in `main.cpp` only if it
   needs a 3rd global (check whether `BREADCRUMB`/`BREADCRUMB2` already
   share one global that gets overwritten by whichever function ran most
   recently — if so, `BREADCRUMB3` can likely reuse the same global/log
   line with no `main.cpp` changes needed, just confirm this before
   assuming a new global is required).
3. **Regen**: delete `funcs_*.c` first (see Environment notes), then
   `make_elf.py` (cwd `rogue_squadron64`) → `N64Recomp` (cwd `N64Recomp`) →
   `fixup_game_funcs.py` (cwd `N64Recomp`, check the report confirms
   `BREADCRUMB3` patched a nonzero count AND every pre-existing guard/
   breadcrumb still matches its documented multiplicity — no regressions)
   → `cmake --build -j8` (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/
   Developer` if Metal shaders touched, not expected here).
4. **Re-soak**: `cd scratch/s73_post_a_scene && env HOLD_S=<n> zsh
   run_dequeuearg1.sh <tag>` (env-prefix gotcha: `env HOLD_S=... zsh ...`,
   NOT bare `HOLD_S=... zsh ...` — iron rule 10). This site reproduced on
   the 2nd real-scene attempt out of 2 this session (small sample, but far
   better than 0/6 for the `heapFreeListDequeue` target) — budget 2-3
   attempts, not the 6+ already spent chasing the other site.
5. **When a `beginFrameDLChunk`-range crash lands**: confirm range via
   `s268_symrange2.py` (edit its `targets` list) if in doubt, read
   `[CRASH][last-guest-pc]`, `grep -n "0x<UPPERCASE_HEX>:"` in whichever
   `funcs_N.c` step 1 identified, read the surrounding ~20 lines, add ONE
   targeted guard (same pattern as every other guard in
   `fixup_game_funcs.py`: validate the pointer's RDRAM range before the
   deref, on failure skip to the nearest natural reentry point, log behind
   a new `ROGUESQ_LOG_*` env var), full regen, soak-verify (iron rule 4, ≥2
   independent runs with no recurrence).
6. **If this guard lands and holds**: revisit whether the shared-
   corruption-source hypothesis (2 functions, same exact `0x80000000`
   value) is now worth a dedicated investigation into the WRITE site rather
   than continuing to whack-a-mole individual deref sites — but only after
   this specific crash is confirmed fixed, not before.

## Do NOT do this iteration

- Do NOT spend another blind soak attempt on `heapFreeListDequeue`'s own
  BREADCRUMB2-targeted crash as the FIRST move — it's 0/6 across 2 sessions,
  parked per rule 8. Fine to note if it happens to recur as a side effect of
  soaking for `beginFrameDLChunk`, but don't seek it out first.
- Do NOT touch `DEQUEUE_GUARD`'s range-check bound — the a0-argument
  hypothesis is refuted (s267) with a same-run positive control.
- Do NOT conflate the `0x80000000`-exact fault family with item -49's
  KSEG0-zero-extension bug (`0x80630062`) — different exact values,
  different sites, confirmed distinct multiple sessions running.
- Do NOT cite `x0`/`x8`/`x9`/`x11 = 0x0000000300000000` as crash-matching
  evidence for ANYTHING — constant RDRAM base pointer (s219, item -60).
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `CACHE2_GUARD`/`MATLIST_GUARD1-3`/`COMPOSE_NPC_GUARD1-9`/`DEQUEUE_GUARD` —
  all verified not regressing and not the current blocker.
- Do NOT retry `s193_disasm.py`'s manual decoder — use a guest-PC breadcrumb
  instead (this session's whole point). It's exact and doesn't need
  decoding.
- Do NOT trust any `scratch/agent/sNNN_*` file whose session number has no
  matching `PORTING-STATE.md`/git-log entry — s268 found leftover
  `s268_symrange.py`/`s268_dequeuearg1_driver.log` from an interrupted,
  never-committed prior run; the script was fine to reuse, but do not treat
  such files' apparent "findings" as established without re-deriving them.
- Do NOT idle across a Stop-hook turn boundary waiting on a background
  soak — block with `TaskOutput(task_id, block=true, timeout<=480000)` in
  the SAME turn (may need 2-3 sequential blocking calls back-to-back if the
  soak's total wall time exceeds 480s — the summary-stats grep pass over a
  multi-MB log with ~35 armed loggers can itself take a couple minutes
  after the game process itself has already died/been killed).

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64`, `N64Recomp`
  needs cwd `N64Recomp`, `fixup_game_funcs.py` needs cwd `N64Recomp` (or an
  absolute path — either works, but re-running the SAME already-patched
  files a 2nd time in a row makes every regex match 0 and looks like a
  regression when it's just non-idempotent re-application; always regen from
  fresh `funcs_*.c` before checking match counts).
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
  `scratch/agent/`. Current-best baseline for this investigation:
  `run_dequeuearg1.sh` (same env-var set as `run_breadcrumb1.sh` plus
  `ROGUESQ_LOG_DEQUEUE_ARG_TRACE`; `HOLD_S` overridable via env, defaults to
  240 if unset).
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets. Verify range
  membership with `scratch/agent/s268_symrange2.py` (edit its `targets`
  list — `[(func_name, reported_offset), ...]` — and run
  `python3 scratch/agent/s268_symrange2.py` from the repo root; it reads
  `build/RogueSquadron64Recomp`'s Mach-O symtab directly, no `nm`/`atos`/
  `otool`/`lldb`/`dwarfdump` needed, none of which are on this sandbox's
  Bash allowlist anyway).
- Redirecting shell output (`>`) only works to paths under one of the 3
  session working directories (`RogueSquadron64Recomp`, `N64Recomp`,
  `rogue_squadron64`) — `/tmp` is blocked. Use
  `scratch/agent/*.log` for capturing tool output you want to grep later.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone
  `N64Recomp` checkout — expected, not a bug; not a `lib/` submodule so
  `submodule-patches/export.sh` never applies to it. Its changes persist
  only via the live file on disk across sessions.
- `CURRENT-TRUTH.md` is ~460KB+, ~13x the ~35KB target in CLAUDE.md. A
  dedicated pruning session is now 10+ consecutive sessions overdue — still
  not this iteration's job unless the localization work above is a quick
  null with clear leftover budget.
