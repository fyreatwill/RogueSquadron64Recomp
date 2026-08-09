# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s529 recap -- read this first

s529 was a fold-in-then-pick iteration (matching the s521-s528 pattern).

1. **Folded in `BEGIN_FRAME_DL_CHUNK_R7_GUARD`'s 2nd confirm** (`scratch/agent/SOAK-RESULTS.md` line for
   `s528_begin_frame_dl_chunk_r7_confirm`, rc=0, 346s): 0 `begin-frame-dl-chunk-r7-guard` fires, 1 benign
   already-catalogued `hangarmenu-a0-guard` co-fire (item -265), `hangarbay-entry n=32` positive control.
   Full 346s scheduled duration, no crash at all. Marked R7 **FULLY CLOSED 2/2**.
2. **Re-ran the tracer fresh**: raw top tier UNCHANGED at 36 sites (`funcs_3.c:15732`/`16198`) because
   the dedupe script ranks by a SHARED DOWNSTREAM WRITE reached via forward taint-propagation from many
   upstream reload sites, not by each site's own local shape -- fixing one upstream site doesn't shrink
   the tier's raw count.
3. **Cross-checked all 36 raw addresses in this tier against the live source directly** (grepped each
   against `fixup_game_funcs.py`, read the local context of every zero-hit one). Found: 10 already
   referenced by R1-R7's own sites/downstream reloads; most of the remaining 26 belong to the
   ALREADY-CLOSED `SIBLING_PTR_WRITE_GUARD` (s459) or `CACHE4_GUARD` (s271) families reusing the same
   textual `+0x63B0` reload idiom in this function, or feed an existing `GENERIC_CACHE_GUARD` deref a
   few instructions later. Only 3 of the 36 were both genuinely unguarded and matched the exact R2/R7
   idiom shape: `0x8000A90C` (fixed this session as R8), `0x8000B2A8`, and `0x8000B400` (both
   pre-verified this session, ready to fix next -- no fresh tracing needed for these two).
4. **Source-traced and FIXED `BEGIN_FRAME_DL_CHUNK_R8_GUARD`** (`funcs_3.c:12407`, guest address
   `0x8000A918`, load pair `0x8000A908`/`0x8000A90C`). Exact same shape as every prior guard: null check
   gates one arm, non-null fallthrough has an unconditional deref with no range check, downstream reload
   at `0x8000A934` feeds the pre-existing `GENERIC_CACHE_GUARD` deref at `0x8000A938` -- skip-on-invalid
   safe. Added to `tools/fixup_game_funcs.py` (N64Recomp repo).
5. **1st live-verify clean**: 0 `begin-frame-dl-chunk-r8-guard` fires, 0 co-fires on any other armed
   guard family, `hangarbay-entry n=32` positive control. Crashed at 122.6s on a NEW,
   previously-uncatalogued `rebuildActiveDisplayObjectList+660`/`last-guest-pc=0x800ab060` signature --
   filed as item -329, single occurrence, not chased. 2nd independent confirm queued:
   `scratch/agent/soak_queue/s529_begin_frame_dl_chunk_r8_confirm.sh`.
6. Tally: item -317 step 3 now 29/~150 fixed, 28 fully closed 2/2, R8 pending its 2nd confirm. ~115
   sites remain, 2 of which (`0x8000B2A8`, `0x8000B400`) are pre-identified genuine next candidates.

Full detail: `docs/CURRENT-TRUTH.md` item -317, `PORTING-STATE.md` Session 529.

## The work unit for the NEXT iteration

**If `scratch/agent/SOAK-RESULTS.md` has a new line for `s529_begin_frame_dl_chunk_r8_confirm`**: read
its directory's own `run.log` (`scratch/agent/soak_results/s529_begin_frame_dl_chunk_r8_confirm/run.log`
-- NOT just the flat top-level summary file). If 0 `begin-frame-dl-chunk-r8-guard` fires and a strong
`hangarbay-entry` positive control, mark `BEGIN_FRAME_DL_CHUNK_R8_GUARD` FULLY CLOSED 2/2 in
`docs/CURRENT-TRUTH.md` item -317 (29 fixed, 29 fully closed) and fold the result into
`PORTING-STATE.md`. Then continue to the next site below in the SAME iteration (fold-in-then-pick
pattern, s521-s529).

**Then (or if no confirm result is queued yet), fix the two pre-identified sites from s529** -- these
were ALREADY confirmed to match the idiom shape this session, so this should be faster than a normal
pick-a-site iteration (no fresh tracer scan needed, just re-verify against current line numbers since
they drift per regen):

1. **`0x8000B2A8`** (load pair `0x8000B2A4`/`0x8000B2A8`, write site around `0x8000B2B0`-`B2B4`,
   downstream feeds `GENERIC_CACHE_GUARD` a few instructions later per the s529 cross-check). Re-find
   its current line number in `RecompiledFuncs/funcs_3.c` (grep `0x8000B2A8`), re-confirm the exact
   `lui/lw` / `beq $v0,$zero,L_x` / unconditional write shape holds (line numbers drift after R8's own
   regen), then fix as `BEGIN_FRAME_DL_CHUNK_R9_GUARD` following the exact pattern of R2/R7/R8 in
   `tools/fixup_game_funcs.py` (N64Recomp repo).
2. **`0x8000B400`** (load pair `0x8000B3FC`/`0x8000B400`) as `BEGIN_FRAME_DL_CHUNK_R10_GUARD`, same
   process, same iteration if time permits (or the next iteration if not -- one work unit is enough).
3. Regen/build/live-verify/queue-2nd-confirm sequence (see Regen reminder below).
4. Update `docs/CURRENT-TRUTH.md` item -317's running tally and tier list, append a `PORTING-STATE.md`
   session entry, commit.

**Once `0x8000B2A8` and `0x8000B400` are both fixed**, this 36-site tier is exhausted. Re-run the
tracer fresh AND apply the s529 cross-check methodology (grep each candidate address against
`fixup_game_funcs.py`, read its actual local source) BEFORE trusting the next tier's raw count --
`funcs_3.c:11625` (`emitColorFillRect`, 30 sites) and `funcs_4.c:4457` (`submitSceneNodeRender`, 30
sites) are the next-ranked candidates but, per s529's lesson, likely also overlap already-closed guard
families (`SIBLING_PTR_WRITE_GUARD`, `GENERIC_CACHE_GUARD`, `CACHE4_GUARD`, etc.) -- don't assume the
raw dedupe count is all-new without checking.

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

### Live-verify recipe (copy the most recent `soak_queue/done/s529_*_manual_*.sh`, edit the guard-specific
comment header and output dir name, add the new guard's `ROGUESQ_LOG_<NAME>=1` to the armed list)
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

Do NOT use `sed 's/r6/r7/g; s/R6/R7/g'` to derive a new guard's script from an old one -- it silently
collapses the OLD guard's own armed env-var line into a duplicate of the NEW one, losing that guard's
instrumentation (hit this exact bug in s527; fixed by copying from the manual script instead, which
already had all guards armed correctly).
