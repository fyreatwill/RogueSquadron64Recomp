# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s513 recap — read this first

s513 did three things:

1. **Triaged the s512-queued `RENDER_LIT_MESH_R5_GUARD` 2nd confirm as INCONCLUSIVE, not a valid
   confirm.** The soak (`scratch/agent/soak_results/s512_render_lit_mesh_r5_confirm`) ran the full
   300s (rc=0) but its ~59k-line log has ZERO lines matching `hangar` anywhere — no
   `hangarbay-entry` positive control, no guard fires of any kind. VI oscillated between width
   1024/origin `0x00790400` and width 640/origin `0x00696100` the whole run — neither the war-room
   (`0x6AB400`) nor outdoor (`0x690400`) origin — so the `PROBE_KEYS` schedule never reached the
   hangar-bay scene. Per Iron Rule 1 this doesn't count. Retried unmodified:
   `scratch/agent/soak_queue/s513_render_lit_mesh_r5_confirm_retry.sh` (queued, not yet run by the
   loop as of this writing). `RENDER_LIT_MESH_R5_GUARD` is at 1/2 confirms, NOT closed yet.
2. **Fixed a SIXTH, distinct write site inside `renderLitMeshFaceGroup`** — same function
   R2/R3/R4/R5 already cover, at yet another address (`funcs_4.c:16575`/`0x80014558`,
   `RENDER_LIT_MESH_R6_GUARD`, 38 shared sites, top of the post-R5-regen tier). 1st live-verify:
   **CLEAN, full 300s scheduled duration, zero crashes, zero fires on ANY guard including the
   guard under test** (cleaner than R5's own — no benign co-fire even). 2nd confirm queued:
   `scratch/agent/soak_queue/s513_render_lit_mesh_r6_confirm.sh`.
3. **Re-ran the tracer scan fresh, post-R6-regen** (`s494_item317_step3_tracer.py --scan` +
   `s506_dedupe.py`) so the next-ranked tier below is CURRENT, not stale — see Option B.

No 3rd occurrence of item -319 (`beginFrameDLChunk+40536`, still at 2), item -320, item -321, or
item -322 landed this session. No pivot.

## Read scratch/agent/SOAK-RESULTS.md tail FIRST — TWO pending confirms to fold in

Both `s513_render_lit_mesh_r5_confirm_retry` and `s513_render_lit_mesh_r6_confirm` are queued; the
loop runs up to 2 queued recipes between iterations, so both may already have results waiting.
Check each independently — do not conflate them, they are different guards:

- **R5 retry result**: if CLEAN (rc=0 or a crash on an unrelated already-catalogued signature) AND
  it shows a real `hangarbay-entry` positive control this time, `RENDER_LIT_MESH_R5_GUARD` closes
  2/2. If it's AGAIN missing a positive control, do not retry a third time blindly — read the full
  log first; something about this specific env-var combo or a PROBE_KEYS timing edge may be
  systematically skipping the hangar phase for this particular queued recipe, worth a quick check
  before just re-running.
- **R6 confirm result**: if CLEAN (0 `render-lit-mesh-r6-guard` fires, has a real positive control),
  `RENDER_LIT_MESH_R6_GUARD` closes 2/2.
- If BOTH land clean this session, item -317 step 3 moves to 16/16 fully closed guards (up from
  14/14) — update the USER DIRECTIVE headline and the item -317 body accordingly in one pass, don't
  do a half-update.
- Also check whether either soak's crash (if any) matches item -319/-320/-321/-322's exact
  `last-guest-pc` — if so, that's a 3rd occurrence and forces the Option-A pivot for that item.

## This session's decision point: two options, pick one (after folding in the above)

### Option A: if a 3rd occurrence of item -319, -320, -321, or -322 has landed, pivot to it

Change `HYPOTHESIS-ID` to match (e.g. `item-319-beginframedlchunk-3rd-occurrence` or
`item-322-heapfreelistdequeue-3rd-occurrence`). For item -319, start from the candidate site list
inside `beginFrameDLChunk` below (freshly re-scanned s513). For item -322, source-trace
`heapFreeListDequeue` itself starting from the s457 backtrace (`docs/PROJECT-OVERVIEW.md` §~1270 /
`PORTING-STATE.md` Session 457) — this would be the first dedicated look at that function's own body
since items -316/step-1 already fixed a DIFFERENT bug inside it (2/2 closed, unrelated shape).

Also worth a look if either recurs: item -320 (`loadCutsceneAssetsByIndex+1860`) and item -321
(`menuOverlayInit+3648`) are both still single-occurrence — source-trace on 2nd occurrence regardless
of exact `last-guest-pc` match for -321.

### Option B: continue the `renderLitMeshFaceGroup`/`beginFrameDLChunk` tier (fallback, proven recipe, 16/16 clean so far incl. R6)

**This tier list is CURRENT as of s513 (post-R6-regen) — do NOT re-scan unless you've made a source
edit since reading this**, in which case re-run both:

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
python3 scratch/agent/s506_dedupe.py
```

**Next tier (count=36 and below, s513 fresh scan)**:

```
funcs_3.c:16582  (write, ctx->r2+0x4, beginFrameDLChunk -- item -319's own function, see Option A note)
funcs_3.c:14280  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_3.c:15157  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_4.c:4880   (write, ctx->r2+0x4, submitSceneNodeRender)
funcs_3.c:14763  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_3.c:16107  (write, ctx->r2+0x4, beginFrameDLChunk)
funcs_4.c:15620  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- a SEVENTH site, if the family keeps paying off)
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

Last checked s511 (zero new leads). Due again s514+. This is a periodic background check, not an
active investigation thread — do not let it consume a full iteration unless it actually turns
something up.

## Fold-in reminder for next session

Read `scratch/agent/SOAK-RESULTS.md`'s tail for BOTH `s513_render_lit_mesh_r5_confirm_retry` and
`s513_render_lit_mesh_r6_confirm` before doing anything else — see the dedicated section above.
