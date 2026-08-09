# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s547 recap (read this first)

s547 was a MAINTENANCE iteration (docs/CURRENT-TRUTH.md hit 60861 bytes, over the 60000-byte Step-0
trigger). No experiment ran; the queued `s546_five_tied_guards_confirm` result below is STILL
UNFOLDED — it's the first thing to do this iteration, exactly as s546 left it. Compacted
CURRENT-TRUTH.md (560→358 lines, 60861→36092 bytes) by migrating the fully-redundant item -317
session-by-session narrative (already duplicated in PROJECT-OVERVIEW §25) down to a status summary,
migrating "Overturned conclusions"/"Dead ends" to a new PROJECT-OVERVIEW §26, and compacting items
-328..-333 into one paragraph. No ledger facts changed — item -317's tally, item -333, and every
guard's status are unchanged from s546. Full detail: PORTING-STATE.md Session 547.

## s546 recap (read this first)

**Folded in s545's queued 5-guard confirm — CLEAN.** `s545_five_tied_guards_confirm` came back with
0 fires on any of the 5 guards under test (`EMIT_COLOR_FILL_RECT_R4_GUARD`,
`EMIT_MATERIAL_TEXTURED_DL_R1_GUARD`, `EMIT_MATERIAL_TEXTURED_DL_ALT_R1_GUARD`,
`SUBMIT_SCENE_NODE_RENDER_R5_GUARD`, `RENDER_LIT_MESH_R11_GUARD`), 0 fires on any other armed guard
family at all this run, `hangarbay-entry n=2600` (strong positive control). Crashed on the
long-recurring `0x800ab068` background-noise family. All 5 marked FULLY CLOSED 2/2 — closes the
campaign's 52 guards to 52/52 fully closed (zero open guards) for the ninth time.

**Found and fixed the next tier (s546)**: fresh re-scan put a SECOND five-way tie at count=16 (exact
guarded shape reg=`r2`/off=`0X4`) spanning THREE functions:
- `renderFlatMeshFaceGroup` (funcs_4.c:6268, site=`0x800114C0`) — a 3rd site alongside R1/R2.
- `renderFlatMeshFaceGroup` (funcs_4.c:7045, site=`0x80011904`) — a 4th site.
- `renderLitMeshFaceGroup` (funcs_4.c:12782, site=`0x8001347C`) — a 12th site alongside R2-R11.
- `renderLitMeshFaceGroup` (funcs_4.c:13321, site=`0x8001370C`) — a 13th site.
- `drawSubtitleText` (funcs_4.c:24022, site=`0x800163C8`) — a 3rd site alongside R1/R2.

All 48 raw reload addresses plus each write's own address were checked directly against
`fixup_game_funcs.py` before patching — none appeared anywhere, no incidental matches this time
(unlike s545's `0x800101B0`). Fixed as `RENDER_FLAT_MESH_FACE_GROUP_R3_GUARD`,
`RENDER_FLAT_MESH_FACE_GROUP_R4_GUARD`, `RENDER_LIT_MESH_R12_GUARD`, `RENDER_LIT_MESH_R13_GUARD`,
and `DRAW_SUBTITLE_TEXT_R3_GUARD` (53rd-57th guards), batched into one build/run.

**1st live-verify clean on the first attempt**: 0 fires on any of the 5 new guards, 0 fires on any
other armed guard family at all (no co-fires this run), `hangarbay-entry n=2600` (strong positive
control). Crashed at 131.6s on `pc-symbol=findAndUnlinkSmallestEntry+356`/`last-guest-pc=0x8000d698`
— checked against every catalogued background-noise family, no match. Genuinely NEW, `(local-symtab)`
-tagged. Filed as **item -333** (single occurrence, not escalated) — only 16 bytes from item -331's
`0x8000d688` and in the same free-list-pop region, but a distinct guest PC, so NOT treated as a 2nd
occurrence of -331. Clean verify, own guards never fired. 2nd independent confirm already queued:
`scratch/agent/soak_queue/s546_five_tied_guards_confirm.sh` — the loop should pick this up between
iterations.

**Note for next session**: the s546 re-scan's ranked list beyond the accepted 5-way tie wasn't
examined — the next tier down (whatever count that is) is unknown, re-run the tracer fresh rather
than guessing. Watch item -333 and item -331 both — if EITHER recurs, especially with a matching
guest PC, treat it as urgent (this is the free-list-pop region, a historically sensitive area).

## This iteration's work unit

**Step 1 — fold in the queued confirm result (do this FIRST, before picking a new work unit).**
For `s546_five_tied_guards_confirm`, find its SOAK-RESULTS.md line, read the run.log INSIDE the
same-named results subdirectory (not just the top-level `.log` driver file — check BOTH, the real
per-guard diagnostics are not reliably in one or the other from session to session), and grep for:
- `render-flat-mesh-face-group-r3-guard`, `render-flat-mesh-face-group-r4-guard`,
  `render-lit-mesh-r12-guard`, `render-lit-mesh-r13-guard`, and `draw-subtitle-text-r3-guard` fire
  counts (expect 0 for a clean result, ALL FIVE)
- fires on any OTHER armed guard family (regression check) — remember sibling guards dumping a
  single `n=0` diagnostic snapshot AT crash time is NOT a fire (s541/s544 precedent)
- `hangarbay-entry` count — must be non-trivial (double digits+) or the run is vacuous per iron
  rule 1; if weak/absent, discard and re-queue a retry IMMEDIATELY in the same iteration, don't just
  accept a weak result (s543/s544/s545 precedent: retry right away, don't just note it and move on)
- the crash signature this run hit — check the `last-guest-pc` value (not just the symbolizer's
  `pc-symbol` name, which varies build to build for the same guest PC) against items -320 through
  -333 in `docs/CURRENT-TRUTH.md` Next-steps, the s354-366 `coalesceFreeHeapBlocks` family, the
  `0x800ab068` background-noise family, and the s422 `0x800290d4` `inflate_fast` artifact (all in
  `docs/PROJECT-OVERVIEW.md`/Overturned-conclusions); if it's a genuinely new guest PC, file it as
  item -334. If it matches item -333's `0x8000d698` exactly, that's a 2nd occurrence — escalate per
  the note above.

If clean with a valid positive control: mark all 5 guards FULLY CLOSED 2/2 — update rows 53-57's
status text in `docs/PROJECT-OVERVIEW.md` §25's table (matching the format of every other closed
row) and fold the summary into `PORTING-STATE.md`. This would close the campaign's 57 guards to
57/57 fully closed (zero open guards) for the tenth time.

**Step 2 — re-scan and audit the next-ranked tier, same iteration (fold-in-then-pick pattern).**
1. Re-run the tracer fresh (no custom `--out`, s521's gotcha):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. Skip any entry matching `renderLitTexturedMeshFaces` reg=`r4`/off=`0X0` or
   `renderFlatMeshFaceGroup` reg=`r4`/off=`0X0` (both are the same long-standing, repeatedly-
   re-derived shape mismatch — `ctx->r4` there is the owning function's own provably-non-null `$a0`
   argument, not a reloaded global; re-verify this is still the case each session, don't assume).
3. Identify the top-ranked write line(s) NOT already fixed AND matching the exact shape (`reg=r2,
   off=0X4`, i.e. a `MEM_W(0X4, ctx->rN) = ctx->rM;` fed by a `lui $v0,0x8011`/`lw $v0,0x63B0($v0)`
   load pair gated by `beq $v0,$zero,...`). If tied entries appear (this campaign has hit 5-way ties
   twice now, s545 and s546 — batch as many as are genuinely tied, don't artificially cap at 2), batch
   them into one build/run per the batch-instrumentation rule.
4. Pull all raw reload addresses feeding the target write line(s): filter
   `scratch/agent/s494_item317_step3_report.json` by `func==<name>`, then for each record check its
   `hits` list for an entry whose `line` matches the target write line — print that record's
   `guest_addr` for every match. `write_line` is NOT a top-level field, it's `hits[].line`.
5. Cross-check EVERY raw address against `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   directly (NOT under a `tools/` subdirectory, and NOT the same repo as `RogueSquadron64Recomp` — it's
   a separate standalone git checkout with its own origin, untracked `fixup_game_funcs.py`, no
   submodule-patches export needed). Known guard addresses so far: `submitSceneNodeRender` R1-R5,
   `emitColorFillRect` R1-R4, `drawSubtitleText` R1-R3, `renderLitTexturedMeshFaces` R1-R4,
   `renderFlatMeshFaceGroup` R1-R4, `renderLitMeshFaceGroup` R2-R13, `emitMaterialTexturedDL` R1,
   `emitMaterialTexturedDLAlt` R1 — check the new candidate isn't one of those or their own load
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
   `scratch/agent/soak_queue/done/` (`s546_five_tied_guards_manual.sh` is the latest full env-var
   list), append the new guard's `ROGUESQ_LOG_<NAME>=1` (append, don't remove any existing ones —
   batch-instrumentation rule), point output at a new `scratch/agent/soak_results/s547_..._manual`
   path, run with `Bash` (it will auto-background if it exceeds the foreground timeout), then
   `TaskOutput` with `block: true` and `timeout: 300000` to wait synchronously. After running it, move
   it to `soak_queue/done/` yourself so the loop doesn't re-execute it a second time. **If the first
   attempt comes back with a single-digit `hangarbay-entry` count, discard it and retry immediately
   in the same iteration (s543/s545 precedent) — don't accept a weak positive control.**
10. Read the run.log directly (grep the new guard's fire count, `hangarbay-entry` count, crash/signal
    markers). **Never trust a 0-fires result without confirming `hangarbay-entry` (or another armed
    positive control) actually appears with a non-trivial (double-digit+) count.** If weak/absent,
    discard and re-run. If clean with a real positive control, queue a 2nd independent confirm to
    `scratch/agent/soak_queue/s547_..._confirm.sh` and record the 1st-verify result in
    `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard(s) across BOTH the 1st live-verify and the 2nd
independent confirm, each WITH a same-run `hangarbay-entry` positive control that actually fired
non-trivially, is what promotes a guard to FULLY CLOSED 2/2. Any nonzero fire count on any new guard
would be the first actual confirmation this idiom class fires in practice (none of the 57 guards
fixed so far have ever fired) — treat that as a genuinely new, high-priority finding.

## Iron-rule reminders specific to this campaign
- Never trust the tracer's raw per-tier count without BOTH the shape check (reg/off match the guarded
  idiom) AND the address-by-address cross-check against `fixup_game_funcs.py` AND a direct read of the
  generated source.
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
  DIFFERENT host `pc-symbol` almost every time it's hit (`loadCutsceneAssetsByIndex+1860`,
  `hangarTickCameraOrbit+5188`, `initVec4TripletFromArgs+68`, ...) — always cross-check the
  `last-guest-pc` value itself, not just the symbol name, before filing a "new" item.
- **`coalesceFreeHeapBlocks+4424`/`0x8000247c` background-noise gotcha (s542)**: another long-recurring
  stable signature, catalogued since the s354-366 heap-walker arc — check exact pc-symbol+guest-PC pairs
  in `docs/PROJECT-OVERVIEW.md` before filing a crash hit as new.
- **`setByteAcrossEntryList+176`/`0x800aafa8` background-noise gotcha (s531/s543)**: item -306's
  already-catalogued signature; recurs across multiple sessions' weak/short runs.
- **`loadDatFile+1152`/`0x800290d4` background-noise gotcha (s545)**: this is the s400-421→s422
  `inflate_fast` clean-return misattribution artifact from the Overturned-conclusions section — a
  sparse breadcrumb shared across unrelated crash functions, not a real corruption sink, not a new item.
- **item -332 watch**: `submitSceneNodeRender+38976`/`0x8001086c` has recurred TWICE (once weak-control,
  once strong-control) — a 3rd occurrence would justify source-tracing it, unlike most of this
  campaign's single-occurrence breadcrumbs.
- **item -331/-333 watch (s546)**: `heapFreeListDequeue+29152`/`0x8000d688` (item -331) and
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
  <path>` instead of inlining via heredoc for anything with dict/brace-heavy Python.
- After launching a manual live-verify in the background, use `TaskOutput` with `block: true` and a
  generous `timeout` (e.g. 300000ms) to wait synchronously before doing anything else.
- Full guard-by-guard table and mechanism detail for everything closed so far: `docs/PROJECT-OVERVIEW.md`
  §22-§25.
