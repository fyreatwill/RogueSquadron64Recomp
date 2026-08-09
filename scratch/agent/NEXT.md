# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s557 recap (read this first)

**Folded in s556's queued confirm — CLEAN, FULLY CLOSED 2/2.**
`s556_residual_rN_0x0_nine_way_confirm` (guards 116-124): CLEAN hangarbay n=2600, 0 fires,
crashed on already-catalogued `initVec4TripletFromArgs+68`/`0x80065e94`. Residual free-list-node
batch 1 **DONE at 124/124** (classic r2/0X4 115 + residual batch 1 9).

**Residual free-list-node batch 2: 7 guards (125-131) fixed, 1st live-verify CLEAN.**
Shape-checked remaining NEEDS_GUARD write tiers after batch 1:
- DEFERRED shape-mismatches: heapFreeListDequeue r2/r3/r16 packing (incl 0x8000D268),
  buildOrientedFaceGeometry s2 packing, drawSubtitleText appendRdpStateDl return
- MATCHED free-list-allocated-node MEM_W(0X0,r4/r7) after freelist pop (count=3): 7 sites
  - RECORD_DEFERRED_DRAW_REF_VARIANT/A/B/C/D_R2 (0x800084E0/C7C4/C8E8/CA10/CB34)
  - HEAP_FREE_LIST_DEQUEUE_R5 (0x8000D0D4)
  - RENDER_LIT_TEXTURED_MESH_FACES_R11 (0x8000FA40)

1st live-verify: hangarbay n=2600, 0 fires on all 7. Crashed on **item -340**
(`sibling-ptr-write-guard site=0x80010B48` bad_ptr=0x18 → crash `0x80010B4C` = bad_ptr+4).
Fixed same session as new SIBLING_PTR_WRITE_GUARD site. 2nd confirm queued:
`scratch/agent/soak_queue/s557_residual_count3_seven_way_confirm.sh`.

Campaign totals: **131 fixed, 124 FULLY CLOSED 2/2, 7 pending confirm** (125-131).
Item -340 fixed on 1st evidence; confirm rides with residual batch 2.

## This iteration's work unit

**Step 1 — fold in the queued confirm result (do this FIRST).**

1. `s557_residual_count3_seven_way_confirm` (2nd confirm for guards 125-131 + item -340 watch):
   expect 0 fires on all seven new residual tags, double-digit+ `hangarbay-entry`. Watch for
   `sibling-ptr-write-guard site=0x80010B4C` fire (item -340 positive engagement) or clean skip.
   If clean on residual tags: mark guards 125-131 FULLY CLOSED 2/2. If item -340's new site fires
   with bad_ptr and no crash at 0x80010B4C, that is confirmatory evidence the gap fix engages.
2. Update `docs/PROJECT-OVERVIEW.md` §25 + `docs/CURRENT-TRUTH.md` item -317/-340.
3. If WEAK (no hangarbay / single-digit / item -306 early death): discard and re-queue retry
   immediately (s543–s552 pattern; budget a 3rd attempt).

**Step 2 — continue residual free-list-node 0X0 (fold-in-then-pick), UNLESS Step 1 surfaced a fire.**

After 125-131 close, re-run tracer + `s506_dedupe.py`. Next residual candidates:
- any remaining freelist-node 0X0 sites still NEEDS_GUARD after 125-131
- packing shape-mismatches remain DEFERRED unless reclassified
- **item -339 watch**: if 0x800088ec recurs, escalate as systematic emit-dl GUARD4 audit
- **item -340**: if 0x80010B4C crash recurs despite guard, escalate (should not if fix lands)

### Discriminating outcome
- Confirm clean → guards 125-131 FULLY CLOSED; next residual batch or packing-audit decision.
- Confirm fire with bad_ptr correlating to crash fault address → real bug catch (item -334 model).
- Residual candidates that fail shape/safety review → document as DEFERRED.

## Iron-rule reminders specific to this campaign
- Confirm free session number at START (`git log --oneline -3`) before naming.
- Guard firing with `n=0` is not automatically dismissible — check bad_ptr vs crash fault address
  (s549 item -334; s557 item -340).
- Never trust tracer tier count without shape check + address cross-check + source read.
- Never trust 0-fires without double-digit+ `hangarbay-entry`. Absent hangarbay = discard immediately.
- Two consecutive weak draws on the same target is now the norm for the item -306 signature (s548–s552);
  budget a 3rd attempt (s553 closed 64-65 on attempt 3 with n=2600).
- Count=N tiers can include shape-mismatched sites that share a taint count but not the classic reload
  (s553/s554/s555 count=7 `0x8000D268` skipped; s557 count=11/7 packing skipped).
- Residual free-list-node 0X0 uses r4/r7 not r2 — do not re-apply classic r2/0X4 filter alone (s556/s557).
- One build/run carries every armed guard env var.
- `s506_dedupe.py` fixed path; never pass custom `--out` to `--scan`.
- Kill with SIGKILL; capture paths must not start with "."; run from `build/` with ROM.
- `fixup_game_funcs.py` is untracked in the standalone N64Recomp checkout — nothing to commit there.
- Build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- After launching manual live-verify in background, wait with TaskOutput block timeout ≥300000ms.
- Full guard table: `docs/PROJECT-OVERVIEW.md` §22-§25.
