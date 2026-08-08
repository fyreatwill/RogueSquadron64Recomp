# NEXT work unit

HYPOTHESIS-ID: item-315-dl-list-reset-guard-rnode-recurrence

## s484 summary: FIXED item -314 (10 guards, 14/20 sites) AND item -315 (found live via item -314's
own confirm soak crashing on a brand-new bug). Both build-verified, 2 soaks clean at both targets,
2nd independent confirm queued (`s484_audio_voice_baseptr_confirm.sh`, in `soak_queue/`).

**Item -314**: guarded the FIRST `-0x6908` reload (global `0x801496F8`) in each of 9 MusyX voice
functions with an `isAudioSlotActive`-style early `return` (10 site anchors, since
`musyxSetVoicePitchBend` needs one per mutually-exclusive branch) -- this transitively protects
every LATER reload of the same never-rewritten-mid-call global in the same function, covering
14 of the 20 unguarded sites found by s483's audit. Deliberately did NOT cover `musyxMixActiveVoices`
(3 sites) or `musyxSynthFrame` (1 site): both sit inside a per-voice loop AFTER earlier iterations
already did real writes, so an early return would abort processing every remaining voice for the
rest of the frame -- needs a loop-scoped "skip this iteration, continue" guard shape, not designed
this session. This is the one remaining open item -314 thread.

**Item -315** (found this session, NOT anticipated going in): the 1st confirm soak for item -314's
fix crashed with `si_addr=0x380000000`/`pc-symbol=submitSceneNodeRender+38556`/
`last-guest-pc=0x80010880` -- a NEW guest PC (grepped `PORTING-STATE.md`, 0 prior hits) that pattern-
matched the `BREADCRUMB6` "near-zero guest pointer" family by `si_addr` alone but needed its own
root-cause read. Found: `DL_LIST_RESET_GUARD` (item -298, s463's blanket 84-site patch) validates
register `r2` (reloaded from global `0x8011A7DC`) before its own guarded write, but at THIS site
(`submitSceneNodeRender`, 0x80010880) the write ACTUALLY goes through a DIFFERENT register, `r4` --
which is itself an earlier, completely unguarded reload of `0x801163B0` (the SAME global
`GENERIC_CACHE_GUARD` already protects, via yet another register). `DL_LIST_RESET_GUARD`'s own
design comment ("rnode is a normal argument register, not derived from G") is wrong for this
instance -- same meta-bug shape as item -312/-313's `DL_LIST_APPEND_GUARD_RWRITE` finding. Fixed
with a site-anchored guard (`S315_RESET_R4_GUARD`) on just this one site; did NOT audit whether the
same rnode-aliasing recurs across `DL_LIST_RESET_GUARD`'s other 83 sites.

## This session's top work unit: pick ONE of the two open threads (whichever the queued confirm's
result favors -- read it first)

1. Read `scratch/agent/SOAK-RESULTS.md` tail for the `s484_audio_voice_baseptr_confirm` verdict (the
   loop should have run it between iterations). If it shows a NEW crash inside item -314's or item
   -315's guarded code (fires > 0 on `audio-voice-baseptr-guard` or `s315-reset-r4-guard`), STOP and
   root-cause that first -- it means one of this session's "proven safe" claims was wrong. If it's
   clean (0 fires, matches the established true-negative baseline, crash if any is a different
   already-catalogued family), both items are confirmed 2/2 and open for follow-up work as below.

2. **Recommended next work unit** (matches the proven-productive item -313 playbook exactly): write
   a scoped Python static-analysis script (like `N64Recomp/scratch_s482/audit_dl_list_append_rwrite*.py`,
   untracked, same repo) that walks all 84 `DL_LIST_RESET_GUARD` sites in `funcs_3.c`/`funcs_4.c` and
   checks, for each site's "rnode" register, whether it is ITSELF fed by an earlier unguarded reload
   of `0x801163B0` (the `GENERIC_CACHE_GUARD` global) within the same function, the same aliasing
   item -315 found at exactly one site (`submitSceneNodeRender`, 0x80010880). If the same shape
   recurs at many sites (item -313's precedent: 78/84), generalize `S315_RESET_R4_GUARD` into a
   blanket fix inside `_dl_list_reset_guard_patch` itself (fold rnode validation into EVERY site,
   mirroring how item -313 folded rwrite validation into `_dl_list_append_guard_patch`). If it's
   genuinely rare/unique to this one site, document that and close item -315 as fully scoped.

3. **Alternative work unit** (lower priority, pick only if #2 turns out low-value): design the
   loop-scoped "skip this iteration, continue" guard shape for item -314's remaining 6 sites
   (`musyxMixActiveVoices` x3 at 0x80090E78/0x80090EA0/0x80090EBC, `musyxSynthFrame` x1 at
   0x800913BC). Read the full loop structure (loop head label, increment/condition) in
   `RecompiledFuncs/funcs_24.c` first -- these sites need a `goto` to the loop's own continue-point,
   not a whole-function early return.

## Regen/build/soak recipe (same as always)
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('.../N64Recomp/RecompiledFuncs/funcs_*.c')]"`
(glob patterns rejected by the shell directly, use python) → `cd ~/Documents/Tools/rogue_squadron64 &&
python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
→ `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (check the report for the expected `xN`
count, no errors) → `cd build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake
--build . -j8`. Soak script template: `scratch/agent/soak_queue/done/s484_audio_voice_baseptr_manual.sh`
(arms every sibling guard env var per the standing rule) -- copy and add the new guard's own
`ROGUESQ_LOG_*` var before running.

## Soak queue status
`s484_audio_voice_baseptr_confirm.sh` queued (2nd independent confirm for BOTH item -314 and item
-315's guards). The loop should have run it; check `scratch/agent/SOAK-RESULTS.md` tail first.
