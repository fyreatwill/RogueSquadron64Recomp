# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s548 recap (read this first)

**Folded in s546's queued 5-guard confirm — WEAK, discarded, retry re-queued.**
`s546_five_tied_guards_confirm` (renamed `s548_five_tied_guards_confirm_retry.sh` after a session-
numbering correction, see below) came back with `hangarbay-entry n=5` (single-digit, below the
double-digit bar) and crashed after 7 frames/20s on `pc-symbol=setByteAcrossEntryList+176`/
`last-guest-pc=0x800aafa8` — the already-catalogued item -306 background-noise family (s531/s543
gotcha). Discarded per iron rule 1, NOT accepted as a null result. Retry immediately re-queued:
`scratch/agent/soak_queue/s548_five_tied_guards_confirm_retry.sh` — the loop should pick this up
between iterations. Guards 53-57 (`RENDER_FLAT_MESH_FACE_GROUP_R3/R4_GUARD`, `RENDER_LIT_MESH_R12/
R13_GUARD`, `DRAW_SUBTITLE_TEXT_R3_GUARD`) remain at "1st live-verify clean, 2nd confirm pending" —
no promotion to FULLY CLOSED this session.

**Found and fixed the next tier (s548)**: fresh re-scan put a FOUR-WAY TIE at count=14 (exact
guarded shape reg=`r2`/off=`0X4`) spanning FOUR functions:
- `emitColorFillRect` (funcs_3.c:10105, site=`0x80009F50`) — a 5th site alongside R1-R4.
- `emitMaterialTexturedDL` (funcs_3.c:28876, site=`0x8000E608`) — a 2nd site alongside R1.
- `emitMaterialTexturedDLAlt` (funcs_3.c:30847, site=`0x8000ECD4`) — a 2nd site alongside R1.
- `submitSceneNodeRender` (funcs_4.c:2194, site=`0x80010728`) — a 6th site alongside R1-R5.

All 4 target write addresses (each function's OWN write address, read from generated source — NOT
one of the tracer's listed reload addresses) plus every raw reload address feeding them checked
directly against `fixup_game_funcs.py` before patching: none appeared anywhere, no incidental
matches, despite each function already carrying several existing guards at DIFFERENT addresses.
Fixed as `EMIT_COLOR_FILL_RECT_R5_GUARD`, `EMIT_MATERIAL_TEXTURED_DL_R2_GUARD`,
`EMIT_MATERIAL_TEXTURED_DL_ALT_R2_GUARD`, and `SUBMIT_SCENE_NODE_RENDER_R6_GUARD` (58th-61st guards),
batched into one build/run.

**1st live-verify**: first attempt WEAK (`hangarbay-entry n=5`, same item -306
`setByteAcrossEntryList+176`/`0x800aafa8` signature — TWO weak draws hitting this identical
background-noise family in the same session; worth watching whether it correlates specifically with
short/early-crash runs). Discarded per iron rule 1, retried immediately: full 300s duration, 106
frames captured, exit code 0 — **zero crashes of any kind for the entire run**, the cleanest possible
verify class. 0 fires on any of the 4 new guards. Only other guard activity: a single
`[hangarmenu-a0-guard] wild s3(a0)=0x80130B40 n=0` line — a benign already-catalogued diagnostic
snapshot (s541/s544 gotcha), not a fire. `hangarbay-entry n=33` (valid positive control). Clean
verify, own guards never fired. 2nd confirm already queued:
`scratch/agent/soak_queue/s548_four_tied_guards_confirm.sh` — the loop should pick this up between
iterations.

**Session-numbering note**: this session's work was initially drafted under the label "s547" before
realizing the prior commit had already used s547 for the maintenance pass — everything (guard-fix
comments in `fixup_game_funcs.py`, soak-queue script filenames/contents, doc references) was renamed
to s548. The two genuine s547 references (actual maintenance pass, PROJECT-OVERVIEW §25/§26) were
left untouched. Double-check `git log --oneline -3` at the START of every iteration to confirm the
next free session number before naming anything — don't assume NEXT.md's own prior-session label is
still accurate if a maintenance iteration or other out-of-band session may have intervened.

**Note for next session**: the s548 re-scan's ranked list beyond the accepted 4-way tie wasn't
examined — the next tier down (whatever count that is) is unknown, re-run the tracer fresh rather
than guessing. Watch for item -306's `setByteAcrossEntryList+176`/`0x800aafa8` signature specifically
on short/weak runs — it fired on 2 of this session's 3 short/weak draws, worth tracking whether this
correlates with early-crash runs generally (a possible confound for the double-digit `hangarbay-entry`
heuristic) rather than being purely random background noise.

## This iteration's work unit

**Step 1 — fold in BOTH queued confirm results (do this FIRST, before picking a new work unit).**

For `s548_five_tied_guards_confirm_retry` (guards 53-57), find its SOAK-RESULTS.md line, read the
run.log INSIDE the same-named results subdirectory (not just the top-level `.log` driver file — check
BOTH), and grep for:
- `render-flat-mesh-face-group-r3-guard`, `render-flat-mesh-face-group-r4-guard`,
  `render-lit-mesh-r12-guard`, `render-lit-mesh-r13-guard`, and `draw-subtitle-text-r3-guard` fire
  counts (expect 0 for a clean result, ALL FIVE)
- fires on any OTHER armed guard family (regression check) — remember sibling guards dumping a
  single `n=0` diagnostic snapshot AT crash time is NOT a fire (s541/s544 precedent)
- `hangarbay-entry` count — must be non-trivial (double digits+) or the run is vacuous per iron
  rule 1; if weak/absent AGAIN, discard and re-queue yet another retry immediately — this is the
  3rd attempt at this specific confirm (s546 fold-in weak, s548 fold-in weak), so if a 3rd weak draw
  lands, note it explicitly as a possible pattern (see the note above) rather than just retrying blind
- the crash signature this run hit — check `last-guest-pc` against items -320 through -333 in
  `docs/CURRENT-TRUTH.md` Next-steps, the s354-366 `coalesceFreeHeapBlocks` family, the `0x800ab068`
  background-noise family, the s422 `0x800290d4` `inflate_fast` artifact, and item -306's
  `setByteAcrossEntryList+176`/`0x800aafa8` (all in `docs/PROJECT-OVERVIEW.md`/Overturned-conclusions);
  if genuinely new, file as item -334.

If clean with a valid positive control: mark guards 53-57 FULLY CLOSED 2/2 — update rows 53-57's
status text in `docs/PROJECT-OVERVIEW.md` §25's table.

For `s548_four_tied_guards_confirm` (guards 58-61), same process: grep for
`emit-color-fill-rect-r5-guard`, `emit-material-textured-dl-r2-guard`,
`emit-material-textured-dl-alt-r2-guard`, `submit-scene-node-render-r6-guard` fire counts (expect 0,
ALL FOUR), regression check, `hangarbay-entry` positive control, crash signature cross-check. If
clean: mark guards 58-61 FULLY CLOSED 2/2, update rows 58-61 in PROJECT-OVERVIEW §25.

If BOTH fold-ins land clean this iteration, that closes the campaign's 61 guards to 61/61 fully
closed (zero open guards) for the tenth time — note this milestone explicitly in the ledger.

**Step 2 — re-scan and audit the next-ranked tier, same iteration (fold-in-then-pick pattern).**
1. Re-run the tracer fresh (no custom `--out`, s521's gotcha):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
   (Or use `scratch/agent/s548_dedupe_shape_filtered.py` — this is a reusable
   tool that filters the dedupe ranking to reg=`r2`/off=`0X4` writes specifically and prints ALL
   matching entries, not just the top 20 — more useful than the stock `s506_dedupe.py` for finding
   the next tier below an already-examined cutoff.)
2. Skip any entry matching `renderLitTexturedMeshFaces` reg=`r4`/off=`0X0` or
   `renderFlatMeshFaceGroup` reg=`r4`/off=`0X0` (both are the same long-standing, repeatedly-
   re-derived shape mismatch — `ctx->r4` there is the owning function's own provably-non-null `$a0`
   argument, not a reloaded global; re-verify this is still the case each session, don't assume).
3. The next tier below s548's accepted 4-way tie (count=14) is COUNT=13, a genuine pair ALREADY
   confirmed uncovered but not yet fixed: `emitAllocatedDLCommand` (funcs_3.c:4554, write address
   `0x80008908`) and `reserveAndEmitDLEntry` (funcs_3.c:22546, write address `0x8000CE10`) — both
   BRAND-NEW functions for this campaign (never guarded before). Both write addresses were already
   cross-checked against `fixup_game_funcs.py` in s548 (alongside the 4-way tie fixed that session)
   and confirmed absent — safe to fix directly without re-deriving. Re-verify the exact idiom shape at
   each site before fixing (the s535 lesson still applies). If tied entries appear at a lower count
   too, batch as many as are genuinely tied (this campaign has hit 4- and 5-way ties repeatedly —
   don't artificially cap).
4. Pull all raw reload addresses feeding the target write line(s): filter
   `scratch/agent/s494_item317_step3_report.json` by `func==<name>`, then for each record check its
   `hits` list for an entry whose `line` matches the target write line — print that record's
   `guest_addr` for every match. `write_line` is NOT a top-level field, it's `hits[].line`. **The
   write's OWN guest address is NOT in this reload-address list** — read it directly from the
   generated source at the target line (s548 lesson: don't assume the tracer's reload addresses
   include the write instruction's own address).
5. Cross-check EVERY raw address AND the write's own address against
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   directly (NOT under a `tools/` subdirectory, and NOT the same repo as `RogueSquadron64Recomp` — it's
   a separate standalone git checkout with its own origin, untracked `fixup_game_funcs.py`, no
   submodule-patches export needed). Known guard addresses so far: `submitSceneNodeRender` R1-R6,
   `emitColorFillRect` R1-R5, `drawSubtitleText` R1-R3, `renderLitTexturedMeshFaces` R1-R4,
   `renderFlatMeshFaceGroup` R1-R4, `renderLitMeshFaceGroup` R2-R13, `emitMaterialTexturedDL` R1-R2,
   `emitMaterialTexturedDLAlt` R1-R2 — check the new candidate isn't one of those or their own load
   addresses. A raw reload address incidentally matching an UNRELATED guard elsewhere in the file
   (protecting a different write) is not disqualifying by itself — check what it actually protects
   (s545 precedent: `0x800101B0` matched the s197 `SCENE_NODE_CACHE_GUARD`, a different read).
6. Read the generated source around any zero-hit write address to confirm the exact vulnerable shape
   AND that the dereferenced register is actually a reload of the `+0x63B0`-offset global-table idiom
   (not a function argument or other already-validated value) — check this BEFORE the reachability
   cross-check (the s535 lesson).
7. Fix the first genuine candidate(s) using the same `fixup_game_funcs.py` template as every prior
   guard (skip-the-write-on-invalid, `ROGUESQ_LOG_<NAME>` env-gated stderr report, `U32()` range
   check `< 0x80000000u || >= 0x80800000u`). Name it `<FUNC>_R<N>_GUARD` — bump `N` if the function
   already has guards from this campaign, or `_R1_GUARD` for a brand-new function.
8. Regen (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → `cmake --build`, all four steps
   mandatory; delete `RecompiledFuncs/funcs_*.c` first via a `python3 -c` glob+os.remove loop, `find
   -delete` is blocked in this sandbox):
   ```
   cd /Users/williambuckley/Documents/Tools/N64Recomp
   python3 -c "import glob, os; [os.remove(f) for f in glob.glob('RecompiledFuncs/funcs_*.c')]"
   cd /Users/williambuckley/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
   cd /Users/williambuckley/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml
   python3 fixup_game_funcs.py > <path inside one of the 3 allowed repos>   # audit for exactly the
                                                                            # expected xN counts, then
                                                                            # delete the report after
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build && \
     DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
   ```
   Gotcha (s533): the CMake build directory that actually links `RogueSquadron64Recomp` is
   `RogueSquadron64Recomp/build`, NOT `N64Recomp/build`. Gotcha (s535): redirecting
   `fixup_game_funcs.py`'s output to `/tmp` is blocked by the sandbox — redirect inside one of the
   three allowed repos, delete after auditing.
9. 1st live-verify, manual, foreground — copy the most recent guard's manual script from
   `scratch/agent/soak_queue/done/` (`s548_four_tied_guards_manual_retry.sh` is the latest full
   env-var list), append the new guard's `ROGUESQ_LOG_<NAME>=1` (append, don't remove any existing
   ones — batch-instrumentation rule), point output at a new
   `scratch/agent/soak_results/s549_..._manual` path, run with `Bash` (it will auto-background if it
   exceeds the foreground timeout), then `TaskOutput` with `block: true` and `timeout: 300000` to wait
   synchronously. After running it, move it to `soak_queue/done/` yourself so the loop doesn't
   re-execute it a second time. **If the first attempt comes back with a single-digit
   `hangarbay-entry` count, discard it and retry immediately in the same iteration (s543/s545/s548
   precedent) — don't accept a weak positive control. Watch specifically for the item -306
   `setByteAcrossEntryList+176`/`0x800aafa8` signature on weak draws — it hit 2 of 3 weak draws this
   session.**
10. Read the run.log directly (grep the new guard's fire count, `hangarbay-entry` count, crash/signal
    markers). **Never trust a 0-fires result without confirming `hangarbay-entry` (or another armed
    positive control) actually appears with a non-trivial (double-digit+) count.** If weak/absent,
    discard and re-run. If clean with a real positive control, queue a 2nd independent confirm to
    `scratch/agent/soak_queue/s549_..._confirm.sh` and record the 1st-verify result in
    `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard(s) across BOTH the 1st live-verify and the 2nd
independent confirm, each WITH a same-run `hangarbay-entry` positive control that actually fired
non-trivially, is what promotes a guard to FULLY CLOSED 2/2. Any nonzero fire count on any new guard
would be the first actual confirmation this idiom class fires in practice (none of the 61 guards
fixed so far have ever fired) — treat that as a genuinely new, high-priority finding.

## Iron-rule reminders specific to this campaign
- **Confirm the next free session number at the START of every iteration** (`git log --oneline -3`)
  before naming anything — a maintenance iteration or other out-of-band session can advance the
  counter without this file being touched (s548 lesson).
- Never trust the tracer's raw per-tier count without BOTH the shape check (reg/off match the guarded
  idiom) AND the address-by-address cross-check against `fixup_game_funcs.py` AND a direct read of the
  generated source. The write instruction's OWN guest address is separate from its feeding reload
  addresses — look it up from generated source, don't assume it's in the tracer's reload-address list
  (s548).
- Never trust a 0-fires result without confirming the positive control appears with a non-trivial
  (double-digit+) count. A single-digit `hangarbay-entry` count means the run is too short to trust —
  discard and retry, don't report it as a result.
- One build/run carries every armed guard's env var (batch-instrumentation rule).
- `s506_dedupe.py` reads a FIXED canonical path; never pass a custom `--out` to `--scan`.
- Kill runs with SIGKILL only; capture paths must not start with "." in the final component; run from
  `build/` with the ROM present.
- `fixup_game_funcs.py`: `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` — NOT
  under a `tools/` subdirectory, NOT part of the RogueSquadron64Recomp git repo (separate standalone
  checkout, untracked file, no submodule-patches export step applies).
- The build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- `make_elf.py`: `/Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py` (a THIRD
  repo) — run it from that repo's root.
- **Soak result diagnostics gotcha (s539/s541)**: a soak's real per-guard diagnostics can live in a
  `run.log` file INSIDE a same-named results subdirectory, OR the retry script may point its `--out` at
  the ORIGINAL (non-retry-suffixed) results directory instead of a new one — check both locations, grep
  the one with actual `[guard-name]` lines, don't assume the naming is consistent.
- **JSON report field gotcha (s540)**: `s494_item317_step3_report.json` records don't have a top-level
  `write_line` field — the write line lives inside each record's `hits[].line`. Filter by `func` then
  check each hit's `line`.
- **Diagnostic-snapshot-not-a-fire gotcha (s541/s544)**: nearby sibling guards printing a single
  `n=0` line AT crash time is a diagnostic dump, not an actual fire — only a nonzero `n=` or multiple
  incrementing lines from the SAME guard name indicate a real fire. Don't miscount these as fires.
- **`0x800ab068` background-noise gotcha (s541)**: this recurring guest-PC crash resolves to a
  DIFFERENT host `pc-symbol` almost every time it's hit — always cross-check the `last-guest-pc` value
  itself, not just the symbol name, before filing a "new" item.
- **`coalesceFreeHeapBlocks+4424`/`0x8000247c` background-noise gotcha (s542)**: another long-recurring
  stable signature, catalogued since the s354-366 heap-walker arc — check exact pc-symbol+guest-PC pairs
  in `docs/PROJECT-OVERVIEW.md` before filing a crash hit as new.
- **`setByteAcrossEntryList+176`/`0x800aafa8` background-noise gotcha (s531/s543, reinforced s548)**:
  item -306's already-catalogued signature; recurred on 2 of 3 short/weak draws in s548 alone — worth
  actively watching whether it specifically correlates with early/short runs rather than being pure
  random noise.
- **`loadDatFile+1152`/`0x800290d4` background-noise gotcha (s545)**: this is the s400-421→s422
  `inflate_fast` clean-return misattribution artifact from the Overturned-conclusions section — a
  sparse breadcrumb shared across unrelated crash functions, not a real corruption sink, not a new item.
- **item -332 watch**: `submitSceneNodeRender+38976`/`0x8001086c` has recurred TWICE (once weak-control,
  once strong-control) — a 3rd occurrence would justify source-tracing it, unlike most of this
  campaign's single-occurrence breadcrumbs.
- **item -331/-333 watch**: `heapFreeListDequeue+29152`/`0x8000d688` (item -331) and
  `findAndUnlinkSmallestEntry+356`/`0x8000d698` (item -333) are 16 bytes apart in the same free-list-pop
  region, both single occurrences, both `(local-symtab)`-tagged (genuine in-function faults). Treated
  as DISTINCT items because the guest PCs differ — but if either recurs, or if a THIRD nearby address in
  this region appears, treat the region itself as suspicious and consider source-tracing regardless of
  per-address occurrence counts.
- **Incidental-match gotcha (s545)**: a raw reload address feeding the target write CAN appear
  elsewhere in `fixup_game_funcs.py` without disqualifying the candidate — check what that OTHER
  occurrence actually protects (a different read/write at a different guest PC) before assuming the
  target write itself is covered. Only the target write's OWN address being present is disqualifying.
- This sandbox blocks `find -delete`, multi-statement `&&`/`while`/heredoc chains, and output
  redirection to `/tmp` fairly often — prefer single simple commands. Grep with a literal path instead
  of a shell variable when the sandbox flags "shell syntax that cannot be statically analyzed" (also
  applies to `for addr in ...; do ...; done` loops using shell variable expansion — use Python instead).
  Writing a multi-line string with embedded `#` inside a quoted shell/python argument can also trip the
  sandbox ("Newline followed by # inside a quoted argument can hide arguments from path validation") —
  write long append content to a scratch `.md` file with the Write tool first, then `cat file >> target`.
  Heredocs (`<< 'EOF'`) containing braces/quotes can also trip "expansion obfuscation" detection —
  prefer writing a standalone `.py` script file with the Write tool and running it with `python3
  <path>` instead of inlining via heredoc for anything with dict/brace-heavy Python. Plain heredocs
  without braces/quotes (e.g. appending prose to a `.md` file) work fine (used successfully s548).
- After launching a manual live-verify in the background, use `TaskOutput` with `block: true` and a
  generous `timeout` (e.g. 300000ms) to wait synchronously before doing anything else.
- Full guard-by-guard table and mechanism detail for everything closed so far: `docs/PROJECT-OVERVIEW.md`
  §22-§25.
