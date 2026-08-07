# NEXT work unit

HYPOTHESIS-ID: orphan-guard-completeness-closeout

## s452 note: this was a MAINTENANCE iteration, not a 4th hypothesis iteration

Step 0's `wc -c docs/CURRENT-TRUTH.md` (61086 bytes) tripped the 60000-byte maintenance trigger, which
runs before work-unit selection — so this satisfied the loop's mandatory-pivot rule for real (a
maintenance pass is a different activity, not a repeat of `orphan-guard-completeness-closeout`) without
needing to force a probe or an artificial pivot on the hypothesis itself. `docs/CURRENT-TRUTH.md`
703→475 lines (61086→41233 bytes); the s445-451 orphan-sweep detail (items -282..-289) and the
already-once-compacted s438-445 BREADCRUMB18/free-list-guard arc (items -274..-280, -263) both migrated
to `docs/PROJECT-OVERVIEW.md` §16 as condensed range pointers. No conclusions changed. Full detail:
`PORTING-STATE.md` Session 452.

**This session's actual work unit is UNCHANGED from below — the S392_H3A/S393_H3B plan still stands.**
If a NEXT maintenance trigger doesn't fire, resume there directly; do not re-read this note as new
work. This IS iteration 4 on the hypothesis thread in the sense that the underlying question is still
open — but iteration 4 was a maintenance pass, not a repeat probe, so the loop's pivot condition should
re-arm fresh starting from the next iteration that actually touches `S392_H3A`/`S393_H3B`.

## What changed session s451

Fixed item -289: the 9 doubly-orphaned `composeNpcOrientationMatrix` guard sites ("guard1"-"guard9",
s100-s261-era, distinct from item -284's own 30-site s446 fix for the same function). All 9 were
gated on the dead file location `funcs_40.c` and the dead function name `static_5_800AB1C8` since
s427. Standalone scan confirmed all 9 anchors unique tree-wide and inside `composeNpcOrientationMatrix`'s
own body span (`funcs_28.c`). Checked the shared `goto L_800AB618;` bail target for independent
orphaning BEFORE ungating (s450's own lesson) — confirmed already live via other already-ungated
guards in the same file (`S284_AB1C8_6`-`_10`, `S390_H2B_*`), so no shared-infrastructure fix was
needed this time. Ungated all 9 (dropped file+`func_start_m` scoping, direct `re.subn` on whole file
text + `SystemExit`-on-`n>1` guard, s446/s448/s450 pattern). Full regen/build clean, 9/9 patches x1,
`strings`-verified. Live-verify: 0 fires (matches item -287 baseline), `hangarbay-entry` n=2700,
crashed ~197s in on the already-catalogued `BREADCRUMB6`/near-`0x80000000` family
(`buildPositionAndCallTransformHelper+1736`, `si_addr=0x380000010` — first seen s273, reconfirmed
"not a new crash class" as recently as s328a). Confirmation soak queued: `s451_composenpc9_confirm.sh`.

**This closes the `funcs_40.c`-gated orphan inventory except `BREADCRUMB7`** (a diagnostic, not a
crash guard — deliberately out of scope, lowest priority). `grep -c 'if p.name == "funcs_40.c":'
fixup_game_funcs.py` now returns 1.

Full detail: `docs/CURRENT-TRUTH.md` item -289, `PORTING-STATE.md` Session 451.

## This session's work unit: `S392_H3A`/`S393_H3B` (50 sites total: 29 + 21)

The next-largest remaining item in item -284's tracked backlog. Grep `S392_H3A_` / `S393_H3B_` in
`fixup_game_funcs.py` (currently ~32/22 raw string hits respectively — includes both the tuple list
definitions and their application loop, so the real site count needs confirming, not assumed from
grep count alone).

**Known wrinkle from item -284's own read (s446), MUST be checked before treating this as a
copy-paste of the s446/s448/s450/s451 method**: `S392_H3A`'s bail label `L_800ADB2C` sits INSIDE
`updateHangarBayScene`'s body (not a separate function) — meaning some or all of these 29 sites may
guard derefs ALREADY covered by `GENERIC_CACHE_GUARD`'s blanket 107-site fix (item -270/-273). Check
for redundancy (does GENERIC_CACHE_GUARD already validate the same pointer before these sites'
own dereference point?) BEFORE re-adding — do not just ungate-and-patch blindly; a chunk of this
family may correctly no-op as redundant, same as 7/11 sites did for `S390_H2B` in item -286.

Same method as s446/s448/s450/s451, adapted:
1. Grep `S392_H3A_`/`S393_H3B_` for exact current line ranges and site count (don't trust the s446
   writeup's counts blindly — confirm against the live file).
2. Raw regen (delete `RecompiledFuncs/funcs_*.c` -> `make_elf.py` -> `N64Recomp`, NO fixup yet).
3. Standalone Python scan: for each site, check tree-wide anchor uniqueness AND whether the site is
   already redundant with an active `GENERIC_CACHE_GUARD` check (read the surrounding code, not just
   grep the anchor).
4. Check the `L_800ADB2C` goto-target dependency: is it independently orphaned? (Unlike composeNpc's
   `L_800AB618`, this one has NOT yet been checked against the current tree — don't assume either
   way, same discipline as s450/s451.)
5. Ungate (whatever the current file/function-name gate is — check first, may differ from the
   `funcs_40.c` pattern since these might already be scoped differently) + `SystemExit`-on-`n>1`
   guard.
6. Full regen -> build -> audit fixup report -> `strings` -> live-verify (full armed-var list, add
   `ROGUESQ_LOG_S392_H3A_GUARD`/`ROGUESQ_LOG_S393_H3B_GUARD` if not already in the standard list —
   check `soak_queue/s451_composenpc9_confirm.sh` for the current baseline armed-var set) -> queue a
   confirmation soak. **Expected result per item -287's baseline: 0 fires is the norm, not an open
   question.**

If `S392_H3A`/`S393_H3B` turns out to be substantially redundant with `GENERIC_CACHE_GUARD` (per the
known wrinkle above), that's a legitimate, useful finding on its own — document the redundancy
percentage and only patch the genuinely-uncovered subset, don't force full application.

After `S392_H3A`/`S393_H3B`, remaining orphan-sweep debt: `BREADCRUMB7` only (diagnostic, lowest
priority — optional, not required before declaring the whole `funcs_40.c` orphan-sweep closed).

If `S392_H3A`/`S393_H3B` starts feeling like diminishing returns relative to session cost, it's
legitimate to instead open a genuinely NEW M3 idiom-class audit (strategic priority #3's other
sanctioned mode) — e.g. a fresh frequency-scan the way s282/s445 opened `GETDATITEM_GUARD`.

## Discriminating measurement

Does `S392_H3A`'s bail-label body-containment check confirm these sites are (a) already covered by
`GENERIC_CACHE_GUARD` (redundant, minimal patch needed), (b) genuinely uncovered (full 29+21-site
patch needed), or (c) a mix — and does `L_800ADB2C` need its own independent-orphaning fix first (as
`L_hangarbay_guard_exit` did for item -288) or not (as `L_800AB618` did not, for item -289)?

## Process notes carried forward

- `tools/probe.sh`'s exit code is trustworthy on its own now (exit 3 on a detected `[CRASH]`, s447).
- `fixup_game_funcs.py` lives in the sibling `N64Recomp` repo
  (`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`), NOT in this repo — it is
  not git-tracked by RogueSquadron64Recomp and needs no `export.sh`.
- When ungating a multi-site family, expect SOME sites to be redundant no-ops against
  earlier-applied guards in the same fixup script — not a bug, don't force-match shortened anchors
  to avoid it. `S392_H3A`/`S393_H3B` is explicitly flagged as likely to have MORE redundancy than
  usual (against `GENERIC_CACHE_GUARD`, not just sibling `-0x25A4` guards).
- Watch for DOUBLY-orphaned gates (file AND function-name-regex referencing a dead old
  `static_N_0xADDR` name) — confirmed pattern across 4 families now (S390_H2, G1-G32/A-E, item -289,
  and now potentially S392/S393 — check, don't assume).
- **s450 lesson, reconfirmed s451**: before ungating any family whose patch body contains a bare
  `goto LABEL` (not a label the patch itself defines), grep for that label's OWN defining block and
  confirm it is not independently orphaned by the same mechanism — a build failure ("undeclared
  label") is the symptom if you skip this check. s451 found the check can also come back CLEAN
  (no fix needed) when the label is already proven live by other already-ungated guards in the same
  file — check first, don't assume either outcome.
- **s449 pattern still applies**: a guard family's confirm soak logging 0 trips no longer needs a
  fresh positive-control round for this whole `-0x25A4`/table-deref/pointer-chase guard idiom class
  — item -287 established the baseline (0 trips under 245000+ reaches). Read a future 0-fires result
  as "consistent with baseline," not "inconclusive."
- **s451 lesson**: the near-`0x80000000`/`BREADCRUMB6` "near-zero guest pointer" crash family
  (`si_addr=0x3800000xx`, `pc-symbol=buildPositionAndCallTransformHelper+...`) is a recurring,
  fully-catalogued background crash signature unrelated to this whole orphan-sweep effort — if a
  future confirm soak hits it again, do not re-investigate, just note the occurrence.
