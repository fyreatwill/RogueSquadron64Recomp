# NEXT work unit

HYPOTHESIS-ID: static5-rename-orphan-sweep

## What changed session s448

Folded in the queued `s447_hangarlist_getdatitem_confirm` soak (read-list #3): it crashed (`rc=3`,
`probe.sh`'s own s447 fix correctly firing) on a recurrence of the already-catalogued 9th crash
class (`updateAnimatedTextureStreaming` SIGBUS, s89/s124/s127) — filed, not chased (strategic
priority #3, unrelated to items -282/-284's target families). Confirmed that crash class's own
guards are NOT orphaned (function genuinely still lives in `funcs_11.c` post-s427). Items -282/-284
remain at 0/0 fires, still unconfirmed either way.

Executed this session's planned work unit: ungated `S390_H2A`/`S390_H2B` (11 sites, item -286),
same proven method as s446/item -284. 4 sites (`S390_H2B_1`-`_4`) actually applied; 7 correctly
no-op as redundant with already-active s284/s285 guards. Regen/build clean, live-verify clean (0
crash, 0 new-guard fires, no positive control yet). Confirmation soak queued:
`scratch/agent/soak_queue/s448_s390h2_confirm.sh` — fold its result in first (read list #3) before
starting new work.

Full detail: `docs/CURRENT-TRUTH.md` item -286, `PORTING-STATE.md` Session 448.

## This session's work unit: the `G1`-`G32` family (item -284's next remaining orphaned family)

Same proven method as s446/s448, applied to the largest remaining family — but this one has an
EXTRA wrinkle s390 didn't: **its gate is doubly-orphaned, not singly.**

`fixup_game_funcs.py` ~line 2837-2846 (search `_hangarbay_deref_guard_sites` and the `if p.name ==
"funcs_40.c":` block right after it): the whole G1-G32 block is gated BOTH on `p.name ==
"funcs_40.c"` (file, same orphaning as every other family in this saga) **AND** on a regex that
locates the function by its dead old name: `r"RECOMP_FUNC void static_5_800AB658\(uint8_t\*
rdram, recomp_context\* ctx\) \{\n"`. `static_5_800AB658` was renamed to `updateHangarBayScene` by
s427 and moved to `funcs_28.c` — since the regex searches for the OLD name, `func_start_m` never
matches regardless of the file gate, so **this entire 32-site family currently produces ZERO
guards**, silently, with no report line at all (the whole `if func_start_m:` body never executes,
unlike s390's `SKIPPED x0` lines which at least appear in the report). Confirm this null-report
behavior first (grep the fixup log for "G1"/"G32" — expect literally nothing, not even a SKIPPED
line) before starting, to make sure the diagnosis is right.

Fix needs BOTH: (1) drop the `p.name == "funcs_40.c"` file gate (or replace with `funcs_28.c` if
you want to keep file-scoping as a sanity floor — check whether `updateHangarBayScene` might ALSO
appear textually in another file the way `L_800AB618` did for s448, before assuming file-scoping is
safe to drop entirely); (2) update the function-name regex to `updateHangarBayScene`.

Same 5-step method as s446/s448:
1. Raw regen (delete `RecompiledFuncs/funcs_*.c` → `make_elf.py` → `N64Recomp`, NO fixup yet) to
   get a pristine tree. Reuse `scratch/agent/s448_delete_funcs.sh` / `s448_run_make_elf.sh` /
   `s448_run_n64recomp.sh` as templates (copy to `s449_*`, update log/rc paths) — or just re-run the
   s448 ones directly if no other regen has happened since (check file mtimes first).
2. Standalone Python scan (model `scratch/agent/s448_scan_s390h2.py`) checking each of the ~30
   named G-sites' exact anchor text for tree-wide uniqueness. **Old fixup-script comment (item -284's
   own note) warns some G-family anchors "ALSO appear verbatim in `funcs_27.c`"** — this needs a
   FULL recheck across all 30ish sites this session, not the 2/32 (G1/G32) sample s446 did. If any
   site is non-unique, do NOT ungate that one blindly — hand-disambiguate (longer anchor context, or
   leave it gated/skip it and note why).
3. Also check for the s448-style extra wrinkles: does `updateHangarBayScene` (now in `funcs_28.c`)
   share guest addresses with other overlay-duplicated code in the same file the way `0x800AB00C`
   etc. did? Does `L_hangarbay_guard_exit` (the G-family's bail label) collide by name with anything
   else in `funcs_28.c`, and if so is the collision safely function-scoped (same check as s448's
   `L_800AB618` collision) or a real problem?
4. Ungate + add the `SystemExit`-on-`n>1` hard guard (s446/s448 pattern) — this family's existing
   loop structure differs slightly (looks up the function body via `func_start_m`/`next_func_m`
   first, then loops sites within that body slice) — check whether the per-site `re.subn` there
   already handles the >1 case or needs the same explicit guard added.
5. Full regen → build → audit fixup report for exactly `x1` per applied site (expect most/all ~30 to
   actually apply this time, since G1-G32 doesn't have s390's redundancy-with-s284/s285 overlap
   issue as far as currently known — but check for it anyway, don't assume) → `strings` on the binary
   → live-verify with all guard-family env vars armed (`ROGUESQ_LOG_HANGAR_BAY_DEREF_GUARD` for this
   family specifically) → queue a confirmation soak.

After G1-G32, remaining families in order (see `docs/CURRENT-TRUTH.md` item -284 for detail):
1. **`S392_H3A`/`S393_H3B`** (50 sites) — chunk 3a's 29 sites may already be covered by
   `GENERIC_CACHE_GUARD`'s blanket fix; check for redundancy before re-adding (same overlap
   pattern s448 found for 7/11 of the S390 sites — check this FIRST before assuming all 50 need
   fresh guards). Chunk 3b (21 sites) likely does need the fix.
2. `BREADCRUMB7` (diagnostic, lowest priority).

## Discriminating measurement

Does the full ~30-site uniqueness scan come back 100% unique (proceed with s446/s448's method) or
does it surface a genuine collision, confirming the old fixup comment's "also in funcs_27.c"
warning is still live (needs manual disambiguation, not blind ungating)?

## Process notes carried forward

- `tools/probe.sh`'s exit code is trustworthy on its own now (exit 3 on a detected `[CRASH]`, s447).
- When ungating a ~30-site family, expect SOME sites to be redundant no-ops against earlier-applied
  guards in the same fixup script (s448 found 7/11 for S390) — this is not a bug, don't force them
  through by shortening anchors to make them "match"; that would just double-guard the same
  dereference pointlessly and add noise.
- Watch for DOUBLY-orphaned gates (both file AND function-name-regex referencing the dead old
  `static_N_0xADDR` name) — G1-G32 is the first confirmed instance; grep any other still-gated
  family's block for a `RECOMP_FUNC void static_5_...` regex before assuming a simple file-gate
  removal is sufficient.
