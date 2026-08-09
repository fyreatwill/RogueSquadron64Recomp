# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s555 recap (read this first)

**Folded in s554's queued confirm — CLEAN, FULLY CLOSED 2/2.**
`s554_count3_count2_twentyseven_way_confirm` (guards 88-114): CLEAN full ~300s (rc=0, 114 frames),
`hangarbay-entry n=3000`, 0 fires on all 27, NO crash. Campaign briefly at 114/114 with zero pending.

**Fresh tracer re-scan of classic r2/0X4: only count=7 shape-mismatch (skipped) + count=1 classic
left.** Fixed the last classic site as guard 115 `HEAP_FREE_LIST_INSERT_R1_GUARD` site=`0x800079D8`
(`heapFreeListInsert`, new function to the R-numbered lineage). 1st live-verify clean
(`hangarbay-entry n=2700`, 0 fires, 0 log lines for the new tag); crashed on known s354-366
`coalesceFreeHeapBlocks+4424`/`0x8000247c`. 2nd confirm queued:
`scratch/agent/soak_queue/s555_count1_heap_free_list_insert_r1_confirm.sh`.

Campaign totals: **115 fixed, 114 FULLY CLOSED 2/2, 1 pending confirm** (115).
**Classic r2/0X4 unaudited classic sites: 0 remaining** after this guard.

## This iteration's work unit

**Step 1 — fold in the queued confirm result (do this FIRST).**

1. `s555_count1_heap_free_list_insert_r1_confirm` (2nd confirm for guard 115): expect 0 fires on
   `heap-free-list-insert-r1-guard`, double-digit+ `hangarbay-entry`. If clean: mark guard 115
   FULLY CLOSED 2/2.
2. Update `docs/PROJECT-OVERVIEW.md` §25 + `docs/CURRENT-TRUTH.md` item -317. **If the confirm
   surfaces a fire, this is a MAJOR finding — investigate instead of pivoting.**
3. If WEAK (no hangarbay / single-digit / item -306 early death): discard and re-queue retry
   immediately (s543–s552 pattern; budget a 3rd attempt).

**Step 2 — PIVOT off classic r2/0X4 (fold-in-then-pick), UNLESS Step 1 surfaced a fire.**

Classic r2/0X4 is done. Pick ONE residual campaign lead:

### Option A (recommended): high-count residual r4/0X0 mesh write sites
1. Re-run tracer + `s506_dedupe.py` (no shape filter — full ranked NEEDS_GUARD list).
2. Top residual ranks (as of s555 pre-fix scan, re-check after confirm closes):
   - `renderLitTexturedMeshFaces` r4/0X0 counts 59/45/41
   - `renderFlatMeshFaceGroup` r4/0X0 counts 27/16
   - `submitSceneNodeRender` r4/0X0 count 15
   - plus smaller r3/r7/r16/r18 sites in heapFreeListDequeue / buildOrientedFaceGeometry
3. Shape-check every candidate: many may already be covered by non-R-numbered family guards
   (`DL_LIST_APPEND_*`, sibling-ptr, etc.) or be intentional unguarded integer stores — do NOT
   blindly apply the r2/0X4 template. Confirm the reload is still a free-list / DL-cursor global
   (or a sibling of that family) before writing a guard.
4. Cross-check write addresses against `fixup_game_funcs.py`. Batch-fix only sites that share one
   proven safe skip-on-invalid shape.

### Option B: scoped gap audit (item -327 / -334 model)
Grep for "validate head, then deref readback without range-check" patterns near existing
`DL_LIST_APPEND_GUARD` / `SIBLING_PTR_WRITE_GUARD` sites — the s549 style that ships fixes on
direct crash-mechanism evidence rather than pure shape ranking.

### Discriminating outcome
- Confirm clean → classic r2/0X4 FULLY CLOSED; residual pivot begins.
- Confirm fire with bad_ptr correlating to crash fault address → real bug catch (item -334 model).
- Residual candidates that fail shape/safety review → document as DEFERRED (like -302/-305/-307).

## Iron-rule reminders specific to this campaign
- Confirm free session number at START (`git log --oneline -3`) before naming.
- Guard firing with `n=0` is not automatically dismissible — check bad_ptr vs crash fault address
  (s549 item -334).
- Never trust tracer tier count without shape check + address cross-check + source read.
- Never trust 0-fires without double-digit+ `hangarbay-entry`. Absent hangarbay = discard immediately.
- Two consecutive weak draws on the same target is now the norm for the item -306 signature (s548–s552);
  budget a 3rd attempt (s553 closed 64-65 on attempt 3 with n=2600).
- Count=N tiers can include shape-mismatched sites that share a taint count but not the classic reload
  (s553/s554/s555 count=7 `0x8000D268` skipped).
- One build/run carries every armed guard env var.
- `s506_dedupe.py` fixed path; never pass custom `--out` to `--scan`.
- Kill with SIGKILL; capture paths must not start with "."; run from `build/` with ROM.
- `fixup_game_funcs.py` is untracked in the standalone N64Recomp checkout — nothing to commit there.
- Build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- `0x800ab068` / `0x80015544` / `findLookupEntryByKey+2212` / `0x80010b7c` / `coalesceFreeHeapBlocks+4424`/`0x8000247c` pc-symbol instability: cross-check `last-guest-pc` only.
- item -332 watch (2 occurrences); item -331/-333 free-list-pop region watch; item -335/-336/-337/-338
  single-occurrence watch.
- After launching manual live-verify in background, wait with TaskOutput block timeout ≥300000ms.
- Full guard table: `docs/PROJECT-OVERVIEW.md` §22-§25.
