# NEXT work unit

## s392 recap

Continued the M3 idiom-class-audit strategic-priority item (fresh work mode opened s389, chunk 2 done
s390). s390 left 53 raw `-0X25A4` hits unguarded in `hangarInitialize` past chunk 2b's exit label
`L_800AB618` (line 125940) through the function's own end (line 133742). Both boundary line numbers
matched NEXT.md's pre-session numbers exactly (no drift). Found the function's remaining internal
`return;` statements are sparse (only at lines 125976, 132777, 133738) — split the 53-site remainder at
the 132777 `return;`: chunk 3a (lines 125940-132777, 32 raw hits) this session, chunk 3b (21 hits,
132777-133742) next.

Delegated classification of chunk 3a's 32 sites to a subagent (self-contained prompt with the exact
NEEDS-GUARD/SAFE criteria and a uniqueness-check instruction). Result: 29 NEEDS-GUARD, 3 SAFE (call-arg
only, never dereferenced: guest addrs 0x800ACA7C, 0x800ACF54, 0x800ACF98). Did NOT hand-transcribe the
agent's anchor text into the patch — re-extracted every anchor programmatically from the live source
using the agent-reported guest-address pairs as slice boundaries, then verified uniqueness with Python
`str.count()` before writing any patch code (avoids the transcription-error risk of retyping 29 multi-line
blocks by hand). Bail target: reused existing label `L_800ADB2C` (a live `goto` target from within the
sub-block already, though it runs a few more real calls before returning rather than sitting immediately
pre-return like chunk 2's bail labels — still an already-exercised normal-flow path).

Verified: byte-identical-except-intended-diff regen (only `funcs_27.c`, 377 added / 0 removed lines = 13
lines × 29 guards); build clean; 3 sequential soaks (`HOLD_S=280`,
`scratch/s73_post_a_scene/run_s327waitpump.sh`) — 1 fully clean 280s hold (0 crashes, title reached,
`[keys]` confirmed driven), 2 hit already-catalogued unrelated crash families
(`coalesceFreeHeapBlocks+4424` = closed s354-366 Thread A heap-coalesce guard; `submitSceneNodeRender+27524`,
suspiciously large symbol offset, likely a nearest-symbol misattribution) — neither in `funcs_27.c`, 0
fires attributable to the new guards. Full detail: `PORTING-STATE.md` Session 392; `docs/CURRENT-TRUTH.md`
item -241.

## This iteration's work unit: `hangarInitialize` chunk 3b (finish the class — this is the LAST chunk)

Per the standing strategic-priority order, continue the M3 idiom-class audit. **Do NOT pick a new idiom
class this iteration** — chunk 3b is small (21 sites) and finishes off `hangarInitialize`'s entire
`-0x25A4` coverage in this one function. Once chunk 3b lands, sweep the REST of the codebase (outside
`hangarInitialize`) for any remaining raw `-0x25A4` hits before declaring the whole idiom class closed —
s283-285's original audit only ever fully covered `hangarInitialize` plus the earlier
`HANGARLIST_GUARD`/`HANGARLIST_GUARD_EARLY/WALK/CLEAR` sites; whether other functions share this idiom is
unconfirmed.

### Step 1 — re-confirm current boundaries fresh (line numbers below are PRE-this-session; re-derive)

In `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`:
- Chunk 3a's own guard insertions push line numbers down by 377 lines past its own insertion range.
  Re-find the boundary via content, not raw line arithmetic: `grep -n "^L_800ADB2C:" funcs_27.c` (was
  132733 pre-session; chunk 3a's own guards inserted BEFORE this point in the file will have shifted it
  down by up to 377 lines depending how many guards land before it — recompute fresh).
- The function's own closing boundary is the next `RECOMP_FUNC` after `hangarInitialize`'s start —
  confirm via `grep -n "^RECOMP_FUNC" funcs_27.c` and take the first hit past `hangarInitialize`'s own
  start line (was 119818 pre-session s390, will also have shifted down by 377).
- The natural chunk-3a/3b split point (was line 132777 pre-session, a `return;` statement) will also have
  shifted down by 377 lines from chunk 3a's own insertions. Confirm via
  `grep -n "return;" funcs_27.c` restricted to the shifted range, cross-check against the `L_800ADB2C`
  label position (3a's bail target sits just before this same `return;`).
- Re-confirm the raw hit count in the new chunk-3b span: `awk 'NR>X && NR<Y && /0X25A4/' funcs_27.c |
  wc -l` should print **21** (X = shifted chunk-3a/3b split point, Y = shifted function end). If it
  doesn't print 21, the shift arithmetic is off — recompute X/Y from the grep hits above, don't guess.

### Step 2 — classify and patch, same model as s390/s392

21 sites is small enough to classify directly (no subagent delegation needed, matching s390's own
"read directly if ≤10" guidance loosely — 21 is a bit over that, use judgment: either delegate the same
subagent-classification pattern used s392, or do it directly if context budget allows). For each
`-0X25A4` reload in range: NEEDS-GUARD if immediately (or after ADD32/shift arithmetic) dereferenced via
`MEM_W`/`MEM_H`/`MEM_HU`/`MEM_B`/`MEM_BU`/`LD` with no prior check; SAFE if only compared/passed as a call
argument. **Lesson from s392**: don't hand-transcribe anchor text from an agent's markdown report — use
the agent's reported guest-address pairs (start/end of each site) to programmatically re-extract exact
anchor text from the live source file via Python slicing, then verify each anchor is a unique substring
with `str.count()` before writing the patch. This is faster AND safer than manual transcription for >5
multi-line anchors.

Guard template (same KSEG0-range check every prior chunk used, `0x80000000..0x80800000` on the raw
just-reloaded register): see `fixup_game_funcs.py`'s `_s392_h3a_guard_text`/`_s392_h3a_sites` as the
format reference (search for `S392_H3A_1`). Name this chunk's site IDs `S392_H3B_N` (or bump the session
prefix if this lands in a session other than s393). Look for an existing nearby epilogue/exit label to
reuse as the bail target before considering inserting a new one — check reachability with `grep -n "goto
L_<candidate>"` restricted to within the chunk-3b span (same discipline as chunk 3a's `L_800ADB2C`
verification).

### Step 3 — verify

Same protocol every session since s377: Python `shutil.copytree` backup (place it OUTSIDE
`RecompiledFuncs/` and delete it after diffing — don't leave stray `RecompiledFuncs_*_backup` dirs lying
around in the N64Recomp repo root, clean up after yourself), delete `funcs_*.c`, regen via `N64Recomp` +
updated `fixup_game_funcs.py`, `filecmp`/diff the full tree against the backup (expect ONLY `funcs_27.c`
to differ, and only by the intended guard insertions — confirm added-line-count = 13 × site-count, 0
removed lines), build, 3 soaks (`HOLD_S=280`,
`zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, run SEQUENTIALLY not in parallel — "one game
run at a time" — each via `Bash` with `run_in_background: true`, wait for the task-completion
notification or poll `TaskOutput` with `block: true`, do NOT try to background via shell `&`). New guard
fire-counts are expected to be 0 (proactive fix, matching every guard in this family so far — the
`ROGUESQ_LOG_S39x_...` diagnostic isn't armed by `run_s327waitpump.sh`, so don't expect to see fire-count
lines in the log even on a clean pass; check crash-absence and `last-guest-pc`/`pc-symbol` attribution
instead, per the s344 crash-signature-blindness lesson — any crash that DOES appear must be checked
against `hangarInitialize`'s own address range (0x800AA... - 0x800AD...ish, funcs_27.c) before treating it
as a regression; a hit elsewhere in the ~20+ already-catalogued crash families is not evidence against
this session's guards).

### After chunk 3b lands: close the class or open chunk 4

If chunk 3b's `awk` count for `-0X25A4` in the remaining span (past chunk 3b's own end through
`hangarInitialize`'s function boundary) comes back 0, the WHOLE function is covered — do a final
whole-function sanity check (`awk` over the entire `hangarInitialize` body, all chunks combined, expect
raw hits == guard count) and then grep the REST of `funcs_27.c` and the rest of `RecompiledFuncs/*.c` for
any other unguarded `-0X25A4` sites outside `hangarInitialize` before declaring the class fully closed —
s283-285's original candidate list was function-scoped to a few specific functions, not a whole-codebase
sweep.

## Iteration budget

HYPOTHESIS-ID: m3-idiom-audit-fresh (unchanged — the slug tracks the audit MODE, not a single class; s389,
s390, and s392 (s391 was a maintenance detour that didn't touch this plan) are all real work under it, the
last two on the SAME idiom class (`hangarInitialize`'s `-0x25A4` family), continued across sessions —
expected and matches how s283-288's original `-0x25A4` audit and the s377-386 backport both spanned many
sessions under one slug. If loop.sh's rule-8 counter forces a pivot preamble next session (its count is
mechanical and may include s391 despite the maintenance detour — see `tools/agent/loop.sh` around
"rule-8 enforcement"), that's expected and should be honored: reassess whether `hangarInitialize`'s
`-0x25A4` coverage is close enough to done to count as one closed investigation (chunk 3b would finish the
function), which is itself a legitimate way to satisfy a forced pivot without abandoning real progress.
