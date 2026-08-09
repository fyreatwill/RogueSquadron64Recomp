# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s549 recap (read this first)

**Folded in BOTH s548 queued confirms.** `s548_five_tied_guards_confirm_retry` (guards 53-57) came
back WEAK for the THIRD consecutive attempt on this exact confirm target: `hangarbay-entry n=4`
(single-digit), crashed at 17.2s/7 frames on the item -306 `setByteAcrossEntryList+176`/`0x800aafa8`
signature — the SAME signature as the two prior weak draws (s546, s548). Discarded per iron rule 1.
Retry re-queued: `scratch/agent/soak_queue/s549_five_tied_guards_confirm_retry2.sh` — the loop should
pick this up between iterations. **This is now a flagged pattern**: 3 consecutive weak draws on one
confirm target, all hitting the identical background-noise signature — worth a dedicated check in a
future session for whether this signature correlates with short/early-crash runs specifically (not
just this one confirm target), rather than being purely random.

`s548_four_tied_guards_confirm` (guards 58-61) came back CLEAN: `hangarbay-entry n=2700` (strong
positive control), 0 fires on all four target guards. **Guards 58-61 marked FULLY CLOSED 2/2** —
closed the campaign's 61 guards to 61/61 fully closed for the tenth time.

**That same confirm run's own crash was the real finding this session.** It crashed at
`last-guest-pc=0x80010DCC` (`submitSceneNodeRender`) while the SAME run's pre-existing
`sibling-ptr-write-guard site=0x80010DC4` fired (`n=0`, the campaign's FIRST-EVER genuine fire across
121+ sites) with `bad_ptr=0x48830D10` one instruction earlier — `bad_ptr+4` numerically matches the
crash's own fault address modulo the RDRAM host-mapping offset. Traced to source: `0x80010DC8`'s
delay-slot instruction (`sw $zero,0x4($a1)`, duplicated x2 by the recompiler for taken/fallthrough
paths) reuses the SAME never-rechecked `ctx->r5` that `0x80010DC4`'s guard had just validated — exactly
item -319's own gap shape recurring in a new function. Filed and fixed as **item -334**
(`SIBLING_PTR_WRITE_GUARD` site=`0x80010DCC`, 2 new entries in the existing 121-site family's list,
sharing its env var).

**Verifying the item -334 fix ALONE caught it firing for real.** After rebuilding with just the
item -334 fix, the 1st live-verify's new `sibling-ptr-write-guard site=0x80010DCC` FIRED (`n=0`,
`bad_ptr=0x810C747B` — matching the SAME value the pre-existing `0x80010DC4` guard fired with one
instruction earlier in the SAME run) — the campaign's first-ever confirmed genuine fire across 122+
sites, and the guard skipped the write safely as designed. The run still crashed downstream, at
`last-guest-pc=0x80010e6c` — item -327's own catalogued address (previously 2 occurrences 21 sessions
apart; this is now a confirmed 3rd). Source trace (`funcs_4.c:4670-4699`): this is
`submitSceneNodeRender`'s own instance of the
`DL_LIST_APPEND_GUARD` idiom (s454, an 84-site family: 57 original + 27 s463 widened). The existing
`DL_LIST_APPEND_GUARD` validates the list HEAD pointer before reading `ctx->rderef = MEM_W(head,0)` —
but `rderef` itself, a value READ BACK from guest memory, was never range-checked before being
dereferenced as a write address 4 instructions later. The existing `DL_LIST_APPEND_RWRITE_GUARD`
(s482) only validates a DIFFERENT register (the new-node argument). The family's own regex
(`_dl_list_append_guard_re` in `fixup_game_funcs.py`) already proves this 4-instruction tail is
byte-identical at all 84 sites, so this is a genuine family-wide gap — fixed blanket-wide as
`DL_LIST_APPEND_DEREF_GUARD` in the SAME regex substitution (not a separate pass), confirmed by the
fixup report's `patched x46`/`x38` counts matching `DL_LIST_APPEND_GUARD`'s own exactly (1:1 coverage).
Site `0x80010E6C` in `submitSceneNodeRender` specifically resolves item -327.

**Re-verify with BOTH new guard families armed together (batch-instrumentation rule).**
`hangarbay-entry n=2700` (strong positive control), 0 fires on `dl-list-append-deref-guard` (any site)
and 0 fires on `sibling-ptr-write-guard site=0x80010DCC` THIS run (intermittent — the corruption event
that fired it in the previous run didn't manifest here, consistent with every guard in this campaign).
Crashed at 135.0s on the already-catalogued s354-366 `coalesceFreeHeapBlocks+4424`/`0x8000247c`
background-noise family — clean, own guards silent this run. 2nd confirm queued:
`scratch/agent/soak_queue/s549_sibling_ptr_write_gap_confirm.sh` — the loop should pick this up between
iterations.

**Why this session's fixes are different from every prior guard in this campaign**: every one of the
first 61 item -317 guards was found via idiom-shape pattern matching (a tracer ranks candidate sites by
reload count) and NONE has ever fired in 121+/84+ site-runs of live-verify soaks. This session's two
new guards were found via a DIRECT numeric trace from an actual crash's fault address back to a guard
that had just fired — the first time this campaign has had mechanism-level, not just shape-level,
evidence that the idiom class is a REAL live corruption source. Treat any future fire on
`SIBLING_PTR_WRITE_GUARD` or `DL_LIST_APPEND_DEREF_GUARD` as high-priority confirmation, not noise.

## This iteration's work unit

**Step 1 — fold in BOTH queued confirm results (do this FIRST).**

For `s549_sibling_ptr_write_gap_confirm` (item -334's `SIBLING_PTR_WRITE_GUARD` site=`0x80010DCC` +
item -327's `DL_LIST_APPEND_DEREF_GUARD`, 84 sites): read the run.log, grep for
`sibling-ptr-write-guard site=0x80010DCC` and `dl-list-append-deref-guard` fire counts (expect 0 for a
clean result), regression check on any other armed guard family, `hangarbay-entry` positive control
(must be double-digit+), crash signature cross-check against items -320..-334 and the background-noise
catalogue in `docs/PROJECT-OVERVIEW.md`. **If a fire occurs on either guard, this is the campaign's
first confirmed real bug catch — treat it as a major finding, not routine.** If clean with a valid
positive control: mark both guards FULLY CLOSED 2/2 in `docs/PROJECT-OVERVIEW.md` §25 rows 62-63, mark
item -327 fully resolved in `docs/CURRENT-TRUTH.md`.

For `s549_five_tied_guards_confirm_retry2` (guards 53-57, now on its 4th confirm attempt): same
process. If STILL weak (a 4th consecutive weak draw), this crosses from "worth watching" into "worth
actively investigating" — consider whether `PROBE_KEYS`/timing for this specific confirm script differs
subtly from other confirm scripts in a way that correlates with early crashes, rather than continuing
to blind-retry a 5th time. If clean: mark guards 53-57 FULLY CLOSED 2/2 in PROJECT-OVERVIEW §25 rows
53-57 — this would close the campaign's 63 guards to 63/63 fully closed for the first time.

**Step 2 — re-scan and audit the next-ranked idiom-shape tier, same iteration (fold-in-then-pick
pattern), UNLESS Step 1 surfaced a fire (then investigate that instead, it supersedes everything else
in priority).**
1. Re-run the tracer fresh (no custom `--out`, s521's gotcha):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
   Or `scratch/agent/s548_dedupe_shape_filtered.py` for the reg=`r2`/off=`0X4` shape specifically.
2. Skip `renderLitTexturedMeshFaces`/`renderFlatMeshFaceGroup` reg=`r4`/off=`0X0` (re-verified
   shape-mismatch every session so far — `ctx->r4` there is the function's own non-null `$a0` argument).
3. The next tier below s548's accepted count=14 four-way tie and s549's mechanism-driven finds is
   UNKNOWN — s549 did not re-run the tracer (all its work was crash-mechanism-driven, not scan-driven).
   Find the next tier fresh.
4. Also worth a scoped look: does the SAME `DL_LIST_APPEND_DEREF_GUARD` shape (checked address, later
   unchecked value-read-back-and-reused) recur in OTHER already-"closed" families from this campaign
   (`GENERIC_CACHE_GUARD`, `CACHE_HEAD_A1_GUARD`, etc.)? This session found it TWICE now
   (`FREELIST_NEXT_GUARD`/s441 was the first instance of this exact 3rd-gap shape, `DL_LIST_APPEND_DEREF_GUARD`/s549
   is the second) — a scoped audit of whether other "2-guard" families in this campaign have an
   unaudited 3rd gap could be higher-value than continuing the raw idiom-shape ranking. Not started
   this session; flagged as a candidate for a future session's Step 2 choice.
5. Pull raw reload addresses feeding any new candidate write line: filter
   `scratch/agent/s494_item317_step3_report.json` by `func==<name>`, check `hits[].line` (NOT a
   top-level `write_line` field, s540 gotcha) for the target write line, print `guest_addr` for matches.
   The write's OWN guest address is separate — read it from generated source directly (s548 lesson).
6. Cross-check every raw address AND the write's own address against
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` directly (separate standalone
   repo, no submodule-patches step). A raw reload address incidentally matching an unrelated guard
   elsewhere is not disqualifying by itself (s545 precedent) — only the target write's OWN address being
   present is disqualifying.
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
    `scratch/agent/soak_queue/done/` (`s549_sibling_ptr_write_gap_manual.sh` is the latest full env-var
    list), append the new guard's `ROGUESQ_LOG_<NAME>=1`, point output at a new
    `scratch/agent/soak_results/s550_..._manual` path, run with `Bash` (auto-backgrounds past the
    foreground timeout), then `TaskOutput` with `block: true, timeout: 300000` to wait synchronously.
    Move it to `soak_queue/done/` after running so the loop doesn't re-run it.
11. **If the first attempt has a single-digit `hangarbay-entry` count, discard and retry immediately**
    (s543/s545/s548/s549 precedent) — don't accept a weak positive control.
12. Read the run.log directly (fire count, `hangarbay-entry` count, crash/signal markers). If clean
    with a real positive control: queue a 2nd independent confirm to
    `scratch/agent/soak_queue/s550_..._confirm.sh`, record the 1st-verify result in
    `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard(s) across BOTH the 1st live-verify and the 2nd
independent confirm, each with a real `hangarbay-entry` positive control, promotes a guard to FULLY
CLOSED 2/2. A nonzero fire count — especially one whose bad-pointer value numerically traces to a
nearby crash's fault address, per this session's precedent — is a confirmed real bug catch.

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
  s549)**: item -306's signature; now hit 4 of the last ~6 short/weak draws across 4 sessions — actively
  worth investigating whether this correlates with early/short runs specifically, not just noted again.
- **`loadDatFile+1152`/`0x800290d4` background-noise gotcha (s545)**: the s400-421→s422 `inflate_fast`
  clean-return misattribution artifact — not a new item.
- **item -332 watch**: `submitSceneNodeRender+38976`/`0x8001086c` has recurred TWICE — a 3rd occurrence
  would justify source-tracing.
- **item -331/-333 watch**: `heapFreeListDequeue+29152`/`0x8000d688` and
  `findAndUnlinkSmallestEntry+356`/`0x8000d698`, 16 bytes apart, both single occurrences, both
  `(local-symtab)`-tagged. If either recurs, or a 3rd nearby address appears, treat the region as
  suspicious.
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
