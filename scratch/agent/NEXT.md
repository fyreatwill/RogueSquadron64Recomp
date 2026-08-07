# NEXT work unit

HYPOTHESIS-ID: static5-rename-orphan-sweep

## What changed session s446

Root-caused item -283's orphaned-guard finding as much bigger than 61 sites: `hangarInitialize`
never existed as a real function post-s427 — it was N64Recomp's pre-fix merger of ~15 separate
functions (now correctly named `loadCutsceneAssetsByIndex`/`runHangarSelectionFrame`/
`composeNpcOrientationMatrix`/`updateHangarBayScene`/`hangarTickCameraOrbit`/etc.) into one
anonymous ~13,770-line blob under a duplicate-symbol collision, which s427's fix split apart.
EVERY guard/patch in `fixup_game_funcs.py` hardcoded to the old anonymous `static_N_0xADDR`
placeholder names (or a specific `funcs_N.c` file) is orphaned this way. Fixed and verified 34
sites this session (`HANGARLIST_GUARD`+`EARLY`/`WALK`/`CLEAR`, 4 sites; the s284/s285 combined
deref-guard list, 30 sites) — full regen+build clean, binary-verified via `strings`, live-verified
0 crashes/0 fires over a full 300s hold with `[hangarbay-entry]` n=3000+ reachability control.
Confirmation soak queued: `scratch/agent/soak_queue/s446_hangarlist_confirm.sh` — fold its result
in first (read list #3) before starting new work.

Full detail: `docs/CURRENT-TRUTH.md` item -284, `PORTING-STATE.md` Session 446.

## This session's work unit: finish the sweep

Same proven method as s446, applied to the remaining orphaned families. Method recap (repeat per
family):
1. For every site's exact anchor text (comment line + generated-code line, verbatim from
   `fixup_game_funcs.py`), run a standalone Python scan across every `RecompiledFuncs/funcs_*.c`
   file counting exact matches. Expect exactly 1 per site.
2. If ALL sites in a family are unique (1 match each): remove the family's old `p.name ==
   "funcs_N.c"` file gate (and/or old `static_N_0xADDR` function-name regex, replacing with the
   real current name) so the anchor's own specificity does the placement. Add a hard
   `SystemExit`-on-`n>1` guard in the fixup code itself (see s446's pattern for the s284 list,
   `fixup_game_funcs.py` ~line 5566) rather than trusting `re.subn`'s count blindly.
3. If ANY site is non-unique (matches in 2+ places, or 2+ times in one place): do NOT ungate that
   whole family blindly. Hand-disambiguate the colliding site(s) first (which occurrence is inside
   the function whose real name matches the guard's intended target?), or scope that one family
   per-file instead of tree-wide.
4. Verify bail labels: every guard's `goto <label>` target must exist INSIDE the same function
   as the guard itself (C requirement) — grep `^<LABEL>:` and confirm its line falls between the
   target function's `RECOMP_FUNC` start and the next function's start in the same file.
5. Full 4-step regen (delete `RecompiledFuncs/funcs_*.c` first, standing item -20 rule) → build →
   audit the fixup report for exactly `x1` per site (not `x0`, not `x2+`) → `strings` on the
   binary to confirm guard format-strings present → live-verify with all guard-family env vars
   armed.

## Remaining families, in order of expected value

1. **`S390_H2A`/`S390_H2B`** (11 sites, chunk 2, `funcs_40.c`→now `funcs_28.c` per s446 sample
   check of site 1 of each). Likely the most mechanical — same shape as this session's fix.
   Do this first.
2. **`G1`-`G32`** (32 sites, target `updateHangarBayScene`, `funcs_40.c`→now `funcs_28.c` per
   sample check of G1/G32). **Known risk, must fully recheck before trusting**: the old fixup
   comment explicitly warns every G-site anchor "ALSO appears verbatim in `funcs_27.c` — a
   different overlay's function reusing the same guest address range" (the
   `hangarInitialize`/`composeNpcOrientationMatrix` collision, first hit s100). This collision may
   no longer exist post-s427 (the truncated-stub copy that caused it might be gone), but s446 only
   sample-checked 2 of 32 sites — run the FULL 32-site uniqueness scan before ungating.
3. **`S392_H3A`/`S393_H3B`** (50 sites, chunks 3a/3b). **New finding from s446**: chunk 3a's bail
   label `L_800ADB2C` is now INSIDE `updateHangarBayScene`'s own body (`funcs_28.c:20409`), not a
   separate function as originally assumed — meaning these 29 sites' guest addresses fall within
   `updateHangarBayScene`, which is ALREADY heavily guarded (`GENERIC_CACHE_GUARD`'s 107-site
   blanket regex sweep, `CACHE_HEAD_A1_GUARD`, `FREELIST_NEXT_GUARD`). **Before re-adding these 29
   guards, check whether `GENERIC_CACHE_GUARD`'s regex already covers the same `-0x25A4` derefs**
   — read `GENERIC_CACHE_GUARD`'s regex pattern (`fixup_game_funcs.py`, search
   `GENERIC_CACHE_GUARD`) and compare against 2-3 of the 29 site addresses directly in
   `funcs_28.c`. If already covered, this whole sub-family may be a closed non-issue, not a gap.
   Chunk 3b (`S393_H3B`, 21 sites, bail `L_800AE060` — confirmed s446 to be inside
   `hangarTickCameraOrbit`) likely does need the fix; check separately from 3a.
4. **`BREADCRUMB7`** (diagnostic, target `updateHangarBayScene`, `funcs_40.c`-scoped) — lowest
   priority, purely diagnostic, not a safety guard.

## Discriminating measurement

For each family: does the full per-site uniqueness scan come back 100% unique (proceed with
s446's method) or does it surface a genuine collision (needs manual disambiguation, higher-cost
path)? This splits "mechanical rename, same as s446" from "needs the S100/G-family collision
analysis redone fresh". Do NOT skip the full scan for G1-G32 just because 2/32 sampled clean — the
old comment's warning was explicit and specific enough to treat as a live risk until reproven false
across the whole family.

## Regen / build notes

Same as s446 — reuse `scratch/agent/s446_delete_funcs.sh` / `s446_run_make_elf.sh` /
`s446_run_n64recomp.sh` / `s446_run_fixup.sh` / `s446_run_build.sh` as templates (copy to
`s447_*` and update log/rc paths, or run in place and just re-check the fresh logs — the scripts
themselves aren't session-numbered in their logic, only their output filenames).
