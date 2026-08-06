# NEXT work unit

## s393 recap

Finished `hangarInitialize` chunk 3b (21 sites, the function's own tail, LAST chunk of the planned
audit) — correctly placed, verified, 0 regressions across 3 soaks (each soak did hit a crash, but every
one at an already-catalogued address far outside `hangarInitialize`: `0x8000b650` staleness per
CURRENT-TRUTH item -239, `coalesceFreeHeapBlocks+2016`, `emitAllocatedDLCommand+9632`).

Then, per NEXT.md's own "after chunk 3b lands, sweep the rest before declaring the class closed"
instruction, found something much more important than leftover surface: **all 29 of s392's chunk-3a
guards (previous session) check the WRONG register** — a placement bug, not a new crash. The anchor
text for every one of those 29 sites starts WITH the raw `-0x25A4($s1)` load's own line, and the guard
is spliced in via `text.replace(anchor, guard + anchor, 1)`, i.e. BEFORE that load runs. So every
chunk-3a guard checks whatever was in that register from the PRECEDING instruction — not the freshly-
loaded pointer it's supposed to validate. Two sites traced by hand (`S392_H3A_1`, `S392_H3A_11`) both
had a small byte-index value in that register at check time (set by an `lbu`/`MEM_BU` two lines earlier)
— always fails the KSEG0 bounds check, so those two sites' guards **unconditionally bail every time**,
silently skipping real hangar-item processing instead of protecting against a rare bad pointer. This was
invisible to s392's own soak verification because `ROGUESQ_LOG_S392_H3A_GUARD` was never armed by any
soak recipe — the only way this bug could show up (a live fire-count) was gated behind an env var nobody
set. Full mechanism and the chunk-1/2/3b vs chunk-3a anchor-shape comparison that found it:
`PORTING-STATE` Session 393; `docs/CURRENT-TRUTH.md` item -243.

## This iteration's work unit: fix s392's chunk-3a guard placement (all 29 sites)

This is now the TOP priority — ahead of any new idiom-class chunk or codebase-wide `-0x25A4` sweep,
because it's a correctness regression in already-shipped work, not new uncovered surface. Do NOT start a
"chunk 4" or expand the audit to other functions until this is fixed and verified.

### Step 1 — reconstruct all 29 anchors correctly

In `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, find `_s392_h3a_sites` (search
`_s392_h3a_sites = [`). For EACH of the 29 tuples:

1. Note the site name, `reg`, bail label (`L_800ADB2C` for all of them), and the guest PC address in the
   anchor's first comment line (e.g. `S392_H3A_1` → `0x800AB7D4`).
2. In the CURRENT `funcs_27.c` (post-chunk-3b, so line numbers have shifted — locate by the `0x800ABxxx`
   guest-address comment, not by line number), find that exact raw `-0x25A4($sN)` load. It currently sits
   right after the (buggy) guard block that was spliced in before it — the guard block's own comment says
   `s392, S392_H3A_N`, making each one easy to find via `grep -n "S392_H3A_N\b"`.
3. Build a NEW anchor that starts AFTER the raw load line (matching chunks 1/2/3b's correct model): the
   anchor should begin at whatever instruction combines the just-loaded register into a further address
   (usually an `ADD32`/`SUB32` line), continue through the first genuine `MEM_*` dereference of the
   resulting address (not just further arithmetic — same "scan forward for the real deref" discipline
   chunk 3b's script used), and `reg` should be the register holding the FRESH raw-loaded value at the
   point right before that combine (verify it isn't clobbered between the load and the combine, same check
   chunk 3b's script did).
4. Verify each new anchor is a unique substring of the CURRENT (already chunk-3b-patched) `funcs_27.c` via
   `str.count() == 1` before writing anything.

Recommended approach: reuse/adapt chunk 3b's extraction script (see `PORTING-STATE` Session 393 for the
exact technique — locate raw load, scan forward for the ADD32/SUB32 combine referencing that register,
then scan forward again for the first real dereference of the combine's destination register) rather than
hand-transcribing 29 anchors. This is the same lesson s392/s393 already learned about anchor transcription
risk, just applied to a repair instead of a fresh chunk.

### Step 2 — apply the fix

Two options, pick whichever is cleaner once you see the actual diff shape:
- **Option A (in-place fix):** rewrite the 29 tuples in `_s392_h3a_sites` directly with the corrected
  anchors/regs, keep the site names (`S392_H3A_N`) and function name (`_s392_h3a_guard_text`) unchanged
  so the diff is minimal and git history reads as "fixed," not "replaced."
- **Option B (supersede):** leave `_s392_h3a_sites` as dead/unused (or delete it) and add a new
  `_s393_h3a_fix_sites` table with corrected placement, re-using the same bail label. Only do this if
  Option A's edit turns out messier than a clean replacement (e.g. if the old buggy guard blocks need to
  be REMOVED from the source, not just have new ones added alongside them — check this first, since
  leaving the old always-bailing guards in place AND adding new correct ones would just mean the new ones
  never get reached).

**Important:** the OLD buggy guard blocks are already baked into `funcs_27.c` via the fixup script (they
regenerate every time `fixup_game_funcs.py` runs). Fixing the site table alone regenerates the SAME buggy
placement unless the old anchor-matching logic is actually replaced, not supplemented. Read the existing
`if p.name == "funcs_27.c": for site, reg, bail_label, anchor in _s392_h3a_sites: ...` loop carefully
before choosing Option A or B.

### Step 3 — verify

Same protocol as every prior chunk: `shutil.copytree` backup (place it as a sibling directory inside the
N64Recomp repo root, e.g. `RecompiledFuncs_s394_backup` — `/tmp` is outside this session's allowed
working directories, delete the backup after diffing), delete `funcs_*.c` (all 45 files — glob patterns
and `find -delete` are blocked by the write-tool/sandbox policy; delete via explicit absolute paths in
batches, or check for a working `rm -f` in this session first), regen (`make_elf.py` → `N64Recomp` →
`fixup_game_funcs.py`), diff the regenerated tree against the backup (expect ONLY `funcs_27.c` to differ,
by an amount consistent with 29 guard-block replacements, not additions — the raw byte delta will differ
from prior chunks since this is a fix, not new coverage). Build clean. 3 sequential soaks (`HOLD_S=280`,
`zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, one at a time via background `Bash` +
`TaskOutput block:true`, never parallel). Check `last-guest-pc`/`pc-symbol` on any crash against
`hangarInitialize`'s own range (`0x800AA6D8`-`0x800AE084`, `funcs_27.c`) before treating it as unrelated —
same crash-signature-blindness discipline as every prior chunk.

**Discriminating measurement for this fix specifically:** consider arming
`ROGUESQ_LOG_S392_H3A_GUARD=1` for at least one of the 3 soaks (the recipe doesn't set it by default —
add `export ROGUESQ_LOG_S392_H3A_GUARD=1` to a throwaway copy of the run script, or set it inline before
invoking) to directly observe whether the fixed guards fire 0 times (expected — proactive fix, matching
every other guard in this family) vs. the OLD buggy guards which would have fired constantly. This is the
one soak variable that would have caught the original bug and is worth spending on the fix's own
verification.

### After this lands

Resume the deferred "sweep the rest of `funcs_27.c` and `RecompiledFuncs/*.c` for any other unguarded
`-0x25A4` sites outside `hangarInitialize`" plan from chunk 3b's own completion — NOW it's meaningful,
since before this fix a "0 remaining raw hits" count would have been misleading (it would count chunk 3a's
sites as "covered" when they weren't actually validating anything).

## Iteration budget

HYPOTHESIS-ID: m3-idiom-audit-fresh (unchanged — this fix is still real work under the same audit-mode
slug; s389, s390, s392, s393 are all under it, this makes iteration 6). Loop.sh's rule-8 counter may force
a pivot preamble — if so, the guard-placement fix landing IS a legitimate close of "chunk 3a" as an
investigation (it corrects and completes that chunk's own work), satisfying a forced pivot without
abandoning real progress, same reasoning s393's own NEXT.md used for chunk 3b.
