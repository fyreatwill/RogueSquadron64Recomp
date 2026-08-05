# NEXT work unit

## s365: Thread B's `s363` head-guard pair had ALREADY DRAINED (NEXT.md said "still pending" — the
## standing stale-NEXT.md gotcha, again). Read both logs: 2/2 byte-identical crash at a NEW offset
## (`drainMeshReleaseQueue+5564`, `last-guest-pc=0x8000821C`) with the s363 head guards
## positive-controlled for the first time (head1/head2 fired) plus every other known guard firing too.
## Source-read found a THIRD unguarded pointer family (a "global-tail" write-through, `ctx->r2`,
## checked only != 0) repeated once per loop, all 5 unguarded; guarded all 5
## (`[drain-mesh-loop{1..5}-tailptr-guard]`). Full regen+rebuild clean. Queued
## `s365_drainmeshtailptrguard_verify1/2.sh`. Full detail: `PORTING-STATE` Session 365,
## `docs/CURRENT-TRUTH.md` item -220.

## Two open threads

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (no change this session — its own `s364`
pair is still pending per SOAK-RESULTS.md's actual tail, confirmed via
`grep -c s364_coalesceheapbailfix_reverify1 scratch/agent/SOAK-RESULTS.md` = 0 hits at session start).**
- `s364_coalesceheapbailfix_reverify1/2.sh` queued in `scratch/agent/soak_queue/`, sorts to drain
  BEFORE this session's new `s365_...` pair (alphabetical: `s364` < `s365`).
- **Running tally going into s364's pair**: `s358_verify1/2` (2 soaks, off-target at
  `drainMeshReleaseQueue+5016`) + `s362_reverify1` (CLEAN, 432s full hold) + `s362_reverify2`
  (off-target, known `fscache_insert_and_retain` Metal-system-crash noise) = 4 soaks post-fix, ZERO
  hits on `coalesceFreeHeapBlocks` itself.
- **Decision tree when `s364_...` drains** (unchanged from s364): both non-target (CLEAN or
  off-target) → 6 consecutive non-recurrence soaks since the s358 fix, clean full-hold in the mix —
  strongly consider explicitly CLOSING this thread with a deliberate write-up next time it's picked
  up. `coalesce_guard_fire_n>=1` at `coalesceFreeHeapBlocks+1052`/`0x80002358` → the s358 bail-target
  fix did NOT hold, re-check for a stale build/reverted patch. `coalesce_guard_fire_n>=1` elsewhere or
  clean → fix confirmed via genuine positive control, ready to close. `coalesce_guard_fire_n>=1` at a
  NEW offset → a further unguarded site, same idiom, source-read and guard it.

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 9 — new evidence + a new guard
landed this session; its own `s365_...` pair not yet drained).**
- `s365_drainmeshtailptrguard_verify1/2.sh` queued in `scratch/agent/soak_queue/`, drains AFTER
  Thread A's `s364_...` pair (alphabetical FIFO: `s364` < `s365`).
- **These are BRAND-NEW instruments** (`tailptr{1..5}_guard_fire_n`, zero prior fire history) — any
  single fire is itself informative, not just a "didn't matter" null.
- **Decision tree when this pair drains** (full detail also in the recipe header):
  - `tailptr{n}_guard_fire_n>=1` for ANY n: first-ever positive control for the new global-tail-
    pointer guards — confirms this third pointer family is a genuinely reachable corruption surface.
    Note WHICH n fired (compare against which n fired for the head guards in s363 — same loop or
    different?).
  - Crash still at `pc-symbol=drainMeshReleaseQueue+5564` / `last-guest-pc=0x8000821C` with ALL
    tailptr guards at 0: the regex substitution didn't actually match what's running — re-check the
    regenerated `funcs_3.c` for the literal patched text.
  - Crash moved to a DIFFERENT `drainMeshReleaseQueue` offset, with a tailptr guard's fire_n>=1:
    guard engaged but didn't fully close the gap — re-read for a further sibling. Candidate to check
    first: does clearing/skip-writing through `ctx->r2` leave a STALE value read again downstream the
    way the head-pointer clear-guard needed its own separate pass in s363?
  - Crash moved OUTSIDE `drainMeshReleaseQueue` entirely, or run is CLEAN: promising, but needs 2-3
    more non-recurrence soaks before calling this specific site closed.
  - Cross-check `last_pc_symbol`/`last-guest-pc` against Thread A's `coalesceFreeHeapBlocks` question
    and the background-noise catalogue below before discarding an off-target result as uninformative.
  - **If BOTH this pair AND a future audit turn up no further unguarded pointer family in
    `drainMeshReleaseQueue`, consider whether the function's guard coverage is now exhaustive** — three
    pointer families (tail-scan cursor, head pointer, global-tail) times 5 structurally identical
    loops is a lot of surface area; a clean sweep after this pair is meaningfully stronger evidence
    than after the head-pointer pair alone.

## Third, deliberately-not-chased thread (background noise, do not escalate reactively)

Three crash symbols now catalogued as background noise, none escalated per the strategic directive's
"no reactive single-crash chases" outside the active M5 threads:
- `trackResourceListWithMappingTables+1192` — n=2 (s347, s362's `s360_..._verify1`).
- `unregisterServiceWorker+536` — n=2 (Session 265, s362's `s360_..._verify2`).
- `fscache_insert_and_retain+1192` — a KNOWN, already-catalogued Metal shader-compiler system crash
  (item -10, first seen s270), NOT a new background-noise sighting — don't double-count it as a fresh
  n=1 against the "3rd hit escalates" bar above; it has its own separate, older history.
If EITHER of the first two gets a 3rd independent hit in a future soak, that crosses into "worth
running `s264_symrange.py`/`s193_disasm.py` to confirm whether it's really host-library code or a
misattributed guest function" — until then, leave alone.

## Notes carried forward
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (guest checkpoint,
  only meaningful if the crashing function is breadcrumbed) answer different questions by design.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` -- matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- A crash under ~5s that never reaches `title_reached` is NOT a meaningful test of any post-title-window
  instrument -- don't count it toward a non-recurrence tally; it belongs in the "boot-time crash family"
  bucket (`musyxSynthFrame+4652` is the one seen so far).
- **Regen-reliability gotcha (item -20)**: `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c`
  that already exists on disk -- ALWAYS delete all `funcs_*.c` before re-running `N64Recomp`. Deleting
  all 45 files needs multiple flat `rm -f path1 path2 ...` calls (no glob, no compound `for`/`xargs`) per
  the sandbox's headless permission matcher; `cd && rm` in one compound command is ALSO denied — use
  absolute paths in the `rm -f` call instead of `cd`-ing first.
- **Implementation gotcha for future `fixup_game_funcs.py` patches**: `re.subn`'s plain-string `repl`
  argument gets backslash-escape-processed by the `re` module itself -- ALWAYS use a lambda callback for
  multi-line replacement text. Verify after any new patch by grepping the regenerated `.c` file for the
  new text and confirming it's on one line.
- **Guard-bail-target gotcha (s358)**: when adding a range-check-and-bail guard that substitutes a
  synthetic value, verify which CONTROL PATH that value actually sends execution down -- a backward
  branch's target label in a loop can be the loop's re-entry point, not an exit.
- **Read-guard/write-guard sibling gotcha (s350->s350b, recurred s357->s359/s361, s363 for a
  DIFFERENT pointer, and now s365 for a THIRD)**: a guard that only protects a READ through a
  corrupted pointer and bails by zeroing a DIFFERENT register does NOT repair the pointer itself. If
  that same pointer is used again UNGUARDED later — especially in a WRITE — the crash simply moves
  there. This gotcha has now recurred across THREE of `drainMeshReleaseQueue`'s pointer families (the
  tail-scan cursor `v1`/`ctx->r3`, the head pointer `a0`/`ctx->r4`, and the global-tail pointer
  `v0`/`ctx->r2`). **When defining an "idiom class" to audit, grep for the DATA-FLOW pattern (any
  place a checked-non-NULL-but-unvalidated pointer gets dereferenced), not just one syntactic shape**
  — a function can host the same risk through more than one register/pointer, and this function has
  now shown it three times.
- **Off-target-but-discriminating gotcha (recurred s360-s365, now 6 sessions running)**: a soak
  recipe's own decision tree can call a result "inconclusive" for the question it was queued to answer
  while the SAME log is highly informative for a DIFFERENT open thread (or the background-noise
  catalogue) -- always check `last_pc_symbol`/`last-guest-pc` against ALL open threads' target sites
  AND the background-noise catalogue, not just the recipe's own named target.
- **Stale-NEXT.md gotcha (recurred s360→s361→s362→s363→s364→s365, now SIX sessions running)**: NEXT.md
  can describe a queued pair as "not yet drained" when `SOAK-RESULTS.md`'s actual tail already shows
  it landed. This session's session-start check caught it again for `s363`'s Thread B pair, and it
  turned out to be the most consequential catch yet (a full new pointer family). **Concrete mechanical
  check, do this every session before trusting NEXT.md's "still pending" claims**:
  `grep -c '<recipe-basename>' scratch/agent/SOAK-RESULTS.md` for every recipe NEXT.md claims is
  outstanding, at the START of every session.
- **Guard fire_n=0 is itself informative, not just "guard didn't matter" (s361)**: when a guarded loop's
  read guard shows 0 fires in a run that crashed just past that loop, don't assume the loop is
  irrelevant — check whether a SHORT-CIRCUIT path around the guarded loop body exists that bypasses the
  guard's own instrumentation entirely while still feeding an unvalidated pointer to code further down.
- **Soak-queue drain order (resolved s362)**: `tools/agent/loop.sh`'s `run_soak_queue()` drains
  `"$qdir"/*.sh` via bash's default lexicographic glob expansion — alphabetical = chronological for the
  `sNNN_..._verifyM.sh` naming convention. Naming a new recipe with an earlier session number than its
  actual queuing session will queue-jump it ahead of genuinely-older pending recipes — do this
  deliberately or not at all.

## Queued this session (s365, ready for the loop)

`s364_coalesceheapbailfix_reverify1/2.sh` (Thread A, queued s364, drains FIRST alphabetically) and
`s365_drainmeshtailptrguard_verify1/2.sh` (Thread B, queued this session, drains SECOND) — 4 recipes
total pending, loop drains up to 2 per gap, so expect Thread A's pair to drain next gap and Thread B's
the gap after.

HYPOTHESIS-ID: m5-audio-destub-linkedlist-corruption-source (iteration 9 — genuine new Thread B
evidence AND a new guard landed this session, not a maintenance/no-op iteration).
