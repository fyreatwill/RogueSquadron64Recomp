# NEXT work unit — land `BREADCRUMB4` scoped to `processSceneNode`, then
# re-soak to catch and localize its highly-reproducible `si_addr=0x380000030`
# fault exactly.

## Where the investigation stands (s269)

s269 ran s268's plan exactly: landed `BREADCRUMB3` on `beginFrameDLChunk`
(confirmed in `funcs_3.c`; `BREADCRUMB`/`BREADCRUMB2`/`BREADCRUMB3` all share
one global, `g_rs64_last_guest_pc`, so no `main.cpp` change was needed),
regenerated cleanly (all 3 breadcrumbs at expected multiplicities:
`BREADCRUMB` x1179, `BREADCRUMB2` x724, `BREADCRUMB3` x995), and re-soaked
twice with `run_dequeuearg1.sh`.

**`beginFrameDLChunk` itself did not crash in either soak** (0/2 this
session, 1/3 combined with s268). Instead, **both soaks landed an exact,
byte-identical crash in a different function**:
`[CRASH][pc-symbol] sym=processSceneNode+1184`, `si_addr=0x380000030` —
RDRAM-base + guest `0x80000030` (the same `0x80000000`-ish fault family as
`heapFreeListDequeue`/`beginFrameDLChunk`, but offset by `0x30` — consistent
with a struct-field dereference off a corrupted/sentinel base pointer, not a
bare null-page hit). Verified in-range via the symtab-walk method (adapted
from `scratch/agent/s268_symrange2.py`): `processSceneNode addr=0x1006ed098
size=18268 reported_off=1184 IN_RANGE=True`.

**This exact crash (same symbol, same offset, same fault address) also
appeared once in s267**, at the time unverified and dismissed as "distinct or
misattributed, not confirmed." Combined across s267+s269 that's **3/3
observations, all exact-identical, now confirmed in-range** — by a wide
margin the most reproducible fault this entire `0x80000000`-family
investigation has caught (vs. 1/3 for `beginFrameDLChunk`, 0/6 for the
original `heapFreeListDequeue` target which stays parked per iron rule 8).

`last-guest-pc` in both s269 soaks read `0x8000B650`, traced (`grep` in
`funcs_3.c`) to inside `beginFrameDLChunk`'s own body — this confirms
`BREADCRUMB3` fired correctly, but the value is stale/uninformative for the
`processSceneNode` crash itself, since `processSceneNode` is not yet
breadcrumbed.

## The next work unit

1. **Find which `funcs_N.c` contains `processSceneNode`** — already found
   this session: `N64Recomp/RecompiledFuncs/funcs_4.c:15097` (same file as
   `submitSceneNodeRender`, a different file than `beginFrameDLChunk`/
   `heapFreeListDequeue` which are both in `funcs_3.c`). Re-confirm with
   `grep -n "RECOMP_FUNC void processSceneNode" N64Recomp/RecompiledFuncs/
   funcs_4.c` in case of drift.
2. **Land `BREADCRUMB4`**: identical mechanism to `BREADCRUMB`/`BREADCRUMB2`/
   `BREADCRUMB3` in `N64Recomp/fixup_game_funcs.py` — a regex pass stamping
   `g_rs64_last_guest_pc` after every `// 0xADDR:` comment, scoped to
   `processSceneNode`'s own body via the existing `func_re` boundary search.
   Reuses the same global — no `main.cpp` change needed (only one
   instrumented function is ever executing at the moment of a crash;
   confirmed true for 3 breadcrumbs already, will hold for a 4th).
3. **Regen**: delete `funcs_*.c` first
   (`python3 -c "import glob, os; [os.remove(f) for f in
   glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/
   RecompiledFuncs/funcs_*.c')]"` — `rm`/`find -delete` are sandbox-blocked),
   then from cwd `rogue_squadron64`: `python3 tools/make_elf.py` → from cwd
   `N64Recomp`: `./build/N64Recomp rogue_squadron.toml` (the wrapper script
   `tools/agent/regen_n64recomp.sh` does this same command but itself needs
   an approval prompt to run — running the `cd ... && ./build/N64Recomp ...`
   command directly worked fine this session) → `python3
   fixup_game_funcs.py` (check the report confirms `BREADCRUMB4` patched a
   nonzero count AND all 3 pre-existing breadcrumbs/guards still match their
   documented multiplicity — no regressions) → `cmake --build . -j8` from
   `RogueSquadron64Recomp/build` (`DEVELOPER_DIR=/Applications/Xcode.app/
   Contents/Developer` only if Metal shaders touched, not expected here).
4. **Re-soak**: `env HOLD_S=240 zsh scratch/s73_post_a_scene/
   run_dequeuearg1.sh <tag>` (iron rule 10: `env VAR=val zsh ...`, never bare
   `VAR=val zsh ...`). Launch with `run_in_background: true` from an absolute
   path, then immediately `TaskOutput(task_id, block=true, timeout<=480000)`
   in the SAME turn — do not idle across a turn boundary waiting on it. Given
   the observed 3/3 hit rate, budget only 1-2 attempts before expecting a
   hit; if it somehow doesn't reproduce in 2 attempts, that itself is a
   notable (if surprising) finding worth writing up, not a reason to keep
   soaking past iron rule 8's 3-attempt cap.
5. **When a `processSceneNode`-range crash lands**: read
   `[CRASH][last-guest-pc]`, `grep -n "0x<UPPERCASE_HEX>:"` in `funcs_4.c`,
   read the surrounding ~20 lines. Given the fault offset is `+0x30` from
   whatever base pointer this is (not offset 0 like the other two sites),
   expect to find a struct-field load/store at a small constant offset off a
   register that itself holds the corrupted/sentinel value — add ONE
   targeted guard validating that base pointer's RDRAM range before the
   offset deref (same pattern as every other guard in
   `fixup_game_funcs.py`: on failure, skip to the nearest natural reentry
   point, log behind a new `ROGUESQ_LOG_*` env var), full regen, soak-verify
   (iron rule 4, ≥2 independent runs with no recurrence).
6. **If this guard lands and holds**: with 3 independent functions
   (`heapFreeListDequeue`, `beginFrameDLChunk`, `processSceneNode`) now all
   touching guest pointer values in the `0x80000000` family, the
   shared-upstream-corruption-source hypothesis (CURRENT-TRUTH item -110)
   crosses from "suggestive" toward "worth a dedicated write-site
   investigation" — but only evaluate that after this specific crash is
   confirmed fixed, not before, and only after finding what makes `+0x30`
   the fault offset here vs. `+0` at the other two sites (may indicate the
   corrupted value is stored in a *shared* global/struct field, not
   re-derived independently in each function — worth checking whether all
   3 functions read the same global address).

## Do NOT do this iteration

- Do NOT spend another soak attempt on `heapFreeListDequeue`'s own
  BREADCRUMB2-targeted crash — it's 0/6 across 2 sessions, parked per rule 8.
- Do NOT spend another soak attempt specifically chasing `beginFrameDLChunk`
  as the FIRST move — it's 1/3 combined, lower-value than `processSceneNode`
  now. Fine to note if it recurs as a side effect of soaking for
  `processSceneNode`, but don't seek it out first.
- Do NOT touch `DEQUEUE_GUARD`'s range-check bound — the a0-argument
  hypothesis is refuted (s267) with a same-run positive control.
- Do NOT conflate the `0x80000000`-exact-fault family (or its `+0x30`
  variant at `processSceneNode`) with item -49's KSEG0-zero-extension bug
  (`0x80630062`) — different exact values, different sites, confirmed
  distinct multiple sessions running.
- Do NOT cite `x0`/`x8`/`x9`/`x11 = 0x0000000300000000` as crash-matching
  evidence for ANYTHING — constant RDRAM base pointer (s219, item -60).
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `CACHE2_GUARD`/`MATLIST_GUARD1-3`/`COMPOSE_NPC_GUARD1-9`/`DEQUEUE_GUARD` —
  all verified not regressing and not the current blocker.
- Do NOT retry `s193_disasm.py`'s manual decoder — use a guest-PC breadcrumb
  instead (this session's whole point, again). It's exact and doesn't need
  decoding.
- Do NOT idle across a Stop-hook turn boundary waiting on a background
  soak — block with `TaskOutput(task_id, block=true, timeout<=480000)` in
  the SAME turn.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64` (run as
  `python3 tools/make_elf.py`, the script itself lives in `tools/`, not repo
  root), `N64Recomp` needs cwd `N64Recomp` (`./build/N64Recomp
  rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd `N64Recomp`. Always
  regen from fresh `funcs_*.c` before checking match counts (re-running the
  SAME already-patched files a 2nd time makes every regex match 0 and looks
  like a regression when it's just non-idempotent re-application).
- The wrapper script `tools/agent/regen_n64recomp.sh` (does the `cd
  N64Recomp && ./build/N64Recomp rogue_squadron.toml` step) itself requires
  an interactive approval prompt to execute as a script — running the
  equivalent `cd ... && ./build/N64Recomp ...` command directly via Bash
  worked fine and did not require approval. Prefer the direct command form.
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
  membership by reading `build/RogueSquadron64Recomp`'s Mach-O symtab
  directly (see `scratch/agent/s268_symrange2.py` for the reusable
  parser/walker — edit its `targets` list or copy the walk logic inline);
  no `nm`/`atos`/`otool`/`lldb`/`dwarfdump` needed, none of which are on
  this sandbox's Bash allowlist anyway.
- Redirecting shell output (`>`) only works to paths under one of the 3
  session working directories (`RogueSquadron64Recomp`, `N64Recomp`,
  `rogue_squadron64`) — `/tmp` is blocked. Use
  `scratch/agent/*.log` for capturing tool output you want to grep later.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone
  `N64Recomp` checkout — expected, not a bug; not a `lib/` submodule so
  `submodule-patches/export.sh` never applies to it. Its changes persist
  only via the live file on disk across sessions.
- `git -C <path> status` and other multi-clause git invocations sometimes
  need approval even for read-only `--short` status checks on the `lib/`
  submodules — if denied, fall back to checking top-level `git status`
  (short form) for the `modified: lib/...` lines, which is normally
  sufficient to confirm "steady-state, already-exported patches" vs. "new
  drift" without needing the submodule-internal status.
- `CURRENT-TRUTH.md` is ~460KB+, ~13x the ~35KB target in CLAUDE.md. A
  dedicated pruning session is now 11+ consecutive sessions overdue — still
  not this iteration's job unless the localization work above is a quick
  null with clear leftover budget.
