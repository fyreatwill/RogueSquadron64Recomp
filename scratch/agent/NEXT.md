# NEXT work unit

## s361: drained a stale `s359` recipe, found a 4th `drainMeshReleaseQueue` crash site, and used it as
## the trigger (pre-committed by s360's own NEXT.md) to run the full systematic idiom-class audit instead
## of one more reactive guard. Read the ENTIRE function (funcs_3.c:1669-2297) and found FIVE structurally
## identical tail-scan loops, not three — loop4 (0x800082A4/0x800082A8) and loop5
## (0x800082F4/0x800082F8) had NO guard at all, landmines nobody had crashed into yet. Guarded all 5
## remaining gaps in one pass (loop3's missing write guard + loop4/loop5's full read+write pairs). Full
## regen+rebuild clean, 60s build-sanity smoke test showed no regression (crashed in an unrelated,
## already-known family, not inside drainMeshReleaseQueue at all).

Full detail: `PORTING-STATE` Session 361, `docs/CURRENT-TRUTH.md` item -216.

## Two open threads

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (iteration 4 fix landed s358, STILL 0/2
informative for its OWN question — both verify soaks crashed off-target, `coalesce_guard_fire_n=0`).**
- No new recipes queued this session for Thread A specifically. Untouched since s358/s360. If a future
  soak (any recipe — all recipes arm all instruments) shows `coalesce_guard_fire_n>=1`, read it per the
  decision tree in PORTING-STATE Session 358/360 (same tree, unchanged).
- **Worth deliberately queuing a fresh, isolated `s358_coalesceheapbailfix_verify3/4.sh` next session**
  if no incidental hit shows up — Thread A has now gone 3+ sessions without a single on-target data
  point.

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 7 — s361's 5-guard idiom-class
audit, awaiting its own first verify pair; s360's own pair from LAST session is still undrained too).**
- **Step 1**: `s361_drainmeshidiomaudit_verify1/2.sh` are queued in `scratch/agent/soak_queue/`
  (`HOLD_S=240`, reports every drain-mesh guard tag including the 5 new ones: `loop3_write_guard_fire_n`,
  `loop4_guard_fire_n`, `loop4_write_guard_fire_n`, `loop5_guard_fire_n`, `loop5_write_guard_fire_n`).
  `s360_drainmeshloop3guard_verify1/2.sh` (queued s360, one session ago) are STILL undrained — 4 recipes
  total pending. **If s360's pair is STILL undrained after another gap, that's 3 gaps skipped for the
  same pair — worth checking whether the loop's queue-drain order is FIFO/mtime/alphabetical and whether
  `s360_*` vs `s361_*` filenames are sorting predictably behind something. Consider renaming or manually
  prioritizing if this recurs a 4th time.**
- **Step 2 (once either pair drains)**: check the crash's `last_pc_symbol`/`last-guest-pc` against:
  - `drainMeshReleaseQueue+5740` / `0x80008260` (loop3 write site, s361's fix): guard fire_n>=1 AND
    still lands here = fix did NOT take, re-check `funcs_3.c` for the guard body. Guard fire_n>=1 and
    last_pc_symbol elsewhere (or clean) = fix confirmed, needs 2-3 more non-recurrence soaks.
  - Any `drain-mesh-loop4-*` or `drain-mesh-loop5-*` tag firing **at all** (even on an otherwise-clean
    run): first-ever evidence those two loops are reachable by the same corruption — was completely
    unknown before this session, worth its own investigation thread if it happens.
  - A crash at a brand-new offset inside `drainMeshReleaseQueue`, past all 5 guard pairs: genuinely
    surprising at this point — would mean a 6th site, or (more likely) a legitimately different bug
    entirely. Re-read the function once more before assuming another sibling gap.
  - `ring_fire_n>=1`: compare `iter_at_bail`/`v1[0]` against the `iter_at_bail=1, v1[0]=0x00010001`
    baseline (6-7 sightings so far) — another match keeps strengthening the
    single-deterministic-corruption-source reading from item -208.

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
  option -- the crash simply moves there. **s361 generalizes this further**: when a function contains
  MULTIPLE instances of the same idiom (this function has 5), a read-guard-only fix for one instance
  doesn't imply the others are safe — read the WHOLE function once a pattern repeats twice, not just the
  one crash site, rather than finding each sibling loop one crash at a time.
- **Off-target-but-discriminating gotcha (s360, recurred s361)**: a soak recipe's own decision tree can
  call a result "inconclusive" for the question it was queued to answer while the SAME log is highly
  informative for a DIFFERENT open thread -- always check `last_pc_symbol`/`last-guest-pc` against ALL
  open threads' target sites, not just the recipe's own named target, before discarding a run as
  uninformative.
- **Guard fire_n=0 is itself informative, not just "guard didn't matter" (s361)**: when a guarded loop's
  read guard shows 0 fires in a run that crashed just past that loop, don't assume the loop is
  irrelevant — check whether a SHORT-CIRCUIT path around the guarded loop body exists (e.g. "if the first
  node's content is already null, skip the walk and use the raw pointer directly") that bypasses the
  guard's own instrumentation entirely while still feeding an unvalidated pointer to code further down.

## Queued this session (s361, ready for the loop)

`s361_drainmeshidiomaudit_verify1/2.sh` (Thread B, `HOLD_S=240`), both in `scratch/agent/soak_queue/`.
`s360_drainmeshloop3guard_verify1/2.sh` (Thread B, one session older) still undrained -- also still
queued. 4 recipes total pending; loop drains up to 2 per gap.

HYPOTHESIS-ID: m5-audio-destub-linkedlist-corruption-source (iteration 7 -- ran the systematic
idiom-class audit NEXT.md pre-committed to as the trigger condition, closed what is very likely the
entire idiom class for this function in one pass instead of one more reactive single-site guard).
Parallel/still-open: m5-audio-destub-coalesce-heap-guard-verify (iteration 4, untouched this session,
still 0/2 informative for its OWN question).
