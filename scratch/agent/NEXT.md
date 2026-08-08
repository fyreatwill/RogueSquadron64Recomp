# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s518 recap -- read this first

s518 did two things, no code changes:

1. **Folded in the loop-run s517 confirm for item -322** (`heapFreeListDequeue` stack-slot-derived
   pointer write, `HEAPLISTDEQ_ATTR_WRITE_GUARD`): ran the FULL 347s scheduled duration with **zero
   crashes of any kind** (not even the background-noise family the 1st verify hit) and 0 guard fires,
   `hangarbay-entry n=2700` positive control. **Item -322 is now CLOSED 2/2.**

2. **Source-traced item -321** (`menuOverlayInit`-area, `last-guest-pc=0x800ab1c4`, previously flagged
   as meeting its 2-occurrence escalation bar with a pc-symbol-mismatch caveat) and **REFUTED the
   escalation**: `0x800AB1C4` is `runHangarSelectionFrame`'s own return-epilogue instruction
   (`N64Recomp/RecompiledFuncs/funcs_28.c:6019`, pure `$sp` arithmetic, not a memory access -- cannot
   fault), and the breadcrumb tracker has zero coverage one level up in either caller
   (`runHangarMenuFromOverlay`, `menuOverlayInit` -- grep-verified 0 `g_rs64_last_guest_pc` writes in
   both). Same breadcrumb-freeze-at-return artifact class as item -263's `BREADCRUMB17`->`18` pair
   (s437/s439). The matching `last-guest-pc` between s510/s515 means "both unwound out of the same
   function," not a shared fault site -- they're plausibly two different downstream crashes. Item -321
   is downgraded to a documented instrumentation gap, not queued as active work (a `BREADCRUMB19` fix
   for `runHangarMenuFromOverlay` is described in `docs/CURRENT-TRUTH.md` item -321 if a future
   recurrence needs it, but nothing currently warrants it).

Both items fully written up: `docs/CURRENT-TRUTH.md` items -321/-322, `PORTING-STATE.md` Session 518.

**M5 audio-lead cadence**: not checked this session (s518 was analysis-only, produced no new run log
to grep). Last checked s517 (clean, cadence reset to s517). Due again s520+; check the next session
that produces a fresh run log.

## The work unit: resume item -317 step 3's blanket sweep

With items -321 and -322 both resolved (closed / refuted), item -317 step 3 is the top-ranked M3 work
unit again. **Re-scan first** -- the last scan (s515) is stale by three guard insertions since (R7,
SUBMIT_SCENE_NODE_RENDER_R1, and s517's HEAPLISTDEQ_ATTR_WRITE, though the latter is in a different
function/file and likely doesn't shift line numbers in the scanned files):

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
python3 scratch/agent/s506_dedupe.py
```

Known tier from the s515 scan (STALE, re-verify against the fresh scan output before committing to a
pick): three `beginFrameDLChunk` sites at count=36 (items -319/-323's own function, still deliberately
skip -- fixing inside it pre-empts those threads' own escalation), `funcs_3.c:14763`/`funcs_3.c:16107`
(32 sites, `beginFrameDLChunk`), then a count=30 group including a possible EIGHTH
`renderLitMeshFaceGroup` site (`funcs_4.c:15153`). **Prefer `renderLitMeshFaceGroup` or non-
`beginFrameDLChunk` sites** (fixing inside `beginFrameDLChunk` pre-empts items -319/-323's own
dedicated threads). 18/18 guards fixed so far, all fully closed 2/2. ~127 locations remain unaudited.
Full guard table and gotchas: `docs/PROJECT-OVERVIEW.md` §22-§23, `PORTING-STATE.md` Sessions 490-518.

**Regen reminder** (verify each step -- this has bitten prior sessions when skipped):
1. Delete all `funcs_*.c` in `N64Recomp/RecompiledFuncs/` first and confirm `0 remaining` -- stale
   files silently survive a partial regen otherwise.
2. `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build . -j8`
   (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` prefix for Metal shader rebuilds).
3. Grep the fixup report AND the freshly-generated source for the new guard's own name -- a silent
   no-op (rc=0, no error, 0 applied) has happened before when a function carried its own pre-existing
   breadcrumb patch and the guard's old/new match string didn't include the inserted line
   (`SUBMIT_SCENE_NODE_RENDER_R1_GUARD`'s gotcha, s515).
4. Live-verify manually in the foreground with every sibling guard's env var armed plus the new
   guard's own `ROGUESQ_LOG_<NAME>=1`, phase-gate on `hangarbay-entry` as the positive control (Iron
   Rule 1 -- a null result needs a same-run positive control). If clean, queue a 2nd independent
   confirm to `scratch/agent/soak_queue/` for the loop to run between iterations, following the
   existing recipe shape (see any `scratch/agent/soak_queue/done/s51*_*.sh` for the template).

`fixup_game_funcs.py` and the regenerated `RecompiledFuncs/*.c` live in the sibling `N64Recomp`
checkout (untracked by its own git) -- not this repo's git tree. This repo's ledger entries (with the
full old/new patch text) are the only durable record of every guard in this lineage since s481; no
`lib/` submodule involvement, no `export.sh` needed for this work.

## Discriminating measurement for the next lead

Same shape every time in this lineage: does the guard itself ever fire (would indicate the reload IS
sometimes invalid, i.e. the fix is load-bearing) vs. 0 fires with a real positive control (null result,
guard is precautionary/dormant but the campaign's own precedent says these are cheap and correct to
add regardless -- see item -317's methodology note in `docs/PROJECT-OVERVIEW.md` §22). A crash during
the live-verify that hits a DIFFERENT, already-catalogued signature is not evidence against the guard
(same disposition as items -317R2 through -322); a NEW uncatalogued signature gets filed as its own
single-occurrence item, not chased further this session.
