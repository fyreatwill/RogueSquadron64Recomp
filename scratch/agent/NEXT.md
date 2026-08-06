# NEXT work unit

## s368: Thread B CLOSED — both M5 Step 5 threads now closed; new thread opens on `heapWalker+1696`

Session-start mechanical check found `s367_drainmeshtailptrguard_verify3/4` had already drained.
Both runs reached title (45.1s/44.8s) with an identical, non-zero fire pattern across every
`drainMeshReleaseQueue` guard family (`tailptr2/3/4/5`, all `head1-5`+clears, all `loop2-5`+writes,
`read`/`write`/`ring`) — the first-ever positive control these guards fire under real gameplay — yet
both crashed at `pc-symbol=heapWalker+1696`/`last-guest-pc=0x8000834c`, which is
`drainMeshReleaseQueue`'s OWN final return checkpoint (item -221): the function completed and
returned normally in both runs. Since `heapWalker+1696` already hit twice in `s364`, *before* the
tailptr guards existed, the guards cannot have caused it — ruling out "guard papers over corruption
that resurfaces downstream" for this pair. Combined with `s365_verify1` (clean, zero fires, full
hold) and s366's static audit, `drainMeshReleaseQueue` is 3-for-3 post-guard soaks with zero crashes
inside the function. **Thread B closes.** Both M5 Step 5 threads (A: item -221 s366, B: item -223
s368) are now closed. Full writeup: CURRENT-TRUTH item -223, PORTING-STATE Session 368.

## Two live threads for the next iteration — pick ONE

### Thread 1 (recommended first — cheap, no build/soak): map `heapWalker+1696` to a guest address

`heapWalker+1696` is now n=4 (2×s364, 2×s367/s368), all four byte-identical, crossing the
background-noise catalogue's "3rd hit" escalation trigger. `s193_disasm.py` confirmation (done s368,
free — pure binary analysis, no new build/soak) decoded the crash instruction:

    python3 scratch/agent/s193_disasm.py build/RogueSquadron64Recomp heapWalker 1696 40

→ `STR W8,[X5,X10]` (indexed store), fed by `LDR X8,[X8,#24]` (-28) and `LDR X10,[X10,#16]` (-16) —
the same "chase an unvalidated pointer through a load, use the loaded value as an index/target for a
further write" idiom already guarded 4x in `heapWalker` (GUARD1-4, s157-s218,
`fixup_game_funcs.py` `_heapwalker_guard_sites` / `_heapwalker_guard3_sites` / `_heapwalker_guard4_sites`
— guest addresses `0x80007A10..0x80007BBC`), but this ARM64 offset does not correspond to any of
those already-patched sites — a 5th, unguarded site in the same function.

**Next step**: find `heapWalker`'s `RECOMP_FUNC` boundary in the regenerated `funcs_3.c` (delete all
`funcs_*.c` first per the regen-reliability gotcha, then rerun `N64Recomp` + `fixup_game_funcs.py` +
cmake if not already fresh), grep for `MEM_W` writes matching a two-hop pointer-chase-then-indexed-
store shape near (but outside) the four existing guard address lists above, identify the exact guest
address, and add a GUARD5 patch following the same pattern (range-check the index/base pointer
before the store, bail to the nearest natural loop-exit label — verify the CONTROL PATH per the
guard-bail-target gotcha, not just that a branch exists). Validation soak: same recipe style as
prior heapWalker guard work (arm `ROGUESQ_LOG_HEAPWALKER_GUARD5`-equivalent + all existing
instruments), 2 soaks, check for a same-run positive control (guard fires) and non-recurrence of the
`heapWalker+1696` signature.

### Thread 2 (alternative — bigger scope): M5 Step 6, PCM sanity-check

No M5 Step 5 threads remain open. Per `M5-AUDIO-PLAN.md` §4 Step 6: confirm real (non-silent,
non-garbage) PCM data reaches `SDL_QueueAudio` once the ucode is live, via a sanity counter/checksum
in `queue_samples` (`audio.cpp`) — the host bridge is already fully implemented, this is a
verification-only step, no new plumbing needed. Read `M5-AUDIO-PLAN.md` §4 Step 5/6 in full before
starting; Step 5 (crash-rate comparison across the 3 reversed gate sites) may need to be confirmed
done first — check PROJECT-OVERVIEW §10 for whether Step 5's rate-comparison bar was met.

## Background-noise catalogue (do NOT escalate reactively — 3rd independent hit is the trigger)

- `trackResourceListWithMappingTables+1192` — n=2 (s347, s362). Apple-framework `dladdr` fallback,
  host code.
- `unregisterServiceWorker+536` — n=2 (Session 265, s362). Apple-framework `dladdr` fallback, host
  code.
- `fscache_insert_and_retain+1192` — KNOWN Metal shader-compiler system crash (item -10, s270).
- `heapWalker+1696` — **ESCALATED s368, n=4, now Thread 1 above** — no longer background noise, has
  its own active investigation thread.
- `musyxSynthFrame+4652` — n=1 (s367), pre-title (<5s), unrelated audio-boot subsystem. Shares a
  `last-guest-pc` value with `heapWalker+1696` purely because that's a persistent global breadcrumb
  — NOT the same crash family (see the same-checkpoint-value gotcha below).

## Notes carried forward (all still current)

- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (guest
  checkpoint, only meaningful if the crashing function is breadcrumbed) answer different questions —
  a stale-but-valid `last-guest-pc` from a function that already returned can look like it implicates
  that function when it doesn't. Always check `pc-symbol` before trusting a `last-guest-pc` match.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode` (force-zeroed); `setDisplayMode` stays
  unmatched/reversed.
- A crash under ~5s that never reaches `title_reached` is NOT a meaningful test of any post-title
  instrument — don't count it toward a non-recurrence tally.
- **Regen-reliability gotcha (item -20)**: `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c`
  that already exists on disk — ALWAYS delete all `funcs_*.c` before re-running `N64Recomp`. Use
  absolute-path flat `rm -f` calls (no glob, no cd, no compound for/xargs) per the sandbox matcher.
- **Implementation gotcha**: `re.subn`'s plain-string `repl` gets backslash-escape-processed by `re`
  — ALWAYS use a lambda callback for multi-line replacement text; verify by grepping the regenerated
  `.c` for the new text on one line.
- **Guard-bail-target gotcha (s358)**: a synthetic-value guard's branch target can be a loop's
  re-entry label, not an exit — verify the CONTROL PATH, not just that a branch exists.
- **Read-guard/write-guard sibling gotcha**: a guard on a READ through a corrupted pointer does not
  repair the pointer — if reused UNGUARDED later (especially a WRITE), the crash moves there. When
  defining an idiom class, grep for the DATA-FLOW pattern, not just one syntactic shape.
- **Off-target-but-discriminating gotcha**: a soak's own "inconclusive" verdict for its target
  question can still be highly informative for a DIFFERENT open thread or the background-noise
  catalogue — always cross-check `last_pc_symbol`/`last-guest-pc` against ALL open threads.
- **Stale-NEXT.md gotcha (recurred NINE sessions running, s360-s368)**: NEXT.md can claim a queued
  pair is "still pending" when `SOAK-RESULTS.md` already shows it drained. Mechanical check every
  session: `grep -c '<recipe-basename>' scratch/agent/SOAK-RESULTS.md`.
- **Guard fire_n=0 is itself informative, not just "didn't matter" (s361)**: check for short-circuit
  paths around a guarded loop body that bypass the guard's own instrumentation while still feeding an
  unvalidated pointer downstream.
- **Same-checkpoint-value ≠ same crash (s367)**: `last-guest-pc` breadcrumb variables are global and
  persist across calls/runs; two crashes sharing the same value can be unrelated subsystems if their
  `pc-symbol` differs. Always check `pc-symbol` before trusting a shared guest-pc as a pattern match.
- **Guard-fired-but-function-completed-normally (s368, new)**: a guard family can fire on literally
  every run (deterministic, not sporadic corruption) while the guarded function still returns
  normally — firing proves the guard is exercised (positive control) but does NOT by itself mean
  the guarded function is still crashing. Check whether the function's OWN return checkpoint was
  reached before concluding a guard-fire run is evidence of an open problem in that function.
- **Timeline-based causation check (s368, new, generalizable)**: when a downstream crash coincides
  with a guard change, check whether the SAME crash signature already existed in soaks that predate
  the guard — if so, the guard can be ruled out as the cause without further instrumentation. Cheap,
  should be the first check whenever a "did my guard just move the crash?" question comes up.
- **Soak-queue drain order (resolved s362)**: `tools/agent/loop.sh` drains `"$qdir"/*.sh` via bash's
  default lexicographic glob — alphabetical = chronological for `sNNN_..._verifyM.sh` naming.

## Queued, ready for the loop

Empty — no soaks queued this session. Thread 1 above needs a source-read/patch step before its
validation soak can be written; Thread 2 needs a scope-check before its own soak recipe.

HYPOTHESIS-ID: heapwalker-guard5-site (iteration 1 — new thread opened s368 after both M5 Step 5
threads closed; `m5-audio-destub-linkedlist-corruption-source` is now CLOSED).
