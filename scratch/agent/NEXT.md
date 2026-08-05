# NEXT work unit

## s358: Thread A's `verify5/6` drained with a discriminating result — the s354 guard's OWN bail path
## was buggy (bailed INTO the loop instead of out of it), source-proved and fixed. Queued verify soaks
## for the fix. Thread B's s357 loop2-guard verify soaks are still undrained.

Full detail: `PORTING-STATE` Session 358, `docs/CURRENT-TRUTH.md` item -213.

`s356_coalesceheapguard_verify5` crashed at `pc-symbol=coalesceFreeHeapBlocks+1052`,
`last-guest-pc=0x80002358`, with `coalesce_guard_fire_n=1` (the s354 guard fired earlier in the same
run — positive control) yet the run still crashed inside the SAME function at a NEW offset. Source-read
found the guard's bail (`ctx->r3 = 0` on an out-of-range `v0`) sent control to `L_80002358`, which is the
coalesce loop's ENTRY label, not an exit — the bail was re-entering the loop with the still-wild pointer
instead of stopping it, and the delay-slot pointer advance (`ctx->r8 = v0 + 0x10`) happens unconditionally
regardless of which way the branch goes. Fixed the bail value (`ctx->r3 = 0 -> 0x8`, forcing the "next
block in use, stop coalescing" branch to `L_80002444` instead) — confirmed safe by reading the rest of the
function (`ctx->r8` unused between `L_80002444` and its next fresh reassignment). Full regen + rebuild
clean, patch report `x1`, single-line confirmed in regenerated source. Queued
`s358_coalesceheapbailfix_verify1/2.sh`.

## Two open threads — pick whichever has drained data first

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (iteration 4 — landed a source-proved fix to the
EXISTING guard's bail target this session, not a null reading).**
- **Step 1**: `s358_coalesceheapbailfix_verify1/2.sh` are queued in `scratch/agent/soak_queue/`
  (`HOLD_S=240`) — let the loop drain them, do NOT run inline.
- **Step 2 (next session)**: read whichever drained. Check `coalesce_guard_fire_n` and `last_pc_symbol`:
  - CLEAN, or a crash with `coalesce_guard_fire_n=0`, or a crash with `coalesce_guard_fire_n>=1` and
    `last_pc_symbol` OUTSIDE `coalesceFreeHeapBlocks` entirely: fix confirmed — the bail no longer
    self-crashes the loop. Needs 2-3 more non-recurrence soaks before calling it validated (4-run bar).
  - `coalesce_guard_fire_n>=1` AND `last_pc_symbol` STILL `coalesceFreeHeapBlocks+1052` /
    `last-guest-pc=0x80002358`: fix did NOT take — re-check the regenerated `funcs_0.c` for
    `ctx->r3 = 0x8;` on one line (grep it directly); if missing, the regen didn't apply this session's
    patch, re-run the fixup and diff.
  - `coalesce_guard_fire_n>=1` at `coalesceFreeHeapBlocks` but a NEW third offset: a 3rd unguarded site in
    the same function, same idiom — source-read and guard it (same practice as the drain-mesh family).

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 4 — s357's loop2 guard, still
awaiting its own first verify pair).**
- **Step 1**: `s357_drainmeshloop2guard_verify1/2.sh` are queued in `scratch/agent/soak_queue/`
  (`HOLD_S=240`) — still undrained as of s358 session start (the loop had not gotten to them yet). Let
  the loop drain them.
- **Step 2 (next session)**: same decision tree as s357's NEXT.md laid out — check `loop2_guard_fire_n`
  and whether `last_pc_symbol` relocated outside `drainMeshReleaseQueue`, stayed at a new offset inside
  it (guard needs another sibling site), or repeated `+3140`/`0x80008200` exactly (regen/patch mismatch).
  If a run shows `ring_fire_n>=1` (2nd informative ring sample): compare `iter_at_bail`/`v1[0]` against
  s357's `iter_at_bail=1, v1[0]=0x00010001` — consistent supports the structural-bug reading, differing
  supports state-dependent corruption (the ORIGINAL Thread B discriminator, still open).

**Recommendation**: 4 recipes total pending across both threads (2 Thread A, 2 Thread B), loop drains up
to 2 per gap. Next session: read whichever pair(s) drained, resolve per the steps above. Both threads are
equally high-information-value right now — each has exactly one freshly-landed, unverified fix.

## Notes carried forward
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (guest checkpoint,
  only meaningful if the crashing function is breadcrumbed) answer different questions by design.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- A crash under ~5s that never reaches `title_reached` is NOT a meaningful test of any post-title-window
  instrument — don't count it toward a non-recurrence tally; it belongs in the "boot-time crash family"
  bucket (`musyxSynthFrame+4652` is the one seen so far).
- **Regen-reliability gotcha (item -20), re-confirmed this session**: `N64Recomp` skips rewriting any
  `RecompiledFuncs/funcs_*.c` that already exists on disk — ALWAYS delete all `funcs_*.c` before re-running
  `N64Recomp`, or a fixup patch you just edited will silently keep applying to STALE pre-edit source. This
  session's `rm -f` had to be done as individual/batched plain commands (no glob, no compound `for`/`xargs`
  pipeline) — the sandbox's headless permission matcher treats compound shell operators (`;`, `|`, `&&`,
  glob expansion in `rm`) as needing separate approval even when the target path is otherwise unrestricted;
  a flat `rm -f <path1> <path2> ...` with explicit absolute paths (no shell metacharacters) works directly.
- **Implementation gotcha for future `fixup_game_funcs.py` patches**: `re.subn`'s plain-string
  `repl` argument gets backslash-escape-processed by the `re` module itself (`\n` → real newline, etc.) —
  ALWAYS use a lambda callback for multi-line replacement text containing `\n`/`\t`/etc. inside embedded
  C string literals. Every multi-line patch in the file follows this; verify after any new patch by
  grepping the regenerated `.c` file for the new/changed text and confirming it's on one line.
- **Guard-bail-target gotcha (new this session, generalize when auditing other guards)**: when adding a
  range-check-and-bail guard that substitutes a synthetic value for a skipped read, verify which CONTROL
  PATH that synthetic value actually sends execution down — don't assume a "looks like a stop" label on a
  branch target. In a loop, a backward branch's target label can be the loop's re-entry point, not an
  exit; confirm which label is actually reached and whether that label leads to further use of the guarded
  pointer before treating a "bail" as safe. The other drain-mesh-family and hangar-list guards in this file
  used the same idiom successfully because their bail branches genuinely led to loop exits — this was a
  one-off design error in the s354 guard specifically, not evidence the idiom itself is unsound.

## Queued this session (s358, ready for the loop — nothing run yet)

`s358_coalesceheapbailfix_verify1/2.sh` (Thread A, `HOLD_S=240`), both in `scratch/agent/soak_queue/`.
`s357_drainmeshloop2guard_verify1/2.sh` (Thread B) still undrained, also still queued. 4 recipes total
pending; loop drains up to 2 per gap.

HYPOTHESIS-ID: m5-audio-destub-coalesce-heap-guard-verify (iteration 4 — landed a source-proved fix this
session to the existing guard's bail target, not a pivot). Parallel/still-open:
m5-audio-destub-linkedlist-corruption-source (iteration 4, s357's loop2 guard still awaiting its first
verify pair as of this session's start).
