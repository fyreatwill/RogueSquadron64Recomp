# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s512 recap — read this first

s512 did three things:

1. **Folded in the s511-queued `s511_render_lit_mesh_r4_confirm` soak.** CLEAN on the guard itself: 0
   `render-lit-mesh-r4-guard` fires, `hangarbay-entry n=31` positive control (present, on the low
   side but within the accepted range per precedent — not a "too weak" discard). `RENDER_LIT_MESH_R4_GUARD`
   is now **FULLY CLOSED, 2/2**. Item -317 step 3 now stands at **14/14 fixed guards fully closed**.
2. **Triaged the crash that soak hit (`heapFreeListDequeue+40432`/`last-guest-pc=0x8000d92c`)
   properly instead of rubber-stamping it "unrelated, filed not chased."** Grepped both docs for the
   `last-guest-pc` and found an EXACT prior hit at s457 (`heapFreeListDequeue+32596`, same
   `last-guest-pc`, full backtrace through `submitSceneNodeRender <- processSceneNode <-
   traverseSceneGraphRecursive <- setupCameraMatrices <- runHangarSelectionFrame <-
   runHangarMenuFromOverlay <- menuOverlayInit <- mainGameLoop`) — at the time filed only as a loose
   observation, never given an item number. This is now genuinely 2 independent occurrences of the
   same signature. Filed as **item -322** (CURRENT-TRUTH.md) — watch for a 3rd before opening a
   dedicated thread, same discipline as items -319/-320/-321.
3. **Fixed a FIFTH, distinct write site inside `renderLitMeshFaceGroup`** — same function R2/R3/R4
   already cover, at yet another address (`funcs_4.c:17784`/`0x80014A8C`, `RENDER_LIT_MESH_R5_GUARD`,
   46 shared sites, top of the fresh post-R4-regen tier). 1st live-verify: **CLEAN, full 300s
   scheduled duration, zero crashes at all** (0 `render-lit-mesh-r5-guard` fires, `hangarbay-entry
   n=33` positive control, one benign `hangarmenu-a0-guard` co-fire). 2nd confirm queued:
   `scratch/agent/soak_queue/s512_render_lit_mesh_r5_confirm.sh`.

No 3rd occurrence of item -319 (`beginFrameDLChunk+40536`, still at 2), item -320, item -321, or the
new item -322 landed this session. No pivot.

## This session's decision point: two options, pick one

### Option A: if a 3rd occurrence of item -319, -320, -321, or -322 has landed, pivot to it

Change `HYPOTHESIS-ID` to match (e.g. `item-319-beginframedlchunk-3rd-occurrence` or
`item-322-heapfreelistdequeue-3rd-occurrence`). For item -319, start from the candidate site list
inside `beginFrameDLChunk` that the s506 tracer scan flagged (item -317's CURRENT-TRUTH entry has the
pointer — re-run the tracer scan fresh, do not reuse any previously recorded line numbers). For item
-322, source-trace `heapFreeListDequeue` itself starting from the s457 backtrace
(`docs/PROJECT-OVERVIEW.md` §~1270 / `PORTING-STATE.md` Session 457 — search there first) — this
would be the first dedicated look at that function's own body since items -316/step-1 already fixed
a DIFFERENT bug inside it (2/2 closed, unrelated shape).

Also worth a look if either recurs: item -320 (`loadCutsceneAssetsByIndex+1860`) and item -321
(`menuOverlayInit+3648`) are both still single-occurrence — source-trace on 2nd occurrence regardless
of exact `last-guest-pc` match for -321 (it might reveal whether it's really the old item -266/-267
bug or a coincidental host-code-sink collision).

### Option B: continue the `renderLitMeshFaceGroup` tier (fallback, same proven recipe, 15/15 clean so far incl. R5)

**Re-run both scripts fresh** (do NOT reuse this session's recorded line numbers, they will have
drifted after R5's insertion):

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
python3 scratch/agent/s506_dedupe.py   # correct grouping key, reuse this script -- do NOT drop hit.line
```

**Next tier as of s512's scan (count=36 and below, taken BEFORE R5 was fixed — RE-VERIFY BEFORE
TOUCHING SOURCE, this list has already shifted)**:

```
funcs_3.c:16582  (write, ctx->r2+0x4, beginFrameDLChunk -- item -319's own function, see Option A note)
funcs_3.c:14280  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_3.c:15157  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_4.c:4880   (write, ctx->r2+0x4, submitSceneNodeRender)
funcs_3.c:14763  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_3.c:16107  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_4.c:15620  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- a SIXTH site in this same function)
```

If picking from this tier, prefer a `renderLitMeshFaceGroup` or `submitSceneNodeRender` site over a
`beginFrameDLChunk` site UNLESS you're deliberately pursuing Option A for item -319 — fixing inside
`beginFrameDLChunk` before item -319 hits its 3rd-occurrence threshold pre-empts that thread's own
dedicated investigation and could mask which specific site was the recurring bug.

If the dedupe script shows this tier has also run dry, move to the next-ranked cluster and re-verify
counts, they may have shifted.

**Regen reminder**: the sandbox blocks both a bare `rm -f funcs_*.c` glob and `find ... -delete` on
`RecompiledFuncs/`. Use a Python one-liner instead:
`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
before `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build`.

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s511 (zero new leads — neither of this session's 2 soaks touched an audio-subsystem
crash signature or surfaced a new audio stub/gate lead). Reset to s511, due again s514+. This is a
periodic background check, not an active investigation thread — do not let it consume a full
iteration unless it actually turns something up.

## Fold-in reminder for next session

Read `scratch/agent/SOAK-RESULTS.md`'s tail for `s512_render_lit_mesh_r5_confirm` before doing
anything else. If CLEAN (rc=0 or a crash on an unrelated already-catalogued signature with 0 fires
on the guard itself), `RENDER_LIT_MESH_R5_GUARD` closes 2/2 and item -317 step 3 moves to 15/15
fixed guards fully closed — then proceed with Option A/B above. If it's NOT clean (the guard itself
fired, or an ambiguous/weak-positive-control result per Iron Rule 1), stop and re-derive before
picking a new site — do not fix forward on an unconfirmed guard. Also check whether the crash it
hits (if any) matches item -319/-320/-321/-322's exact `last-guest-pc` — if so, that's a 3rd
occurrence and forces the Option-A pivot for that item.
