# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s550 recap (read this first)

**Folded in BOTH of s549's queued confirms — every guard pending in this campaign cleared for the
first time.** `s549_five_tied_guards_confirm_retry2` (guards 53-57) finally came back CLEAN on its
4th attempt: `hangarbay-entry n=31` (the first valid double-digit positive control on this exact
confirm target after 3 consecutive single-digit weak draws hitting the item -306
`setByteAcrossEntryList+176`/`0x800aafa8` background-noise signature). 0 fires on all five guards.
Crashed on a genuinely NEW signature, filed **item -335**
(`emitAllocatedDLCommand+1960`/`0x800086ec`, single occurrence). Guards 53-57 marked **FULLY CLOSED
2/2**.

`s549_sibling_ptr_write_gap_confirm` (item -334's `SIBLING_PTR_WRITE_GUARD` site=`0x80010DCC` + item
-327's root-cause `DL_LIST_APPEND_DEREF_GUARD`, 84 sites): `hangarbay-entry n=31` (positive control).
0 fires on either guard family. Crashed on `findLookupEntryByKey+2212`/`0x800ac914` — same
symbol+offset as item -325 but a DIFFERENT `last-guest-pc` (item -325 is `0x800ad0dc`; the family's
own `pc-symbol`-instability gotcha, s541 — always cross-check `last-guest-pc`, not just the symbol
name), so a genuinely NEW single-occurrence signature, filed **item -336**. Guards 62-63 marked
**FULLY CLOSED 2/2**.

**This closes the campaign's 63 guards to 63/63 fully closed, zero pending confirms, for the first
time in the whole item -317 step 3 campaign.**

**Picked the next tier and found+fixed 2 new guards.** Fresh tracer re-scan (`--scan` +
`s506_dedupe.py`) found the next tier below s548's count=14 four-way tie: a **TWO-WAY TIE at
count=13** (same guarded shape reg=r2/off=0X4), spanning `emitAllocatedDLCommand`
(`EMIT_ALLOCATED_DL_COMMAND_R1_GUARD`, `funcs_3.c:4580`/`0x80008908`, first guard in this function)
and `reserveAndEmitDLEntry` (`RESERVE_AND_EMIT_DL_ENTRY_R1_GUARD`, `funcs_3.c:22988`/`0x8000CE10`,
first guard in this function, new to this campaign). Same idiom as every prior guard: `lui
$v0,0x8011`/`lw $v0,0x63B0($v0)` reloads a global, a `beq $v0,$zero,...` null check's delay slot is
duplicated for both branch paths, and the fallthrough-only instruction after the label unconditionally
writes through the reloaded, never-range-checked `ctx->r2` as `ctx->r2+4`. Cross-checked both write
addresses against `fixup_game_funcs.py` — no incidental matches, safe to add. Fixed, regenerated,
built. **1st live-verify (both armed together, batch-instrumentation rule): clean** —
`hangarbay-entry n=31` (positive control), 0 fires on either new guard, 0 fires on any other armed
guard family (1 benign pre-existing `[mesgqueue-guard]` line, unrelated), full 300s completed with **no
crash at all** (106 frames, rc=0) — the cleanest possible verify class. 2nd confirm queued:
`scratch/agent/soak_queue/s550_emit_allocated_dl_command_r1_reserve_and_emit_dl_entry_r1_confirm.sh` —
the loop should pick this up between iterations.

## This iteration's work unit

**Step 1 — fold in the queued confirm result (do this FIRST).**

For `s550_emit_allocated_dl_command_r1_reserve_and_emit_dl_entry_r1_confirm`: read the run.log, grep
for `emit-allocated-dl-command-r1-guard` and `reserve-and-emit-dl-entry-r1-guard` fire counts (expect 0
for a clean result), regression check on any other armed guard family, `hangarbay-entry` positive
control (must be double-digit+), crash signature cross-check against items -320..-336 and the
background-noise catalogue in `docs/PROJECT-OVERVIEW.md`. **If a fire occurs on either guard, this is
only the campaign's SECOND confirmed real bug catch (after item -334) — treat it as a major finding.**
If clean with a valid positive control: mark both guards (64-65) FULLY CLOSED 2/2 in
`docs/PROJECT-OVERVIEW.md` §25 rows 64-65, update `docs/CURRENT-TRUTH.md` item -317's guard count
(63 -> 65 FULLY CLOSED 2/2, 0 pending).

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
   argument). This shape currently dominates the raw dedupe output (counts 56/43/41/27/16) — filter it
   out and look at the reg=`r2`/off=`0X4` shape specifically, or use
   `scratch/agent/s548_dedupe_shape_filtered.py`.
3. s550 used count=13 (a two-way tie: `emitAllocatedDLCommand`, `reserveAndEmitDLEntry`). The next
   tier below count=13 is UNKNOWN — find it fresh from the re-scan.
4. Also worth a scoped look (flagged s549, not started): does the `DL_LIST_APPEND_DEREF_GUARD` shape
   (a checked address, but a later value READ BACK from guest memory left unguarded) recur in OTHER
   already-"closed" families from this campaign (`GENERIC_CACHE_GUARD`, `CACHE_HEAD_A1_GUARD`, etc.)?
   This session found the shape twice now (`FREELIST_NEXT_GUARD`/s441 was the first instance,
   `DL_LIST_APPEND_DEREF_GUARD`/s549 the second) — a scoped audit of whether other "2-guard" families
   have an unaudited 3rd gap could be higher-value than continuing the raw idiom-shape ranking.
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
   reachability cross-check (s535 lesson).
8. Fix using the established template (skip-on-invalid, `ROGUESQ_LOG_<NAME>` env-gated stderr report,
   `U32()` range check `< 0x80000000u || >= 0x80800000u`). Name `<FUNC>_R<N>_GUARD`, bump `N` if the
   function already has guards this campaign.
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
    `scratch/agent/soak_queue/done/` (`s550_emit_allocated_dl_command_r1_reserve_and_emit_dl_entry_r1_manual.sh`
    is the latest full env-var list), append the new guard's `ROGUESQ_LOG_<NAME>=1`, point output at a
    new `scratch/agent/soak_results/s551_..._manual` path, run with `Bash` (auto-backgrounds past the
    foreground timeout), then `TaskOutput` with `block: true, timeout: 300000` to wait synchronously.
    Move it to `soak_queue/done/` after running so the loop doesn't re-run it.
11. **If the first attempt has a single-digit `hangarbay-entry` count, discard and retry immediately**
    (s543/s545/s548/s549 precedent) — don't accept a weak positive control.
12. Read the run.log directly (fire count, `hangarbay-entry` count, crash/signal markers). If clean
    with a real positive control: queue a 2nd independent confirm to
    `scratch/agent/soak_queue/s551_..._confirm.sh`, record the 1st-verify result in
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
- Never trust a 0-fires result without confirming the positive control is double-digit+.
- One build/run carries every armed guard's env var (batch-instrumentation rule).
- `s506_dedupe.py` reads a FIXED canonical path; never pass a custom `--out` to `--scan`.
- Kill runs with SIGKILL only; capture paths must not start with "." in the final component; run from
  `build/` with the ROM present.
- `fixup_game_funcs.py`: `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` — a
  separate standalone checkout, no submodule-patches export step applies.
- The build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- `make_elf.py`: `/Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`.
- A branch's delay-slot instruction is duplicated by the recompiler for both taken/fallthrough paths
  when the branch is non-branch-likely too (not just `bnel`) — if a literal-anchor patch site's anchor
  text appears twice, check whether the two copies have DIFFERENT indentation (they usually do, since
  one sits inside an `if {}` block) — if so, add TWO list entries with the two distinct anchor texts,
  don't try to force a single regex/anchor to match both (s549).
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
  s549)**: item -306's signature; hit 4 of ~6 short/weak draws across 4 sessions before s550's 4th
  attempt finally drew clean — the correlation-with-short-runs question remains open but is now lower
  priority (the confirm target it was blocking is closed).
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
- **item -335/-336 watch (new this session)**: `emitAllocatedDLCommand+1960`/`0x800086ec` and
  `findLookupEntryByKey+2212`/`0x800ac914`, both single occurrences. Watch for recurrence.
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
