# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s505 recap — read this first

s505 picked up Option A from s504's decision point: item -318's `appendRdpStateDl+144`/
`last-guest-pc=0x800109b8` crash (3 independent occurrences, met its own pre-set 3rd-occurrence
threshold). Source-traced the mechanism (own read + an independently dispatched Explore-agent pass,
both converging on the same root cause) and FIXED it with `APPEND_RDP_STATE_DL_ENTRY_GUARD`
(`funcs_3.c:26484`, `appendRdpStateDl`'s function entry — range-check the `$a0`/`ctx->r4` DL-append-cursor
argument, early-return if invalid; covers all 6 call sites from one patch point). 1st live-verify CLEAN
(0 fires, 0 regressions, `hangarbay-entry n=31` positive control). **2nd confirm queued**:
`scratch/agent/soak_queue/s506_append_rdp_state_dl_entry_confirm.sh` — the loop will run it; read its
verdict from `scratch/agent/SOAK-RESULTS.md` next session and fold it in (close item -318 2/2 if clean,
same as every other item in this lineage).

**Side finding**: the s505 live-verify's own crash was `beginFrameDLChunk+40536`/
`last-guest-pc=0x8000b0d0` — byte-identical to item -319's s503 single data point, now a **2nd
independent occurrence**. Item -319 is not yet at its 3rd-occurrence threshold; just watch for the next
one (don't chase yet).

## This session's decision point (once the s506 confirm result is in): two options, pick one

### Option A: if a 3rd `beginFrameDLChunk+40536` occurrence has landed (item -319), pivot to it

Same recipe as item -318: change `HYPOTHESIS-ID` to `item-319-beginframedlchunk-3rd-occurrence`, source
trace `beginFrameDLChunk` in `funcs_3.c`/`funcs_4.c` around guest `0x8000b0d0` (last-guest-pc) and the
native `+40536` offset, look for the same "unguarded reload passed as argument or dereferenced directly"
idiom that's now fixed 9 times in this lineage (items -312..-318).

### Option B: continue the tied-40 tier (fallback, same proven recipe, 9/9 clean so far incl. item -318)

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
```

then dedupe (group `(file, hit.line, hit.kind, hit.off, hit.reg)` from
`scratch/agent/s494_item317_step3_report.json`, count sources, sort descending). **Tied-at-40 tier as of
s503 (re-verify before touching source — line numbers may have drifted; s505 touched `funcs_3.c` at
`appendRdpStateDl`, offset 0x8000DE70, which is BEFORE line ~5695-8688 in file order but AFTER any code
above it shifted by the guard insertion — re-run the scan, don't trust these numbers blindly)**:

```
funcs_3.c:7384   (write, ctx->r2+0x4)
funcs_3.c:8344   (write, ctx->r2+0x4)
funcs_3.c:7700   (write, ctx->r2+0x4)
funcs_3.c:8688   (write, ctx->r2+0x4)
funcs_4.c:17346  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- flagged since s497, unfixed 9 sessions)
```

Recommend `funcs_3.c:7384` if you stay on this path (re-verify the line number first).

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s502 (zero new leads). Due again once 3+ sessions have passed — s506+ (i.e. **this session
or later, check it**).

## Reference: the fix recipe (repeated 9x now, copy exactly, for either option)

1. Delete `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (or `funcs_4.c` if
   the new lead is there — only the file you're touching).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. Add the new guard block to `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (copy the most recent
   guard block verbatim — `APPEND_RDP_STATE_DL_ENTRY_GUARD` is the freshest template if guarding at a
   function entry with early-return; the `EMIT_FRAME_RDP_INIT_DL_R2*_GUARD` blocks are the freshest
   template if guarding a single in-line write with a skip-on-invalid `else` branch).
5. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — redirect the FULL report to an in-repo
   scratch file (not `/tmp`) and grep it for the new guard's `patched x1` line; confirm no NEW
   anchor-count mismatches beyond the known-permanent S392_H3A/S393_H3B remainder.
6. `cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`
7. Copy the most recent `sNNN_..._manual.sh` in `scratch/agent/manual_runs/` to a new `sNNN_..._manual.sh`,
   add the new guard's env var, run it, grep its `run.log` (not the top-level summary) for the new
   guard's tag and for all other `-guard` tags to check for regressions.
8. Copy the manual script to a `_confirm.sh` variant in `scratch/agent/soak_queue/` for the loop to run.
9. Re-run the tracer `--scan` (if continuing Option B), dedupe, update this file's tied-40 tier and
   recommendation.
10. Update `PORTING-STATE.md` (new session entry), `docs/CURRENT-TRUTH.md` (relevant item body + count),
    commit, `scratch/agent/STATUS`=DONE, `scratch/agent/OUTCOME`=ADVANCED.
