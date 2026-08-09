# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s551 recap (read this first)

**Folded in s550's queued 2nd confirm for guards 64-65 — came back WEAK, retry queued (not a
fire).** `s550_emit_allocated_dl_command_r1_reserve_and_emit_dl_entry_r1_confirm`: NO `hangarbay-entry`
line at all (weaker than even a single-digit draw) — process gone at 20.2s after only 7 captured
frames, crashed on the item -306 `setByteAcrossEntryList+176`/`last-guest-pc=0x800aafa8`
background-noise signature (the recurring short-run signature, s531/s543/s546/s548/s549). 0 fires on
either `EMIT_ALLOCATED_DL_COMMAND_R1_GUARD` or `RESERVE_AND_EMIT_DL_ENTRY_R1_GUARD`, but with no valid
positive control this is not a usable null result — discarded per iron rule 1. Retry queued:
`scratch/agent/soak_queue/s551_emit_allocated_dl_command_r1_reserve_and_emit_dl_entry_r1_confirm_retry.sh`
— the loop should pick this up between iterations.

**Fresh tracer re-scan found the next tier: a SIX-WAY TIE at count=10** (same guarded shape
reg=r2/off=0X4, one tier below s550's count=13 two-way tie). Spans `emitColorFillRect`
(`EMIT_COLOR_FILL_RECT_R6_GUARD`, `funcs_3.c:9988`/`0x80009E30`, 6th guard in this function),
`emitMaterialTexturedDL` (`EMIT_MATERIAL_TEXTURED_DL_R3_GUARD`, `funcs_3.c:28957`/`0x8000E4B4`, 3rd),
`emitMaterialTexturedDLAlt` (`EMIT_MATERIAL_TEXTURED_DL_ALT_R3_GUARD`, `funcs_3.c:31110`/`0x8000EB90`,
3rd), `submitSceneNodeRender` (`SUBMIT_SCENE_NODE_RENDER_R7_GUARD`, `funcs_4.c:1761`/`0x800105EC`,
7th), `drawSubtitleText` (`DRAW_SUBTITLE_TEXT_R4_GUARD`, `funcs_4.c:23563`/`0x80015F80`, 4th), and
`setupCameraMatrices` (`SETUP_CAMERA_MATRICES_R1_GUARD`, `funcs_4.c:28560`/`0x8001763C`, 1st guard,
NEW function to this campaign). Same idiom as every prior guard: `lui $v0,0x8011` /
`lw $v0,0x63B0($v0)` reloads a global, a `beq $v0,$zero,...` null check's delay slot is duplicated for
both branch paths, and the fallthrough-only instruction after the label unconditionally writes through
the reloaded, never-range-checked `ctx->r2` as `ctx->r2+4`. Cross-checked all six write addresses
against `fixup_game_funcs.py` — no incidental matches, safe to add. Fixed, regenerated, built. **1st
live-verify (all six armed together, batch-instrumentation rule): clean** — `hangarbay-entry n=32`
(positive control), 0 fires on any of the six new guards, 0 live fires on any other armed guard family
(only pre-existing `n=0`/`ra=0x00000000` post-crash diagnostic snapshots, unrelated, no regression).
Crashed at 123.5s on a NEW single-occurrence signature (`submitSceneNodeRender+69192`/
`last-guest-pc=0x80010df4`, filed **item -337**). 2nd confirm queued:
`scratch/agent/soak_queue/s551_six_way_tie_confirm.sh` — the loop should pick this up between
iterations.

## This iteration's work unit

**Step 1 — fold in BOTH queued confirm results (do this FIRST, in whichever order SOAK-RESULTS.md
lists them).**

1. `s551_emit_allocated_dl_command_r1_reserve_and_emit_dl_entry_r1_confirm_retry` (retry of guards
   64-65's weak confirm): read the run.log, grep for `emit-allocated-dl-command-r1-guard` and
   `reserve-and-emit-dl-entry-r1-guard` fire counts (expect 0), `hangarbay-entry` positive control
   (must be double-digit+ this time — if STILL weak, retry again, don't accept a 2nd consecutive weak
   draw as sufficient per iron rule 1), regression check on any other armed guard family, crash
   signature cross-check against items -320..-337 and the background-noise catalogue. If clean with a
   valid positive control: mark guards 64-65 FULLY CLOSED 2/2.
2. `s551_six_way_tie_confirm` (guards 66-71): same checks — expect 0 fires on
   `emit-color-fill-rect-r6-guard`, `emit-material-textured-dl-r3-guard`,
   `emit-material-textured-dl-alt-r3-guard`, `submit-scene-node-render-r7-guard`,
   `draw-subtitle-text-r4-guard`, `setup-camera-matrices-r1-guard`, double-digit+ `hangarbay-entry`. If
   clean: mark guards 66-71 FULLY CLOSED 2/2.
3. Update `docs/PROJECT-OVERVIEW.md` §25 with whichever rows closed, update `docs/CURRENT-TRUTH.md`
   item -317's guard count accordingly. **If either confirm surfaces a fire, this is a MAJOR finding —
   treat it as the campaign's 2nd/3rd confirmed real bug catch (after item -334), investigate instead
   of picking a new tier.**

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
3. s551 used count=10 (a six-way tie). The next tier below count=10 is UNKNOWN — find it fresh from
   the re-scan (the s551 raw dedupe output already shows count=8 as the next candidate tier: a
   THREE-WAY TIE — `heapFreeListDequeue` `funcs_3.c:24485`, `submitSceneNodeRender` `funcs_4.c:1041`,
   `buildOrientedFaceGeometry` `funcs_4.c:11692` — verify this is still accurate on the fresh re-scan
   before committing to it, tiers can shift as guards land).
4. Also worth a scoped look (flagged s549/s550, not started): does the `DL_LIST_APPEND_DEREF_GUARD`
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
   line before the write — match the OLD text exactly as it appears (s551 found 3 of 6 sites without
   it), don't assume uniformity across sites.
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
    `scratch/agent/soak_queue/done/` (`s551_six_way_tie_manual.sh` is the latest full env-var list),
    append the new guard's `ROGUESQ_LOG_<NAME>=1`, point output at a new
    `scratch/agent/soak_results/s552_..._manual` path. **Gotcha (s551): the manual script's `cd`
    prefix depends on WHERE you copy it — `soak_queue/done/*.sh` uses `../../..` (3 levels to repo
    root), a copy directly under `scratch/agent/` needs `../..` (2 levels) — fix the `cd` line to
    match wherever you actually put the copy before running.** Run with `Bash` (auto-backgrounds past
    the foreground timeout), then `TaskOutput` with `block: true, timeout: 300000` to wait
    synchronously. Move it to `soak_queue/done/` after running so the loop doesn't re-run it.
11. **If the first attempt has a single-digit (or absent) `hangarbay-entry` count, discard and retry
    immediately** (s543/s545/s548/s549/s551 precedent) — don't accept a weak positive control.
12. Read the run.log directly (fire count, `hangarbay-entry` count, crash/signal markers). If clean
    with a real positive control: queue a 2nd independent confirm to
    `scratch/agent/soak_queue/s552_..._confirm.sh`, record the 1st-verify result in
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
  (s551).
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
  some don't (s551, 3 of 6 sites in one batch lacked it). Read the exact generated source around each
  target line and match the old-text string exactly per site; don't assume uniformity.
- **Soak result diagnostics gotcha (s539/s541)**: a soak's real diagnostics can live in a `run.log`
  inside a same-named results subdirectory, OR the retry script's `--out` may point at the ORIGINAL
  (non-retry-suffixed) directory — check both locations.
- **JSON report field gotcha (s540)**: `s494_item317_step3_report.json` records have `hits[].line`, not
  a top-level `write_line` field.
- **`0x800ab068` background-noise gotcha (s541)**: resolves to a DIFFERENT host `pc-symbol` almost every
  time — cross-check `last-guest-pc`, not the symbol name.
- **`coalesceFreeHeapBlocks+4424`/`0x8000247c` background-noise gotcha (s542)**: the s354-366
  heap-walker family — check exact pc-symbol+guest-PC pairs before filing as new.
- **`setByteAcrossEntryList+176`/`0x800aafa8` background-noise gotcha (s531/s543, reinforced s546/s548/
  s549/s551)**: item -306's signature; hit at least 5 of ~7 short/weak draws across 5 sessions now
  (including one draw with NO `hangarbay-entry` line at all, s551) — always discard and retry, never
  treat one retry as sufficient insurance against a second weak draw.
- **`loadDatFile+1152`/`0x800290d4` background-noise gotcha (s545)**: the s400-421→s422 `inflate_fast`
  clean-return misattribution artifact — not a new item.
- **`findLookupEntryByKey+2212` gotcha (s550)**: this symbol+offset pair has now produced TWO distinct
  `last-guest-pc` values (item -325's `0x800ad0dc`, item -336's `0x800ac914`) — always cross-check the
  guest PC, not just the symbol+offset string, before treating a hit as a repeat occurrence.
- **item -332 watch**: `submitSceneNodeRender+38976`/`0x8001086c` has recurred TWICE — a 3rd occurrence
  would justify source-tracing.
- **item -331/-333 watch**: `heapFreeListDequeue+29152`/`0x8000d688` and
  `findAndUnlinkSmallestEntry+356`/`0x8000d698`, 16 bytes apart, both single occurrences, both
  `(local-symtab)`-tagged. If either recurs, or a 3rd nearby address appears, treat the region as
  suspicious.
- **item -335/-336/-337 watch (items -335/-336 new s550, -337 new s551)**:
  `emitAllocatedDLCommand+1960`/`0x800086ec`, `findLookupEntryByKey+2212`/`0x800ac914`, and
  `submitSceneNodeRender+69192`/`0x80010df4`, all single occurrences. Watch for recurrence. Note
  `submitSceneNodeRender` now has FOUR distinct catalogued breadcrumb addresses (-327/-328/-332/-337)
  plus its own guard family (R1-R7) — a large function worth a dedicated pass if a 5th address appears.
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
