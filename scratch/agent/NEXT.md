# NEXT work unit

HYPOTHESIS-ID: item-312-confirm-then-m3-m5-pivot

## s481 summary: closed the loadCutsceneAssetsByIndex+1860 breadcrumb (misattribution, item -310
class), root-caused and FIXED a real new bug instead (item -312, DONE pending 2nd confirm)

Per NEXT.md's own fallback order, reproduced the `loadCutsceneAssetsByIndex+1860` breadcrumb (2 prior
hits, s463/s468) with the current (post-s480 local-symtab fix) build. The trustworthy
`(local-symtab)`-tagged crash named `submitSceneNodeRender+63868`, NOT `loadCutsceneAssetsByIndex` —
confirms both prior hits were `dladdr` nearest-exported-symbol misattributions, same blind-spot class
as item -310. **Do not re-file this signature under `loadCutsceneAssetsByIndex` again.**

That reproduction handed back a genuinely new, well-evidenced bug instead of a null result:
`submitSceneNodeRender` (funcs_4.c, guest site 0x80010E74) writes its own `$a0` argument into the
free-list-cache-head global, `GENERIC_CACHE_GUARD` sanitizes a REREAD copy of that global but not the
original argument register, and `DL_LIST_APPEND_GUARD`'s own `rwrite` slot then dereferences that
same unsanitized register as a write address — a violation of `DL_LIST_APPEND_GUARD`'s own documented
scope assumption, true at its other 56 sites but not this one. Fixed with a single site-anchored
guard in `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (`DL_LIST_APPEND_GUARD_RWRITE`,
`ROGUESQ_LOG_DL_LIST_APPEND_RWRITE_GUARD`). Full regen/build clean; all pre-existing guard counts in
this lineage unregressed. 1 manual confirmation soak ran clean (hit an unrelated, already-catalogued
crash family instead — bonus: local-symtab named it `loadDatFile+1152` directly, matching item -259's
`atos`-derived finding without needing `atos`). Full derivation: `PORTING-STATE.md` Session 481;
ledger entry: `docs/CURRENT-TRUTH.md` item -312.

## This session's top work unit: check the queued confirm soak, then decide item -312's status

1. Read `scratch/agent/SOAK-RESULTS.md` tail for `s481_rwrite_guard_confirm` (queued this session at
   `scratch/agent/soak_queue/s481_rwrite_guard_confirm.sh`). If it ran clean (0 crash at this exact
   site OR an unrelated already-catalogued crash family, matching this whole lineage's established
   true-negative baseline): mark item -312 fully CLOSED in `docs/CURRENT-TRUTH.md` (mirror the
   2-soak-confirm pattern items -301/-303/-304/-306 already use).
2. If it crashed AT THIS SAME SITE (`dl-list-append-rwrite-guard` fires but still faults, or a crash
   at `site=0x80010E74`/`submitSceneNodeRender` with 0 fires): the guard has a gap of its own — before
   writing more code, re-read the fresh crash log's exact register state and compare against s481's
   trace in `PORTING-STATE.md` Session 481 to find what differs.

## Fallback order if item -312 is clean (per USER DIRECTIVE, unchanged)

1. A new M5 lead (checked clean as recently as s478 — check again, it's been 3 sessions).
2. If M5 yields nothing: M3 systematic idiom-class audit resumption needs a genuinely new discovery
   method — both prior opcode-scan lineages (`lui`+`lw` s465-476, `lui`+`sw` s477) are spent, and
   there is no queued high-recurrence breadcrumb left untried after item -312. Consider: a scan for
   OTHER `DL_LIST_APPEND_GUARD`-style "guard covers rload, not rwrite" gaps across its other 56 sites
   (this session's fix was single-site because the aliasing was confirmed unique to
   `submitSceneNodeRender`, but that confirmation was a grep for the literal address, not a structural
   check of whether `rwrite` could alias an unguarded reload in any OTHER of the 56 — worth a
   dedicated audit if nothing better surfaces).
3. If neither yields a concrete, boundable unit: BLOCKED with a specific question, per s480's NEXT.md
   note — the same one still applies (M3's opcode-scan lineages, its breadcrumbs, and M5 are all
   closed/clean; ask the human what should replace them as the standing M3 discovery method).

## Soak queue status

`scratch/agent/soak_queue/s481_rwrite_guard_confirm.sh` queued this session (2nd independent
confirmation for item -312's fix, arms all passive breadcrumb/instrument env vars per the standing
rule). `scratch/agent/soak_queue/done/s481_cutscene_breadcrumb_verify.sh` and
`scratch/agent/soak_queue/done/s481_rwrite_guard_verify.sh` are this session's own manual (foreground)
diagnostic/positive-control runs, already consumed — no need to rerun either.
