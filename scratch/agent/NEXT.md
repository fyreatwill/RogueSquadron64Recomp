# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s509 recap — read this first

s509 did two things:

1. **Folded in the s508-queued `s508_emit_frame_rdp_init_dl_r2i_confirm` soak.** CLEAN: 0
   `emit-frame-rdp-init-dl-r2i-guard` fires, `hangarbay-entry n=2600` positive control, zero other
   guard-family fires, ran the full 348s scheduled duration with **no crash at all**.
   `EMIT_FRAME_RDP_INIT_DL_R2I_GUARD` is now **FULLY CLOSED, 2/2**. Item -317 step 3 stands at
   **11/11 fixed guards fully closed** (12 fixed total counting this session's new one below).
2. **Fixed the next tied-40 lead**, `EMIT_FRAME_RDP_INIT_DL_R2J_GUARD` (`funcs_3.c:8727`/`0x80009A24`,
   `emitFrameRdpInitDl`, 10th guard in that function). **Important**: the line had drifted from
   NEXT.md's recorded `funcs_3.c:8714` to `funcs_3.c:8727` this session — re-verify every session,
   line numbers drift after every guard insertion in the same file. 1st live-verify: CLEAN — 0
   `emit-frame-rdp-init-dl-r2j-guard` fires, 0 fires on any other armed sibling guard,
   `hangarbay-entry n=2700` strong positive control. Crashed at 122.6s on the already-catalogued
   `tickWrappingTimerAccumulatorList` (`funcs_11.c`) crash family (`pc-symbol=memcpy_recomp+288`,
   `last-guest-pc=0x80054780`, byte-identical to s462/s487's own confirms), unrelated to this guard.
   2nd confirm queued: `scratch/agent/soak_queue/s509_emit_frame_rdp_init_dl_r2j_confirm.sh`.

Neither this session's own crash nor the folded-in R2I confirm produced a 3rd occurrence of item -319
(`beginFrameDLChunk+40536`, still at 2) or a 2nd of item -320 (`loadCutsceneAssetsByIndex+1860`,
filed s508, still at 1). Neither threshold triggered — no pivot.

## This session's decision point: two options, pick one

### Option A: if a 3rd `beginFrameDLChunk+40536` occurrence has landed (item -319), pivot to it

Change `HYPOTHESIS-ID` to `item-319-beginframedlchunk-3rd-occurrence`. Start from the candidate site
list inside `beginFrameDLChunk` that the s506 tracer scan flagged (item -317's CURRENT-TRUTH entry has
the pointer — re-run the tracer scan fresh, do not reuse any previously recorded line numbers, they've
drifted) rather than a fresh source trace from scratch.

Also worth a look: **item -320** (`loadCutsceneAssetsByIndex+1860`) is still a single-occurrence
breadcrumb — if it recurs before item -319 hits 3, source-trace it the same way item -318 was
(6-call-site reload-then-pass-as-arg pattern is a reasonable first hypothesis given the lineage, but
verify from scratch, don't assume).

### Option B: continue the tied-40 tier (fallback, same proven recipe, 12/12 clean so far incl. R2J)

The tied-40 tier is now down to its LAST member. If R2J's confirm also closes clean, the next pick is
`funcs_4.c:17346`-ish (`renderLitMeshFaceGroup`, flagged since s497, unfixed 12 sessions running) —
re-verify the line first, it's a different file/function than the R2*-series and may have drifted
independently.

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
python3 scratch/agent/s506_dedupe.py   # correct grouping key, reuse this script -- do NOT drop hit.line
```

**Tied-at-40 tier as of s509 (RE-VERIFY BEFORE TOUCHING SOURCE — confirmed drifting most sessions)**:

```
funcs_4.c:17346  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- flagged since s497, unfixed 12 sessions, now the sole remaining tied-40 lead)
```

If the dedupe script shows the tied-40 tier has run dry (i.e. `funcs_4.c:17346` is fixed or the count
drops below the next tier), move to the next-ranked cluster: `funcs_4.c:3299`-ish (26 sites),
`funcs_3.c:28922`-ish (18 sites), or the `beginFrameDLChunk` cluster flagged in Option A above.

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s506 (zero new leads). Due again — **s510+, due next session or the one after**.

## Reference: the fix recipe (repeated 12x now, copy exactly, for either option)

1. Delete `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (or `funcs_4.c` if
   the new lead is there — only the file you're touching).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. Add the new guard block to `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (copy the
   `EMIT_FRAME_RDP_INIT_DL_R2J_GUARD` block verbatim — freshest template for a single in-line write
   with a skip-on-invalid `else` branch; `APPEND_RDP_STATE_DL_ENTRY_GUARD` is the freshest template if
   guarding at a function entry with early-return instead).
5. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — redirect the FULL report to an in-repo
   scratch file (not `/tmp`) and grep it for the new guard's `patched x1` line; confirm no NEW
   anchor-count mismatches beyond the known-permanent S392_H3A/S393_H3B remainder (50 total).
6. `cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`
7. Copy the most recent `sNNN_..._manual.sh` in `scratch/agent/manual_runs/` to a new `sNNN_..._manual.sh`,
   add the new guard's env var, run it, grep its `run.log` (not the top-level summary `.log`) for
   `CRASH`/`pc-symbol`, the new guard's own fire count, `hangarbay-entry` (positive control), and any
   other `-guard]` fires (regression check). **If the crash lands early with a weak (single-digit)
   `hangarbay-entry` count, discard and retry once before banking the result — Iron Rule 1.**
8. Write a 2nd-confirm queue script to `scratch/agent/soak_queue/` (self-contained, same env-var set
   plus the new guard's var) for the loop to run.
9. When folding in a queued confirm from `SOAK-RESULTS.md`, always open the actual `run.log` inside its
   capture directory (`scratch/agent/soak_results/<name>/run.log`) — the top-level `SOAK-RESULTS.md`
   line for a loop-run (non-manual) soak only has `rc`/duration, no guard-fire detail.
