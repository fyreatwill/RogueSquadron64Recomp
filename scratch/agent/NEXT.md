# NEXT work unit

HYPOTHESIS-ID: item-307-scan-buckets

## s473 summary: resolved item -296's flagged `hi16=0x8012, offset=-0x23a8` gap (141 sites) -- found
and FIXED a real methodology gap in the already-CLOSED item -296, closing 1 new guard site (120th)
and classifying the rest. A from-scratch taint-propagation scan
(`scratch_s473_taint_scan_23a8.py`, N64Recomp repo, untracked), validated against the KNOWN
119-address guard list before trusting any new finding, found: 119 already-guarded (exact match), 1
genuine unguarded write-through-the-reload (`setupCameraMatrices`, fixed as SIBLING_PTR_WRITE_GUARD's
120th site), 2 false positives (`do_lwl` unaligned-load helper calls, confirmed by direct read), 10
sites where the reload crosses a REAL function call via the guest ABI convention (`ctx->r4`/`r7` still
tainted at a `fn(rdram, ctx);` call -- a genuinely novel propagation path, flagged not chased), and 19
no-use sites (spot-checked 4/19, not exhaustive). Clean regen/build, `strings`-verified 120/120 +
all 10 sibling families unchanged, live-verify 0 fires + hangarbay-entry n=31 positive control,
crashed on an unrelated new signature (filed not chased). 2nd confirm soak queued:
`s473_siblingptrwrite120_confirm.sh`. Full derivation: `PORTING-STATE.md` Session 473; ledger:
`docs/CURRENT-TRUTH.md` item -306 (new) and item -296 (amended).

## This session's top work unit: classify a fresh bucket from the s465 codebase-wide frequency scan

Two next-ranked candidates remain, both genuinely fresh (no known partial-coverage caveat like the
-0x23a8 bucket had) but far more scattered than anything closed so far in this sub-arc -- budget
accordingly, this may take the full session just to characterize:

1. **`hi16=0x8011, offset=-0x35e0`** (23 sites, 9 files) -- the more scattered of the two by file
   count, likely means more distinct downstream shapes (per the item -300 lesson: a bucket spanning
   multiple files/functions is more likely to hide a second shape a short sample would miss).
2. **`hi16=0x8013, offset=0xb50`** (21 sites, 11 files) -- even more files for slightly fewer sites.

Recommended approach, following the method that worked this session and s305/s463-472's:
1. `cd ~/Documents/Tools/N64Recomp && python3 scratch_s468_shapecheck_generic.py 8011 -35E0` (remember:
   **always pass the offset in UPPERCASE hex** -- lowercase silently returns "total sites: 0", a
   documented tool bug from s472).
2. Before trusting the tool's own `hit_deref` classification, check whether ANY of these 23/21 sites
   overlap an already-guarded global (grep the candidate's resolved address --
   `0x80110000 - <offset>` for hi16=0x8011, `0x80130000 - <offset>` for hi16=0x8013 -- against every
   existing guard's address comment in `fixup_game_funcs.py`) the way this session found `-0x23a8`
   secretly overlapped item -296. If it's genuinely fresh (no overlap), proceed with the standard
   classify-then-patch recipe used for items -298/-299/-300/-301/-303/-304.
3. Given this session's finding that a naive tool can silently undercount (ADD32-preserves-taint,
   early-break-on-`if`, and the newly-discovered ABI-call-boundary blind spot), prefer
   `scratch_s473_taint_scan_23a8.py` as a STARTING TEMPLATE for a new bucket's own taint scan
   (parameterize the target offset/hi16, keep the ABI-call check) over trusting
   `scratch_s468_shapecheck_generic.py`'s shallow 6-20-line window in isolation. Cross-validate any
   "no risk found" result against a positive-count sanity check (does a manual sample of 3-5 sites
   match the tool's classification?) before declaring a bucket closed or deferred.
4. For each classified risk shape, patch/guard per the established per-site literal-anchor mechanism
   (see any of items -298 through -305 in CURRENT-TRUTH for the pattern), regen/build/live-verify,
   queue a confirm soak.

## Candidate follow-up (not this session unless the above proves intractable): the ABI-call-boundary
propagation path found s473

10 sites (`submitSceneNodeRender` x2, `renderLitMeshFaceGroup` x4, `drawSubtitleText` x3,
`setupCameraMatrices` x1) pass the `-0x23a8` reload as an implicit ABI argument into
`appendRdpStateDl`/`emitAllocatedDLCommand`/`buildOrientedFaceGeometry`/`drawTextGlyphRect`. Whether
these callees dereference their `$a0`/`$a3` argument unguarded is UNVERIFIED -- would need each
callee's own body read. Plausibly safe (same idiom as the already-hardened `DL_LIST_APPEND_GUARD`
family, just across a function boundary) but not confirmed. Low priority unless a crash signature
ever symbolizes inside one of those 4 functions with a wild pointer.

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

Unchanged from prior sessions -- 10 of the (now 120) sites sit in `submitSceneNodeRender`, tied to a
still-open 2-occurrence wait-for-recurrence breadcrumb. 0 fires across every soak so far, including
s473's live-verify.

## Soak queue status

`s473_siblingptrwrite120_confirm.sh` queued this session (2nd independent confirm for item -306's new
guard site). Check `scratch/agent/SOAK-RESULTS.md` tail at the start of next session as usual.
