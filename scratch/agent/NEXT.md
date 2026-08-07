# NEXT work unit

HYPOTHESIS-ID: static5-rename-orphan-sweep

## What changed session s447

Folding in the two newest `SOAK-RESULTS.md` lines (both logged `rc=0`, "clean") per the standing
read-list found they weren't clean: `s445_getdatitem_confirm` and `s446_hangarlist_confirm` both
called `tools/probe.sh` directly with no self-check of `run.log`, and `probe.sh`'s capture loop
fell through to an implicit `exit 0` on ANY mid-capture process death, crash or not. Both runs'
`run.log`s in fact contain `[CRASH]` blocks — s445 hit `sym=cvmsPoolAlloc+496` (an already-
catalogued, unrelated ~s73/s267 misattribution family), s446 hit `sym=coalesceFreeHeapBlocks+3192`
(an already-catalogued, unrelated s264-era/BREADCRUMB11 family). Neither guard fix is implicated —
both crashes are old, pre-existing, unrelated signatures — but both guard families (item -282
GETDATITEM_GUARD, item -284 HANGARLIST_GUARD+S284/S285) logged 0 fires in these runs, so their
confirmation status is still OPEN, not closed.

Fixed the root cause in `tools/probe.sh` itself (not just the two recipe scripts): it now checks
`run.log` for `[CRASH]` after the capture loop and `exit 3`s instead of falling through to 0.
Verified with a same-session positive control (against s446's crashed run.log) and negative
control (against a known-genuinely-clean run.log). Requeued a corrected combined confirm soak:
`scratch/agent/soak_queue/s447_hangarlist_getdatitem_confirm.sh` — fold its result in first (read
list #3) before starting new work; it covers both item -282 and item -284 in one run.

Full detail: `docs/CURRENT-TRUTH.md` item -285, `PORTING-STATE.md` Session 447.

## This session's work unit: the S390_H2A/S390_H2B sweep (carried over from s446, unexecuted)

Same proven method as s446 (item -284), applied to the next remaining orphaned family. Method
recap (repeat per family):
1. For every site's exact anchor text (comment line + generated-code line, verbatim from
   `fixup_game_funcs.py`), run a standalone Python scan across every `RecompiledFuncs/funcs_*.c`
   file counting exact matches. Expect exactly 1 per site.
2. If ALL sites in a family are unique (1 match each): remove the family's old `p.name ==
   "funcs_N.c"` file gate (and/or old `static_N_0xADDR` function-name regex, replacing with the
   real current name) so the anchor's own specificity does the placement. Add a hard
   `SystemExit`-on-`n>1` guard in the fixup code itself (see s446's pattern, `fixup_game_funcs.py`
   ~line 5566) rather than trusting `re.subn`'s count blindly.
3. If ANY site is non-unique (matches in 2+ places, or 2+ times in one place): do NOT ungate that
   whole family blindly. Hand-disambiguate first.
4. Verify bail labels: every guard's `goto <label>` target must exist INSIDE the same function as
   the guard itself — grep `^<LABEL>:` and confirm its line falls between the target function's
   `RECOMP_FUNC` start and the next function's start in the same file.
5. Full 4-step regen (delete `RecompiledFuncs/funcs_*.c` first, standing item -20 rule) → build →
   audit the fixup report for exactly `x1` per site → `strings` on the binary to confirm guard
   format-strings present → live-verify with all guard-family env vars armed.

**`S390_H2A`/`S390_H2B`** (11 sites, chunk 2, `funcs_40.c`→now `funcs_28.c` per s446's sample check
of site 1 of each). Likely the most mechanical remaining piece — same shape as s446's fix. Do this
first; it's the smallest remaining family.

After S390, the remaining families in order (see `docs/CURRENT-TRUTH.md` item -284 for full detail
on each's specific risk):
2. **`G1`-`G32`** (32 sites) — needs a FULL 32-site uniqueness recheck (only 2/32 sampled so far)
   before trusting the old fixup comment's collision warning is stale.
3. **`S392_H3A`/`S393_H3B`** (50 sites) — chunk 3a's 29 sites may already be covered by
   `GENERIC_CACHE_GUARD`'s blanket fix; check for redundancy before re-adding. Chunk 3b (21 sites)
   likely does need the fix.
4. **`BREADCRUMB7`** (diagnostic, lowest priority).

## Discriminating measurement

For each family: does the full per-site uniqueness scan come back 100% unique (proceed with s446's
method) or does it surface a genuine collision (needs manual disambiguation)? This splits
"mechanical rename, same as s446" from "needs the S100/G-family collision analysis redone fresh".

## Regen / build notes

Same as s446 — reuse `scratch/agent/s446_delete_funcs.sh` / `s446_run_make_elf.sh` /
`s446_run_n64recomp.sh` / `s446_run_fixup.sh` / `s446_run_build.sh` as templates (copy to `s448_*`
and update log/rc paths).

## Process note for future soak recipes

`tools/probe.sh`'s exit code is now trustworthy on its own (exit 3 on a detected `[CRASH]` in
`run.log`, s447) — a recipe no longer strictly needs its own self-check to get an accurate `rc` in
`SOAK-RESULTS.md`. Keep the self-check anyway for the descriptive crash-line message (matches the
s434/s442/s447 pattern) — it costs nothing and is one less thing to trust blindly.
