# NEXT work unit

HYPOTHESIS-ID: item-314-loop-scoped-audio-voice-guard

## s486 summary: MAINTENANCE iteration (Step 0 triggered), plus one soak result folded in

`docs/CURRENT-TRUTH.md` was 62,202 bytes at session start (over the 60,000-byte Step 0 trigger). Per
`tools/agent/ITERATION.md` this was a maintenance-only iteration — no experiment run. Compacted
CURRENT-TRUTH from 705 lines/62,202 bytes to 497 lines/44,933 bytes (net -208 lines, exceeds the
>=200 threshold for ADVANCED): migrated the full s481-486 narrative (items -312/-313/-314/-315, the
`DL_LIST_APPEND_GUARD`/`DL_LIST_RESET_GUARD`/`AUDIO_SLOT_ACTIVE_GUARD` scope-generalization arc) to a
new `docs/PROJECT-OVERVIEW.md` §20, collapsed the giant USER DIRECTIVE running narrative and the four
standalone item blocks down to short pointers, merged several already-closed Next-steps item ranges
(-261..-290, -231..-249, -230..-14) into single consolidated paragraphs, and deleted one fully-
redundant line ("Sanctioned tooling work unit", superseded by the merged -231..-249 paragraph).

Also folded in the one new soak result that landed since the last commit, per the standing "read
SOAK-RESULTS.md tail first" instruction: `s485_dl_list_reset_rnode_confirm` (item -315's 2nd
independent confirm) came back `rc=3`, 0 fires on `dl-list-reset-rnode-guard` or any sibling guard —
the crash was a host-side event (`last-guest-pc=0x800ab0e0`, garbage `pc-symbol` offset because the
crashing host PC sits in system/framework code the local-symtab table doesn't cover) that is
byte-identical to item -303's own s472 confirm, already catalogued there as an async Metal.framework
shader-compiler-thread SIGSEGV (same family as items -10/-9). **Item -315 is now FULLY CLOSED, 2/2
independent confirms clean.** All four items opened in the s481-485 arc (-312/-313/-314/-315) are now
fully closed. Full narrative: `docs/PROJECT-OVERVIEW.md` §20.

## This session's next work unit

Per the USER DIRECTIVE's M3 priority: no untried high-expected-value instruction-pattern scan and no
un-investigated high-recurrence breadcrumb remain queued. Two options, in order of preference:

1. **Recommended: item -314's own deferred 6-site loop-scoped-guard follow-up.** `musyxMixActiveVoices`
   (3 sites: 0x80090E78/0x80090EA0/0x80090EBC) and `musyxSynthFrame` (1 site: 0x800913BC) still have
   unguarded `-0x6908` reloads of the `0x801496F8` audio-voice-array-base global (`AUDIO_SLOT_ACTIVE_GUARD`
   lineage), deliberately left unguarded because they sit INSIDE a per-voice loop AFTER earlier
   iterations already did real writes — a plain early-`return` guard (the shape used for the other 9
   sites) would abort processing every remaining voice for the rest of the frame. Needs a loop-scoped
   "skip this iteration, continue" guard shape instead. Read the full loop structure (loop head label,
   increment/condition) in `RecompiledFuncs/funcs_24.c` first (exact line numbers:
   `PORTING-STATE.md` Session 483), then design + apply + soak using the recipe below.

2. **Alternative** (if #1 turns out low-value or the loop shape is awkward to retrofit safely): a
   fresh M3 idiom-class scan from scratch, following the s465/s477 precedent — grep-enumerate every
   `lui`+`lw` global reload across all 50 `funcs_*.c` files not already covered by a named guard, rank
   by frequency, pick the top fresh bucket. Or, since the standing M5-lead-check cadence (every 3+
   sessions, last checked s478) is now overdue, check for a fresh M5 audio-destub lead first.

## Regen/build/soak recipe (same as always)
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('.../N64Recomp/RecompiledFuncs/funcs_*.c')]"`
(glob patterns rejected by the shell directly, use python) → `cd ~/Documents/Tools/rogue_squadron64 &&
python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
→ `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (check the report for the expected
counts, no errors) → `cd build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake
--build . -j8`. Arm every sibling guard env var per the standing rule (passive instruments are free).

## Soak queue status
Empty (`scratch/agent/soak_queue/` has only `cancelled/` and `done/` subdirectories, no pending
recipes) — nothing queued from this maintenance-only session, since no code changed.
