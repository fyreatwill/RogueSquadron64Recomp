# NEXT work unit

## s386 recap

Batch 9/N (the closing batch) of the fixup_game_funcs.py function-scope-match backport: converted the
final 4 sites — `loadCraftShadowTextures` (funcs_16.c), `mat3x3InverseInto` (funcs_5.c),
`tickTextureMaterialExpiry` (funcs_6.c), `coalesceFreeHeapBlocks` (funcs_0.c). A fresh scan + direct code
read (not trusting s385's rolled-forward "3 untriaged" claim) found `loadCraftShadowTextures` had been
missed from that list — always re-derive the untriaged set from a fresh `scan_filescoped.py` + content
read each batch, since line numbers drift and a prior session's named list can be stale. All 4 anchors
verified to sit cleanly inside their target function's own body span before delegating the conversion
edit. Byte-identical regen-diff verified clean (fixup-report and full `RecompiledFuncs/` tree both diff
empty before/after). Build clean. Soak clean: 0 crash markers over 17,355 log lines across 120s, VI
reached the full 0→320→512→640→1024 phase timeline.

**Running total: 168/176 converted, 8 remain — all 8 are confirmed permanent design exclusions. The
fixup_game_funcs.py function-scope-match backport task is CLOSED OUT as of s386.** It will not resurface
as a recurring "sanctioned tooling" work unit. Full breakdown of the 8 exclusions and the two live
follow-up items: `docs/CURRENT-TRUTH.md` Sanctioned-tooling paragraph and Next-steps item -238.

## This iteration's work unit: pick one of two options

The sanctioned-tooling backlog item is gone. Per the 2026-08-04 user directive's strategic-priority order
(CURRENT-TRUTH top of file), with M5 audio having no open thread as of s376, the next work is either one
of the two small named follow-ups from the closed backport, or M3 idiom-class audit work. Pick based on
size: the follow-ups are small and well-scoped (good single-iteration units); M3 work needs a fresh
idiom-class candidate chosen via grep-enumeration, not a single-crash chase.

### Option A (smallest, well-scoped, do this first): `runHangarMenuFromOverlay`/`hasKasanMoorDefected` collision fix

A file-scoped patch's bare-label anchor (around line ~8657 in the current `fixup_game_funcs.py` — re-scan
for the exact current line, it drifts) textually matches an unrelated function (`hasKasanMoorDefected`) in
a different overlay file, so the file-scoped `subn` silently patches both. Needs `p.name` filtering added
to that one patch so it only fires in the overlay file the intended function (`runHangarMenuFromOverlay`)
actually lives in. Steps:
1. Locate the patch (grep `runHangarMenuFromOverlay` and `hasKasanMoorDefected` in
   `~/Documents/Tools/N64Recomp/fixup_game_funcs.py`) and read the full context to find both functions'
   home files (check `RecompiledFuncs/*.c` for which overlay file each `RECOMP_FUNC` actually lives in).
2. Add a `p.name == "<correct overlay file>.c"` guard (or equivalent restriction) so the regex only
   applies where `runHangarMenuFromOverlay` lives, not wherever `hasKasanMoorDefected` also happens to
   match the same bare label.
3. Same verification protocol as every batch: backup script, clear `RecompiledFuncs/`, regen twice
   (before/after), diff fixup-report + tree — this time they will NOT be byte-identical (that's the
   point: the fix should make `hasKasanMoorDefected`'s file lose a spurious match while
   `runHangarMenuFromOverlay`'s file keeps its real one). Confirm the diff is exactly that one change, not
   a regression elsewhere.
4. Build + soak, same clean-shape expectation as every prior batch.

### Option B: `musyxSynthFrame`/`initN64RspMixer` synth-rearm-ptr ownership question

Read-only investigation, not a patch: does the `ROGUESQ_LOG_AUDIOTICK_TRACE`-gated diagnostic at
`0x800919D4` genuinely belong in `initN64RspMixer` instead of `musyxSynthFrame`, as the byte-identical
regen-diff catch in s384 suggested? Read both functions' source in `RecompiledFuncs/funcs_5.c` (or
wherever they currently live) around that address, understand what the code at `0x800919D4` actually does
in context, and either confirm the diagnostic's current file-scoped placement is fine as-is (not worth
moving, low priority, not armed in any soak recipe) or write up a concrete relocation plan. Lower urgency
than Option A — pick this only if Option A is somehow blocked.

### Option C: M3 idiom-class audit (if both follow-ups are exhausted or deferred)

Per the standing strategic-priority order (item 3), grep-enumerate a new idiom class of guard sites the
same way s282-288 did for `-0x25A4`, classify every site, guard or prove dead, close the class. Do NOT
reactively chase a single breadcrumb — check `scratch/agent/SOAK-RESULTS.md` for recurring crash-marker
patterns first to pick a real, currently-live idiom class rather than inventing one.

## Iteration budget

HYPOTHESIS-ID: post-backport-followups (new thread, pivoted from `fixup-scope-backport` which closed
s386). Start fresh budget count on whichever option is picked.
