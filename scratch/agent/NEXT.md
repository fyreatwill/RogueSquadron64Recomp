# NEXT work unit

HYPOTHESIS-ID: item-308-scan-buckets

## s474 summary: item -307 `hi16=0x8011, offset=-0x35e0` (23 sites, 9 files) CLASSIFIED AND DEFERRED,
not a guard candidate -- same disposition as item -305 (compare-only integer-flag idiom, never
dereferenced). Folded item -306's 2nd confirm soak (clean, 0 fires). Found and fixed TWO more
methodology tool bugs along the way:

1. **Pre-existing bug in `scratch_s468_shapecheck_generic.py`** (likely present in every prior bucket
   scanned with it): its classify loop checks register taint via Python substring containment
   (`f"ctx->r{t}" in args`), which false-matches `"ctx->r2"` inside `"ctx->r29"` -- so a reload landed
   in `$v0`(r2) immediately followed by the near-universal `ctx->r29 = ADD32(ctx->r29, N);` stack
   prologue gets falsely flagged as touching the tainted register, and the next stack-spill line
   misclassified as `WRITE_THROUGH`. Confirmed on all 3 of this bucket's flagged sites. NOT fixed in
   the tool itself (out of scope) -- **treat any raw `hit_deref=True`/`WRITE_THROUGH` flag from this
   tool as unverified until read directly**, on this or any past bucket.
2. **New bug in this session's own `scratch_s474_taint_scan_35e0.py`**, caught before it produced a
   wrong ledger entry: taint wasn't cleared across a real function call, so `ctx->r2` ($v0, the MIPS
   o32 return-value register) stayed "tainted" from a pre-call reload when it actually held the
   callee's own return value post-call. Fixed by clearing caller-saved regs (`r2,r3,r8-r15,r24,r25`)
   after any real-call line. **If you build a new taint scan from this template for the next bucket,
   this fix must already be present -- use `scratch_s474_taint_scan_35e0.py` as the new starting
   template, not `scratch_s473_taint_scan_23a8.py`.**

Full derivation: `PORTING-STATE.md` Session 474; ledger: `docs/CURRENT-TRUTH.md` item -307 (new) and
item -306 (confirm-soak fold).

## This session's top work unit: classify the last known fresh bucket from the s465 scan

**`hi16=0x8013, offset=0xb50`** (21 sites, 11 files) -- the most-scattered bucket left in the s465
codebase-wide frequency scan (more files than sites). Per the item -300 lesson, a bucket spanning
many files/functions is more likely to hide a second downstream shape than a short sample would
catch -- budget a full session for this one too.

Recommended approach (now a 4-step recipe, refined again this session):
1. `cd ~/Documents/Tools/N64Recomp && python3 scratch_s468_shapecheck_generic.py 8013 B50` (uppercase
   offset, no leading `-` since this one is positive -- confirm the tool's `off_raw` parsing handles
   a positive hex with no sign the same way as `-70F8` etc. before trusting the site count).
2. Before trusting ANY `hit_deref=True`/`WRITE_THROUGH` flag from step 1, read that exact site
   directly -- this session found 3/3 flagged sites in its bucket were a tool false positive (see bug
   #1 above). Don't skip this even if the flagged count is small.
3. Grep every existing guard's address comment in `fixup_game_funcs.py` for the resolved global
   address (`0x80130000 - 0xB50` for hi16=0x8013) to rule out an item -306-style partial-coverage
   overlap before treating the bucket as fresh.
4. Copy `scratch_s474_taint_scan_35e0.py` as the starting template (NOT the older s473 one -- it's
   missing the caller-saved-register-clear fix), retarget `target`/`files`/`LUI_RE`'s hi16 literal for
   the new hi16/offset, re-run, and validate the site count matches step 1's canonical count exactly
   (file:line, not just total) before trusting any classification. Then spot-check >=8-10 sites
   directly across as many of the 11 files as practical (the item -300 lesson bites hardest on
   wide-file-count buckets like this one). Also grep for WRITE sites to the same global
   (`MEM_W(0XB50, ctx->rN) = ...` and any negated/hi16-relative variant) the way this session did --
   it's a fast independent corroboration of pointer-vs-integer shape.
5. If a real unguarded-deref/write-through risk shape IS found (unlike the last 2 buckets), patch per
   the established per-site literal-anchor mechanism (items -298/-299/-300/-301/-303/-304), regen/
   build/live-verify, queue a confirm soak. If it classifies as compare-only/integer-flag like the
   last two, no code change needed -- CLASSIFY AND DEFER per the item -305/-307 pattern, no soak to
   queue.

## After this bucket: the s465 scan's known candidate list is EXHAUSTED

Once `hi16=0x8013, offset=0xb50` is resolved, every bucket surfaced by the s465 codebase-wide
frequency scan will have a disposition (closed-with-guard, or classified-and-deferred). Next session
after that needs a genuinely NEW discovery source for M3 idiom-class work -- rerunning the s465 scan
methodology on a different instruction pattern, or falling back to the M3 priority-3 reactive-audit
fallback described in ITERATION.md's strategic-priority section. Flag this explicitly rather than
inventing a new bucket without a re-scan.

## Candidate follow-up (not yet scheduled, low priority): the ABI-call-boundary propagation path
found s473, still unverified

10 sites (`submitSceneNodeRender` x2, `renderLitMeshFaceGroup` x4, `drawSubtitleText` x3,
`setupCameraMatrices` x1, from item -306's audit) pass a reload as an implicit ABI argument into
`appendRdpStateDl`/`emitAllocatedDLCommand`/`buildOrientedFaceGeometry`/`drawTextGlyphRect`. Whether
these callees dereference their `$a0`/`$a3` argument unguarded is UNVERIFIED. Low priority unless a
crash signature ever symbolizes inside one of those 4 functions with a wild pointer.

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

Unchanged from prior sessions -- 10 of the 120 `SIBLING_PTR_WRITE_GUARD` sites sit in
`submitSceneNodeRender`, tied to a still-open 2-occurrence wait-for-recurrence breadcrumb. 0 fires
across every soak so far, including s474's (no soak run this session -- no code change).

## Soak queue status

None queued this session (item -307 had no code change to verify). Check `scratch/agent/SOAK-
RESULTS.md` tail at the start of next session as usual in case anything else lands from the queue.
