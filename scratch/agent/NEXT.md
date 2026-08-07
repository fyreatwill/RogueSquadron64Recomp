# NEXT work unit

HYPOTHESIS-ID: orphan-guard-completeness-closeout

## What changed session s449

Closed the open ambiguity that had blocked items -282/-284/-286 for 4 sessions (mandatory-pivot
rule fired after 3 straight iterations on `static5-rename-orphan-sweep`): added unconditional
REACHED counters to the already-ungated `GETDATITEM_GUARD` (6 sites) and `HANGARLIST_GUARD_EARLY`/
`WALK`/`CLEAR` (3 sites) in `N64Recomp/fixup_game_funcs.py`. One 117s live run got a strong
positive control: `HANGARLIST_GUARD_EARLY`/`WALK`/`CLEAR` were reached 123000/58500/64500 times
respectively with 0 trips — these are confirmed TRUE NEGATIVES, not soak-coverage gaps.
`GETDATITEM_GUARD` reached 5/6 sites (n=1 each, lower confidence, still refutes "unreached").

**This changes the framing of the remaining orphan-sweep work, not its validity.** `G1`-`G32`,
`S392_H3A`/`S393_H3B`, and `BREADCRUMB7` are still genuine correctness debt (orphaned gates
silently disable guards — that's a defect regardless of firing rate) and strategic priority #3
still wants the idiom class formally closed. But go in expecting 0 fires: this family of guard
is now evidence-backed as unlikely to explain any *currently open* crash. Do not read a future
0-fires confirm soak on these families as inconclusive — it would match the now-established
baseline, not be a new null result requiring another positive-control round.

The incidental new crash this session (`pc-symbol=heapFreeListDequeue+19316` misattribution,
`last-guest-pc=0x8000d534`, `menuOverlayInit <- mainGameLoop` backtrace) is filed (CURRENT-TRUTH
item -287) but NOT this session's target — strategic priority #3 rules out reactive chases on a
single occurrence with no positive control.

Full detail: `docs/CURRENT-TRUTH.md` item -287, `PORTING-STATE.md` Session 449.

## This session's work unit: finish the `G1`-`G32` family (32 sites, doubly-orphaned)

Unchanged from s448's plan (still accurate, just reframed above as completeness not crash-hunting).
Same proven method as s446/s448, applied to the largest remaining family — but this one has an
EXTRA wrinkle s390 didn't: **its gate is doubly-orphaned, not singly.**

`fixup_game_funcs.py` (search `_hangarbay_deref_guard_sites` and the `if p.name ==
"funcs_40.c":` block right after it): the whole G1-G32 block is gated BOTH on `p.name ==
"funcs_40.c"` (file, same orphaning as every other family in this saga) **AND** on a regex that
locates the function by its dead old name: `r"RECOMP_FUNC void static_5_800AB658\(uint8_t\*
rdram, recomp_context\* ctx\) \{\n"`. `static_5_800AB658` was renamed to `updateHangarBayScene` by
s427 and moved to `funcs_28.c` — since the regex searches for the OLD name, `func_start_m` never
matches regardless of the file gate, so **this entire 32-site family currently produces ZERO
guards**, silently, with no report line at all. Confirm this null-report behavior first (grep the
fixup log for "G1"/"G32" — expect literally nothing) before starting.

Fix needs BOTH: (1) drop the `p.name == "funcs_40.c"` file gate (or replace with `funcs_28.c` —
check whether `updateHangarBayScene` might ALSO appear textually in another file the way
`L_800AB618` did for s448, before assuming file-scoping is safe to drop entirely); (2) update the
function-name regex to `updateHangarBayScene`.

Same 5-step method as s446/s448/s449:
1. Raw regen (delete `RecompiledFuncs/funcs_*.c` -> `make_elf.py` -> `N64Recomp`, NO fixup yet) to
   get a pristine tree. `scratch/agent/s449_delete_funcs.sh`/`s449_run_make_elf.sh`/
   `s449_run_n64recomp.sh` are ready templates — copy to `s450_*`, update log/rc paths, or reuse
   directly if no other regen has happened since (check file mtimes first).
2. Standalone Python scan checking each of the ~30 named G-sites' exact anchor text for
   tree-wide uniqueness (model: `scratch/agent/s448_scan_s390h2.py`). **Old fixup-script comment
   warns some G-family anchors "ALSO appear verbatim in `funcs_27.c`"** — needs a FULL recheck
   across all ~32 sites this session, not a sample. If any site is non-unique, hand-disambiguate
   (longer anchor context) rather than force-matching.
3. Check the s448-style extra wrinkles: does `updateHangarBayScene` (now `funcs_28.c`) share
   guest addresses with overlay-duplicated code in the same file? Does its bail label collide by
   name with anything else in `funcs_28.c`, and if so is the collision function-scoped-safe (same
   check as s448's `L_800AB618` collision)?
4. Ungate + add the `SystemExit`-on-`n>1` hard guard (s446/s448 pattern).
5. Full regen -> build -> audit fixup report for exactly `x1` per applied site -> `strings` on the
   binary -> live-verify with `ROGUESQ_LOG_HANGAR_BAY_DEREF_GUARD` armed alongside every other
   guard-family env var (see `scratch/agent/soak_queue/done/s448_s390h2_confirm_*.sh` for the full
   armed-var list to copy) -> queue a confirmation soak. **Expected result per s449: 0 fires is
   the baseline now, not an open question — do not spend another session chasing "why 0."**

After G1-G32, remaining families in order (see `docs/CURRENT-TRUTH.md` item -284 for detail):
1. **`S392_H3A`/`S393_H3B`** (50 sites) — chunk 3a's 29 sites may already be covered by
   `GENERIC_CACHE_GUARD`'s blanket fix; check for redundancy before re-adding (chunk 3b's 21
   likely does need the fix).
2. `BREADCRUMB7` (diagnostic, lowest priority).

If G1-G32 (or the whole remaining orphan-sweep list) starts feeling like diminishing returns
relative to session cost, it's legitimate to instead open a genuinely NEW M3 idiom-class audit
(strategic priority #3's other sanctioned mode) — e.g. a fresh frequency-scan the way s282/s445
opened `GETDATITEM_GUARD`, rather than continuing to finish this specific closed-ambiguity family.

## Discriminating measurement

Does the full ~32-site uniqueness scan come back 100% unique (proceed with s446/s448's method) or
does it surface a genuine collision, confirming the old fixup comment's "also in funcs_27.c"
warning is still live (needs manual disambiguation)?

## Process notes carried forward

- `tools/probe.sh`'s exit code is trustworthy on its own now (exit 3 on a detected `[CRASH]`, s447).
- `fixup_game_funcs.py` lives in the sibling `N64Recomp` repo (`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`), NOT in this repo — it is not git-tracked by RogueSquadron64Recomp and needs no `export.sh`.
- When ungating a ~30-site family, expect SOME sites to be redundant no-ops against earlier-applied
  guards in the same fixup script — not a bug, don't force-match shortened anchors to avoid it.
- Watch for DOUBLY-orphaned gates (file AND function-name-regex referencing the dead old
  `static_N_0xADDR` name) — G1-G32 is the first confirmed instance.
- **New pattern from s449**: when a guard family's confirm soak logs 0 trips, that alone no longer
  needs a fresh positive-control round for THIS class of `-0x25A4`-style deref guard — s449
  established the baseline (0 trips under 245000+ reaches) for the sibling families. A future
  0-fires result on `G1`-`G32`/`S392`/`S393` should be read as "consistent with the established
  baseline," not "inconclusive, needs another soak."
