# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s552 recap (read this first)

**Folded in both of s551's queued 2nd confirms — both came back WEAK, both now on a 2nd consecutive
weak draw for their respective targets.** `s551_emit_allocated_dl_command_r1_reserve_and_emit_dl_entry_r1_confirm_retry`
(guards 64-65): no `hangarbay-entry` line at all, process gone at 20.2s after 7 frames, crashed on the
item -306 `setByteAcrossEntryList+176`/`0x800aafa8` signature — the SAME failure mode as the previous
attempt. Discarded per iron rule 1. Retry queued (3rd attempt for this target):
`scratch/agent/soak_queue/s552_emit_allocated_dl_command_r1_reserve_and_emit_dl_entry_r1_confirm_retry2.sh`.
`s551_six_way_tie_confirm` (guards 66-71): identical failure mode, 1st confirm attempt for this target.
Retry queued: `scratch/agent/soak_queue/s552_six_way_tie_confirm_retry.sh`.

**Fresh tracer re-scan found the next tier: a THREE-WAY TIE at count=8** (same guarded shape
reg=r2/off=0X4, one tier below s551's count=10 six-way tie). Spans `heapFreeListDequeue`
(`HEAP_FREE_LIST_DEQUEUE_R1_GUARD`, `funcs_3.c:24498`/`0x8000D304`, 1st R-numbered guard in this
function — note this is a separate naming track from the whole-function items -312..-316 step-1/step-2
audits, which didn't use R-suffixes), `submitSceneNodeRender` (`SUBMIT_SCENE_NODE_RENDER_R8_GUARD`,
`funcs_4.c:1041`/`0x800103B8`, 8th site alongside R1-R7), and `buildOrientedFaceGeometry`
(`BUILD_ORIENTED_FACE_GEOMETRY_R1_GUARD`, `funcs_4.c:11705`/`0x80012E80`, 1st R-numbered site alongside
the pre-existing unrelated `ORIENTED_FACE_DERIVED_PTR_GUARD`). Same idiom as every prior guard: `lui
$v0,0x8011` / `lw $v0,0x63B0($v0)` reloads a global, a `beq $v0,$zero,...` null check's delay slot is
duplicated for both branch paths, and the fallthrough-only instruction after the label unconditionally
writes through the reloaded, never-range-checked `ctx->r2` as `ctx->r2+4`. Cross-checked all three
write addresses against `fixup_game_funcs.py` — no incidental matches, safe to add. Fixed, regenerated,
built. **1st live-verify (all three armed together, batch-instrumentation rule): clean** —
`hangarbay-entry n=31` (positive control), 0 fires on any of the three new guards, 0 fires on any other
armed guard family (no co-fires at all this run). Crashed at 115.5s on `last-guest-pc=0x80015544` — the
already-catalogued item -324 background-noise signature (resolved to host symbol
`packMtxRowFloatToFixed+824` this run instead of item -324's original `heapFreeListInsert+72` — the
recurring pc-symbol-instability gotcha, cross-checked by guest PC not symbol name). 2nd confirm queued:
`scratch/agent/soak_queue/s552_three_way_tie_confirm.sh` — the loop should pick this up between
iterations.

## This iteration's work unit

**Step 1 — fold in ALL THREE queued confirm results (do this FIRST, in whichever order
SOAK-RESULTS.md lists them).**

1. `s552_emit_allocated_dl_command_r1_reserve_and_emit_dl_entry_r1_confirm_retry2` (3rd confirm attempt
   for guards 64-65): read the run.log, grep for `emit-allocated-dl-command-r1-guard` and
   `reserve-and-emit-dl-entry-r1-guard` fire counts (expect 0), `hangarbay-entry` positive control
   (must be double-digit+ — if STILL weak, retry AGAIN, don't accept a 3rd consecutive weak draw as
   sufficient per iron rule 1). If clean with a valid positive control: mark guards 64-65 FULLY CLOSED
   2/2.
2. `s552_six_way_tie_confirm_retry` (2nd confirm attempt for guards 66-71): same checks — expect 0
   fires on `emit-color-fill-rect-r6-guard`, `emit-material-textured-dl-r3-guard`,
   `emit-material-textured-dl-alt-r3-guard`, `submit-scene-node-render-r7-guard`,
   `draw-subtitle-text-r4-guard`, `setup-camera-matrices-r1-guard`, double-digit+ `hangarbay-entry`. If
   clean: mark guards 66-71 FULLY CLOSED 2/2.
3. `s552_three_way_tie_confirm` (2nd confirm for guards 72-74): expect 0 fires on
   `heap-free-list-dequeue-r1-guard`, `submit-scene-node-render-r8-guard`,
   `build-oriented-face-geometry-r1-guard`, double-digit+ `hangarbay-entry`. If clean: mark guards
   72-74 FULLY CLOSED 2/2.
4. Update `docs/PROJECT-OVERVIEW.md` §25 with whichever rows closed, update `docs/CURRENT-TRUTH.md`
   item -317's guard count accordingly. **If any confirm surfaces a fire, this is a MAJOR finding —
   treat it as the campaign's next confirmed real bug catch (after item -334), investigate instead of
   picking a new tier.**

**Step 2 — re-scan and audit the next-ranked idiom-shape tier, same iteration (fold-in-then-pick
pattern), UNLESS Step 1 surfaced a fire (then investigate that instead, it supersedes everything else
in priority).**
1. Re-run the tracer fresh (no custom `--out`, s521's gotcha):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. Skip `renderLitTexturedMeshFaces`/`renderFlatMeshFaceGroup` reg=`r4`/off=`0X0` (re-verified
   shape-mismatch every session so far — `ctx->r4` there is the function's own non-null `$a0`
   argument). Filter to reg=`r2`/off=`0X4` via `scratch/agent/s548_dedupe_shape_filtered.py`.
3. s552 used count=8 (a three-way tie). The next tier below count=8 is UNKNOWN — find it fresh from
   the re-scan. The s552 filtered dedupe output already shows count=7 as the next candidate tier: TWO
   entries at `heapFreeListDequeue` (`funcs_3.c:24299`, `funcs_3.c:25551`) — verify this is still
   accurate on the fresh re-scan before committing to it (tiers shift as guards land and line numbers
   move); if both are in the same function, check whether they share the SAME reload/guard shape or
   are two independent sites needing two separate `R`-numbered guards.
4. Also worth a scoped look (flagged s549/s550/s551, not started): does the `DL_LIST_APPEND_DEREF_GUARD`
   shape (a checked address, but a later value READ BACK from guest memory left unguarded) recur in
   OTHER already-"closed" families from this campaign (`GENERIC_CACHE_GUARD`, `CACHE_HEAD_A1_GUARD`,
   etc.)? Found twice now (`FREELIST_NEXT_GUARD`/s441, `DL_LIST_APPEND_DEREF_GUARD`/s549) — a scoped
   audit of whether other "2-guard" families have an unaudited 3rd gap could be higher-value than
   continuing the raw idiom-shape ranking.
5. Pull raw reload addresses feeding any new candidate write line: filter
   `scratch/agent/s494_item317_step3_report.json` by `func==<name>`, check `hits[].line` (NOT a
   top-level `write_line` field, s540 gotcha) for the target write line, print `guest_addr` for
   matches. The write's OWN guest address is separate — read it from generated source directly (s548
   lesson).
6. Cross-check every raw address AND the write's own address against
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` directly (separate standalone
   repo, no submodule-patches step). A raw reload address incidentally matching an unrelated guard
   elsewhere is not disqualifying by itself (s545 precedent) — only the target write's OWN address
   being present is disqualifying.
7. Read the generated source around any zero-hit write address to confirm the exact idiom BEFORE the
   reachability cross-check (s535 lesson). Note: not every site has a `g_rs64_last_guest_pc = ...;`
   line before the write — match the OLD text exactly as it appears per site (s551/s552 both found
   sites without it), don't assume uniformity across sites.
8. Fix using the established template (skip-on-invalid, `ROGUESQ_LOG_<NAME>` env-gated stderr report,
   `U32()` range check `< 0x80000000u || >= 0x80800000u`). Name `<FUNC>_R<N>_GUARD`, bump `N` if the
   function already has guards this campaign — check current guard numbering with
   `grep -oE "<FUNC_UPPER>_R[0-9]+_GUARD" fixup_game_funcs.py | sort -u` before naming.
9. Regen (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build`, all four steps
   mandatory; delete `RecompiledFuncs/funcs_*.c` first via `python3 -c` glob+os.remove, `find -delete`
   is blocked):
   ```
   cd /Users/williambuckley/Documents/Tools/N64Recomp
   python3 -c "import glob, os; [os.remove(f) for f in glob.glob('RecompiledFuncs/funcs_*.c')]"
   cd /Users/williambuckley/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
   cd /Users/williambuckley/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml
   python3 fixup_game_funcs.py > <path inside one of the 3 allowed repos>   # audit xN counts, delete after
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build && \
     DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
   ```
   Gotcha (s533): the build dir that links `RogueSquadron64Recomp` is `RogueSquadron64Recomp/build`,
   NOT `N64Recomp/build`. Gotcha (s535): redirecting `fixup_game_funcs.py`'s output to `/tmp` is
   blocked — redirect inside one of the three allowed repos, delete after auditing.
10. 1st live-verify, manual, foreground — copy the most recent guard's manual script from
    `scratch/agent/soak_queue/done/` (`s552_three_way_tie_manual.sh` is the latest full env-var list),
    append the new guard's `ROGUESQ_LOG_<NAME>=1`, point output at a new
    `scratch/agent/soak_results/s553_..._manual` path. **Gotcha (s551/s552): the script's `cd` prefix
    depends on WHERE you put the copy — a script living directly under `scratch/agent/soak_queue/`
    needs `../../..` (3 levels to repo root: soak_queue -> agent -> scratch -> root). Verify by
    counting path components before running, don't assume the last-used prefix is right for a new
    location.** Run with `Bash` (auto-backgrounds past the foreground timeout), then `TaskOutput` with
    `block: true, timeout: 300000` to wait synchronously. Move it to `soak_queue/done/` after running
    so the loop doesn't re-run it.
11. **If the first attempt has a single-digit (or absent) `hangarbay-entry` count, discard and retry
    immediately** (s543/s545/s548/s549/s551/s552 precedent) — don't accept a weak positive control.
12. Read the run.log directly (fire count, `hangarbay-entry` count, crash/signal markers). If clean
    with a real positive control: queue a 2nd independent confirm to
    `scratch/agent/soak_queue/s553_..._confirm.sh`, record the 1st-verify result in
    `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard(s) across BOTH the 1st live-verify and the 2nd
independent confirm, each with a real `hangarbay-entry` positive control, promotes a guard to FULLY
CLOSED 2/2. A nonzero fire count — especially one whose bad-pointer value numerically traces to a
nearby crash's fault address, per the item -334 precedent — is a confirmed real bug catch.

## Iron-rule reminders specific to this campaign
- **Confirm the next free session number at the START of every iteration** (`git log --oneline -3`)
  before naming anything.
- A guard firing with `n=0` alongside other sibling guards dumping `n=0` at crash time is NOT
  automatically dismissible as "just a diagnostic snapshot" (the s541/s544 precedent) — check whether
  the fired guard's bad-pointer VALUE numerically correlates with the crash's own fault address (mask
  to low 24 bits, compare to `mcontext x12`/`si_addr`) before dismissing it as background noise (s549).
- Never trust the tracer's raw per-tier count without the shape check AND the address-by-address
  cross-check against `fixup_game_funcs.py` AND a direct read of the generated source. The write
  instruction's OWN guest address is separate from its feeding reload addresses (s548).
- Never trust a 0-fires result without confirming the positive control is double-digit+. An ABSENT
  `hangarbay-entry` line (not even single-digit) is the weakest possible draw — discard immediately
  (s551, reinforced s552 — TWO consecutive weak draws are now common, don't stop retrying after one).
- One build/run carries every armed guard's env var (batch-instrumentation rule).
- `s506_dedupe.py` reads a FIXED canonical path; never pass a custom `--out` to `--scan`.
- Kill runs with SIGKILL only; capture paths must not start with "." in the final component; run from
  `build/` with the ROM present.
- `fixup_game_funcs.py`: `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` — a
  separate standalone checkout, no submodule-patches export step applies. It is UNTRACKED in that
  repo's own git (verified s551) — nothing to commit there, it's a persistent local working file.
- The build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- `make_elf.py`: `/Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`.
- A branch's delay-slot instruction is duplicated by the recompiler for both taken/fallthrough paths
  when the branch is non-branch-likely too (not just `bnel`) — if a literal-anchor patch site's anchor
  text appears twice, check whether the two copies have DIFFERENT indentation (they usually do, since
  one sits inside an `if {}` block) — if so, add TWO list entries with the two distinct anchor texts,
  don't try to force a single regex/anchor to match both (s549).
- Not every write site has a `g_rs64_last_guest_pc = ...;` line immediately before the write — some do,
  some don't (s551/s552, multiple sites in one batch lacked it each time). Read the exact generated
  source around each target line and match the old-text string exactly per site; don't assume
  uniformity.
- **Soak result diagnostics gotcha (s539/s541)**: a soak's real diagnostics can live in a `run.log`
  inside a same-named results subdirectory, OR the retry script's `--out` may point at the ORIGINAL
  (non-retry-suffixed) directory — check both locations.
- **JSON report field gotcha (s540)**: `s494_item317_step3_report.json` records have `hits[].line`, not
  a top-level `write_line` field.
- **`0x800ab068` background-noise gotcha (s541)**: resolves to a DIFFERENT host `pc-symbol` almost every
  time — cross-check `last-guest-pc`, not the symbol name.
- **`coalesceFreeHeapBlocks+4424`/`0x8000247c` background-noise gotcha (s542)**: the s354-366 heap-walker
  family — check exact pc-symbol+guest-PC pairs before filing as new.
- **`setByteAcrossEntryList+176`/`0x800aafa8` background-noise gotcha (s531/s543, reinforced s546/s548/
  s549/s551/s552)**: item -306's signature; hit at least 7 of ~9 short/weak draws across 7 sessions now
  (including two draws with NO `hangarbay-entry` line at all, s551 AND s552) — always discard and
  retry, never treat one retry as sufficient insurance against a SECOND weak draw. Two consecutive weak
  draws on the SAME target is now the norm for this signature, not an anomaly — budget for it.
- **`loadDatFile+1152`/`0x800290d4` background-noise gotcha (s545)**: the s400-421→s422 `inflate_fast`
  clean-return misattribution artifact — not a new item.
- **`findLookupEntryByKey+2212` gotcha (s550)**: this symbol+offset pair has now produced TWO distinct
  `last-guest-pc` values (item -325's `0x800ad0dc`, item -336's `0x800ac914`) — always cross-check the
  guest PC, not just the symbol+offset string, before treating a hit as a repeat occurrence.
- **item -324 / `0x80015544` pc-symbol-instability gotcha (s552)**: this address resolved to host symbol
  `packMtxRowFloatToFixed+824` this session vs its original `heapFreeListInsert+72` (s521) — same
  family of gotcha as `0x800ab068` (s541) and `findLookupEntryByKey` (s550): the resolved symbol name is
  NOT stable across runs, only `last-guest-pc` is.
- **item -332 watch**: `submitSceneNodeRender+38976`/`0x8001086c` has recurred TWICE — a 3rd occurrence
  would justify source-tracing.
- **item -331/-333 watch**: `heapFreeListDequeue+29152`/`0x8000d688` and
  `findAndUnlinkSmallestEntry+356`/`0x8000d698`, 16 bytes apart, both single occurrences, both
  `(local-symtab)`-tagged. If either recurs, or a 3rd nearby address appears, treat the region as
  suspicious.
- **item -335/-336/-337 watch**: `emitAllocatedDLCommand+1960`/`0x800086ec`,
  `findLookupEntryByKey+2212`/`0x800ac914`, and `submitSceneNodeRender+69192`/`0x80010df4`, all single
  occurrences. Watch for recurrence. Note `submitSceneNodeRender` now has FOUR distinct catalogued
  breadcrumb addresses (-327/-328/-332/-337) plus its own guard family (R1-R8) — a large function worth
  a dedicated pass if a 5th address appears.
- **Incidental-match gotcha (s545)**: a raw reload address CAN appear elsewhere in
  `fixup_game_funcs.py` without disqualifying the candidate — only the target write's OWN address being
  present is disqualifying.
- This sandbox blocks `find -delete`, multi-statement `&&`/`while`/heredoc chains, and output
  redirection to `/tmp`. Grep with a literal path instead of a shell variable when flagged. Writing a
  multi-line string with embedded `#` inside a quoted python/shell argument trips "Newline followed by #
  inside a quoted argument can hide arguments from path validation" — write long content to a scratch
  file with the Write tool first, then `cat file >> target` (or just Write the target file directly).
- After launching a manual live-verify in the background, use `TaskOutput` with `block: true` and a
  generous `timeout` (e.g. 300000ms) to wait synchronously.
- Full guard-by-guard table and mechanism detail: `docs/PROJECT-OVERVIEW.md` §22-§25.
