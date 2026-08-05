# NEXT work unit

## s366: Thread A CLOSED, background-noise entry added, drainMeshReleaseQueue audit found exhaustive

Session-start mechanical check (the standing gotcha) found `s364_coalesceheapbailfix_reverify1/2` had
already drained — NEXT.md said "still pending." Both crashed off-target (`coalesce_guard_fire_n=0`
both, `pc-symbol=heapWalker+1696`, `last-guest-pc=0x8000834c` byte-identical). Source cross-check:
`0x8000834c` is `drainMeshReleaseQueue`'s own final checkpoint (`nop` before `return`) — the function
completed normally, crash is genuinely downstream inside `heapWalker`. Cataloged as new
background-noise entry (n=2, guest code, do NOT chase — only escalate at a 3rd independent hit).

**Closed `m5-audio-destub-coalesce-heap-guard-verify` (Thread A)**: 6 soaks post-s358-fix
(`s358_verify1/2`, `s362_reverify1/2`, `s364_reverify1/2`), zero `coalesceFreeHeapBlocks` hits,
including one 432s clean full-hold. No more soaks queued for this thread. Reopens only if
`coalesceFreeHeapBlocks+1052`/`0x80002358` ever recurs (would mean the s358 fix regressed).

Also ran a proactive full-function idiom-class audit of `drainMeshReleaseQueue` (source-read, no
build/run) cross-referencing every table-/list-loaded-pointer dereference against the 3 known
families × 5 loops. Found and hand-verified ONE syntactically-bare-but-provably-safe read per loop
(the loop-back "advance cursor" read, e.g. `funcs_3.c:1768`) — safe by loop invariant (pointer always
pre-validated by the head guard or the previous iteration's tail-scan guard before this line). **No
new unguarded family found — coverage reads as exhaustive.**

## One open thread

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 10 — its own `s365` pair still
queued, not yet drained; s366 added a static exhaustiveness result while waiting).**
- `s365_drainmeshtailptrguard_verify1/2.sh` is now the ONLY pending pair in `scratch/agent/soak_queue/`
  (Thread A's queue entries are gone — closed, nothing left to drain for it). Confirm at session start
  with `grep -c s365_drainmeshtailptrguard scratch/agent/SOAK-RESULTS.md` (expect 0 if truly still
  queued — but CHECK, don't trust this file's claim, per the now-7-session-running stale-NEXT.md
  gotcha).
- **Decision tree when it drains** (unchanged from s365, now reinforced by s366's static audit):
  - `tailptr{n}_guard_fire_n>=1` for ANY n: first positive control for the global-tail-pointer guards.
  - Crash still at `drainMeshReleaseQueue+5564`/`0x8000821C` with all tailptr guards at 0: the regex
    substitution didn't actually match — re-check regenerated `funcs_3.c` for the literal patched
    text.
  - Crash moved to a DIFFERENT `drainMeshReleaseQueue` offset with a tailptr guard firing: guard
    engaged but didn't close the gap — but s366's audit found no further candidate site, so if this
    happens, treat it as evidence the audit MISSED something and re-read the function fresh rather
    than assuming another sibling of the 3 known families.
  - Crash moved OUTSIDE `drainMeshReleaseQueue` entirely, or the run is CLEAN: given s366's static
    audit ALSO found no further gap, **this result plus one more non-recurrence soak would be enough
    to call Thread B's `drainMeshReleaseQueue` question closed** (two independent lines of evidence:
    static exhaustiveness + empirical non-recurrence) — write the closure explicitly rather than
    queuing indefinite further verify pairs.
  - Cross-check `last_pc_symbol`/`last-guest-pc` against the background-noise catalogue (now 3
    entries, see below) before discarding an off-target result as uninformative.

## Background-noise catalogue (do NOT escalate reactively — 3rd independent hit is the trigger)

- `trackResourceListWithMappingTables+1192` — n=2 (s347, s362's `s360_..._verify1`). Apple-framework
  `dladdr` fallback, host code.
- `unregisterServiceWorker+536` — n=2 (Session 265, s362's `s360_..._verify2`). Apple-framework
  `dladdr` fallback, host code.
- `fscache_insert_and_retain+1192` — KNOWN, separately catalogued Metal shader-compiler system crash
  (item -10, first seen s270). Not part of the n=2/n=3 counting above (own older history).
- **NEW (s366): `heapWalker+1696`** — n=2 (both `s364` verify runs, byte-identical
  `last-guest-pc=0x8000834c`), **guest code** (part of the old s150-219 whack-a-mole chase but a
  genuinely new offset), always immediately following a CLEAN `drainMeshReleaseQueue` return. Do not
  chase; a 3rd independent hit crosses into "worth `s264_symrange.py`/`s193_disasm.py` confirmation."

## Notes carried forward (all still current)
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (guest checkpoint,
  only meaningful if the crashing function is breadcrumbed) answer different questions by design — and
  as s366 showed, a stale-but-valid `last-guest-pc` from a FUNCTION THAT ALREADY RETURNED can look like
  it implicates that function when it doesn't; always check whether the guest-pc value is a function's
  own exit checkpoint before assuming it's mid-execution.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` -- matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- A crash under ~5s that never reaches `title_reached` is NOT a meaningful test of any post-title-window
  instrument -- don't count it toward a non-recurrence tally.
- **Regen-reliability gotcha (item -20)**: `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c`
  that already exists on disk -- ALWAYS delete all `funcs_*.c` before re-running `N64Recomp`. Use
  absolute-path flat `rm -f` calls (no glob, no cd, no compound for/xargs) per the sandbox matcher.
- **Implementation gotcha**: `re.subn`'s plain-string `repl` gets backslash-escape-processed by `re` --
  ALWAYS use a lambda callback for multi-line replacement text; verify by grepping the regenerated `.c`
  for the new text on one line.
- **Guard-bail-target gotcha (s358)**: a synthetic-value guard's branch target can be a loop's
  re-entry label, not an exit -- verify the CONTROL PATH, not just that a branch exists.
- **Read-guard/write-guard sibling gotcha (recurred 3x across pointer families in this one function)**:
  a guard on a READ through a corrupted pointer does not repair the pointer -- if reused UNGUARDED
  later (especially a WRITE), the crash moves there. When defining an idiom class, grep for the
  DATA-FLOW pattern, not just one syntactic shape.
- **Off-target-but-discriminating gotcha (recurred 6+ sessions)**: a soak's own "inconclusive" verdict
  for its target question can still be highly informative for a DIFFERENT open thread or the
  background-noise catalogue -- always cross-check `last_pc_symbol`/`last-guest-pc` against ALL open
  threads, not just the recipe's own named target.
- **Stale-NEXT.md gotcha (recurred SEVEN sessions running, s360-s366)**: NEXT.md can claim a queued
  pair is "still pending" when `SOAK-RESULTS.md` already shows it drained. Mechanical check every
  session, before trusting any "still pending" claim: `grep -c '<recipe-basename>'
  scratch/agent/SOAK-RESULTS.md`.
- **Guard fire_n=0 is itself informative, not just "didn't matter" (s361)**: check for short-circuit
  paths around a guarded loop body that bypass the guard's own instrumentation while still feeding an
  unvalidated pointer downstream.
- **Soak-queue drain order (resolved s362)**: `tools/agent/loop.sh` drains `"$qdir"/*.sh` via bash's
  default lexicographic glob — alphabetical = chronological for `sNNN_..._verifyM.sh` naming.

## Queued, ready for the loop

`s365_drainmeshtailptrguard_verify1/2.sh` — only pair in the queue, drains next gap (up to 2 recipes
per gap, so both should drain together).

HYPOTHESIS-ID: m5-audio-destub-linkedlist-corruption-source (iteration 10 — Thread A closed as a
sibling result; Thread B itself is one static audit closer to closure, awaiting its own pair's drain).
