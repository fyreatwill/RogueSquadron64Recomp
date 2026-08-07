# NEXT work unit

HYPOTHESIS-ID: dl-list-reset-5824-intervening-14

## s463 CLOSED item -298's own 70/70 clean sites (`DL_LIST_RESET_GUARD`) and extended item -291
(`DL_LIST_APPEND_GUARD`) from 57 to 84/84 sites — see `docs/CURRENT-TRUTH.md` item -298 and
`PORTING-STATE.md` Session 463 for the full derivation. Confirmation soak queued:
`scratch/agent/soak_queue/s463_dllistguards_confirm.sh`.

**Open thread: item -298's own remaining 14 sites.** These are the SAME `DL_LIST_RESET_GUARD` shape
(reload global `0x8011A7DC`, then write the reloaded pointer directly as a write address with no
intervening deref) but with 1-6 lines of unrelated intervening code between the reload and the write
pair — the blanket regex used for the other 70 sites can't span that gap, so each site needs its own
per-site literal anchor, the exact same mechanical process `SIBLING_PTR_WRITE_GUARD`/item -296 used
for its own 14/119 non-uniform sites.

## This iteration's work unit (default, unless Step 0/a fresher soak result changes the picture)

1. Re-run `python3 scratch_s463_classify_5824.py` in `~/Documents/Tools/N64Recomp` (untracked,
   still on disk from s463) to regenerate the `C_UNCLASSIFIED` bucket — 14 sites, each printed with
   its address and the next ~8 lines of surrounding code. (If the script is gone, re-derive it: the
   pattern is `reload_re` from `scratch_s463_scan_5824.py` chained into a manual read of what follows
   each of the 111 original non-canonical addresses not already claimed by `DL_LIST_APPEND_GUARD`'s
   84 or `DL_LIST_RESET_GUARD`'s 70.)
2. For each of the 14, read enough context to confirm: (a) it really is the list-reset shape (reload
   → intervening unrelated code → `sw` writing some register through the SAME reloaded register used
   as the address), and (b) capture the literal anchor text (the `// 0xADDR: sw ...` comment line plus
   the `MEM_W(...) = ...;` line, verbatim, like `SIBLING_PTR_WRITE_GUARD`'s own `_SIBLING_PTR_WRITE_SITES`
   list in `fixup_game_funcs.py`) — confirm each anchor is tree-wide-unique via
   `grep -c "<anchor text>" RecompiledFuncs/*.c` before touching the patch list (this idiom class's
   own established discipline, never skip the uniqueness check).
3. Add a `_DL_LIST_RESET_SITES` list (same structure as `_SIBLING_PTR_WRITE_SITES`) to
   `fixup_game_funcs.py`, patch generation reusing the SAME "skip on invalid head" remediation and
   the SAME `ROGUESQ_LOG_DL_LIST_RESET_GUARD`/`[dl-list-reset-guard]` tag already wired up for the
   70-site blanket-regex batch (just route these 14 through per-site substitution instead).
4. Full pipeline (`make_elf.py` → delete stale `funcs_*.c` → `N64Recomp` → `fixup_game_funcs.py` →
   `cmake --build`), confirm the report shows all 14 applied (check the total
   `DL_LIST_RESET_GUARD`-tagged site count in the built binary is now 84, not 70), live-verify (full
   300s schedule, all passive guards armed including `ROGUESQ_LOG_DL_LIST_RESET_GUARD`), queue a
   confirm soak. This CLOSES item -298 outright (0 sites remaining across the whole re-scoped -0x5824
   non-canonical population) if it comes back clean.

## Fallback if step 1 finds the class isn't as clean as expected

If any of the 14 sites turn out NOT to share the list-reset shape (read step 2 finds a genuinely
different pattern), stop and reclassify rather than forcing a fit — same discipline as every prior
idiom-class audit. In that case, fall back to `BREADCRUMB7` (diagnostic, lowest priority, the last
untouched item from the `static5-rename-orphan-sweep`) or a fresh frequency scan per
`docs/PROJECT-OVERVIEW.md` §14's method (closed for lack of a hit at the time, not necessarily
exhausted now that 3 more idiom classes have been found since).

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

10 of item -296's 119 `SIBLING_PTR_WRITE_GUARD` sites are in `submitSceneNodeRender`, the same
function named in a still-open "wait-for-recurrence breadcrumb" (2 independent single-occurrence
crashes, different `last-guest-pc` each time, not confirmed as one bug). 0 fires across every soak
so far, including s463's. If any future soak shows a `sibling-ptr-write-guard` fire specifically at
one of those 10 sites, that's new evidence worth immediate follow-up — the one exception to "don't
chase breadcrumbs."

## Incidental observation, not chased (s463, via the queued s462 confirm soak)

The `s462_stepactivesongtracks_confirm` soak (run between s462 and s463) crashed at 109.1s on
`pc-symbol=memcpy_recomp+288`, `last-guest-pc=0x80054780`, inside `tickWrappingTimerAccumulatorList`
(`funcs_11.c`) — a function with its own long, already-catalogued crash history (`BREADCRUMB9`, the
s343 div-by-zero, the s426-441 epilogue-misattribution saga). No `funcs_25.c` frame anywhere —
unrelated to item -292's own patch (which stays CLOSED). Do not chase; file only.
