# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s508 recap — read this first

s508 did three things:

1. **Folded in the s507-queued `s507_emit_frame_rdp_init_dl_r2h_confirm` soak.** CLEAN: 0
   `emit-frame-rdp-init-dl-r2h-guard` fires, `hangarbay-entry n=2700` positive control, one benign
   all-zero `compose-npc-orient-guard9` co-fire. `EMIT_FRAME_RDP_INIT_DL_R2H_GUARD` is now **FULLY
   CLOSED, 2/2**. Item -317 step 3 stands at **10/10 fixed guards fully closed** (11 fixed total
   counting this session's new one below).
2. **The R2H confirm's crash was a brand-new signature** — `loadCutsceneAssetsByIndex+1860`,
   `last-guest-pc=0x800aafb8`, filed as **item -320** (single occurrence, not source-traced, watch
   for a 2nd). Not the async Metal-compiler-thread cluster (items -10/-9) — that family always shows
   a nonsense dyld-shared-cache `pc-symbol`; this one resolved to a real function name with a coherent
   guest call stack (`menuOverlayInit → runHangarMenuFromOverlay → runHangarSelectionFrame →
   loadCutsceneAssetsByIndex`).
3. **Fixed the next tied-40 lead**, `EMIT_FRAME_RDP_INIT_DL_R2I_GUARD` (`funcs_3.c:7713`/`0x800096A0`,
   `emitFrameRdpInitDl`, 9th guard in that function, 11th in the whole item -317 step 3 campaign).
   **Important**: this session's tracer re-scan confirmed the line number was UNCHANGED from the prior
   session's recorded pick — but do NOT assume that holds again; re-verify every session, line numbers
   drift after every guard insertion in the same file. 1st live-verify: a first attempt crashed early
   (20s, `hangarbay-entry n=4`) on the async-Metal-compiler-thread cluster — too weak a positive control
   to count (Iron Rule 1), discarded and retried. The retry is CLEAN: 0
   `emit-frame-rdp-init-dl-r2i-guard` fires, `hangarbay-entry n=2600`, crashed at 109.9s on the SAME
   already-catalogued async cluster (`last-guest-pc=0x800aadf8`, nonsense `pc-symbol`, byte-close to
   items -10/-9's known signature). 2nd confirm queued:
   `scratch/agent/soak_queue/s508_emit_frame_rdp_init_dl_r2i_confirm.sh`.

## This session's decision point: two options, pick one

### Option A: if a 3rd `beginFrameDLChunk+40536` occurrence has landed (item -319), pivot to it

Change `HYPOTHESIS-ID` to `item-319-beginframedlchunk-3rd-occurrence`. Start from the candidate site
list inside `beginFrameDLChunk` that the s506 tracer scan flagged (item -317's CURRENT-TRUTH entry has
the pointer — re-run the tracer scan fresh, do not reuse any previously recorded line numbers, they've
drifted) rather than a fresh source trace from scratch.

Also worth a look: **item -320** (`loadCutsceneAssetsByIndex+1860`) is a fresh single-occurrence
breadcrumb — if it recurs before item -319 hits 3, source-trace it the same way item -318 was
(6-call-site reload-then-pass-as-arg pattern is a reasonable first hypothesis given the lineage, but
verify from scratch, don't assume).

### Option B: continue the tied-40 tier (fallback, same proven recipe, 11/11 clean so far incl. R2I)

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
python3 scratch/agent/s506_dedupe.py   # correct grouping key, reuse this script -- do NOT drop hit.line
```

**Tied-at-40 tier as of s508 (RE-VERIFY BEFORE TOUCHING SOURCE — confirmed drifting most sessions)**:

```
funcs_3.c:8714   (write, ctx->r2+0x4, emitFrameRdpInitDl)   <- recommended next pick, re-verify line first
funcs_4.c:17346  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- flagged since s497, unfixed 11 sessions)
```

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s506 (zero new leads). Due again once 3+ sessions have passed — **s510+, due next
session or the one after**.

## Reference: the fix recipe (repeated 11x now, copy exactly, for either option)

1. Delete `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (or `funcs_4.c` if
   the new lead is there — only the file you're touching).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. Add the new guard block to `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (copy the
   `EMIT_FRAME_RDP_INIT_DL_R2I_GUARD` block verbatim — freshest template for a single in-line write
   with a skip-on-invalid `else` branch; `APPEND_RDP_STATE_DL_ENTRY_GUARD` is the freshest template if
   guarding at a function entry with early-return instead).
5. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — redirect the FULL report to an in-repo
   scratch file (not `/tmp`) and grep it for the new guard's `patched x1` line; confirm no NEW
   anchor-count mismatches beyond the known-permanent S392_H3A/S393_H3B remainder.
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
