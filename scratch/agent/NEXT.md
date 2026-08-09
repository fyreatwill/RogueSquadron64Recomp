# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s530 recap -- read this first

s530 was a fold-in-then-pick iteration (matching the s521-s530 pattern).

1. **Folded in `BEGIN_FRAME_DL_CHUNK_R8_GUARD`'s 2nd confirm** (`s529_begin_frame_dl_chunk_r8_confirm`,
   rc=3, 171s): 0 `begin-frame-dl-chunk-r8-guard` fires, 1 benign already-catalogued
   `hangarmenu-a0-guard` co-fire, `hangarbay-entry n=33` positive control. Crashed on
   `pc-symbol=unregisterServiceWorker+536`, `last-guest-pc=0x800ab1c4` -- byte-identical to item -321's
   s515 sighting (already REFUTED s518 as a shared-epilogue false corroboration, no new action). Marked
   `BEGIN_FRAME_DL_CHUNK_R8_GUARD` **FULLY CLOSED 2/2**.
2. **Fixed the two s529 pre-identified candidates**, both already confirmed to match the exact R2/R7/R8
   idiom shape: `BEGIN_FRAME_DL_CHUNK_R9_GUARD` (`funcs_3.c`/`0x8000B2B4`, load pair
   `0x8000B2A4`/`0x8000B2A8`) and `BEGIN_FRAME_DL_CHUNK_R10_GUARD` (`funcs_3.c`/`0x8000B40C`, load pair
   `0x8000B3FC`/`0x8000B400`). Both patched in `tools/fixup_game_funcs.py` (N64Recomp repo), full
   regen/build applied cleanly.
3. **1st live-verify, both guards armed together in one run** (batch-instrumentation rule): 0 fires on
   either new guard, 0 regressions on any other armed guard family, `hangarbay-entry n=35` positive
   control. Full 300s scheduled duration completed with **NO crash at all** (118 frames captured) --
   the cleanest possible verify class. 2nd independent confirm queued:
   `scratch/agent/soak_queue/s530_begin_frame_dl_chunk_r9_r10_confirm.sh`.
4. **With R9/R10 fixed, the s529 36-site raw tier is now EXHAUSTED** -- all 3 genuinely-unguarded,
   matching-shape candidates from last session's cross-check (R8/R9/R10) are fixed. No more pre-verified
   candidates remain queued; the NEXT iteration must re-scan.
5. Tally: item -317 step 3 now 31/~150 fixed, 29 fully closed 2/2, R9/R10 pending their 2nd confirm.
   ~115 sites remain, all unaudited (next tier, stale scan).

Full detail: `docs/CURRENT-TRUTH.md` item -317, `PORTING-STATE.md` Session 530.

## The work unit for the NEXT iteration

**If `scratch/agent/SOAK-RESULTS.md` has a new line for `s530_begin_frame_dl_chunk_r9_r10_confirm`**:
read its directory's own `run.log` (`scratch/agent/soak_results/s530_begin_frame_dl_chunk_r9_r10_confirm/run.log`
-- NOT just the flat top-level summary file). If 0 fires on both `begin-frame-dl-chunk-r9-guard` and
`begin-frame-dl-chunk-r10-guard` and a strong `hangarbay-entry` positive control, mark both
`BEGIN_FRAME_DL_CHUNK_R9_GUARD` and `R10_GUARD` FULLY CLOSED 2/2 in `docs/CURRENT-TRUTH.md` item -317
(31 fixed, 31 fully closed -- item -317 step 3 would then be 100% closed on everything fixed so far) and
fold the result into `PORTING-STATE.md`. Then continue to the next step below in the SAME iteration
(fold-in-then-pick pattern, s521-s530).

**Then (or if no confirm result is queued yet), re-scan for the next tier** -- no pre-identified
candidates remain this time, so this requires a fresh scan + the s529/s530 cross-check methodology
(do NOT skip the cross-check and trust the raw tracer count):

1. **Re-run the tracer fresh**, letting `--scan` write its default output path (do NOT pass a custom
   `--out` -- s521's gotcha: `s506_dedupe.py` reads a fixed canonical path and silently ranks against
   stale data otherwise):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. **Take the top-ranked tier from the dedupe output.** Last known (STALE, s528 scan): `funcs_3.c:11625`
   (`emitColorFillRect`, 30 sites) and `funcs_4.c:4457` (`submitSceneNodeRender`, 30 sites) were
   next-ranked after the now-exhausted `beginFrameDLChunk` 36-site tier -- but re-confirm with a fresh
   scan since fixing R9/R10 may shift rankings.
3. **Cross-check EVERY raw address in the new top tier against the live source directly** (the s529/s530
   lesson): grep each guest address against `tools/fixup_game_funcs.py` (N64Recomp repo) for existing
   PATCH coverage, and read the actual generated context around any zero-hit address in
   `RecompiledFuncs/funcs_*.c`. Expect most of the raw count to already be covered by
   `SIBLING_PTR_WRITE_GUARD` (s459), `CACHE4_GUARD` (s271), `GENERIC_CACHE_GUARD` (s434), or this
   lineage's own earlier guards reusing the same textual `+0x63B0`-style reload idiom -- only genuinely
   unguarded sites matching the exact idiom shape (null check gates one arm safely via a harmless
   delay-slot write, non-null fallthrough has an unconditional deref with no
   `0x80000000`-`0x80800000` range check, downstream reload feeds an existing guard) are real candidates.
4. **Fix the first genuine candidate found** as `BEGIN_FRAME_DL_CHUNK_R11_GUARD` (or a new function-name
   prefix if the new tier is in a different function -- e.g. `EMIT_COLOR_FILL_RECT_R1_GUARD` or
   `SUBMIT_SCENE_NODE_RENDER_R2_GUARD`), following the exact `fixup_game_funcs.py` pattern of
   R2/R7/R8/R9/R10 (see the guard's own comment block for the template to copy).
5. Regen/build/live-verify/queue-2nd-confirm sequence (see Regen reminder below). If time permits and
   the cross-check turned up more than one genuine candidate in the same tier, fix and verify them
   together in one build/run (batch-instrumentation rule, as done this session with R9+R10) rather than
   spending a build-run cycle per guard.
6. Update `docs/CURRENT-TRUTH.md` item -317's running tally and tier list, append a `PORTING-STATE.md`
   session entry, commit.

Watch for recurrences (passive, filed not chased unless they hit): item -326 (`do_rom_read`/
`piDmaWorker` shape, historically significant if it recurs -- 3rd occurrence would overturn a
375+-session-old "fixed" conclusion), -327 (`submitSceneNodeRender+67668`, 2 occurrences 21 sessions
apart, watch for a 3rd), -328 (`submitSceneNodeRender+69820`, single occurrence), -329
(`rebuildActiveDisplayObjectList+660`/`0x800ab060`, single occurrence).

### Regen reminder (all 4 steps, every time, in order)
```
cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
cd ~/Documents/Tools/N64Recomp && python3 -c "
import glob, os
for f in glob.glob('RecompiledFuncs/funcs_*.c'):
    os.remove(f)
"
./build/N64Recomp rogue_squadron.toml
python3 fixup_game_funcs.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build && \
  DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
```

### Live-verify recipe (copy the most recent `soak_queue/done/s530_*_manual_*.sh`, edit the guard-specific
comment header, output dir name, and add the new guard's `ROGUESQ_LOG_<NAME>=1` to the armed list --
copy by hand or with a targeted, single-string-literal `sed` substitution of the OUTPUT PATH ONLY, as
done this session; do NOT use a broad `s/r6/r7/g` style substitution -- it silently collapses an OLD
guard's own armed env-var line into a duplicate of the NEW one, losing that guard's instrumentation
(hit this exact bug in s527))
Run in foreground (backgrounds itself past 120s automatically -- wait for the notification, don't poll):
```
zsh scratch/agent/soak_queue/s5NN_<name>_manual.sh
```
Then, after a clean or acceptable-crash result, copy the SAME script (now with all guards armed
including the new one) to `scratch/agent/soak_queue/s5NN_<name>_confirm.sh` with the output dir renamed
`..._confirm`, leaving it for the loop to run as the 2nd independent confirm. Also move the manual
script itself into `soak_queue/done/` with a timestamp suffix (matching its `soak_results/` directory
mtime) -- the loop's own runner does this automatically for queued recipes, but a manual foreground run
must be moved by hand or it sits unprocessed in the active queue.
