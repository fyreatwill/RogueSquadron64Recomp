# NEXT work unit

## s359: Thread B's `verify1/2` drained with a discriminating result — the s357 loop2 READ guard's own
## uncovered sibling WRITE site crashed (guard fired, crash relocated to a new offset in the same
## function), an exact repeat of the s350->s350b read-guard/write-guard-sibling pattern one loop over.
## Source-proved and guarded it. Thread A's s358 verify pair is STILL undrained (2 gaps skipped now).

Full detail: `PORTING-STATE` Session 359, `docs/CURRENT-TRUTH.md` item -214.

`s357_drainmeshloop2guard_verify1` crashed at `pc-symbol=drainMeshReleaseQueue+3752`,
`last-guest-pc=0x80008218`, with `loop2_guard_fire_n=1` (s357's read guard fired earlier in the same run
-- positive control) and both first-loop guards also firing. Ring-buffer breadcrumb showed
`iter_at_bail=1, v1[0]=0x00010001` -- the 4th independent sighting of that exact poisoned value.
Source-read found the s357 loop2 read guard's bail zeroes `ctx->r2` but never repairs `ctx->r3` (`v1`);
4 instructions later the function unconditionally writes through that same unrepaired `v1`
(`0x80008218`) -- same gap s350 had before s350b fixed it, one loop over. Fixed: new
range-check-and-bail guard at `0x80008218` (`fixup_game_funcs.py`, tag
`[drain-mesh-loop2-write-guard]`). Full regen + rebuild clean, patch report `x1` (2 compiler-duplicated
occurrences), confirmed single-line. Queued `s359_drainmeshloop2writeguard_verify1/2.sh`.

## Two open threads — pick whichever has drained data first

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (iteration 4 fix landed s358, STILL awaiting its
first verify pair -- 2 consecutive gaps skipped by the loop as of s359).**
- **Step 1**: `s358_coalesceheapbailfix_verify1/2.sh` are queued in `scratch/agent/soak_queue/`
  (`HOLD_S=240`) -- let the loop drain them, do NOT run inline. If they are STILL undrained next session
  (a 3rd gap skipped), that itself is worth a one-line note in the ledger -- check whether Thread B's
  recipes are just consistently sorting first (alphabetical/mtime order in the queue directory) and
  consider renaming/reordering so Thread A gets a turn.
- **Step 2 (once drained)**: read whichever drained. Check `coalesce_guard_fire_n` and `last_pc_symbol`:
  - CLEAN, or a crash with `coalesce_guard_fire_n=0`, or a crash with `coalesce_guard_fire_n>=1` and
    `last_pc_symbol` OUTSIDE `coalesceFreeHeapBlocks` entirely: fix confirmed -- the bail no longer
    self-crashes the loop. Needs 2-3 more non-recurrence soaks before calling it validated (4-run bar).
  - `coalesce_guard_fire_n>=1` AND `last_pc_symbol` STILL `coalesceFreeHeapBlocks+1052` /
    `last-guest-pc=0x80002358`: fix did NOT take -- re-check the regenerated `funcs_0.c` for
    `ctx->r3 = 0x8;` on one line; if missing, the regen didn't apply this session's patch.
  - `coalesce_guard_fire_n>=1` at `coalesceFreeHeapBlocks` but a NEW third offset: a 3rd unguarded site,
    same idiom -- source-read and guard it.

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 5 -- s359's loop2 write guard, still
awaiting its own first verify pair).**
- **Step 1**: `s359_drainmeshloop2writeguard_verify1/2.sh` are queued in `scratch/agent/soak_queue/`
  (`HOLD_S=240`) -- let the loop drain them.
- **Step 2 (once drained)**: check `loop2_write_guard_fire_n` and `last_pc_symbol`:
  - CLEAN, or crash with `loop2_write_guard_fire_n=0`, or `last_pc_symbol` OUTSIDE
    `drainMeshReleaseQueue`: fix confirmed -- needs 2-3 more non-recurrence soaks (4-run bar).
  - `loop2_write_guard_fire_n>=1` AND `last_pc_symbol` STILL `drainMeshReleaseQueue+3752` /
    `last-guest-pc=0x80008218`: fix did NOT take -- re-check regenerated `funcs_3.c` for the guard body
    at that site (grep `drain-mesh-loop2-write-guard`).
  - `loop2_write_guard_fire_n>=1` but a NEW offset inside `drainMeshReleaseQueue`: a 4th sibling site in
    the same function/idiom family -- source-read and guard it (same practice as every prior step in this
    chain: s350->s350b->s357->s359).
  - If `ring_fire_n>=1` again: compare `iter_at_bail`/`v1[0]` against the now-4-sample-strong
    `iter_at_bail=1, v1[0]=0x00010001` baseline -- a 5th match keeps strengthening the
    single-deterministic-corruption-source reading from item -208; a mismatch would be the first evidence
    against it (the original Thread B discriminator, still open after 4 consistent samples).

**Recommendation**: 4 recipes total pending across both threads (2 Thread A -- now 2 gaps stale, 2 Thread
B -- freshly queued this session). Next session: prioritize draining/reading Thread A specifically if its
recipes still haven't run (they're now the oldest-waiting instrument in the whole queue); otherwise read
whichever pair(s) drained and resolve per the steps above.

## Notes carried forward
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (guest checkpoint,
  only meaningful if the crashing function is breadcrumbed) answer different questions by design.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` -- matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- A crash under ~5s that never reaches `title_reached` is NOT a meaningful test of any post-title-window
  instrument -- don't count it toward a non-recurrence tally; it belongs in the "boot-time crash family"
  bucket (`musyxSynthFrame+4652` is the one seen so far).
- **Regen-reliability gotcha (item -20), re-confirmed again this session**: `N64Recomp` skips rewriting
  any `RecompiledFuncs/funcs_*.c` that already exists on disk -- ALWAYS delete all `funcs_*.c` before
  re-running `N64Recomp`. Deleting all 45 files needs multiple flat `rm -f path1 path2 ...` calls (no
  glob, no compound `for`/`xargs`) per the sandbox's headless permission matcher.
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

## Queued this session (s359, ready for the loop)

`s359_drainmeshloop2writeguard_verify1/2.sh` (Thread B, `HOLD_S=240`), both in
`scratch/agent/soak_queue/`. `s358_coalesceheapbailfix_verify1/2.sh` (Thread A) still undrained -- also
still queued. 4 recipes total pending; loop drains up to 2 per gap.

HYPOTHESIS-ID: m5-audio-destub-linkedlist-corruption-source (iteration 5 -- landed a source-proved fix
this session on informative data, not a pivot; same s350->s350b pattern recurring one loop over).
Parallel/still-open: m5-audio-destub-coalesce-heap-guard-verify (iteration 4, s358's fix still awaiting
its first verify pair, 2 gaps skipped as of this session's start).
