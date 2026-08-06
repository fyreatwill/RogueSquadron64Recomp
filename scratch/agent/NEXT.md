# NEXT work unit

## s387 recap

Fixed Option A from s386's NEXT.md: the `runHangarMenuFromOverlay`/`hasKasanMoorDefected` bare-label
collision in `fixup_game_funcs.py`. The `L_800C68AC:` file-scoped patch had no `p.name` guard, so it
silently spliced the s179 loop-iteration diagnostic into `hasKasanMoorDefected` (funcs_29.c, wrong
function, same reused local-label text) as well as its real target `runHangarMenuFromOverlay`
(funcs_43.c, `static_5_800C6854`). Confirmed the bug empirically (baseline regen showed both files
patched), fixed it with `p.name == "funcs_43.c"`, and verified via the same byte-identical regen-diff
protocol as every backport batch: report diff showed exactly one line removed (`funcs_29.c`'s spurious
match); tree diff showed exactly one file's hash changed (`funcs_29.c`), `funcs_43.c` and all 43 other
files untouched. Build clean, soak clean (0 crash markers over 17,375 log lines, full VI phase timeline
0→320→640→1024→640→512 over 120s). No `lib/` files touched (the edit lives in the standalone
`~/Documents/Tools/N64Recomp` tool checkout, untracked by git there — same as every prior backport
session), so `submodule-patches/export.sh` didn't apply.

## This iteration's work unit: pick one of two options

Only one item remains from the closed backport's follow-up list; M3 idiom-class audit is the fallback.

### Option B (do this first — it's the last named follow-up): `musyxSynthFrame`/`initN64RspMixer` synth-rearm-ptr ownership question

Read-only investigation, not a patch: does the `ROGUESQ_LOG_AUDIOTICK_TRACE`-gated diagnostic at
`0x800919D4` genuinely belong in `initN64RspMixer` instead of `musyxSynthFrame`, as the byte-identical
regen-diff catch in s384 suggested? Steps:
1. Read both functions' source in `~/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_5.c` (or wherever
   they currently live — re-grep, don't trust this line number) around address `0x800919D4`.
2. Understand what the code at that address actually does in context: is it genuinely inside
   `initN64RspMixer`'s own instruction range, or does `musyxSynthFrame` tail-call/fall through into it
   in a way that makes the current file-scoped placement defensible?
3. Either (a) confirm the diagnostic's current file-scoped placement is fine as-is (not worth moving,
   low priority, not armed in any soak recipe — close the item with a one-line note), or (b) write a
   concrete relocation plan (which function-scope anchor, which file) as a future work unit.
4. This is a documentation/investigation-only work unit — it can close as ADVANCED via a new finding
   (the ownership answer) without necessarily requiring a code change, per the iteration contract's
   "or landed... a NEW document" allowance. If it does turn into a patch, follow the standard
   backup/regen-diff/build/soak protocol used for every backport site.

### Option C: M3 idiom-class audit (if Option B is somehow blocked)

Per the standing strategic-priority order (item 3), grep-enumerate a new idiom class of guard sites the
same way s282-288 did for `-0x25A4`, classify every site, guard or prove dead, close the class. Do NOT
reactively chase a single breadcrumb — check `scratch/agent/SOAK-RESULTS.md` for recurring crash-marker
patterns first to pick a real, currently-live idiom class rather than inventing one. Note:
`SOAK-RESULTS.md`'s tail as of s387 shows the queue has been quiet since s369 (last real queued-soak
entries were manual s379/s386 batch-verification runs, not idiom-hunting soaks) — a fresh scan for
recurring crash markers across `scratch/agent/soak_results/*.log` may be needed to find a live candidate
rather than assuming one is sitting in SOAK-RESULTS.md already.

## Iteration budget

HYPOTHESIS-ID: post-backport-followups (same thread as s387; this is iteration 2 of this slug since it
pivoted from `fixup-scope-backport` at s386 close). Pivot or close the slug if Option B doesn't produce a
discriminating answer within 1-2 more iterations.
