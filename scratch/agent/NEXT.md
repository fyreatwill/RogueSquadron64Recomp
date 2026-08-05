# NEXT work unit

## s363: Thread B's own `s361` verify pair drained (was unread by s362 — a one-session-narrower
## repeat of the s360/s361/s362 stale-doc pattern). `verify1` crashed at
## `pc-symbol=drainMeshReleaseQueue+796`, `last-guest-pc=0x8000819C`, with ALL 10 existing tail-scan
## guards (5 loops × read+write) plus `ring_fire_n` firing at least once earlier in the SAME run —
## i.e. genuinely outside all 5 already-guarded loops. Source-read found an unguarded "priming read"
## through the loop's HEAD pointer (`a0`/`ctx->r4`, distinct from the already-guarded tail-scan cursor
## `v1`/`ctx->r3`) repeated identically before each of the 5 loops, paired with an unguarded
## clear-write through the same pointer later in each loop's exit path — 10 new unguarded sites total.
## Guarded all 10 in `fixup_game_funcs.py`, regen+rebuild clean, queued
## `s363_drainmeshheadguard_verify1/2.sh`. Full detail: `PORTING-STATE` Session 363,
## `docs/CURRENT-TRUTH.md` item -218.

## Two open threads

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 8, s363 landed new evidence +
a real fix — the 5 head-pointer guard pairs — its OWN verify pair not yet drained).**
- `s363_drainmeshheadguard_verify1/2.sh` queued in `scratch/agent/soak_queue/`, sorted to drain AFTER
  Thread A's still-pending `s362_...` pair (alphabetical = chronological FIFO, confirmed s362).
- **These are BRAND-NEW instruments with zero prior fire history** — unlike the tail-scan guards
  (which have fired routinely for sessions), any single fire of `head{n}_guard` or
  `head{n}_clear_guard` (n=1..5) is itself informative, not just a "didn't matter" null.
- **Decision tree when this pair drains** (full detail also in the recipe header):
  - `head{n}_guard_fire_n>=1` OR `head{n}_clear_guard_fire_n>=1` for ANY n: first-ever positive
    control for the new guards — confirms the head-pointer dereference is a genuinely reachable
    corruption surface, not a speculative fix. Note WHICH n fired (loop1 through loop5) — worth
    tracking whether it's always the same loop or scattered, same question the tail-scan loops'
    5-way spread already raised.
  - Crash still at `pc-symbol=drainMeshReleaseQueue+796` / `last-guest-pc=0x8000819C` with ALL head
    guards at 0: the regex substitution didn't actually match what's running — re-check the
    regenerated `funcs_3.c` for the literal patched text (grep for `drain-mesh-head1-guard`).
  - Crash moved to a DIFFERENT `drainMeshReleaseQueue` offset, with a head guard's fire_n>=1: guard
    engaged but didn't fully close the gap — re-read for a further sibling the same way
    s350->s350b/s357->s359/this session's own discovery were found. Given the priming-read/
    clear-write pair is now closed for all 5 loops, a further gap would mean a THIRD dereference
    through the head pointer somewhere, or a genuinely new idiom.
  - Crash moved OUTSIDE `drainMeshReleaseQueue` entirely, or run is CLEAN: promising, but per the
    project's own evidentiary bar needs 2-3 more non-recurrence soaks before calling this thread
    closed — queue another pair using the same recipe template.
  - Cross-check `last_pc_symbol`/`last-guest-pc` against Thread A's `coalesceFreeHeapBlocks` question
    and the background-noise catalogue below before discarding an off-target result as uninformative
    (the recurring s360/s361/s362 "off-target-but-discriminating" pattern).

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (iteration 5, re-queued s362, still 0/4
informative for its OWN question across all 4 soaks since the s358 bail-target fix).**
- `s362_coalesceheapbailfix_reverify1/2.sh` queued in `scratch/agent/soak_queue/`, sorted to drain
  BEFORE Thread B's new `s363_...` pair (alphabetical sort: `s362` < `s363`).
- **Decision tree when this pair drains** (unchanged from s358/s362's original, reproduced here):
  `coalesce_guard_fire_n=0` again → still off-target, re-queue again (this thread's own hit rate on
  its target function appears genuinely low, not a red flag by itself — 4 sessions of misses on a
  narrow single-function target isn't surprising given the drain-mesh threads keep landing hits on a
  much larger, more-frequently-executed function instead). `coalesce_guard_fire_n>=1` AND
  `last_pc_symbol=coalesceFreeHeapBlocks+1052` / `last-guest-pc=0x80002358` → the s358 bail-target fix
  did NOT work, re-read the regenerated source. `coalesce_guard_fire_n>=1` and crash elsewhere (or
  clean) → fix confirmed, needs 1-2 more non-recurrence soaks to close. `coalesce_guard_fire_n>=1` at
  a NEW `coalesceFreeHeapBlocks` offset → a further unguarded site, same idiom, source-read and guard
  it.

## Third, deliberately-not-chased thread (background noise, do not escalate reactively)

Two crash symbols now have 2 independent exact hits each, both read as Apple system-framework
`dladdr` nearest-symbol fallbacks over stripped code (not game bugs), both explicitly NOT escalated
per the strategic directive's "no reactive single-crash chases" outside the active M5 threads:
- `trackResourceListWithMappingTables+1192` — s347 `rate_4` + s362's `s360_..._verify1`.
- `unregisterServiceWorker+536` — Session 265 + s362's `s360_..._verify2`.
If EITHER gets a 3rd independent hit in a future soak (any recipe — all soaks report `pc-symbol`),
that crosses into "worth running `s264_symrange.py`/`s193_disasm.py` to confirm whether it's really
host-library code or a misattributed guest function" — until then, leave alone.

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
- **Read-guard/write-guard sibling gotcha (s350->s350b, recurred s357->s359/s361, now s363 for a
  DIFFERENT pointer)**: a guard that only protects a READ through a corrupted pointer and bails by
  zeroing a DIFFERENT register (the loop-continuation value) does NOT repair the pointer itself. If
  that same pointer is used again UNGUARDED later — especially in a WRITE, which has no "just return
  a synthetic value" option — the crash simply moves there. s363 found this gotcha applies BEYOND the
  original tail-scan cursor: `drainMeshReleaseQueue` has a SECOND pointer family (the head pointer,
  `ctx->r4`) with the exact same priming-read/clear-write pair, once per loop, that the original
  idiom-class audit's search pattern didn't cover because it wasn't part of the loop body syntax.
  **When defining an "idiom class" to audit, grep for the DATA-FLOW pattern (any place a
  checked-non-NULL-but-unvalidated pointer gets dereferenced), not just one syntactic shape
  (e.g. "loop that follows v1=*v1") — a function can host the same risk through more than one
  register/pointer.**
- **Off-target-but-discriminating gotcha (s360, recurred s361, s362)**: a soak recipe's own decision
  tree can call a result "inconclusive" for the question it was queued to answer while the SAME log is
  highly informative for a DIFFERENT open thread (or a THIRD deliberately-parked background-noise
  catalogue) -- always check `last_pc_symbol`/`last-guest-pc` against ALL open threads' target sites AND
  the background-noise catalogue, not just the recipe's own named target, before discarding a run as
  uninformative.
- **Stale-NEXT.md gotcha (recurred s360→s361→s362→s363, one session narrower each time)**: NEXT.md can
  describe a queued pair as "not yet drained" when `SOAK-RESULTS.md`'s actual tail already shows it
  landed — always cross-check the two at session start rather than trusting NEXT.md's own claim about
  queue state. This has now happened 4 sessions running; consider adding an explicit
  `grep SOAK-RESULTS.md` step to the session-start checklist itself rather than relying on memory of
  this note.
- **Guard fire_n=0 is itself informative, not just "guard didn't matter" (s361)**: when a guarded loop's
  read guard shows 0 fires in a run that crashed just past that loop, don't assume the loop is
  irrelevant — check whether a SHORT-CIRCUIT path around the guarded loop body exists that bypasses the
  guard's own instrumentation entirely while still feeding an unvalidated pointer to code further down.
- **Soak-queue drain order (resolved s362)**: `tools/agent/loop.sh`'s `run_soak_queue()` drains
  `"$qdir"/*.sh` via bash's default lexicographic glob expansion — alphabetical = chronological for the
  `sNNN_..._verifyM.sh` naming convention. Naming a new recipe with an earlier session number than its
  actual queuing session will queue-jump it ahead of genuinely-older pending recipes — do this
  deliberately or not at all.

## Queued this session (s363, ready for the loop)

`s362_coalesceheapbailfix_reverify1/2.sh` (Thread A, queued s362, drains FIRST alphabetically) and
`s363_drainmeshheadguard_verify1/2.sh` (Thread B, queued this session, drains SECOND) — 4 recipes
total pending, loop drains up to 2 per gap, so expect Thread A's pair to drain next gap and Thread B's
the gap after.

HYPOTHESIS-ID: m5-audio-destub-linkedlist-corruption-source (iteration 8 — s363 landed new evidence
and a real fix this session, unlike s362's null result; pivoting the slug's iteration count forward
since real progress was made). Parallel/still-open: m5-audio-destub-coalesce-heap-guard-verify
(iteration 5, unchanged this session, its re-queued pair still pending).
