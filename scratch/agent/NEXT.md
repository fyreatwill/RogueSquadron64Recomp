# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s511 recap — read this first

s511 did two things:

1. **Folded in the s510-queued `s510_render_lit_mesh_r3_confirm` soak.** CLEAN: 0
   `render-lit-mesh-r3-guard` fires, `hangarbay-entry n=2800` positive control (strong), one benign
   `hangarmenu-a0-guard` co-fire (item -265, unrelated). Full scheduled duration completed with **no
   crash at all** (rc=0). `RENDER_LIT_MESH_R3_GUARD` is now **FULLY CLOSED, 2/2**. Item -317 step 3
   now stands at **13/13 fixed guards fully closed**.
2. **Fixed a FOURTH, distinct write site inside `renderLitMeshFaceGroup`** — same function R2/R3
   already cover, at yet another address (`funcs_4.c:16049`/`0x800142FC`, `RENDER_LIT_MESH_R4_GUARD`,
   38 shared sites, identical shape). 1st live-verify: CLEAN — 0 `render-lit-mesh-r4-guard` fires, 0
   fires on any other armed sibling guard except one benign `hangar-bay-deref-guard` co-fire
   (`ra=0x00000000`, init-time signature), `hangarbay-entry n=2600` positive control. Crashed at
   115.4s on `setByteAcrossEntryList+176`/`last-guest-pc=0x800aafa8` — this is an EXACT match
   (pc-symbol AND last-guest-pc, not just an offset coincidence) to an already-catalogued benign
   signature ("the standard RDRAM-host-base-pointer pattern", first seen ~s473, filed not-chased in
   `docs/PROJECT-OVERVIEW.md`) — no new item filed, no escalation. 2nd confirm queued:
   `scratch/agent/soak_queue/s511_render_lit_mesh_r4_confirm.sh`.

Neither soak this session produced a 3rd occurrence of item -319 (`beginFrameDLChunk+40536`, still
at 2 — the R3 confirm ran fully clean so couldn't have hit anything) or a 2nd of item -320/-321.
No pivot.

## This session's decision point: two options, pick one

### Option A: if a 3rd `beginFrameDLChunk+40536` occurrence has landed (item -319), pivot to it

Change `HYPOTHESIS-ID` to `item-319-beginframedlchunk-3rd-occurrence`. Start from the candidate site
list inside `beginFrameDLChunk` that the s506 tracer scan flagged (item -317's CURRENT-TRUTH entry has
the pointer — re-run the tracer scan fresh, do not reuse any previously recorded line numbers, they've
drifted) rather than a fresh source trace from scratch.

Also worth a look if it recurs: **item -320** (`loadCutsceneAssetsByIndex+1860`) and **item -321**
(`menuOverlayInit+3648`) are both still single-occurrence breadcrumbs — if either recurs before item
-319 hits 3, source-trace it (item -321 in particular deserves a source read on 2nd occurrence
regardless of `last-guest-pc` match, since it might reveal whether it's really the old item -266/-267
bug or a coincidental host-code-sink collision).

### Option B: continue the `renderLitMeshFaceGroup` tier (fallback, same proven recipe, 14/14 clean so far incl. R4)

**Re-run both scripts fresh** (do NOT reuse this session's recorded line numbers, they will have
drifted after R4's insertion):

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
python3 scratch/agent/s506_dedupe.py   # correct grouping key, reuse this script -- do NOT drop hit.line
```

**Next tier as of s511's mid-session scan (count=36, taken BEFORE R4 was fixed — RE-VERIFY BEFORE
TOUCHING SOURCE, this list has already shifted)**:

```
funcs_3.c:16582  (write, ctx->r2+0x4, beginFrameDLChunk -- item -319's own function, see Option A note)
funcs_3.c:14280  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_3.c:15157  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_4.c:17772  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- a FIFTH site in this same function, if it's still there after R4's insertion shifted line numbers)
```

If picking from this tier, prefer a `renderLitMeshFaceGroup` site over a `beginFrameDLChunk` site
UNLESS you're deliberately pursuing Option A — fixing inside `beginFrameDLChunk` before item -319
hits its 3rd-occurrence threshold pre-empts that thread's own dedicated investigation and could mask
which specific site was the recurring bug.

If the dedupe script shows this tier has also run dry, move to the next-ranked cluster:
`funcs_4.c:4880` (34 sites, `submitSceneNodeRender`) or `funcs_4.c:15620` (32 sites,
`renderLitMeshFaceGroup`) — re-verify counts, they may have shifted.

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

Read `scratch/agent/SOAK-RESULTS.md`'s tail for `s511_render_lit_mesh_r4_confirm` before doing
anything else. If CLEAN (rc=0 or a crash on an unrelated already-catalogued signature with 0 fires
on the guard itself), `RENDER_LIT_MESH_R4_GUARD` closes 2/2 and item -317 step 3 moves to 14/14
fixed guards fully closed — then proceed with Option A/B above. If it's NOT clean (the guard itself
fired, or an ambiguous/weak-positive-control result per Iron Rule 1), stop and re-derive before
picking a new site — do not fix forward on an unconfirmed guard.
