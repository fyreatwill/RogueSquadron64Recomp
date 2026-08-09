# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s556 recap (read this first)

**Folded in s555's queued confirm — CLEAN, FULLY CLOSED 2/2.**
`s555_count1_heap_free_list_insert_r1_confirm` (guard 115): CLEAN full ~300s (rc=0, 114 frames),
`hangarbay-entry n=3000`, 0 fires, NO crash. Classic r2/0X4 campaign **DONE at 115/115**.

**Residual free-list-node rN/0X0 pivot: 9 guards (116-124) fixed, 1st live-verify CLEAN.**
Full-rank NEEDS_GUARD re-scan after classic empty: top residual is free-list head reloaded into
`$a0`/`$a3` then written at `MEM_W(0X0, rN)` (list-prepend). Shape-checked; fixed as:
- RENDER_LIT_TEXTURED_MESH_FACES_R7..R10 (0x8000FD50/FC80/FE70/FF20)
- RENDER_FLAT_MESH_FACE_GROUP_R7/R8 (0x80011BA8/11958)
- SUBMIT_SCENE_NODE_RENDER_R10 (0x8001077C)
- EMIT_ALLOCATED_DL_COMMAND_R4 (0x80008858)
- RESERVE_AND_EMIT_DL_ENTRY_R4 (0x8000CD58)

1st live-verify: hangarbay n=2600, 0 fires on all 9. Crashed on new breadcrumb item -339
(`emitAllocatedDLCommand+13216`/`0x800088ec` — GUARD3/GUARD4 gap; not a regression of the new
guards). 2nd confirm queued: `scratch/agent/soak_queue/s556_residual_rN_0x0_nine_way_confirm.sh`.

Campaign totals: **124 fixed, 115 FULLY CLOSED 2/2, 9 pending confirm** (116-124).

## This iteration's work unit

**Step 1 — fold in the queued confirm result (do this FIRST).**

1. `s556_residual_rN_0x0_nine_way_confirm` (2nd confirm for guards 116-124): expect 0 fires on all
   nine new tags, double-digit+ `hangarbay-entry`. If clean: mark guards 116-124 FULLY CLOSED 2/2.
2. Update `docs/PROJECT-OVERVIEW.md` §25 + `docs/CURRENT-TRUTH.md` item -317. **If the confirm
   surfaces a fire, this is a MAJOR finding — investigate instead of pivoting.**
3. If WEAK (no hangarbay / single-digit / item -306 early death): discard and re-queue retry
   immediately (s543–s552 pattern; budget a 3rd attempt).

**Step 2 — continue residual free-list-node 0X0 (fold-in-then-pick), UNLESS Step 1 surfaced a fire.**

After 116-124 close, re-run tracer + `s506_dedupe.py`. Next residual candidates from s556 pre-fix
ranking (re-check after confirm):
- heapFreeListDequeue r3/0X0 and r3/0X4 count=11 (shape-check: may be s0-derived packing, not freelist)
- emitAllocatedDLCommand / reserveAndEmitDLEntry lower-count 0X0 sites already covered by R4?
- buildOrientedFaceGeometry r4/r18 secondary counts
- shape-mismatched count=7 at 0x8000D268 (still skip unless shape reclassified)
- **item -339 watch**: if 0x800088ec recurs, escalate as systematic emit-dl GUARD4 audit (heapWalker s218 model) — that is an idiom-class fix, not a single-crash chase

### Discriminating outcome
- Confirm clean → guards 116-124 FULLY CLOSED; next residual batch begins.
- Confirm fire with bad_ptr correlating to crash fault address → real bug catch (item -334 model).
- Residual candidates that fail shape/safety review → document as DEFERRED.

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
- Residual free-list-node 0X0 uses r4/r7 not r2 — do not re-apply classic r2/0X4 filter alone (s556).
- One build/run carries every armed guard env var.
- `s506_dedupe.py` fixed path; never pass custom `--out` to `--scan`.
- Kill with SIGKILL; capture paths must not start with "."; run from `build/` with ROM.
- `fixup_game_funcs.py` is untracked in the standalone N64Recomp checkout — nothing to commit there.
- Build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- `0x800ab068` / `0x80015544` / `findLookupEntryByKey+2212` / `0x80010b7c` / `coalesceFreeHeapBlocks+4424`/`0x8000247c` / `0x800088ec` pc-symbol instability: cross-check `last-guest-pc` only.
- item -332 watch (2 occurrences); item -331/-333 free-list-pop region watch; item -335/-336/-337/-338/-339
  single-occurrence watch.
- After launching manual live-verify in background, wait with TaskOutput block timeout ≥300000ms.
- Full guard table: `docs/PROJECT-OVERVIEW.md` §22-§25.
