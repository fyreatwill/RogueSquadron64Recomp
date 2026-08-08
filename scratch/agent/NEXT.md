# NEXT work unit

HYPOTHESIS-ID: item-313-blanket-rwrite-confirm-then-m5-m3-pivot

## s482 summary: item -312's confirm soak came back clean, but a structural re-audit of its own
"grep-verified unique" scope claim found the claim was WRONG — generalized the fix (item -313)

Read `scratch/agent/SOAK-RESULTS.md`: `s481_rwrite_guard_confirm` (queued s481) ran `rc=0`, 0
crash, `dl-list-append-rwrite-guard fires=0` — item -312's site-anchored fix confirmed clean, 2/2
soaks. Per NEXT.md's own fallback order, checked for a fresh M5 lead first (full re-read of
PROJECT-OVERVIEW §10-12 + every audio-adjacent mention in sessions 479-481: zero hits, s478's "no
new lead" verdict unchanged). Fell through to option 2 — NEXT.md's own flagged follow-up: item
-312's "the site literal 0x80010E68/0x80010E74 is unique in the codebase (grep-verified)" claim
was a grep for one ADDRESS, not a structural check of whether the same aliasing SHAPE recurs
elsewhere. It does — up to 78 more of `DL_LIST_APPEND_GUARD`'s 84 sites share the exact "write arg
into the `0x63B0` free-list-cache-head as new head, self-round-trip-reload the SAME register
straight back with nothing validating it, then reach the guard's own unguarded
write-through-rwrite" shape, confirmed via direct source read of a 2nd concrete instance
(`emitFrameRdpInitDl`, funcs_3.c, site=0x80008FD4 — byte-for-byte identical structure to the
already-fixed submitSceneNodeRender bug). Generalized the fix into the blanket `DL_LIST_APPEND_
GUARD` patch itself (`N64Recomp/fixup_game_funcs.py`): addr6's write now validates `rwrite` at
EVERY site, not just one. Deleted item -312's now-superseded site-specific patch. Full regen/build
clean; 5 sibling guard families (`GENERIC_CACHE_GUARD` 107, `DL_BUFFER_POOL_GUARD` 84,
`SIBLING_PTR_WRITE_GUARD` 120, `DL_LIST_RESET_GUARD` 84, `FREELIST_NEXT_GUARD` 105) all matched
their established ledger counts, 0 regression. 1 manual confirmation soak clean: 0 fires on
`dl-list-append-rwrite-guard` or any sibling guard, `hangarbay-entry n=31` positive control, crash
was an unrelated already-catalogued family (`initVec4TripletFromArgs+68`, near-`0x80000000` wild
pointer, BREADCRUMB6 family) — filed not chased. Full derivation: `PORTING-STATE.md` Session 482;
ledger: `docs/CURRENT-TRUTH.md` item -313 (item -312 marked SUPERSEDED, not simply closed).

## This session's top work unit: check the queued confirm soak, then decide item -313's status

1. Read `scratch/agent/SOAK-RESULTS.md` tail for `s482_blanket_rwrite_guard_confirm` (queued this
   session at `scratch/agent/soak_queue/s482_blanket_rwrite_guard_confirm.sh`). If it ran clean (0
   crash AT ANY of the 84 guarded sites, OR an unrelated already-catalogued crash family — matching
   this whole lineage's established true-negative baseline): mark item -313 fully CLOSED in
   `docs/CURRENT-TRUTH.md`, and note the whole `DL_LIST_APPEND_GUARD` lineage (items -291, -312,
   -313) as closed.
2. If it crashed WITH `dl-list-append-rwrite-guard` firing but STILL faulting (a guard-gap-inside-
   the-guard, unlikely given the remediation shape matches every other guard in this family), or at
   one of the 78 newly-covered sites specifically: re-read that site's exact register trace before
   writing more code — do not assume it's the same submitSceneNodeRender mechanism without checking.

## Fallback order if item -313 is clean (per USER DIRECTIVE, unchanged from s478/s482's re-checks)

1. A fresh M5 lead check (checked clean s478, re-checked clean s482 — still nothing; if this
   session is 3+ sessions past s482, check again per the standing cadence, otherwise skip straight
   to option 2).
2. M3 systematic idiom-class audit resumption. Both opcode-scan lineages (`lui`+`lw` s465-476,
   `lui`+`sw` s477) are spent, and the `DL_LIST_APPEND_GUARD` structural-shape audit (this session's
   method) just closed cleanly too. Two untried angles worth considering: (a) apply the SAME
   "grep-verified unique, but is the SHAPE actually unique?" skepticism to any OTHER already-CLOSED
   guard that shipped a site-anchored (not blanket) patch on a uniqueness claim — grep
   `N64Recomp/fixup_game_funcs.py` for "site-anchored" / literal (not regex) patches and re-audit
   each one's uniqueness claim the same way this session did; (b) no untried high-recurrence
   breadcrumb remains queued after item -312/-313, so if (a) also comes up empty, this M3 discovery
   method may be exhausted too — escalate to BLOCKED with a specific question per s480's note.
3. If neither yields a concrete, boundable unit: BLOCKED — the same question s480/s481 already
   flagged still applies: M3's opcode-scan lineages, its breadcrumbs, its structural-shape audits,
   and M5 are all closed/clean; ask the human what should replace them as the standing M3 discovery
   method.

## Soak queue status

`scratch/agent/soak_queue/s482_blanket_rwrite_guard_confirm.sh` queued this session (2nd
independent confirmation for item -313's blanket fix, arms all passive breadcrumb/instrument env
vars per the standing rule). `scratch/agent/soak_queue/done/s482_blanket_rwrite_guard_manual.sh` is
this session's own manual (foreground) live-verify, already consumed — no need to rerun.
