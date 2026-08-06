# NEXT work unit

## s369: heapWalker GUARD5 landed — first empirical verification is the next iteration's job

s368 left `heapWalker+1696` (n=4, byte-identical `last-guest-pc=0x8000834c`) as an escalated,
not-yet-identified 5th unguarded site in `heapWalker`. This session mapped it to a guest address and
landed the guard. Summary (full detail: CURRENT-TRUTH item -224, PORTING-STATE Session 369):

- `otool`/`nm`/`objdump`/`dwarfdump` are all still sandbox-blocked (reconfirmed this session) — kept
  using the hand-rolled `scratch/agent/s193_disasm.py`, extended with a register-offset LDR/STR
  decoder case (it previously only covered immediate-offset forms).
- Ruled out symbol misattribution first (heapWalker's compiled size is ~10 KB / ~2500 ARM64 instrs
  vs ~800 bytes / ~175 MIPS instrs of guest code — `+1696` is genuinely inside the function).
- Decoded the crash instruction: `STR W8,[X9,X10]` fed by `LDR X8,[X8,#24]` / `LDR X10,[X10,#16]`.
  Cross-checked against `recomp_context`'s field layout (`gpr r0,r1,r2,...`, `gpr`=`uint64_t` → r2 at
  +16, r3 at +24) — these are plain `ctx->r2`/`ctx->r3` struct reads, NOT a raw-pointer chase (item
  -223's original characterization was a plausible but wrong first read).
- Source cross-check landed on `MEM_W(0X4, ctx->r2) = ctx->r3;` (guest `0x80007A3C` + 4 unrolled
  siblings), where `ctx->r2` is a freshly-read global table-head pointer checked only for `!= 0`,
  never range-validated — same idiom as guards 1/3/4, new register.
- Guarded all 5 sites (`ROGUESQ_LOG_HEAPWALKER_GUARD5`), armed by default in
  `scratch/s73_post_a_scene/run_s327waitpump.sh`. Full regen+rebuild clean, patch report `x1` per
  site, idempotency-refusal confirmed on a 2nd fixup run.
- Queued `s369_heapwalkerguard5_verify1.sh` / `s369_heapwalkerguard5_verify2.sh` (HOLD_S=240) — the
  loop should drain these before the next iteration starts.

## Next iteration: drain the s369 pair and read the decision tree

**Mechanical check first** (the stale-NEXT.md gotcha has recurred 9+ sessions running):
`grep -c 's369_heapwalkerguard5' scratch/agent/SOAK-RESULTS.md` — if it already shows 2 lines, the
pair has drained; read the actual logs before assuming anything below is still pending.

Once `s369_heapwalkerguard5_verify1/2` results are in, apply this decision tree (also embedded in
the soak scripts themselves, `scratch/agent/soak_queue/done/s369_heapwalkerguard5_verify*.sh` after
they drain):

1. **`guard5_fire_n>=1` in either run**: first-ever positive control for the new instrument — the
   site is real and reachable. This alone does NOT confirm it's THE crash cause; check whether a
   crash still occurred in the SAME run despite the fire (would mean this guard papered over one
   write but the corruption source is upstream/elsewhere, or a 6th site exists).
2. **Both clean, OR both crash at a symbol/guest-pc other than `heapWalker+1696`/`0x8000834c`, with
   `title_reached` set (a real hold, not a <5s pre-title crash)**: 2 non-recurrence data points. Per
   this whole M5 saga's standing closure bar, that's enough to call this thread CLOSED — write the
   closure into CURRENT-TRUTH, fold into the M5 status summary, and move to whichever of Step 6 (PCM
   sanity-check) or a re-scope per `M5-AUDIO-PLAN.md` §4 is next.
3. **Still crashing at `heapWalker+1696`/`0x8000834c` with `guard5_fire_n=0` in both runs**: the guard
   regex likely didn't match the literal patched text, or the site identification is wrong. Re-grep
   `RecompiledFuncs/funcs_3.c` for `GUARD5` first (mechanical, free) before revisiting the source
   analysis.
4. **Still crashing at the same signature WITH `guard5_fire_n>=1` in the SAME run**: the guard fired
   but the crash persisted at the identical checkpoint. Don't jump straight to "6th site" — first
   check whether the fire correlates with the crash timing or is unrelated background activity
   (compare against any clean run's guard5 fire count once available).
5. A `<5s` pre-title crash (`title_reached` blank) is not informative for this thread's tally per the
   standing rule — re-queue rather than count it.

## Background-noise catalogue (do NOT escalate reactively — 3rd independent hit is the trigger)

- `trackResourceListWithMappingTables+1192` — n=2 (s347, s362). Apple-framework `dladdr` fallback,
  host code.
- `unregisterServiceWorker+536` — n=2 (Session 265, s362). Apple-framework `dladdr` fallback, host
  code.
- `fscache_insert_and_retain+1192` — KNOWN Metal shader-compiler system crash (item -10, s270).
- `heapWalker+1696` — was ESCALATED s368 at n=4; guarded s369; now this thread's own open question
  (see decision tree above), not generic background noise.
- `musyxSynthFrame+4652` — n=1 (s367), pre-title (<5s), unrelated audio-boot subsystem.

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
  absolute-path flat `rm -f` calls (no glob, no cd, no compound for/xargs) per the sandbox matcher;
  a single `rm -f path1 path2 ...` with many literal absolute-path arguments IS allowed (confirmed
  s369) even though it lists 15 paths at once — it's one command, not a compound one.
- **`fixup_game_funcs.py`'s own idempotency guard (confirmed s369)**: refuses a 2nd run once
  `funcs_0.c` carries `// RS64_FIXUP_APPLIED`, exiting 1 with an explicit message. That's the correct,
  expected outcome on a 2nd invocation without a fresh `N64Recomp` regen first — not a bug to chase.
- **Sandbox tool-access gotcha (reconfirmed s369)**: `otool`, `nm`, `objdump`, `dwarfdump` all require
  approval that can't be granted non-interactively — any ARM64↔guest-address mapping work has to go
  through `scratch/agent/s193_disasm.py`'s hand-rolled Mach-O symbol table reader + instruction
  decoder (now covers immediate-offset AND register-offset LDR/STR/LDP/STP/exclusive forms).
- **Implementation gotcha**: `re.subn`'s plain-string `repl` gets backslash-escape-processed by `re`
  — ALWAYS use a lambda callback for multi-line replacement text; verify by grepping the regenerated
  `.c` for the new text on one line.
- **Guard-bail-target gotcha (s358)**: a synthetic-value guard's branch target can be a loop's
  re-entry label, not an exit — verify the CONTROL PATH, not just that a branch exists.
- **Read-guard/write-guard sibling gotcha**: a guard on a READ through a corrupted pointer does not
  repair the pointer — if reused UNGUARDED later (especially a WRITE), the crash moves there. When
  defining an idiom class, grep for the DATA-FLOW pattern, not just one syntactic shape.
- **`MEM_W` macro signature (confirmed s369, `include/recomp.h:95-96`)**: `MEM_W(offset, reg)` =
  `*(int32_t*)(rdram + ((reg)+(offset)) - 0xFFFFFFFF80000000)`. Both arguments are ADDED (order-
  independent). In generator-produced code the offset arg is ALWAYS a compile-time hex literal (from
  the MIPS instruction's 16-bit immediate field) — a register/computed expression as the offset only
  appears in hand-written diagnostic PATCH blocks (e.g. `funcs_24.c`'s musyx-dma diagnostic), never
  in normal recompiler output. Don't expect to grep for "MEM_W(ctx->rX, ctx->rY)" as a discriminator
  — it won't exist outside hand-written patches.
- **`recomp_context` field layout (confirmed s369, `include/recomp.h:414-418`)**: `gpr r0, r1, r2,
  r3, ...` with `gpr` = `uint64_t` (8 bytes each) — so struct byte offsets are r0=0, r1=8, r2=16,
  r3=24, r4=32, etc. Useful any time a hand-decoded ARM64 load shows a small (`<256`-ish) immediate
  self-dereference offset near a `ctx`-adjacent register — check this table before assuming it's a
  guest-memory pointer chase.
- **Off-target-but-discriminating gotcha**: a soak's own "inconclusive" verdict for its target
  question can still be highly informative for a DIFFERENT open thread or the background-noise
  catalogue — always cross-check `last_pc_symbol`/`last-guest-pc` against ALL open threads.
- **Stale-NEXT.md gotcha (recurred TEN sessions running, s360-s369)**: NEXT.md can claim a queued
  pair is "still pending" when `SOAK-RESULTS.md` already shows it drained. Mechanical check every
  session: `grep -c '<recipe-basename>' scratch/agent/SOAK-RESULTS.md`.
- **Guard fire_n=0 is itself informative, not just "didn't matter" (s361)**: check for short-circuit
  paths around a guarded loop body that bypass the guard's own instrumentation while still feeding an
  unvalidated pointer downstream.
- **Same-checkpoint-value ≠ same crash (s367)**: `last-guest-pc` breadcrumb variables are global and
  persist across calls/runs; two crashes sharing the same value can be unrelated subsystems if their
  `pc-symbol` differs. Always check `pc-symbol` before trusting a shared guest-pc as a pattern match.
- **Guard-fired-but-function-completed-normally (s368)**: a guard family can fire on literally every
  run (deterministic, not sporadic corruption) while the guarded function still returns normally —
  firing proves the guard is exercised (positive control) but does NOT by itself mean the guarded
  function is still crashing. Check whether the function's OWN return checkpoint was reached before
  concluding a guard-fire run is evidence of an open problem in that function.
- **Timeline-based causation check (s368, generalizable)**: when a downstream crash coincides with a
  guard change, check whether the SAME crash signature already existed in soaks that predate the
  guard — if so, the guard can be ruled out as the cause without further instrumentation.
- **Symbol-boundary sanity check (s369, new, generalizable)**: before trusting any hand-decoded
  "function+offset" crash address, compare that symbol's vmaddr against the NEXT symbol's vmaddr in
  the Mach-O symbol table (`scratch/agent/s193_disasm.py`'s `find_segments_and_syms`, query both
  names) — if the offset exceeds the gap, the address may actually be inside a different, adjacent
  function with no size info to catch the misattribution. Cheap, should be the first check whenever
  hand-decoding a large offset into a small-looking source function.
- **Self-dereferencing-load ambiguity (s369, new, generalizable)**: a hand-decoded `LDR Xn,[Xn,#K]`
  near a crash site is NOT automatically a guest-memory pointer chase — it can just as easily be an
  ordinary `ctx->rN` struct-field read if `Xn` transiently held the `ctx` pointer. Check the small
  immediate `K` against `recomp_context`'s known field-offset table (above) before assuming the more
  exotic "corrupted pointer chased through its own fields" interpretation.
- **Soak-queue drain order (resolved s362)**: `tools/agent/loop.sh` drains `"$qdir"/*.sh` via bash's
  default lexicographic glob — alphabetical = chronological for `sNNN_..._verifyM.sh` naming.

## Queued, ready for the loop

`s369_heapwalkerguard5_verify1.sh` and `s369_heapwalkerguard5_verify2.sh` in
`scratch/agent/soak_queue/` — both HOLD_S=240, all current guard instruments (including the new
GUARD5) armed by default via `run_s327waitpump.sh`.

HYPOTHESIS-ID: heapwalker-guard5-site (iteration 2 — guard landed s369, awaiting first empirical
verification).
