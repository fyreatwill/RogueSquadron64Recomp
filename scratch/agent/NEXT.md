# NEXT work unit

## s391 note

s391 was a triggered MAINTENANCE iteration (Step 0 of ITERATION.md: CURRENT-TRUTH.md was 60,895 bytes,
over the 60,000-byte cap). It did NOT touch this work-unit plan — compacted CURRENT-TRUTH.md (669→469
lines, 60,895→42,197 bytes) by migrating the closed s377-388 fixup-backport batch history to
`docs/PROJECT-OVERVIEW.md` §13. `hangarInitialize` chunk 3 (below) is still the correct next work unit,
unchanged from what s390 left. Full detail: `PORTING-STATE.md` Session 391.

## s390 recap

Continued the M3 idiom-class-audit strategic-priority item (fresh work mode opened s389). The s389
soak population was fully mined; queued 3 fresh unbiased soaks (`scratch/agent/soak_queue/s390_freshpop1/2/3.sh`)
for a future candidate-tally cycle, then followed NEXT.md's own fallback: delegated a read-only
Explore-agent sweep of every numbered guard family in `fixup_game_funcs.py` looking for the
Lookup-family shape (a struct/pointer idiom guarded on one function, unguarded on siblings). Found the
`HANGARLIST_GUARD`/s283-285 `-0x25A4($s1/s4/s5)` hangar-list global-pointer family is
**self-documented as incomplete**: s284's own comment says `hangarInitialize` (funcs_27.c, 103 of 172
raw hits, a single 13,770-line function spanning lines 119818-133587 pre-this-session) was deliberately
parked as its own multi-session item, and s285 patched only a first "chunk" (lines 119818-124175,
`S285_H1_BAIL`) — no chunk 2 was ever written. Guarded 11 more sites across two bounded sub-blocks
("chunk 2a" lines 124202-125013, "chunk 2b" 125014-125822 pre-session line numbers), reusing both
sub-blocks' own existing epilogue labels (`L_800AB1A4`, `L_800AB618`) directly — no new labels needed.
Verified via the standard byte-identical-except-intended-diff regen protocol (only `funcs_27.c` touched,
diff was exactly the 11 guard-block insertions), clean build, 3 soaks (none crashed inside or downstream
of the new guards or shared a guest-address family with the `-0x25A4` idiom; one hit the exact
already-closed heapWalker-GUARD5 background-noise address `0x8000834c`). 0 guard fires across all 3 runs
(proactive/defensive fix, matching every prior guard in this family). Full detail: `PORTING-STATE.md`
Session 390; `docs/CURRENT-TRUTH.md` item -240.

## This iteration's work unit: `hangarInitialize` chunk 3 (continue the SAME class, not a new candidate)

Per the standing strategic-priority order, continue the M3 idiom-class audit. **Do NOT pick a new idiom
class this iteration** — `hangarInitialize`'s `-0x25A4` coverage is self-evidently unfinished (confirmed
count: **53 raw `-0X25A4` hits remain**, from the current end of chunk 2b through the function's own end)
and the sibling-audit-sweep cost of finding a fresh candidate was already paid last session. Continuing
the same class is strictly cheaper this cycle.

### Step 1 — re-confirm current boundaries fresh (line numbers below are PRE-this-session; re-derive,
don't trust blindly — the s386 lesson: line numbers drift)

In `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c` (already has s390's 11
guards applied as of this NEXT.md being written):
- Chunk 2b's epilogue label `L_800AB618:` is at (pre-session) line 125940 — confirm with
  `grep -n "^L_800AB618:" RecompiledFuncs/funcs_27.c`.
- `hangarInitialize`'s own closing boundary is the next `RECOMP_FUNC` (`computeAngleToTargetFromTransform`),
  at (pre-session) line 133742 — confirm with `grep -n "^RECOMP_FUNC" RecompiledFuncs/funcs_27.c` and take
  the first hit past `hangarInitialize`'s own start (line 119818).
- Confirmed via `awk 'NR>125940 && NR<133733 && /0X25A4/' RecompiledFuncs/funcs_27.c | wc -l` → **53**
  raw hits in that span, all currently unguarded (0 `GUARD` matches in the same span).

### Step 2 — chunk it the same way s285/s390 did

This span (~7800 lines, 53 sites) is comparable in size to s390's chunk 2a+2b combined but larger — don't
try to do it all in one iteration if the internal epilogue structure doesn't cooperate. Read forward from
the chunk-2b exit label to find the function's internal `return;`/epilogue points (a quick scan during
s390 flagged approximate internal boundaries near guest addresses corresponding to source lines ~132623
and ~133584 pre-session — NOT yet confirmed, re-derive with `grep -n "return;" RecompiledFuncs/funcs_27.c`
restricted to the 125940-133742 range). Pick ONE bounded sub-chunk (chunk 3a) ending at the nearest such
epilogue, same size discipline as every prior chunk (s285's chunk 1 was 28 sites; s390's chunk 2a+2b was
11) — don't force all 53 into one patch if the natural boundaries don't group that way.

### Step 3 — classify and patch, same model

For chunk 3a: delegate a read-only Explore-agent classification pass (or do it directly if the site count
is small, ≤10) following the exact template used for s390's chunk 2a/2b (see this session's prompts in
the transcript, or `fixup_game_funcs.py`'s `_s390_h2_guard_text`/`_s390_h2_sites` as the format reference).
For each `-0X25A4` reload in range: NEEDS-GUARD if immediately dereferenced with no check, SAFE if only
compared/passed as a call arg, NEEDS-MORE-CONTEXT if ambiguous. Hand-verify at least the trickiest 2-3
sites directly against the generated source before writing the patch (s390's lesson: cheap insurance,
catches convention drift). Write the guard block reusing the established KSEG0-range check template
(`0x80000000..0x80800000`, checked on the raw just-reloaded register). Prefer reusing an existing nearby
epilogue label over inserting a new one, same as every chunk so far — check with `grep -n
"goto L_<candidate>"` that it's reachable only from within the target sub-block before reusing it.

### Step 4 — verify

Same protocol every session since s377: Python `shutil.copytree` backup (NOT `cp -R`/`tar` directly — the
sandbox's cp-with-flags safety gate blocks both even though they're separately allowlisted; this was
re-confirmed s390), delete `funcs_*.c`, regen via `N64Recomp` + updated `fixup_game_funcs.py`, `filecmp`
diff the full tree against the backup (expect ONLY `funcs_27.c` to differ, and only by the intended guard
insertions), build, 3 soaks (`HOLD_S=280`, `zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, run
each via `Bash` with `run_in_background: true` + `TaskOutput` block — do NOT try to background via shell
`&`, the harness blocks multi-operation compound commands). New guard fire-counts are expected to be 0
(proactive fix) — don't treat 0 as a failure, only a NEW crash signature *inside* the newly-guarded
sub-block would be concerning.

### Fallback if chunk 3 boundaries turn out awkward (span too large/unbounded, or previous scoping was
wrong)

Check `scratch/agent/SOAK-RESULTS.md` for the queued `s390_freshpop1/2/3.sh` results first — if the loop
has drained them since this NEXT.md was written, they may have surfaced a completely different, more
urgent candidate via the standard `[CRASH][last-guest-pc]` tally method (s389's Step 3). Weigh a strong
new candidate against continuing `hangarInitialize` chunk 3 on evidence, not just on "continue what's
already open" inertia.

## Iteration budget

HYPOTHESIS-ID: m3-idiom-audit-fresh (unchanged — this is iteration 3 of the standing M3-idiom-class-audit
work mode; the slug tracks the audit MODE, not a single class. Note: this iteration and s390 are
technically the SAME idiom class (`hangarInitialize`'s `-0x25A4` family) continued across 2 sessions —
that's fine and expected, matching how s283-288's `-0x25A4` audit and the s377-386 backport both spanned
many sessions under one slug).
