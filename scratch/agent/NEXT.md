# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s514 recap — read this first

s514 did four things:

1. **Folded in both of s513's pending confirms and CLOSED both 2/2**: `RENDER_LIT_MESH_R5_GUARD`'s
   retried 2nd confirm (this time with a valid `hangarbay-entry n=2600` positive control — s513's
   missing-positive-control problem did not recur) crashed on an already-catalogued
   `rebuildActiveDisplayObjectList+540`/`last-guest-pc=0x800ab060` signature (byte-identical match at
   `PORTING-STATE.md:41991`), unrelated; `RENDER_LIT_MESH_R6_GUARD`'s 2nd confirm crashed on the
   already-catalogued async Metal-shader-compiler-thread cluster (`last-guest-pc=0x800ab0e0`, items
   -10/-9), unrelated. **Item -317 step 3 is now 16/16 fully closed guards** (up from 14/14).
2. **Fixed a SEVENTH, distinct write site inside `renderLitMeshFaceGroup`** —
   `RENDER_LIT_MESH_R7_GUARD` (`funcs_4.c:15620`/`0x80014140`, 32 shared reload sites). 1st
   live-verify: **clean on the guard itself** (0 fires, `hangarbay-entry n=2600` positive control, 4
   benign init-time co-fires), but crashed on a genuinely NEW signature. 2nd confirm queued:
   `scratch/agent/soak_queue/s514_render_lit_mesh_r7_confirm.sh`.
3. **Filed item -323** (`beginFrameDLChunk+27456`/`last-guest-pc=0x8000ae40`, single occurrence) —
   same function as item -319's own recurring crash but a DIFFERENT `last-guest-pc`
   (`0x8000b0d0`), so NOT the same crash per the s422 overturned-conclusion precedent. Watch for a
   2nd occurrence.
4. **Cleaned up a pre-existing corruption artifact** at the tail of `PORTING-STATE.md`: a prior
   session's Edit-tool-call XML (`</new_string></invoke>`) had leaked into the actual file content
   instead of being executed. Removed, no ledger content lost.

M5 cadence check: grepped s506-s513's soak logs for any audio-subsystem signature, zero hits. Reset
to s514, due again s517+.

No 3rd occurrence of item -319, -320, -321, or -322 landed this session. No pivot.

## Read scratch/agent/SOAK-RESULTS.md tail FIRST — ONE pending confirm to fold in

`s514_render_lit_mesh_r7_confirm` is queued; the loop runs up to 2 queued recipes between
iterations, so it may already have a result waiting.

- **R7 confirm result**: if CLEAN (0 `render-lit-mesh-r7-guard` fires, has a real `hangarbay-entry`
  positive control — check this carefully, s512/s513 both had one attempt come back missing it),
  `RENDER_LIT_MESH_R7_GUARD` closes 2/2 and item -317 step 3 moves to 17/17. Update the USER
  DIRECTIVE headline and the item -317 body in one pass.
- If it's missing a positive control, don't blindly retry a 3rd time — read the full log first (same
  triage s513 did for R5's first attempt).
- Check whether its crash (if any) matches item -319/-320/-321/-322/-323's exact `last-guest-pc`. If
  it matches -319 or -323 exactly, that could be a 3rd occurrence (for -319) or a 2nd occurrence (for
  -323) — check both.

## This session's decision point: two options, pick one (after folding in the above)

### Option A: if a 3rd occurrence of item -319/-320/-321/-322, or a 2nd of item -323, has landed, pivot to it

Change `HYPOTHESIS-ID` to match. For item -319 or -323 (both inside `beginFrameDLChunk`), start from
the candidate site list below — re-scan first, it's one guard insertion stale. For item -322,
source-trace `heapFreeListDequeue` itself starting from the s457 backtrace
(`docs/PROJECT-OVERVIEW.md` §~1270 / `PORTING-STATE.md` Session 457).

### Option B: continue the `renderLitMeshFaceGroup`/`beginFrameDLChunk` tier (fallback, proven recipe, 17/17 clean so far incl. R7)

**MUST re-scan before picking — the s513 scan is now one guard insertion stale (R7 added s514)**:

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
python3 scratch/agent/s506_dedupe.py
```

Last known tier (count=36 and below, s513 scan, NOW STALE):

```
funcs_3.c:16582  (write, ctx->r2+0x4, beginFrameDLChunk -- items -319/-323's own function)
funcs_3.c:14280  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_3.c:15157  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_4.c:4880   (write, ctx->r2+0x4, submitSceneNodeRender)
funcs_3.c:14763  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_3.c:16107  (write, ctx->r2+0x4, beginFrameDLChunk)
```

**Prefer `submitSceneNodeRender` (funcs_4.c:4880) over any `beginFrameDLChunk` site** unless
deliberately pursuing Option A for item -319/-323 — fixing inside `beginFrameDLChunk` before either
hits its escalation threshold (3rd occurrence for -319, 2nd for -323) risks masking which specific
site is the recurring bug. `renderLitMeshFaceGroup` itself may be dry after 7 guards (R2-R7); the
fresh scan will show whether an 8th site still exists in that function or the tier has moved on.

**Regen reminder**: the sandbox blocks both a bare `rm -f funcs_*.c` glob and `find ... -delete` on
`RecompiledFuncs/`. Use a Python one-liner instead:
`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
before `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build`.

## Maintenance heads-up

`docs/CURRENT-TRUTH.md` is at 58,277 bytes as of s514 — under the 60,000-byte trigger but close.
Next session that crosses it becomes a MAINTENANCE iteration per Step 0 of ITERATION.md.

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s514 (zero new leads). Due again s517+. Periodic background check only.
