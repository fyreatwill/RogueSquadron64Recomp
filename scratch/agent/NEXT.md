# NEXT work unit

## s367: Thread B's `s365` pair drained — 1 genuine non-recurrence banked, 1 more queued

Session-start mechanical check found `s365_drainmeshtailptrguard_verify1/2` had already drained
(`grep -c s365_drainmeshtailptrguard scratch/agent/SOAK-RESULTS.md` → 2). Read both logs directly.

- `verify1`: **CLEAN**, full 446s hold, `title_reached` at 45.2s, and for the first time in the whole
  s350-367 arc EVERY guard fire counter (coalesce, read/write, loop2-5, head1-5+clears, tailptr1-5,
  ring) was 0. A genuine non-recurrence data point that reached and passed through title.
- `verify2`: crashed in <5s, `title_reached` blank (never reached title) — per the standing rule this
  doesn't count either way. Crash was `pc-symbol=musyxSynthFrame+4652`, an unrelated pre-title
  audio-boot crash in a different subsystem. Its `last-guest-pc=0x8000834c` coincidentally matches the
  s366 `heapWalker+1696` background-noise checkpoint value — checked source, confirmed this is just
  the global "last breadcrumb hit" var persisting from a prior call, not a real link between the two
  crash families. Not added to the background-noise catalogue (has its own unambiguous symbol).

**Net**: 1 of the 2 non-recurrence soaks Thread B's closure bar calls for (static exhaustiveness audit
already done s366; empirical non-recurrence now at 1/2). Queued
`s367_drainmeshtailptrguard_verify3.sh` / `s367_drainmeshtailptrguard_verify4.sh` — same recipe,
`HOLD_S=240`, all current guard instruments armed — for the second data point.

## One open thread

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 11 — its own `s367` pair now
queued, not yet drained).**
- `s367_drainmeshtailptrguard_verify3/4.sh` are the ONLY pending pair in
  `scratch/agent/soak_queue/`. Confirm at session start with `grep -c s367_drainmeshtailptrguard
  scratch/agent/SOAK-RESULTS.md` (expect 0 if truly still queued — but CHECK, don't trust this file's
  claim; this gotcha has now recurred EIGHT sessions running, s360-s367).
- **Decision tree when it drains**:
  - Both CLEAN or both crash OUTSIDE `drainMeshReleaseQueue` **and both reach title** (check
    `title_reached` is non-blank in each — a <5s pre-title crash does NOT count as a data point,
    re-queue instead of counting it): **Thread B CLOSES.** Two independent lines of evidence are then
    complete — s366's static exhaustiveness audit (no further unguarded family found by source
    inspection) + 2 empirical non-recurrence soaks (`s365_verify1` + one of `s367_verify3/4`). Write
    the closure explicitly in CURRENT-TRUTH; the M5 Step 5 investigation would then have NO open
    threads (Thread A closed s366, Thread B closes here) — re-evaluate what M5's next step is (return
    to the design doc's step 6, or re-scope per the M5-AUDIO-PLAN.md sequence) rather than inventing a
    new drainMeshReleaseQueue probe.
  - Any `tailptr{n}_guard_fire_n>=1`, any `head{n}_guard_fire_n`/`_clear_guard_fire_n>=1`, or any
    `loop{n}_guard_fire_n`/`_write_guard_fire_n>=1`: a guard fired — do NOT close. This is either the
    first positive control for one of the newer guard families, or evidence the coverage isn't as
    exhaustive as s366 concluded. Re-read the function fresh rather than assuming a known family.
  - Crash still at `drainMeshReleaseQueue+5564`/`0x8000821C` with all tailptr guards at 0: the regex
    substitution didn't actually match — re-check regenerated `funcs_3.c` for the literal patched
    text.
  - Another <5s pre-title crash: still uninformative, don't count it — re-queue a fresh pair rather
    than treating it as data.
  - Cross-check `last_pc_symbol`/`last-guest-pc` against the background-noise catalogue below before
    discarding an off-target result as uninformative for other open questions.

## Background-noise catalogue (do NOT escalate reactively — 3rd independent hit is the trigger)

- `trackResourceListWithMappingTables+1192` — n=2 (s347, s362's `s360_..._verify1`). Apple-framework
  `dladdr` fallback, host code.
- `unregisterServiceWorker+536` — n=2 (Session 265, s362's `s360_..._verify2`). Apple-framework
  `dladdr` fallback, host code.
- `fscache_insert_and_retain+1192` — KNOWN, separately catalogued Metal shader-compiler system crash
  (item -10, first seen s270). Not part of the n=2/n=3 counting above (own older history).
- `heapWalker+1696` — n=2 (both `s364` verify runs, byte-identical `last-guest-pc=0x8000834c`), guest
  code, always immediately following a CLEAN `drainMeshReleaseQueue` return. Do not chase; a 3rd
  independent hit crosses into "worth `s264_symrange.py`/`s193_disasm.py` confirmation." (s367 found a
  same-guest-pc-value crash that is NOT this family — see below — do not conflate the two.)
- **NEW (s367, informational, NOT added to the escalation-counted list)**: `musyxSynthFrame+4652`,
  pre-title (<5s), `last-guest-pc=0x8000834c`. Shares the same guest-pc checkpoint value as
  `heapWalker+1696` above purely because that checkpoint is a global "last breadcrumb hit" variable
  that persists across calls — NOT evidence the two crash families are related. This one already has
  its own unambiguous host symbol (`musyxSynthFrame`) in a different subsystem (audio boot), so it
  gets its own tracking if it recurs rather than being folded into the `heapWalker+1696` count. n=1 so
  far.

## Notes carried forward (all still current)

- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (guest checkpoint,
  only meaningful if the crashing function is breadcrumbed) answer different questions by design — a
  stale-but-valid `last-guest-pc` from a function that already returned (or, as s367 showed, from a
  totally unrelated crash that just happens to share the last-written checkpoint value) can look like
  it implicates that function when it doesn't. Always check the actual `pc-symbol` before trusting a
  `last-guest-pc` match.
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
- **Stale-NEXT.md gotcha (recurred EIGHT sessions running, s360-s367)**: NEXT.md can claim a queued
  pair is "still pending" when `SOAK-RESULTS.md` already shows it drained. Mechanical check every
  session, before trusting any "still pending" claim: `grep -c '<recipe-basename>'
  scratch/agent/SOAK-RESULTS.md`.
- **Guard fire_n=0 is itself informative, not just "didn't matter" (s361)**: check for short-circuit
  paths around a guarded loop body that bypass the guard's own instrumentation while still feeding an
  unvalidated pointer downstream.
- **Same-checkpoint-value ≠ same crash (s367, new)**: `last-guest-pc` breadcrumb variables are global
  and persist across calls/runs; two crashes sharing the same `last-guest-pc` value can be from
  completely unrelated subsystems if their `pc-symbol` (the actual host crash address) differs. Always
  check `pc-symbol` before treating a shared guest-pc as a pattern match.
- **Soak-queue drain order (resolved s362)**: `tools/agent/loop.sh` drains `"$qdir"/*.sh` via bash's
  default lexicographic glob — alphabetical = chronological for `sNNN_..._verifyM.sh` naming.

## Queued, ready for the loop

`s367_drainmeshtailptrguard_verify3.sh` / `s367_drainmeshtailptrguard_verify4.sh` — only pair in the
queue, drains next gap (up to 2 recipes per gap, so both should drain together).

HYPOTHESIS-ID: m5-audio-destub-linkedlist-corruption-source (iteration 11 — 1 of 2 non-recurrence
soaks banked toward Thread B's closure bar; the second pair is queued and, combined with s366's
static audit, would close the thread on the next drain if both come back clean/outside-function and
reach title).
