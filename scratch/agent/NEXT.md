# NEXT work unit

HYPOTHESIS-ID: item-322-heapfreelistdequeue-source-trace

## STOP: this iteration starts as MAINTENANCE

`docs/CURRENT-TRUTH.md` is 60,308 bytes as of s515 -- over the 60,000-byte Step-0 trigger in
`tools/agent/ITERATION.md`. Run `wc -c < docs/CURRENT-TRUTH.md` to confirm, then compact per the
Maintenance section (migrate durable material to `docs/PROJECT-OVERVIEW.md`, prune/merge superseded
and closed Next-steps items, keep the numbering monotonic, refresh the stale "as of session N"
headline). A net shrink of >=200 lines counts as ADVANCED. Do NOT run experiments (including the
item -322 work below) in the same iteration as a triggered maintenance pass -- do maintenance first,
then item -322 becomes the FOLLOWING iteration's work unit.

## s515 recap -- read this first

s515 did three things:

1. **Folded in s514's queued `RENDER_LIT_MESH_R7_GUARD` 2nd confirm**: CLEAN, 0 fires, real
   `hangarbay-entry` positive control, full 300s duration with zero crash at all. CLOSED 2/2. Item
   -317 step 3 is now **17/17 fully closed guards** (up from 16/16).
2. **Fixed `SUBMIT_SCENE_NODE_RENDER_R1_GUARD`** (`funcs_4.c:4880`/`0x80010F38`, `submitSceneNodeRender`,
   34 shared reload sites) -- the tier's first site outside `renderLitMeshFaceGroup`/
   `emitFrameRdpInitDl`, found by a fresh re-scan after `renderLitMeshFaceGroup` appeared dry post-R7.
   Hit and fixed a real gotcha along the way: `submitSceneNodeRender` carries its own pre-existing
   per-instruction `g_rs64_last_guest_pc = ...;` breadcrumb patch, which broke the naive R7-style
   old/new string template (silent 0-count match, no error) until the breadcrumb line was added to
   both strings. **Lesson for the next guard in this lineage: always grep the fixup report for the
   new guard's own name after every run**, not just check for "no error." 1st live-verify: clean on
   the guard itself (0 fires, real positive control, 2 benign co-fires, no regression). 2nd confirm
   queued: `scratch/agent/soak_queue/s515_submit_scene_node_render_r1_confirm.sh`.
3. **Item -322 (`heapFreeListDequeue`/`last-guest-pc=0x8000d92c`) hit its 3RD independent occurrence**
   (the crash SUBMIT_SCENE_NODE_RENDER_R1_GUARD's 1st live-verify landed on) -- ESCALATED past the
   campaign's 3-occurrence dedicated-thread threshold (same threshold item -318's `appendRdpStateDl`
   used before its own fix). This is now the single highest-priority work unit, ranking above the
   item -317 step 3 tier itself.

Full detail: `PORTING-STATE.md` Session 515, `docs/CURRENT-TRUTH.md` items -317/-322.

## The work unit (AFTER maintenance, if Step 0 triggered it): source-trace item -322

`heapFreeListDequeue`/`last-guest-pc=0x8000d92c` has three independent occurrences now (s457, s512,
s515), all sharing the exact `last-guest-pc`, surfaced from three different guard-under-test
contexts (never the guard itself). Per item -311, post-s480 crashes carry a real `(local-symtab)`
`pc-symbol` -- but the `pc-symbol` offset has drifted across all three sightings (32596 -> 40432,
expected guard-insertion code-layout drift), so `last-guest-pc` is the reliable identity signal, not
the offset.

**s457's full backtrace** (the strongest evidence -- a real `heapFreeListDequeue` frame, not just a
`pc-symbol` guess):
```
heapFreeListDequeue <- submitSceneNodeRender <- processSceneNode <- traverseSceneGraphRecursive
<- setupCameraMatrices <- runHangarSelectionFrame <- runHangarMenuFromOverlay <- menuOverlayInit
<- mainGameLoop
```
Full detail: `PORTING-STATE.md` Session 457 (grep for it).

### Discriminating approach

1. Grep `RecompiledFuncs/funcs_3.c` and `funcs_4.c` for `heapFreeListDequeue` to find its definition
   and every call site.
2. Read the function body. Per item -310's now-superseded false lead (a symbolizer blind spot, FIXED
   by item -311), treat this as genuinely `heapFreeListDequeue` -- don't re-dismiss it as an
   artifact.
3. Look for the same shape every item -317-lineage fix has had: a derived-pointer reload with a null
   check but no `0x80000000`-`0x80800000` range check on the non-null fallthrough before a
   dereference or write-through.
4. If `last-guest-pc=0x8000d92c` maps to a specific instruction inside `heapFreeListDequeue` (compute
   via `nm`/`objdump` on the recompiled binary or by matching the guest address against the function's
   known base), that pins the exact faulting instruction rather than requiring a blind full-function
   audit.
5. Fix with the same skip-on-invalid pattern as every prior guard in this lineage (the function's own
   step-1 guards from the -312..-316 lineage may be a useful reference for shape, since
   `heapFreeListDequeue` was ALSO step 1 of that earlier sweep -- check whether this is a genuinely
   new site or a gap in that earlier audit).
6. Live-verify with the full armed env-var set (every existing guard, plus the new one) -- 1st
   live-verify clean on the guard itself is the discriminating result. Queue the 2nd confirm per the
   standing pattern.

### Fallback if item -322 doesn't pin to one instruction quickly

If step 4 doesn't cleanly resolve to a single guarded site (e.g. `heapFreeListDequeue` has many
similarly-shaped reloads and the backtrace alone doesn't disambiguate), fall back to Option B: resume
item -317 step 3's tier (now 17/17 closed, `SUBMIT_SCENE_NODE_RENDER_R1_GUARD` making 18 fixed) at
the next-ranked lead. Re-scan first (`s494_item317_step3_tracer.py --scan` +
`scratch/agent/s506_dedupe.py`) -- s515's scan is already one guard insertion stale. Known tier from
the s515 scan (STALE, re-verify): three `beginFrameDLChunk` sites at count=36 (items -319/-323's own
function, still deliberately skip), `funcs_3.c:14763`/`funcs_3.c:16107` (32 sites,
`beginFrameDLChunk`), then a count=30 group including a possible EIGHTH `renderLitMeshFaceGroup` site
(`funcs_4.c:15153` -- that function may not be fully dry after all).

**Regen reminder** (a real gotcha hit this session -- verify each step, don't trust silence):
```
python3 -c "import glob, os; files = glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c'); [os.remove(f) for f in files]; print(len(glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')), 'remaining')"
```
Confirm it prints `0 remaining` before running `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`.
After `fixup_game_funcs.py`, grep its report output for the new guard's own name -- a clean exit code
is NOT sufficient evidence the patch landed (s515 hit exactly this: rc 0, no error, but a silent
0-count skip). Then `cmake --build . -j8`.

## Reminder: item -319/-320/-321/-323 status (unchanged this session)

- Item -319 (`beginFrameDLChunk+40536`): 2 occurrences (s503, s505). No 3rd this session.
- Item -320 (`loadCutsceneAssetsByIndex+1860`): 1 occurrence (s508). No 2nd this session.
- Item -321 (`menuOverlayInit+3648`): 1 occurrence (s510), possible item -266/-267 recurrence. No 2nd
  this session.
- Item -323 (`beginFrameDLChunk+27456`): 1 occurrence (s514). No 2nd this session.

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s514 (zero new leads). Due again s517+. Periodic background check only -- not due yet.
