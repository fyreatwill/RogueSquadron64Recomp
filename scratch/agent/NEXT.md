# NEXT work unit

## s360: Thread A's long-overdue `s358_coalesceheapbailfix_verify1/2` drained -- off-target for Thread A's
## own question (coalesce_guard_fire_n=0 both times) but discriminating for Thread B: both crashed
## byte-identically at a NEW site inside `drainMeshReleaseQueue` -- a THIRD unguarded tail-scan loop in
## the same function, same idiom as loop1 (s350/s350b) and loop2 (s357/s359). Source-proved and guarded
## it (`[drain-mesh-loop3-guard]`). Thread B's s359 pair is STILL undrained.

Full detail: `PORTING-STATE` Session 360, `docs/CURRENT-TRUTH.md` item -215.

Both `s358_coalesceheapbailfix_verify1` and `verify2` crashed at `pc-symbol=drainMeshReleaseQueue+5016`,
`last-guest-pc=0x80008248`, with loop1's guards firing (positive control) and `ring_fire_n=1` showing
`iter_at_bail=1, v1[0]=0x00010001` -- the same poisoned value, now 6-7 independent sightings. Source-read
found a third unguarded tail-scan loop (`0x80008244`/`0x80008248`, walking a list nested inside an outer
loop over list-head slots). Guarded the confirmed read site (`0x80008248`); left `0x80008244` flagged not
guarded, same 2-step practice as the other two loops. Full regen + rebuild clean, patch report `x1`.
Queued `s360_drainmeshloop3guard_verify1/2.sh`.

## Two open threads -- pick whichever has drained data first

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (iteration 4 fix landed s358, STILL 0/2
informative for its OWN question -- both verify soaks crashed off-target, `coalesce_guard_fire_n=0`).**
- No new recipes queued this session for Thread A specifically -- the s358 fix itself is unconfirmed
  (neither non-recurrence-validated nor shown-to-still-fail). If a future soak (any recipe, since all
  recipes arm all instruments) shows `coalesce_guard_fire_n>=1`, read it per this decision tree:
  - `coalesce_guard_fire_n>=1` AND `last_pc_symbol` OUTSIDE `coalesceFreeHeapBlocks` entirely, or a CLEAN
    run with the guard firing: fix confirmed -- needs 2-3 more non-recurrence soaks (4-run bar).
  - `coalesce_guard_fire_n>=1` AND `last_pc_symbol` STILL `coalesceFreeHeapBlocks+1052` /
    `last-guest-pc=0x80002358`: fix did NOT take -- re-check regenerated `funcs_0.c` for `ctx->r3 = 0x8;`
    on one line.
  - `coalesce_guard_fire_n>=1` at `coalesceFreeHeapBlocks` but a NEW third offset: a 3rd unguarded site,
    same idiom -- source-read and guard it.
- **Consider deliberately queuing a fresh, isolated `s358_coalesceheapbailfix_verify3/4.sh` next session**
  if no incidental hit shows up -- Thread A has now gone 2 verify soaks without a single on-target data
  point, worth a dedicated pair rather than waiting for Thread B's recipes to happen to hit it.

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 6 -- s360's loop3 read guard, still
awaiting its own first verify pair; also 3 loops deep now, worth asking whether this function needs a
systematic audit instead of one-loop-at-a-time whack-a-mole).**
- **Step 1**: `s360_drainmeshloop3guard_verify1/2.sh` are queued in `scratch/agent/soak_queue/`
  (`HOLD_S=240`) -- let the loop drain them. Thread B's PRIOR pair, `s359_drainmeshloop2writeguard_
  verify1/2.sh`, is STILL undrained (queued s359, not yet run as of this session's end) -- now the
  oldest-waiting Thread B instrument, 4 recipes total pending across both threads.
- **Step 2 (once s359 or s360 drained)**: check the relevant `*_guard_fire_n` and `last_pc_symbol`:
  - CLEAN, or crash with the relevant guard's fire_n=0, or `last_pc_symbol` OUTSIDE
    `drainMeshReleaseQueue`: fix confirmed -- needs 2-3 more non-recurrence soaks (4-run bar).
  - guard fire_n>=1 AND `last_pc_symbol` STILL the exact site that guard targets: fix did NOT take --
    re-check regenerated `funcs_3.c` for the guard body at that site (grep the guard's diagnostic tag).
  - guard fire_n>=1 but a NEW offset inside `drainMeshReleaseQueue`: a 4th sibling site in the same
    function/idiom family -- source-read and guard it (same practice as s350->s350b->s357->s359->s360).
  - If `ring_fire_n>=1` again: compare `iter_at_bail`/`v1[0]` against the now-6/7-sample-strong
    `iter_at_bail=1, v1[0]=0x00010001` baseline -- another match keeps strengthening the
    single-deterministic-corruption-source reading from item -208; a mismatch would be the first evidence
    against it.
- **Worth flagging, not yet acting on**: `drainMeshReleaseQueue` now has THREE independently-discovered
  unguarded tail-scan loops with the identical idiom (read v1=*v1, then read *v1 again unguarded). If a
  4th site turns up, that's the trigger to stop whack-a-moling individual sites and instead grep-enumerate
  every `lw ... ; lw ...(0(reg))` pair in this function's disassembly in one pass (the s282-s288
  `-0x25A4` idiom-class-audit model the strategic directive prefers) -- would likely close the whole class
  in one session instead of one guard per crash.

**Recommendation**: 4 recipes total pending (2 Thread B stale from s359, 2 Thread B fresh from s360;
Thread A has 0 queued -- see its note above about deliberately queuing a fresh isolated pair). Next
session: prioritize draining/reading whichever of s359/s360 drained; if s359 is STILL undrained after a
3rd gap, that's worth checking whether Thread B recipes are systematically sorting first in the queue
(alphabetical/mtime) and consider a workaround.

## Notes carried forward
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (guest checkpoint,
  only meaningful if the crashing function is breadcrumbed) answer different questions by design.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` -- matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- A crash under ~5s that never reaches `title_reached` is NOT a meaningful test of any post-title-window
  instrument -- don't count it toward a non-recurrence tally; it belongs in the "boot-time crash family"
  bucket (`musyxSynthFrame+4652` is the one seen so far).
- **Regen-reliability gotcha (item -20), re-confirmed AGAIN this session (initially skipped the delete
  step, caught it before running the fixup script)**: `N64Recomp` skips rewriting any
  `RecompiledFuncs/funcs_*.c` that already exists on disk -- ALWAYS delete all `funcs_*.c` before
  re-running `N64Recomp`. Deleting all 45 files needs multiple flat `rm -f path1 path2 ...` calls (no
  glob, no compound `for`/`xargs`) per the sandbox's headless permission matcher; `cd && rm` in one
  compound command is ALSO denied (write ops after `cd` need separate approval) -- use absolute paths in
  the `rm -f` call instead of `cd`-ing first.
- **Implementation gotcha for future `fixup_game_funcs.py` patches**: `re.subn`'s plain-string `repl`
  argument gets backslash-escape-processed by the `re` module itself -- ALWAYS use a lambda callback for
  multi-line replacement text. Verify after any new patch by grepping the regenerated `.c` file for the
  new text and confirming it's on one line.
- **Guard-bail-target gotcha (s358)**: when adding a range-check-and-bail guard that substitutes a
  synthetic value, verify which CONTROL PATH that value actually sends execution down -- a backward
  branch's target label in a loop can be the loop's re-entry point, not an exit.
- **Read-guard/write-guard sibling gotcha (s350->s350b, recurred s357->s359)**: a guard that only
  protects a READ through a corrupted pointer and bails by zeroing a DIFFERENT register (the
  loop-continuation value) does NOT repair the pointer itself. If that same pointer is used again
  UNGUARDED later in the function -- especially in a WRITE, which has no "just return a synthetic value"
  option -- the crash simply moves there. When auditing any list-walk guard, always check every use of
  the walked pointer between the guard and the function's next fresh reassignment of it, not just the
  guarded read.
- **Off-target-but-discriminating gotcha (s360)**: a soak recipe's own decision tree can call a result
  "inconclusive" for the question it was queued to answer while the SAME log is highly informative for a
  DIFFERENT open thread -- always check `last_pc_symbol`/`last-guest-pc` against ALL open threads'
  target sites, not just the recipe's own named target, before discarding a run as uninformative.

## Queued this session (s360, ready for the loop)

`s360_drainmeshloop3guard_verify1/2.sh` (Thread B, `HOLD_S=240`), both in `scratch/agent/soak_queue/`.
`s359_drainmeshloop2writeguard_verify1/2.sh` (Thread B, older) still undrained -- also still queued. 4
recipes total pending; loop drains up to 2 per gap.

HYPOTHESIS-ID: m5-audio-destub-linkedlist-corruption-source (iteration 6 -- landed a source-proved fix
this session on informative data, not a pivot; 3rd loop in the same function, same idiom).
Parallel/still-open: m5-audio-destub-coalesce-heap-guard-verify (iteration 4, still 0/2 informative for
its OWN question after this session's pair drained off-target).
