# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s506 recap — read this first

s506 did three things:

1. **Folded in the loop's queued s506 soak** (item -318's 2nd confirm attempt) and found it
   **INCONCLUSIVE, not a valid confirm**: crashed at only 20.0s/8 frames on an unrelated already-
   catalogued crash (`rebuildActiveDisplayObjectList+540`) with ZERO guard-fire lines of any kind,
   including zero `hangarbay-entry` positive-control fires. Per Iron Rule 1 this doesn't count. Item
   -318 stays at 1/2 confirms. Retry queued: `scratch/agent/soak_queue/s506_append_rdp_state_dl_entry_confirm_retry.sh`
   — the loop will run it; read the verdict from `scratch/agent/SOAK-RESULTS.md` next session and fold
   it in (this time checking `hangarbay-entry` actually fired before trusting it as a confirm).
2. **M5 audio-lead cadence check** (due since s502+3): grepped PORTING-STATE Sessions 503-505, zero
   audio/MusyX/voice/song/sound/sfx hits. No new lead. Cadence reset to s506 (due again s510+).
3. **Fixed the next tied-40 lead**, `EMIT_FRAME_RDP_INIT_DL_R2G_GUARD` (`funcs_3.c:7384`/`0x80009578`,
   `emitFrameRdpInitDl`, 7th guard in that function, 9th in the whole item -317 step 3 campaign). 1st
   live-verify CLEAN (0 fires, 0 regressions except one benign pre-existing `hangarmenu-a0-guard` fire,
   `hangarbay-entry n=32` positive control; crashed on the already-catalogued `coalesceFreeHeapBlocks`
   heap-walker family, unrelated). 2nd confirm queued: `scratch/agent/soak_queue/s506_emit_frame_rdp_init_dl_r2g_confirm.sh`.

**Side finding, not yet acted on**: this session's fresh tracer scan (`s494_item317_step3_tracer.py
--scan`, re-deduped correctly by `(file, hit.line, hit.kind, hit.off, hit.reg)` — grouping WITHOUT
`hit.line` silently merges unrelated sites, a mistake caught and corrected in-session, see
`scratch/agent/s506_dedupe.py`) surfaced a cluster of ~9 candidate guard sites (counts 28-36) inside
`beginFrameDLChunk` itself — the exact function item -319's recurring crash (`beginFrameDLChunk+40536`,
2 independent occurrences, s503/s505) lives in. Still not at the 3rd-occurrence threshold. If a 3rd
lands, this list (`funcs_3.c:16530/14228/15105/14711/16055/12843/15589/13316/13808`) is a ready-made
starting point instead of a fresh source trace from zero.

## This session's decision point: two options, pick one

### Option A: if a 3rd `beginFrameDLChunk+40536` occurrence has landed (item -319), pivot to it

Change `HYPOTHESIS-ID` to `item-319-beginframedlchunk-3rd-occurrence`. Start from the candidate site
list above (all inside `beginFrameDLChunk`, same `write off=0X4 reg=r2` shape as the whole item -317/-318
lineage) rather than a fresh source trace — check which candidate's guest address maps closest to
`last-guest-pc=0x8000b0d0`/`+40536` first.

### Option B: continue the tied-40 tier (fallback, same proven recipe, 9/9 clean so far incl. R2G)

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
python3 scratch/agent/s506_dedupe.py   # correct grouping key, reuse this script -- do NOT drop hit.line
```

**Tied-at-40 tier as of s506 (re-verify before touching source — line numbers may have drifted)**:

```
funcs_3.c:8344   (write, ctx->r2+0x4)   <- recommended next pick
funcs_3.c:7700   (write, ctx->r2+0x4)
funcs_3.c:8688   (write, ctx->r2+0x4)
funcs_4.c:17346  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- flagged since s497, unfixed 9 sessions)
```

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s506 (zero new leads). Due again once 3+ sessions have passed — s510+.

## Reference: the fix recipe (repeated 9x now, copy exactly, for either option)

1. Delete `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (or `funcs_4.c` if
   the new lead is there — only the file you're touching).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. Add the new guard block to `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (copy the
   `EMIT_FRAME_RDP_INIT_DL_R2G_GUARD` block verbatim — freshest template for a single in-line write
   with a skip-on-invalid `else` branch; `APPEND_RDP_STATE_DL_ENTRY_GUARD` is the freshest template if
   guarding at a function entry with early-return instead).
5. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — redirect the FULL report to an in-repo
   scratch file (not `/tmp`) and grep it for the new guard's `patched x1` line; confirm no NEW
   anchor-count mismatches beyond the known-permanent S392_H3A/S393_H3B remainder.
6. `cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`
7. Copy the most recent `sNNN_..._manual.sh` in `scratch/agent/manual_runs/` to a new `sNNN_..._manual.sh`,
   add the new guard's env var, run it, grep its `run.log` (not the top-level summary) for the new
   guard's tag, for `hangarbay-entry` (positive control — MUST be nonzero or the run doesn't count),
   and for all other `-guard` tags to check for regressions.
8. Copy the manual script to a `_confirm.sh` variant in `scratch/agent/soak_queue/` for the loop to run.
9. Re-run the tracer `--scan` + `s506_dedupe.py` (if continuing Option B), update this file's tied-40
   tier and recommendation.
10. Update `PORTING-STATE.md` (new session entry), `docs/CURRENT-TRUTH.md` (relevant item body + count),
    commit, `scratch/agent/STATUS`=DONE, `scratch/agent/OUTCOME`=ADVANCED.
