# NEXT work unit

HYPOTHESIS-ID: item-317-step3-183-site-blanket-sweep

## s494 built and positive-controlled the step-3 tracer -- do NOT rebuild it, audit + use it

`scratch/agent/s494_item317_step3_tracer.py` is done and passes its positive control (2 synthetic
repros of the already-fixed sites' exact pre-fix shapes, PLUS a reclassification check against the
REAL regenerated post-fix `funcs_4.c` that correctly calls the now-fixed `buildOrientedFaceGeometry`
site SAFE). Run `python3 scratch/agent/s494_item317_step3_tracer.py --selftest` first to reconfirm it
still passes (should take <1s, no game run needed) before trusting anything below.

Raw scan (`scratch/agent/s494_item317_step3_report.json`, re-run via `--scan` if you regen
`funcs_3.c`/`funcs_4.c` in between): 448 total `0X63B0` reload sites (not the ~183 estimate that was
in this file before s494 -- that number predated a full regex census), 393 flagged `NEEDS_GUARD`, 55
`SAFE_NO_DEREF`. **Deduped by actual downstream dereference location** (not by reload site) this
collapses to **~150-160 distinct (file, line, register, offset) candidate guard placements across 30
functions** -- the real actionable target size, ranked by how many reload sites share each location
(top: `funcs_4.c:18192`, 48 sites converging on one unguarded `MEM_W(0X4, ctx->r2)` write -- the exact
`DL_LIST_APPEND`/`CACHE_HEAD_A1` idiom shape items -291/-316 already partially fixed elsewhere).

**Known tool limitation, must be resolved before bulk-applying anything**: the tracer only recognizes
ONE taint-clearing guard shape (`uint32_t x = U32(ctx->rN); if (x<0x80000000u||x>=0x80800000u)`,
matching both step-1/step-2 fixes). Confirmed it ALSO correctly handles the different-shaped
`NODE_LIST_HEAD_GUARD` if/else-with-fallback-zero pattern (both branches are plain `ctx->rN=...`
assignments the generic transfer function already tracks) -- but it has NOT been audited against every
other existing guard family (`SIBLING_PTR_WRITE_GUARD`, `DL_BUFFER_POOL_GUARD`,
`TEXDATA_TABLE_GUARD`, etc.), each hand-written with its own code shape. Any location the tool flags
could be a false positive if it uses a guard shape the tool doesn't recognize.

## This session's work unit, two sub-steps in order

**Step A -- audit before trusting at scale (do this first, it's cheap).** Pick 5-8 of the ~150
distinct hit locations (mix: a few from the top-shared list, a few singletons) and manually read 20-30
lines of surrounding context around each with `sed`/`Read` to confirm: (a) is the flagged register
genuinely undefended right up to the dereference, or (b) does an existing guard family the tool doesn't
recognize already clear it? Log a verdict per sampled location. If the false-positive rate in this
sample is high (>1-2 of 5-8), the tool needs another guard-shape-recognition pass before step B --
treat that as its own sub-work-unit, don't guess a fix on top of an unaudited tool.

**Step B -- fix the highest-confidence, highest-shared-count location(s).** One concrete lead already
spotted and worth checking FIRST: `funcs_4.c:5030` (`MEM_W(0X0, ctx->r4) = ctx->r3;`, 35 shared reload
sites, sits 3 lines after the existing `NODE_LIST_HEAD_GUARD` block which validates `ctx->r2`/sets
`ctx->r3`'s fallback but never touches `ctx->r4` -- the register this specific write actually
dereferences). If step A confirms it's real, follow the established fix pattern from steps 1/2: guard
the register actually dereferenced (`ctx->r4`), not an upstream proxy, block-skip to a safe landing
label, live-verify with a same-run positive control before queueing a 2nd confirm.

**Do NOT attempt all ~150 locations in one pass.** Fix the highest-shared-count, audit-confirmed
locations first (each fix likely closes many of the 393 raw reload-site flags at once, same as how
NODE_LIST_HEAD_GUARD's original 30-site fix collapsed a much larger raw count). Re-run `--scan` after
each fix to see the flagged count actually drop -- that's the tool's own regression/progress signal,
free (no game run needed).

**Fallback if step A finds the tool needs more guard-shape work**: extend
`transfer()`'s `range_check_var`/`range_check_bound` handling in the tracer script to recognize
additional guard code shapes found during the audit, re-run `--selftest` (must still pass), then
re-scan.

## Regen/build/soak recipe (only needed once step B produces an actual code change)
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
→ `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp
&& ./build/N64Recomp rogue_squadron.toml` → `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(check the report for expected counts, no errors, no SKIPPED lines other than the known-permanent
S392_H3A/H3B item -290 remainder; the script REFUSES a second run on already-patched files via its own
`RS64_FIXUP_APPLIED` marker — regenerate from scratch if you need to re-run it) → **`cd
/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`** (NOT `~/Documents/Tools/N64Recomp/build`
— that's the recompiler CLI's own build and silently no-ops) →
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`. Arm every sibling guard
env var per the standing rule. Live-verify BEFORE queueing a 2nd confirm and BEFORE folding into the
ledger.

## M5 lead-check
Cleared s494 (no new lead; sessions 489-493 were entirely the item -316/-317 lineage, unrelated to
audio). Due again once 3+ sessions have passed from s494, i.e. s498+.

## Soak queue status
Empty.
