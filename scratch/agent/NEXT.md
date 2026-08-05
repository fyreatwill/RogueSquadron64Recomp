# NEXT work unit

## s362: drained the stale `s360` verify pair (0/2 informative for either open thread — both crashed
## off-target before reaching either guarded function), resolved the 3-session-recurring "does the soak
## queue drain in order?" confusion by reading `tools/agent/loop.sh` source (answer: yes, plain
## alphabetical glob order = chronological order for `sNNN_..._verifyM.sh` names, no bug — the apparent
## skipping was pure queue-depth arithmetic), and re-queued Thread A with a fresh isolated pair. No code
## changed this session (nothing to source-prove: both drained crashes were off-target, already-
## catalogued diffuse-background-population hits, not new evidence for either thread).

Full detail: `PORTING-STATE` Session 362, `docs/CURRENT-TRUTH.md` item -217.

## Two open threads

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (iteration 5, re-queued s362, still 0/4
informative for its OWN question across all 4 soaks since the s358 bail-target fix).**
- `s362_coalesceheapbailfix_reverify1/2.sh` queued in `scratch/agent/soak_queue/`, sorted to drain
  AFTER Thread B's pair (see below). Full instrument set (all 5 drain-mesh loop tags + coalesce +
  ring), `HOLD_S=240`. No code changed — pure re-roll to buy more independent attempts at landing
  inside `coalesceFreeHeapBlocks` at all.
- **Decision tree when this pair drains** (unchanged from s358's original, reproduced in the recipe
  header): `coalesce_guard_fire_n=0` again → still off-target, re-queue again (thread's own hit rate on
  its target function appears low, not a red flag by itself). `coalesce_guard_fire_n>=1` AND
  `last_pc_symbol=coalesceFreeHeapBlocks+1052` / `last-guest-pc=0x80002358` → the s358 bail-target fix
  did NOT work, re-read the regenerated source. `coalesce_guard_fire_n>=1` and crash elsewhere (or
  clean) → fix confirmed, needs 1-2 more non-recurrence soaks to close. `coalesce_guard_fire_n>=1` at a
  NEW `coalesceFreeHeapBlocks` offset → a further unguarded site, same idiom, source-read and guard it.

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 7 — s361's 5-guard idiom-class
audit, STILL awaiting its own first verify pair).**
- `s361_drainmeshidiomaudit_verify1/2.sh` still queued in `scratch/agent/soak_queue/`, sorted to drain
  BEFORE Thread A's pair (both threads' recipes obey the now-confirmed alphabetical=chronological FIFO
  order — no action needed to enforce this, just don't rename Thread B's files to sort later).
- **Decision tree once it drains** (unchanged from s361's own header): check `last_pc_symbol`/
  `last-guest-pc` against:
  - `drainMeshReleaseQueue+5740` / `0x80008260` (loop3 write site, s361's fix): `loop3_write_guard_
    fire_n>=1` AND still lands here = fix did NOT take, re-check `funcs_3.c`. Fires AND lands elsewhere
    (or clean) = fix confirmed, needs 2-3 more non-recurrence soaks.
  - Any `drain-mesh-loop4-*` or `drain-mesh-loop5-*` tag firing at all (even on an otherwise-clean run):
    first-ever evidence those two loops are reachable by the same corruption — was completely unknown
    before s361, worth its own investigation thread if it happens.
  - A crash at a brand-new offset inside `drainMeshReleaseQueue`, past all 5 guard pairs: genuinely
    surprising at this point — would mean a 6th site, or (more likely) a legitimately different bug.
    Re-read the function once more before assuming another sibling gap.
  - `ring_fire_n>=1`: compare `iter_at_bail`/`v1[0]` against the `iter_at_bail=1, v1[0]=0x00010001`
    baseline (6-7 sightings so far) — another match keeps strengthening the
    single-deterministic-corruption-source reading from item -208.
  - **Also check against Thread A's question and against the diffuse-background-population symbols
    below** — a crash that's off-target for Thread B's own question may still be informative for
    something else (the s360/s361/s362 recurring "off-target-but-discriminating" pattern).

## Third, deliberately-not-chased thread (background noise, do not escalate reactively)

Two crash symbols now have 2 independent exact hits each, both read as Apple system-framework
`dladdr` nearest-symbol fallbacks over stripped code (not game bugs), both explicitly NOT escalated
per the strategic directive's "no reactive single-crash chases" outside the active M5 threads:
- `trackResourceListWithMappingTables+1192` — s347 `rate_4` + s362's `s360_..._verify1`.
- `unregisterServiceWorker+536` — Session 265 + s362's `s360_..._verify2`.
If EITHER gets a 3rd independent hit in a future soak (any recipe — all soaks report `pc-symbol`),
that crosses from "background noise" into "worth running `s264_symrange.py`/`s193_disasm.py` to
confirm whether it's really host-library code or a misattributed guest function" — until then, leave
alone; chasing n=2 singletons here would be exactly the discouraged whack-a-mole pattern.

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
- **Read-guard/write-guard sibling gotcha (s350->s350b, recurred s357->s359, s361 for loop3)**: a guard
  that only protects a READ through a corrupted pointer and bails by zeroing a DIFFERENT register (the
  loop-continuation value) does NOT repair the pointer itself. If that same pointer is used again
  UNGUARDED later in the function -- especially in a WRITE, which has no "just return a synthetic value"
  option -- the crash simply moves there. When a function contains MULTIPLE instances of the same idiom
  (this function has 5), a read-guard-only fix for one instance doesn't imply the others are safe — read
  the WHOLE function once a pattern repeats twice, not just the one crash site.
- **Off-target-but-discriminating gotcha (s360, recurred s361, s362)**: a soak recipe's own decision
  tree can call a result "inconclusive" for the question it was queued to answer while the SAME log is
  highly informative for a DIFFERENT open thread (or, per s362, for a THIRD deliberately-parked
  background-noise catalogue) -- always check `last_pc_symbol`/`last-guest-pc` against ALL open threads'
  target sites AND the background-noise catalogue, not just the recipe's own named target, before
  discarding a run as uninformative.
- **Guard fire_n=0 is itself informative, not just "guard didn't matter" (s361)**: when a guarded loop's
  read guard shows 0 fires in a run that crashed just past that loop, don't assume the loop is
  irrelevant — check whether a SHORT-CIRCUIT path around the guarded loop body exists that bypasses the
  guard's own instrumentation entirely while still feeding an unvalidated pointer to code further down.
- **Soak-queue drain order (resolved s362)**: `tools/agent/loop.sh`'s `run_soak_queue()` drains
  `"$qdir"/*.sh` via bash's default lexicographic glob expansion — i.e. alphabetical, which equals
  chronological for the `sNNN_..._verifyM.sh` naming convention. Not a bug; apparent "skipping" was
  always just queue-depth (2 drain per gap) vs. arrival rate (~2/session/thread) arithmetic. Naming a
  new recipe with an earlier session number than its actual queuing session will queue-jump it ahead of
  genuinely-older pending recipes — do this deliberately or not at all (s362 named Thread A's re-queue
  `s362_...` specifically so it would NOT queue-jump Thread B's already-pending `s361_...` pair).

## Queued this session (s362, ready for the loop)

`s361_drainmeshidiomaudit_verify1/2.sh` (Thread B, queued s361, drains FIRST alphabetically) and
`s362_coalesceheapbailfix_reverify1/2.sh` (Thread A, queued this session, drains SECOND) — 4 recipes
total pending, loop drains up to 2 per gap, so expect Thread B's pair to drain next gap and Thread A's
the gap after.

HYPOTHESIS-ID: m5-audio-destub-linkedlist-corruption-source (iteration 7, unchanged from s361 — no new
evidence landed for Thread B this session, its own verify pair still hasn't drained). Parallel/still-
open: m5-audio-destub-coalesce-heap-guard-verify (iteration 5, re-queued this session after 4 sessions
at 0/4 informative).
