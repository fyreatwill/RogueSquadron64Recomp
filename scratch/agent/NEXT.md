# NEXT work unit

HYPOTHESIS-ID: maintenance-pass-then-item-314-loop-guard

## Step 0 FIRES NEXT SESSION: docs/CURRENT-TRUTH.md is 62,202 bytes (over the 60,000 trigger)

Per `tools/agent/ITERATION.md` Step 0, the VERY NEXT iteration must run `wc -c <
docs/CURRENT-TRUTH.md` first and, since it's over 60000, treat itself as a MAINTENANCE iteration:
compact CURRENT-TRUTH toward ~35 KB (migrate durable material to `docs/PROJECT-OVERVIEW.md`,
prune/merge superseded and closed items — items -312/-313/-314/-315 are ALL now fully closed 2/2 and
are good candidates to compress into a single terse "DONE" line each once their 2nd confirms land —
renumber if the backlog has drifted), refresh the stale "as of session N" headline, and NOT run any
experiment this pass. A net shrink of >=200 lines counts as ADVANCED.

## s485 summary: item -315 generalization CLOSED (pending 2nd confirm)

`DL_LIST_RESET_RNODE_GUARD` now folds rnode-address validation into ALL 84 `DL_LIST_RESET_GUARD`
sites (70 blanket + 14 per-site), closing the class item -315 opened (its own fix was scoped to
exactly 1 of 84 sites). Audit found 73/84 VULNERABLE-SHAPE (2 confirmed via direct source read),
guarded all 84 uniformly regardless of classification. Build-verified, 1 manual soak ran the FULL
duration with ZERO crash (0 fires on the new guard or any sibling). 2nd independent confirm queued:
`s485_dl_list_reset_rnode_confirm.sh` (in `soak_queue/`, not yet run by the loop as of this write).

Also closed this session (read from the queued soak first, per last session's own instruction):
`s484_audio_voice_baseptr_confirm` came back clean — items -314 and -315 (original scope) are BOTH
2/2 independent confirms clean, fully done.

## This session's next work unit (AFTER the maintenance pass above)

1. Read `scratch/agent/SOAK-RESULTS.md` tail for `s485_dl_list_reset_rnode_confirm`'s verdict. If
   it shows ANY fire on `dl-list-reset-rnode-guard` or a NEW crash inside the guarded region, STOP
   and root-cause it before anything else — it would mean the "guard uniformly, it's a no-op on
   valid pointers" reasoning was wrong somewhere in the 84 sites. If clean (0 fires, crash if any is
   a different already-catalogued family, or no crash at all like the 1st run), item -315 is FULLY
   CLOSED, 2/2, no further action needed on this thread.

2. **Recommended next M3 work unit**: item -314's own remaining 6-site thread —
   `musyxMixActiveVoices` (3 sites: 0x80090E78/0x80090EA0/0x80090EBC) and `musyxSynthFrame` (1 site:
   0x800913BC) still have unguarded `-0x6908` reloads of the `0x801496F8` audio-voice-array-base
   global, deliberately left alone because they sit INSIDE a per-voice loop AFTER earlier iterations
   already did real writes — a plain early-`return` guard (item -314's shape for its other 9 sites)
   would abort processing every remaining voice for the rest of the frame. Needs a loop-scoped "skip
   this iteration, continue" guard shape instead. Read the full loop structure (loop head label,
   increment/condition) in `RecompiledFuncs/funcs_24.c` first, then design + apply + soak using the
   same recipe below.

3. **Alternative** (if #2 turns out low-value or the loop shape is awkward to retrofit safely): a
   fresh M3 idiom-class scan from scratch, following the s465/s477 precedent — grep-enumerate every
   `lui`+`lw` global reload across all 50 `funcs_*.c` files not already covered by a named guard,
   rank by frequency, pick the top fresh bucket. Or, per the standing M5-lead-check cadence (only run
   every 3+ sessions), check for a fresh M5 audio-destub lead if it's been 3+ sessions since the last
   check (s478 was the last one; this makes it due).

## Regen/build/soak recipe (same as always)
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('.../N64Recomp/RecompiledFuncs/funcs_*.c')]"`
(glob patterns rejected by the shell directly, use python) → `cd ~/Documents/Tools/rogue_squadron64 &&
python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
→ `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (check the report for the expected
counts, no errors) → `cd build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake
--build . -j8`. Soak script template: `scratch/agent/soak_queue/done/s485_dl_list_reset_rnode_manual.sh`
(arms every sibling guard env var per the standing rule) -- copy and add any new guard's own
`ROGUESQ_LOG_*` var before running.

## Soak queue status
`s485_dl_list_reset_rnode_confirm.sh` queued (2nd independent confirm for item -315's
generalization). The loop should run it before the next iteration reads this file — check
`scratch/agent/SOAK-RESULTS.md` tail first.
