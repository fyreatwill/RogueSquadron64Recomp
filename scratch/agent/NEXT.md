# NEXT work unit

## s364: MAINTENANCE iteration (Step 0 triggered at 62,206 bytes). Compacted `docs/CURRENT-TRUTH.md`
## 689→489 lines (200-line shrink), folding the closed s354-362 M5 guard-hunting arc into one summary
## item (-217..-210), keeping s363's finding as its own entry (-218). While reading the ledger, found
## `s362`'s own Thread A reverify pair had drained (unread by s363): `reverify1` CLEAN (432s full hold,
## 0 crashes); `reverify2` crashed at the already-catalogued `fscache_insert_and_retain+1192` (Metal
## system crash, item -10, not guest code) — off-target-but-known noise. Re-queued
## `s364_coalesceheapbailfix_reverify1/2.sh`. Full detail: `PORTING-STATE` Session 364,
## `docs/CURRENT-TRUTH.md` items -219/-218/-217..-210.

## Two open threads

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (iteration 6, no code change this session,
2 more soaks folded — now 4/4 non-target since the s358 fix, approaching its own closure bar).**
- `s364_coalesceheapbailfix_reverify1/2.sh` queued in `scratch/agent/soak_queue/`, sorted to drain
  AFTER Thread B's still-pending `s363_...` pair (alphabetical: `s363` < `s364`).
- **Running tally since the s358 bail-target fix**: `s358_verify1/2` (2 soaks, both crashed off-target
  at `drainMeshReleaseQueue+5016`, a Thread B site) + `s362_reverify1` (CLEAN, full 432s hold) +
  `s362_reverify2` (off-target, known `fscache_insert_and_retain` Metal-system-crash noise) = 4 soaks
  total post-fix, ZERO hits on `coalesceFreeHeapBlocks` itself (1 clean full hold + 3 off-target).
- **Decision tree when `s364_...` drains**: `coalesce_guard_fire_n=0` again (CLEAN or off-target) →
  this is the closure-bar territory — if BOTH `s364_verify1` and `s364_verify2` are non-target, that's
  6 consecutive non-recurrence soaks since the s358 fix with a clean full-hold in the mix; strongly
  consider explicitly CLOSING this thread next session (needs a deliberate write-up, not silent
  abandonment — say why 6/6 clears the bar). `coalesce_guard_fire_n>=1` AND
  `last_pc_symbol=coalesceFreeHeapBlocks+1052` / `last-guest-pc=0x80002358` → the s358 bail-target fix
  did NOT actually hold, re-read the regenerated source (check for a stale build or reverted patch).
  `coalesce_guard_fire_n>=1` and crash elsewhere (or clean) → fix confirmed via a genuine positive
  control, thread ready to close. `coalesce_guard_fire_n>=1` at a NEW `coalesceFreeHeapBlocks` offset →
  a further unguarded site, same idiom, source-read and guard it.

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 8, unchanged this session — its
own `s363_...` pair still pending, not yet drained).**
- `s363_drainmeshheadguard_verify1/2.sh` queued in `scratch/agent/soak_queue/`, drains BEFORE Thread
  A's `s364_...` pair (alphabetical FIFO).
- **These are BRAND-NEW instruments (the 5 head-pointer guard pairs added s363) with zero prior fire
  history** — any single fire of `head{n}_guard` or `head{n}_clear_guard` (n=1..5) is itself
  informative, not just a "didn't matter" null.
- **Decision tree when this pair drains** (unchanged from s363, full detail also in the recipe header):
  - `head{n}_guard_fire_n>=1` OR `head{n}_clear_guard_fire_n>=1` for ANY n: first-ever positive
    control for the new guards — confirms the head-pointer dereference is a genuinely reachable
    corruption surface. Note WHICH n fired.
  - Crash still at `pc-symbol=drainMeshReleaseQueue+796` / `last-guest-pc=0x8000819C` with ALL head
    guards at 0: the regex substitution didn't actually match what's running — re-check the
    regenerated `funcs_3.c` for the literal patched text.
  - Crash moved to a DIFFERENT `drainMeshReleaseQueue` offset, with a head guard's fire_n>=1: guard
    engaged but didn't fully close the gap — re-read for a further sibling.
  - Crash moved OUTSIDE `drainMeshReleaseQueue` entirely, or run is CLEAN: promising, but needs 2-3
    more non-recurrence soaks before calling this thread closed.
  - Cross-check `last_pc_symbol`/`last-guest-pc` against Thread A's `coalesceFreeHeapBlocks` question
    and the background-noise catalogue below before discarding an off-target result as uninformative.

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
- **Read-guard/write-guard sibling gotcha (s350->s350b, recurred s357->s359/s361, then s363 for a
  DIFFERENT pointer)**: a guard that only protects a READ through a corrupted pointer and bails by
  zeroing a DIFFERENT register (the loop-continuation value) does NOT repair the pointer itself. If
  that same pointer is used again UNGUARDED later — especially in a WRITE, which has no "just return
  a synthetic value" option — the crash simply moves there. This gotcha has now recurred across BOTH
  of `drainMeshReleaseQueue`'s pointer families (the tail-scan cursor `v1`/`ctx->r3` AND the head
  pointer `a0`/`ctx->r4`). **When defining an "idiom class" to audit, grep for the DATA-FLOW pattern
  (any place a checked-non-NULL-but-unvalidated pointer gets dereferenced), not just one syntactic
  shape** — a function can host the same risk through more than one register/pointer.
- **Off-target-but-discriminating gotcha (recurred s360-s364, now 5 sessions running)**: a soak
  recipe's own decision tree can call a result "inconclusive" for the question it was queued to answer
  while the SAME log is highly informative for a DIFFERENT open thread (or the background-noise
  catalogue) -- always check `last_pc_symbol`/`last-guest-pc` against ALL open threads' target sites
  AND the background-noise catalogue, not just the recipe's own named target.
- **Stale-NEXT.md gotcha (recurred s360→s361→s362→s363→s364, now FIVE sessions running)**: NEXT.md can
  describe a queued pair as "not yet drained" when `SOAK-RESULTS.md`'s actual tail already shows it
  landed. This session's session-start check (per the ITERATION.md read-order) caught it again for
  `s362`'s Thread A pair. **This is now a standing, not occasional, failure mode — the fix isn't
  "remember to check harder," it's a mechanical cross-check.** Suggest a concrete next step: before
  trusting NEXT.md's "still pending" claims, run
  `grep -c '<recipe-basename>' scratch/agent/SOAK-RESULTS.md` for every recipe NEXT.md claims is
  outstanding, at the START of every session, not just when something feels off.
- **Guard fire_n=0 is itself informative, not just "guard didn't matter" (s361)**: when a guarded loop's
  read guard shows 0 fires in a run that crashed just past that loop, don't assume the loop is
  irrelevant — check whether a SHORT-CIRCUIT path around the guarded loop body exists that bypasses the
  guard's own instrumentation entirely while still feeding an unvalidated pointer to code further down.
- **Soak-queue drain order (resolved s362)**: `tools/agent/loop.sh`'s `run_soak_queue()` drains
  `"$qdir"/*.sh` via bash's default lexicographic glob expansion — alphabetical = chronological for the
  `sNNN_..._verifyM.sh` naming convention. Naming a new recipe with an earlier session number than its
  actual queuing session will queue-jump it ahead of genuinely-older pending recipes — do this
  deliberately or not at all.

## Queued this session (s364, ready for the loop)

`s363_drainmeshheadguard_verify1/2.sh` (Thread B, queued s363, drains FIRST alphabetically) and
`s364_coalesceheapbailfix_reverify1/2.sh` (Thread A, queued this session, drains SECOND) — 4 recipes
total pending, loop drains up to 2 per gap, so expect Thread B's pair to drain next gap and Thread A's
the gap after.

HYPOTHESIS-ID: m5-audio-destub-linkedlist-corruption-source (iteration 8, UNCHANGED this session — s364
was a MAINTENANCE iteration, not a pivot; no new Thread B evidence landed). Parallel/still-open:
m5-audio-destub-coalesce-heap-guard-verify (iteration 6, its own re-queued pair drained and produced 2
more non-recurrence data points this session — nearing its closure bar, see Thread A section above).
