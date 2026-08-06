# NEXT work unit

## s394 recap

Fixed the TOP-priority item from s393's NEXT.md: all 29 of s392's chunk-3a `_s392_h3a_sites` guards
(`hangarInitialize`, `funcs_27.c`) had their anchor built starting WITH the raw `-0x25A4($sN)` load's own
line, so the guard was spliced in BEFORE that load ran and checked a stale register instead of the
freshly-loaded pointer. Wrote a fresh Python extraction/verification script (parsed the live
`_s392_h3a_sites` table via `ast.literal_eval`, located each site's raw load in the current `funcs_27.c`
by its own marker comment, scanned forward for the first genuine `MEM_*` dereference — or, for one site
(`S392_H3A_26`) whose load feeds a shared control-flow join with no in-line dereference, scanned through
the `goto` line instead) and rewrote all 29 tuples in place (Option A, same site names/`reg`/`bail_label`,
only anchor text changed). Verified: regen diff shows ONLY `funcs_27.c` changed, 58 removed / 58 added
(net zero — a pure placement fix, not new coverage). Build clean. 3 soaks: verify1 (armed with
`ROGUESQ_LOG_S392_H3A_GUARD=1`) hit an already-catalogued unrelated crash
(`trackResourceListWithMappingTables+1228`) but **`[s392-h3a-guard]` fired 0 times** with a same-run
positive control (824 `[hangar-loop]` lines, hangar/craft-select scene actively held) confirming the fix
works as expected; verify2 (unarmed) hit an unrelated crash (`allocateDisplayListBuffer+880`, traced to
`funcs_4.c`); verify3 (unarmed) fully clean, 0 crashes. Full detail: `PORTING-STATE` Session 394;
`docs/CURRENT-TRUTH.md` item -244 (item -243 marked FIXED).

Also ran (did not act on) a rough Step-5 sweep count: `funcs_27.c` has 102 raw `-0x25A4` hits vs 89
existing guard markers (~13 possibly still unguarded); `funcs_40.c` has 69 raw hits vs 67 markers (~2
possibly unguarded); `funcs_19.c` has 1 unrelated raw hit (loads directly into a float register, not
part of this idiom family). These are RAW grep counts only — no per-site classification (genuinely
unguarded vs. already covered by a differently-shaped guard vs. confirmed-SAFE call-arg-only) was done.

## This iteration's work unit: classify and guard the Step-5 sweep remainder

The guard-placement correctness bug (item -243) is now closed. The deferred "sweep the rest of
`funcs_27.c`/`RecompiledFuncs/*.c` for unguarded `-0x25A4` sites outside the already-audited chunks" plan
from chunk 3b's own completion is now meaningful (before s394's fix, counting chunk 3a's sites as
"covered" would have been misleading — they weren't actually validating anything).

### Step 1 — get an accurate per-site count in `funcs_27.c` (hangarInitialize)

s394's raw count (102 hits, 89 markers, ~13 unaccounted) is NOT a reliable "sites needing a guard" count
— a single guard block can sit near multiple raw loads, and some raw loads may already be covered by an
existing guard's downstream reach even without a 1:1 marker. Write a script that:
1. Finds every raw `MEM_W(ctx->r\d+, -0X25A4)` occurrence in the current `funcs_27.c` with its line
   number and preceding/following context (~10 lines each side).
2. For each, checks whether it already sits immediately after a `{ // PATCH: unguarded -0x25A4 ... }`
   guard block (already covered — skip) or not (candidate for a NEW site).
3. For each NEW candidate, classify the same way every prior chunk did: does the loaded register feed an
   `ADD32`/`SUB32` combine (or get used directly) that reaches a genuine `MEM_*` dereference before any
   intervening call/return/branch that would make it moot? If yes: NEEDS-GUARD. If it's only ever passed
   as a call argument and never dereferenced in this function: confirmed SAFE (matching the precedent
   from s392's own 3 SAFE sites).

Recommended: delegate this classification pass to a subagent if the candidate count is large (matching
the precedent set by s392's own delegation for a similar-sized batch), keeping this session's own budget
for the guard-writing + regen + verify cycle.

### Step 2 — same for `funcs_40.c` (the `updateHangarBayScene`/`static_5_800A9270` family)

69 raw hits vs 67 existing markers (`G1`-`G32`, `HANGARLIST_GUARD*`, `S284_*`, `S285_A9270_R4` etc. —
see `fixup_game_funcs.py` around line 5225+ and the G1-G32 site list). Same classify-then-guard approach;
this file's existing guard families are numerous and may already close more of the gap than the raw
count suggests — check carefully before assuming ~2 new sites are needed.

### Step 3 — `funcs_19.c`'s 1 outlier

Single raw hit, loads directly into `ctx->f28.u32l` (a float register) rather than following the
`$sN`-base-pointer-then-ADD32-combine idiom this whole audit has targeted. Check whether it's actually
part of the same hangar-list-pointer family (unlikely, given the float destination) or an unrelated
`-0x25A4`-offset load that happens to share the same displacement by coincidence — do not assume it's in
scope without checking the surrounding function's identity and purpose first.

### Step 4 — apply guards + verify

Same protocol as every prior chunk: build anchors starting AFTER the raw load (through the first genuine
`MEM_*` dereference — apply s394's now-corrected discipline from the start this time, no risk of
repeating the chunk-3a mistake), verify uniqueness, `shutil.copytree` backup, delete all `funcs_*.c`,
regen (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py`), diff (expect ONLY the touched files to
change, by an amount matching new ADDITIONS this time, not a placement fix), build clean, 3 sequential
soaks (`HOLD_S=280`, `run_s327waitpump.sh`, one at a time via backgrounded `Bash` polled directly — do
NOT rely on passive notification-only waiting for background game-process tasks; poll the run.log/output
file at intervals, per this session's own lesson). Check `last-guest-pc`/`pc-symbol` on any crash against
BOTH `hangarInitialize`'s range (`0x800AA6D8`-`0x800AE084`, `funcs_27.c`) AND `funcs_40.c`'s hangar
functions before treating it as unrelated.

## Iteration budget

HYPOTHESIS-ID: m3-idiom-audit-fresh (unchanged — this is the natural continuation of the same audit
thread; s389, s390, s392, s393, s394 are all under it, this makes iteration 7). If loop.sh's rule-8
counter forces a pivot preamble, note that s394's guard-placement fix landing IS itself a legitimate,
complete close of the chunk-3a defect (not a repeat of prior work) — the same reasoning s393 and s394's
own NEXT.md predecessors used.

## Process lesson from s394 (apply this session)

Background game-process soaks (`Bash` `run_in_background: true`) do NOT reliably deliver a
"task complete" notification while your turn is idle/ended — poll the soak's `run.log` (or the
background task's own output file) directly at intervals using short, individual `Bash` calls (or a
`python3 -c "import time; time.sleep(N)"` loop for waiting, since raw shell `sleep` beyond a few seconds
is blocked by this session's sandbox policy) rather than assuming a notification will arrive on its own.
Only conclude/end a turn once the soak's actual completion marker (`--- done ---` in the log, or the
driver's own `--- summary ---` block) has been directly observed via `Read`/`grep`.
