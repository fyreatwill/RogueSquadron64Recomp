# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s510 recap — read this first

s510 did two things:

1. **Folded in the s509-queued `s509_emit_frame_rdp_init_dl_r2j_confirm` soak.** CLEAN: 0
   `emit-frame-rdp-init-dl-r2j-guard` fires, `hangarbay-entry n=31` positive control (lower than
   usual but above the single-digit discard threshold — not discarded), one benign
   `hangarmenu-a0-guard` co-fire (item -265, unrelated). `EMIT_FRAME_RDP_INIT_DL_R2J_GUARD` is now
   **FULLY CLOSED, 2/2**. Item -317 step 3 now stands at **12/12 fixed guards fully closed** (13
   fixed total counting this session's new one below).
   - The run's own crash (`pc-symbol=menuOverlayInit+3648`, `last-guest-pc=0x800ab1c4`) is
     host-symbol-offset-identical to the historically-CLOSED item -266/-267 chain but carries a
     DIFFERENT `last-guest-pc` than any of that chain's original occurrences — filed as new item
     -321, explicitly flagged as a **possible-but-unconfirmed** recurrence (not concluded — see the
     s422 `0x800290d4` precedent for why a bare pc-symbol match isn't sufficient). Watch for a 2nd
     occurrence with a matching `last-guest-pc` before escalating.
2. **Fixed a SECOND, distinct tied-40 lead inside `renderLitMeshFaceGroup`** — the same function
   `RENDER_LIT_MESH_R2_GUARD` (s496) already partially covers, but at a different write site
   (`funcs_4.c:17346`/`0x800148E8`, `RENDER_LIT_MESH_R3_GUARD`). 1st live-verify: CLEAN — 0
   `render-lit-mesh-r3-guard` fires, 0 fires on any other armed sibling guard except one benign
   `hangarmenu-a0-guard` co-fire, `hangarbay-entry n=35` positive control. Full scheduled duration
   completed with **no crash at all** (121 frames, rc=0). 2nd confirm queued:
   `scratch/agent/soak_queue/s510_render_lit_mesh_r3_confirm.sh`.

Neither this session's own crash (item -321, new) nor the folded-in R2J confirm produced a 3rd
occurrence of item -319 (`beginFrameDLChunk+40536`, still at 2) or a 2nd of item -320
(`loadCutsceneAssetsByIndex+1860`, still at 1). Neither threshold triggered — no pivot.

## This session's decision point: two options, pick one

### Option A: if a 3rd `beginFrameDLChunk+40536` occurrence has landed (item -319), pivot to it

Change `HYPOTHESIS-ID` to `item-319-beginframedlchunk-3rd-occurrence`. Start from the candidate site
list inside `beginFrameDLChunk` that the s506 tracer scan flagged (item -317's CURRENT-TRUTH entry has
the pointer — re-run the tracer scan fresh, do not reuse any previously recorded line numbers, they've
drifted) rather than a fresh source trace from scratch. s510's own fresh scan already found the
top 3 `beginFrameDLChunk` candidates at count=36: `funcs_3.c:16582`, `funcs_3.c:14280`,
`funcs_3.c:15157` (re-verify lines before touching source, they drift every guard insertion).

Also worth a look if it recurs: **item -320** (`loadCutsceneAssetsByIndex+1860`) and **item -321**
(`menuOverlayInit+3648`, NEW this session) are both still single-occurrence breadcrumbs — if either
recurs before item -319 hits 3, source-trace it (item -321 in particular deserves a source read on
2nd occurrence regardless of `last-guest-pc` match, since it might reveal whether it's really the old
item -266/-267 bug or a coincidental host-code-sink collision).

### Option B: continue the tied-40 tier (fallback, same proven recipe, 13/13 clean so far incl. R3)

**The tied-40 tier is now DRY** — its only member (`funcs_4.c:17346`) was fixed this session. Re-run
both scripts fresh (do NOT reuse this session's recorded line numbers, they will have drifted):

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
python3 scratch/agent/s506_dedupe.py   # correct grouping key, reuse this script -- do NOT drop hit.line
```

**Next tier as of s510's scan (count=36, RE-VERIFY BEFORE TOUCHING SOURCE)**:

```
funcs_3.c:16582  (write, ctx->r2+0x4, beginFrameDLChunk -- item -319's own function, see Option A note)
funcs_3.c:14280  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_3.c:15157  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_4.c:17759  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- a THIRD site in this same function)
```

If picking from this tier, prefer a `renderLitMeshFaceGroup` site (`funcs_4.c:17759`) over a
`beginFrameDLChunk` site UNLESS you're deliberately pursuing Option A — fixing inside
`beginFrameDLChunk` before item -319 hits its 3rd-occurrence threshold pre-empts that thread's own
dedicated investigation and could mask which specific site was the recurring bug.

If the dedupe script shows this tier has also run dry, move to the next-ranked cluster:
`funcs_4.c:15620` (32 sites), `funcs_4.c:4880` (34 sites, `submitSceneNodeRender`), or
`funcs_4.c:3299`-ish (26 sites, per s506's older scan — re-verify count, may have shifted).

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s510 (zero new leads — none of this session's 3 soaks touched an audio-subsystem crash
signature or stub). Due again — **s513+**.

## Reference: the fix recipe (repeated 13x now, copy exactly, for either option)

1. Delete `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (or `funcs_4.c` if
   the new lead is there — only the file you're touching).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. Add the new guard block to `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (copy the
   `RENDER_LIT_MESH_R3_GUARD` block verbatim — freshest template for a single in-line write with a
   skip-on-invalid `else` branch; `APPEND_RDP_STATE_DL_ENTRY_GUARD` is the freshest template if
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
