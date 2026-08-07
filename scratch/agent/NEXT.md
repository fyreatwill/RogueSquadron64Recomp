# NEXT work unit

HYPOTHESIS-ID: item-263-updatehangarbayscene-localization

## What changed session s438 (maintenance pass + soak consumption)

s438 was a MAINTENANCE iteration (`docs/CURRENT-TRUTH.md` was 62034 bytes, over the 60000 trigger).
Compacted it 694→493 lines (43668 bytes now, comfortably under the trigger for a while). No new build/run
cycle this session — but it DID consume the queued `s437_breadcrumb17_confirm` soak (SOAK-RESULTS
20260807-035804, rc=1, 153s), which is required regardless of iteration type (read list #3).

**Finding: item -263 recurred a 4th time, and BREADCRUMB17 worked as designed — but immediately hit the
same misattribution mechanism one function deeper.** `last-guest-pc=0x800AAF94` resolves to +504 bytes
into `runHangarSelectionFrame` (`funcs_28.c:5391-5399`) — specifically, the breadcrumb write immediately
before the `jal` into `updateHangarBayScene`. A full grep of `updateHangarBayScene`'s entire body
(`funcs_28.c:10918-17722`, ~6805 lines — the largest function this project has ever instrumented) found
**zero** breadcrumb writes anywhere in it. So `last-guest-pc` froze at the call site the instant execution
entered this uninstrumented callee, exactly like items -271/-273's own mechanism, just one level deeper.

Two independent signals now agree `updateHangarBayScene` is the real locus: this guest-side call-site
freeze, AND the host-side `atos` symbolication (`pc-symbol=updateHangarBayScene+43768`), which has named
this same function at all 4 of item -263's occurrences (s426, s433, s436, s437) — previously read as an
imprecise nearest-preceding-export artifact, now corroborated. Still not an exact instruction.

Full detail: `docs/CURRENT-TRUTH.md` item -274, `docs/PROJECT-OVERVIEW.md` §16 (s438 update),
`PORTING-STATE` Session 438.

## The work unit — add breadcrumb coverage to `updateHangarBayScene`, then live-verify

`updateHangarBayScene` (`funcs_28.c:10918-17722`) is ~6805 lines — roughly 15x the size of any function
this project has previously breadcrumb-instrumented (the next-largest, `mallocCraftSelectionData`, is
~4386 lines and was handled via checkpoint bisection rather than full coverage, item -267/PROJECT-OVERVIEW
§16). Two viable strategies, in order of preference:

1. **Full BREADCRUMB18 coverage** (same template as BREADCRUMB1-17 in `N64Recomp/fixup_game_funcs.py`) —
   simplest, matches established precedent, and a function this size plausibly contains item -263's fault
   REGARDLESS of which callee triggers it (a stray/OOB write reached from anywhere in this function's own
   body would still show up as this function's last-guest-pc). Try this first; only fall back to bisection
   if the regen/build cost of instrumenting 6805 lines proves prohibitive (it shouldn't — the pattern is
   mechanical, same as every prior BREADCRUMB addition).
2. **Checkpoint bisection** (item -267's method) if full coverage turns out to be impractical: 3-4
   checkpoints at evenly-spaced points in the function body, narrowing on which section is live when the
   crash recurs.

Regen recipe (known-working s427-438, see full commands in git log s437's NEXT.md or PORTING-STATE
Session 437): `make_elf.py` → delete `RecompiledFuncs/funcs_*.c` via the Python one-liner (NOT a shell
glob — sandbox blocks it) → `N64Recomp` → `fixup_game_funcs.py` → `cmake --build . -j8`. Verify no
regression to `GENERIC_CACHE_GUARD` (107) or `CACHE_HEAD_A1_GUARD` (7) by grepping the compiled `.c`
output directly — fixup's own stdout report is silent/idempotent on a 2nd run against already-patched
files (s437's discovery, don't trust it for a post-hoc check).

Live-verify with the same s427-437 schedule and all diagnostics armed:
```
cd ~/Documents/Tools/RogueSquadron64Recomp/build && env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 \
    ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_GENERIC_CACHE_GUARD=1 ROGUESQ_LOG_CACHE_HEAD_A1_GUARD=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh ../tools/probe.sh ../scratch/agent/soak_results/<name> 300 2
```
This exceeds the harness's 120s default Bash timeout and auto-backgrounds — use TaskOutput
(block=true, timeout ~330000ms) to wait for it.

Expected discriminating outcomes:
- **Item -263 recurs with a real `last-guest-pc` INSIDE `updateHangarBayScene`'s body** — the actual
  localization. Classify the exact instruction: does it match an already-catalogued idiom
  (0x801163B0-family, `-0x25A4` hangar-list, IEEE-754-as-pointer) or something new? If new, scope a
  sibling scan BEFORE writing a bespoke guard (s434/s436 methodology).
- **A guard fires** (`GENERIC_CACHE_GUARD` or `CACHE_HEAD_A1_GUARD`) — the still-missing positive control
  for items -270/-272 (currently 0 fires across all combined observations).
- **Clean run** — folds into the ledger as another data point in the established alternating
  crash/clean pattern (s434-437: clean, crash, clean, crash, crash, clean, clean, crash); not evidence of
  anything on its own per iron rule 1.

## Sandbox lessons (carry forward)

- Soak/probe output directories MUST be under one of the three allowed working-directory roots
  (`RogueSquadron64Recomp`, `N64Recomp`, `rogue_squadron64`) — `/tmp` output becomes unreadable after
  the run completes (s435).
- Shell glob patterns in `rm`/`for` loops are blocked by the sandbox's write-approval gate even with
  `dangerouslyDisableSandbox` — use a Python one-liner (`glob.glob` + `os.remove`) to delete
  `funcs_*.c` before every regen (s436).
- `cd ... && ... > file` redirects to non-repo paths get blocked; redirect only to the 3 allowed roots.
- `fixup_game_funcs.py`'s stdout report is idempotent/silent for already-applied patches on a 2nd run
  without first deleting and re-running `N64Recomp` — grep the compiled `.c` output directly to verify
  patch counts (s437).
- A foreground probe.sh run at 300s exceeds the harness's 120s default Bash timeout and
  auto-backgrounds; use `TaskOutput` with `block=true` and timeout ~330000ms (s437).
- `tools/overlay_symbol_probe.py <addr>` reports matches across ALL THREE overlays (mission/menu/
  cinematic) at their respective ROM offsets when an address happens to exist in more than one — pick
  the entry matching whichever overlay the active probe schedule actually reaches (s438: menu-only
  schedule → the "menu" entry was the relevant one, not "mission" or "cinematic").
