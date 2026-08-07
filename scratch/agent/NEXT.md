# NEXT work unit

HYPOTHESIS-ID: orphan-guard-completeness-closeout

## What changed session s450

Fixed the `G1`-`G32` family (item -288): 29 sites plus a previously-unaccounted 5-site sibling
family (`A`-`E`, an older s110 table-deref guard) and their shared `L_hangarbay_guard_exit`
epilogue label were ALL doubly-orphaned since s427 (gated to dead file `funcs_40.c` + dead
function name `static_5_800AB658`, needed `funcs_28.c`/`updateHangarBayScene`). Standalone scan
(`scratch/agent/s450_scan_g1g32.py`) confirmed 0 collisions tree-wide, refuting the old fixup
comment's stale "also in funcs_27.c" warning. First build failed on an undeclared label because
the epilogue-label block and the A-E block were independently orphaned too and hadn't been fixed
yet — fixed all three together. Full regen/build clean, 35/35 patches x1, `strings`-verified.
Live-verify: 0 fires (matches the item -287 baseline), crashed on the already-closed item -259
signature family (not this session's target). Confirmation soak queued: `s450_g1g32_confirm.sh`.

**Incidental finding, NOT fixed this session (item -289, new)**: auditing the remaining
`if p.name == "funcs_40.c":` gates found **9 more doubly-orphaned sites in a DIFFERENT, OLDER
`composeNpcOrientationMatrix` guard family** (s100-era "guard1"-"guard8"-equivalent, distinct
from item -284's own 30-site fix for the same function) — confirmed silently producing zero
report lines this session. This plus the already-known `BREADCRUMB7` (item -284) are now the
FULL remaining inventory of `funcs_40.c`-gated orphans (10 blocks total).

Full detail: `docs/CURRENT-TRUTH.md` items -288/-289, `PORTING-STATE.md` Session 450.

## This session's work unit: item -289, the 9 orphaned `composeNpcOrientationMatrix` guard sites

Same proven method as s446/s448/s450, applied to the smallest remaining family. Unlike the G1-G32
fix, these 9 sites (`fixup_game_funcs.py` lines ~1907-2381 as of s450, search
`if p.name == "funcs_40.c":` — there are exactly 10 remaining matches, 9 for this family + 1 for
`BREADCRUMB7`) are independent single-site blocks (not one shared list like `_hangarbay_deref_guard_sites`),
each with its own `func_start_m` search for the dead name `static_5_800AB1C8`. Grep
`target: composeNpcOrientationMatrix` in the fixup script to enumerate all 9 block locations exactly.

**Check first**: does `composeNpcOrientationMatrix` (now `funcs_28.c` per item -284/s446) have its
own `goto`-target label(s) that these 9 sites jump to, and if so, is that label ALSO independently
orphaned (same trap that cost this session an extra build-fail cycle on item -288)? Grep each
site's patch function body for `goto L_` and check whether the target label already exists
unconditionally in the current tree (item -284's s446 fix already un-orphaned
`composeNpcOrientationMatrix` itself and its own epilogue infrastructure for the s446 list — CHECK
whether these 9 OLDER sites reuse that same infrastructure or need their own, don't assume either
way).

Same 5-step method as s446/s448/s450:
1. Raw regen (delete `RecompiledFuncs/funcs_*.c` -> `make_elf.py` -> `N64Recomp`, NO fixup yet).
   `scratch/agent/s450_delete_funcs.sh`/`s450_run_make_elf.sh`/`s450_run_n64recomp.sh` are ready
   templates — copy to `s451_*`, update paths, or reuse directly if no other regen has happened
   since (check file mtimes first).
2. Standalone Python scan (model: `scratch/agent/s450_scan_g1g32.py`'s `exec`-extraction pattern,
   adapted for 9 separate single-site patterns rather than one list) checking each site's anchor
   for tree-wide uniqueness AND for landing inside `composeNpcOrientationMatrix`'s own body span.
3. Check any `goto`-target label dependency (see above) BEFORE ungating — this is the exact
   lesson s450 paid a wasted build cycle to learn.
4. Ungate (file `funcs_40.c` -> `funcs_28.c`, function regex `static_5_800AB1C8` ->
   `composeNpcOrientationMatrix`) + add the `SystemExit`-on-`n>1` hard guard (s446/s448/s450
   pattern) to each site.
5. Full regen -> build -> audit fixup report for exactly `x1` per applied site -> `strings` on the
   binary -> live-verify with the full armed-var list (copy from
   `scratch/agent/soak_queue/s450_g1g32_confirm.sh`, add this family's own env var) -> queue a
   confirmation soak. **Expected result per item -287's baseline: 0 fires is the norm now, not an
   open question — do not spend another session chasing "why 0."**

After item -289, remaining families in order (see `docs/CURRENT-TRUTH.md` item -284 for detail):
1. **`S392_H3A`/`S393_H3B`** (50 sites) — chunk 3a's 29 sites may already be covered by
   `GENERIC_CACHE_GUARD`'s blanket fix; check for redundancy before re-adding (chunk 3b's 21
   likely does need the fix).
2. `BREADCRUMB7` (diagnostic, lowest priority — a diagnostic, not a crash guard).

If item -289 (or the whole remaining orphan-sweep list) starts feeling like diminishing returns
relative to session cost, it's legitimate to instead open a genuinely NEW M3 idiom-class audit
(strategic priority #3's other sanctioned mode) — e.g. a fresh frequency-scan the way s282/s445
opened `GETDATITEM_GUARD`, rather than continuing to finish this specific closed-ambiguity family.

## Discriminating measurement

Does the full 9-site uniqueness scan come back 100% unique and body-contained (proceed with
s446/s448/s450's method), and does the `goto`-target label check find a pre-existing dependency
that needs its own fix first (as item -288 did) or not?

## Process notes carried forward

- `tools/probe.sh`'s exit code is trustworthy on its own now (exit 3 on a detected `[CRASH]`, s447).
- `fixup_game_funcs.py` lives in the sibling `N64Recomp` repo (`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`), NOT in this repo — it is not git-tracked by RogueSquadron64Recomp and needs no `export.sh`.
- When ungating a multi-site family, expect SOME sites to be redundant no-ops against
  earlier-applied guards in the same fixup script — not a bug, don't force-match shortened
  anchors to avoid it.
- Watch for DOUBLY-orphaned gates (file AND function-name-regex referencing the dead old
  `static_N_0xADDR` name) — confirmed pattern across at least 3 families now (S390_H2, G1-G32/A-E,
  and item -289 pending).
- **New s450 lesson**: before ungating any family whose patch body contains a bare `goto LABEL`
  (not a label the patch itself defines), grep for that label's OWN defining block and confirm
  it is not independently orphaned by the same mechanism — a build failure
  ("undeclared label") is the symptom if you skip this check, costing a full extra
  regen/fixup/build cycle to diagnose and fix. Check BEFORE the first build attempt, not after.
- **s449 pattern still applies**: a guard family's confirm soak logging 0 trips no longer needs a
  fresh positive-control round for this whole `-0x25A4`/table-deref guard idiom class — item -287
  established the baseline (0 trips under 245000+ reaches). Read a future 0-fires result as
  "consistent with baseline," not "inconclusive."
