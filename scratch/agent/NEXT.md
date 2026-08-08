# NEXT work unit

HYPOTHESIS-ID: item-322-heapfreelistdequeue-source-trace

## s516 recap -- read this first

s516 was a MAINTENANCE iteration (Step 0 triggered: CURRENT-TRUTH.md was 60,308 bytes, over the
60,000 cap). It did three things:

1. **Folded in the s515-queued `SUBMIT_SCENE_NODE_RENDER_R1_GUARD` 2nd confirm**: CLEAN, 0 fires,
   real `hangarbay-entry` positive control (n=2700), one benign co-fire. Item -317 step 3 is now
   **18/18 fully closed 2/2 guards**.
2. **The confirm's crash surfaced item -321's 2nd occurrence**: `last-guest-pc=0x800ab1c4`,
   byte-identical to item -321's single s510 sighting. Meets item -321's own stated 2-occurrence
   escalation bar -- BUT this occurrence's `pc-symbol` (`unregisterServiceWorker+536`) is a completely
   different function name from s510's (`menuOverlayInit+3648`), not the offset-only drift every other
   repeat signature in this campaign has shown. Flagged as escalated-with-a-caveat: source-trace it to
   confirm identity, don't assume it. Queued as the 2nd-priority M3 thread, behind item -322.
3. **Compacted `docs/CURRENT-TRUTH.md`**: 60,308 -> 45,613 bytes (655 -> 410 lines, 245 net lines
   removed). Migrated the item -317 step 3 continuation (10 guards, s506-515) and item -318's full
   mechanism to `docs/PROJECT-OVERVIEW.md` §23. Left CURRENT-TRUTH items -317 through -323 as short
   current-status pointers into §22-§23.

Full detail: `PORTING-STATE.md` Session 516, `docs/CURRENT-TRUTH.md` items -317/-321/-322,
`docs/PROJECT-OVERVIEW.md` §23.

## The work unit: source-trace item -322 (`heapFreeListDequeue`)

`heapFreeListDequeue`/`last-guest-pc=0x8000d92c` has three independent occurrences now (s457, s512,
s515), all sharing the exact `last-guest-pc`, surfaced from three different guard-under-test contexts
(never the guard itself). This is the single highest-priority work unit -- it already hit the
campaign's 3-occurrence escalation threshold, ranking above the item -317 step 3 tier itself.

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
   by item -311), treat this as genuinely `heapFreeListDequeue` -- don't re-dismiss it as an artifact.
3. Look for the same shape every item -317-lineage fix has had: a derived-pointer reload with a null
   check but no `0x80000000`-`0x80800000` range check on the non-null fallthrough before a
   dereference or write-through.
4. If `last-guest-pc=0x8000d92c` maps to a specific instruction inside `heapFreeListDequeue` (compute
   via `nm`/`objdump` on the recompiled binary or by matching the guest address against the function's
   known base), that pins the exact faulting instruction rather than requiring a blind full-function
   audit. **Note from s516**: writing `nm` output to a file via shell redirection was blocked by the
   sandbox this session (both `/tmp` and `scratch/` destinations needed approval) -- if that recurs,
   either accept the approval prompt or work from the tool's direct stdout instead of a redirect.
5. Fix with the same skip-on-invalid pattern as every prior guard in this lineage (the function's own
   step-1 guards from the -312..-316 lineage may be a useful reference for shape, since
   `heapFreeListDequeue` was ALSO step 1 of that earlier sweep -- check whether this is a genuinely
   new site or a gap in that earlier audit).
6. Live-verify with the full armed env-var set (every existing guard, plus the new one) -- 1st
   live-verify clean on the guard itself is the discriminating result. Queue the 2nd confirm per the
   standing pattern.

### Fallback if item -322 doesn't pin to one instruction quickly

If step 4 doesn't cleanly resolve to a single guarded site, fall back to Option B: resume item -317
step 3's tier (18/18 closed, ~127 leads remain) at the next-ranked lead. Re-scan first
(`s494_item317_step3_tracer.py --scan` + `scratch/agent/s506_dedupe.py`) -- the s515 scan is now two
guard insertions stale (R7 + SUBMIT_SCENE_NODE_RENDER_R1). Known tier from the s515 scan (STALE,
re-verify): three `beginFrameDLChunk` sites at count=36 (items -319/-323's own function, still
deliberately skip), `funcs_3.c:14763`/`funcs_3.c:16107` (32 sites, `beginFrameDLChunk`), then a
count=30 group including a possible EIGHTH `renderLitMeshFaceGroup` site (`funcs_4.c:15153`).

**Regen reminder** (verify each step, don't trust silence -- s515 hit a silent 0-count fixup skip):
```
python3 -c "import glob, os; files = glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c'); [os.remove(f) for f in files]; print(len(glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')), 'remaining')"
```
Confirm it prints `0 remaining` before running `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`.
After `fixup_game_funcs.py`, grep its report output for the new guard's own name -- a clean exit code
is NOT sufficient evidence the patch landed. Then `cmake --build . -j8`.

## Reminder: item -319/-320/-321/-323 status

- Item -319 (`beginFrameDLChunk+40536`): 2 occurrences (s503, s505). Unchanged s516.
- Item -320 (`loadCutsceneAssetsByIndex+1860`): 1 occurrence (s508). Unchanged s516.
- Item -321 (`menuOverlayInit`-area/`last-guest-pc=0x800ab1c4`): **2 occurrences now (s510, s515)** --
  meets its own escalation bar but with a pc-symbol-mismatch caveat (see recap above). 2nd-priority M3
  thread, behind item -322.
- Item -323 (`beginFrameDLChunk+27456`): 1 occurrence (s514). Unchanged s516.

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s514 (zero new leads). Due again s517+. Periodic background check only -- not due yet.
