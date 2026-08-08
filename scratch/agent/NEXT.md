# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s517 recap -- read this first

s517 source-traced and FIXED item -322 (`heapFreeListDequeue`/`last-guest-pc=0x8000d92c`, escalated
at s515 to 3 occurrences: s457, s512, s515). Added `HEAPLISTDEQ_ATTR_WRITE_GUARD` (`fixup_game_funcs.py`,
`funcs_3.c:0x8000D92C`) guarding a stack-slot-derived pointer (loaded unguarded from `0x3C($sp)`,
itself filled far upstream from a fixed-global-array-base + `index<<2` computation) before a
write-through. 1st live-verify (manual, foreground, full sibling-guard env-var set): **CLEAN** -- 0
`heaplistdeq-attr-write-guard` fires, 1 benign `hangarmenu-a0-guard` co-fire (item -265, already
catalogued), `hangarbay-entry n=34` positive control. Crashed at 121.2s on the already-catalogued
`coalesceFreeHeapBlocks+4424`/`last-guest-pc=0x8000247c` background-noise family (documented since
s354-366), unrelated to this guard. 2nd independent confirm queued:
`scratch/agent/soak_queue/s517_heaplistdeq_attr_write_confirm.sh`.

**Side finding (not chased, noted for later)**: `heapFreeListDequeue`'s tail (`0x8000D8xx`-`0x8000D9xx`)
reads like vertex/face-attribute-copy code (calls `transformAndEmitFaceVertices`), not heap
bookkeeping -- plausibly this function is a generic pooled-buffer-dequeue-with-eviction helper shared
across heap AND display-list/vertex-buffer pools, not heap-only. Doesn't change the fix (address-scoped
either way); flagged in case a future session needs the real semantics.

**Also resolved a tooling red herring**: the `pc-symbol+NNNN` offset in crash logs is a NATIVE code
offset (from `nm` against the native crash PC, per `src/main/main.cpp`'s handler), NOT a guest-address
delta -- never use it to estimate a guest-side offset within a function. Only `last-guest-pc` is
reliable for that. Worth remembering if a future item's occurrences show `pc-symbol` offset drift like
item -322's did (32596→40432) -- that drift is expected guard-insertion layout noise in the *native*
binary, not evidence of anything about guest-side identity.

**M5 audio-lead cadence check (independent of rule 8)**: grepped this session's own log
(`scratch/agent/soak_results/s517_heaplistdeq_attr_write_manual/run.log`) for
`musyx`/`waitForAnyAudioSlot`/`audio-slot`/`audio-voice` -- one hit, `[audio-wait-pump-stall]
countdown=16 after 64 musyxSynthFrame pumps`, already-catalogued (appears in prior sessions' logs
too, not new). Zero new audio-subsystem lead. Cadence reset to s517, due again s520+.

Full detail: `PORTING-STATE.md` Session 517, `docs/CURRENT-TRUTH.md` item -322.

## The work unit: fold in the s517 confirm, or resume item -317 step 3's tier

**Step 1**: check `scratch/agent/SOAK-RESULTS.md` tail for a line mentioning
`s517_heaplistdeq_attr_write_confirm`. If present:
- Read its log (`scratch/agent/soak_results/s517_heaplistdeq_attr_write_confirm_*.log` + `run.log`).
- If clean on `heaplistdeq-attr-write-guard` (0 fires) with a real `hangarbay-entry` positive control:
  item -322 is CLOSED 2/2. Update `docs/CURRENT-TRUTH.md` item -322 to reflect full closure, move
  `scratch/agent/soak_queue/s517_heaplistdeq_attr_write_confirm.sh` awareness (the loop already moves
  consumed recipes to `soak_queue/done/` automatically), then proceed to item -321's source-trace (the
  2nd-priority M3 thread, `menuOverlayInit`-area / `last-guest-pc=0x800ab1c4`, 2 occurrences with a
  pc-symbol-mismatch caveat -- see CURRENT-TRUTH item -321 for the caveat and what "source-trace to
  confirm identity" means there) as this iteration's work unit.
- If it fired or was inconclusive: treat as a real finding, don't just re-queue blindly -- read the
  log fully before deciding next steps (Iron Rule 1: a null result needs a positive control; a FIRING
  result needs the same rigor before concluding it's real corruption vs. an artifact).

**Step 2** (if the confirm hasn't run yet, or after closing item -322): resume item -317 step 3's
~150-location blanket sweep at its next-ranked lead. **Re-scan first** -- the s515 scan is now stale
by two guard insertions (R7 + SUBMIT_SCENE_NODE_RENDER_R1) plus this session's HEAPLISTDEQ_ATTR_WRITE:
```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
python3 scratch/agent/s506_dedupe.py
```
Known tier from the s515 scan (STALE, re-verify): three `beginFrameDLChunk` sites at count=36 (items
-319/-323's own function, still deliberately skip -- fixing inside it pre-empts those threads' own
escalation), `funcs_3.c:14763`/`funcs_3.c:16107` (32 sites, `beginFrameDLChunk`), then a count=30
group including a possible EIGHTH `renderLitMeshFaceGroup` site (`funcs_4.c:15153`). Prefer
`renderLitMeshFaceGroup` or non-`beginFrameDLChunk` sites. 18/18 guards fixed so far, all fully closed
2/2 (item -317 step 3 tally, unaffected by item -322's separate fix). Full guard table and gotchas:
`docs/PROJECT-OVERVIEW.md` §22-§23, `PORTING-STATE.md` Sessions 490-517.

**Regen reminder** (verify each step, don't trust silence -- s515 hit a silent 0-count fixup skip):
```
python3 -c "import glob, os; files = glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c'); [os.remove(f) for f in files]; print(len(glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')), 'remaining')"
```
Confirm it prints `0 remaining` before running `make_elf.py` (`cd rogue_squadron64 && python3
tools/make_elf.py`) -> `N64Recomp` (`cd N64Recomp && ./build/N64Recomp rogue_squadron.toml`) ->
`fixup_game_funcs.py` (`cd N64Recomp && python3 fixup_game_funcs.py`). After fixup, grep its report
output for the new guard's own name -- a clean exit code is NOT sufficient evidence the patch landed
(functions with their own pre-existing `g_rs64_last_guest_pc` breadcrumb patches need that line
included in the old/new match strings, or the match silently fails 0-for-1). Then
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8` from `build/`.

## Reminder: item -319/-320/-321/-323 status

- Item -319 (`beginFrameDLChunk+40536`): 2 occurrences (s503, s505). Unchanged s517.
- Item -320 (`loadCutsceneAssetsByIndex+1860`): 1 occurrence (s508). Unchanged s517.
- Item -321 (`menuOverlayInit`-area/`last-guest-pc=0x800ab1c4`): 2 occurrences (s510, s515) -- meets
  its own escalation bar but with a pc-symbol-mismatch caveat. 2nd-priority M3 thread, behind item
  -322's confirm (see Step 1 above).
- Item -323 (`beginFrameDLChunk+27456`): 1 occurrence (s514). Unchanged s517.

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s517 (zero new leads, see recap above). Due again s520+. Periodic background check only
-- not due yet.
