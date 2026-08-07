# NEXT work unit

HYPOTHESIS-ID: item-306-hi8012-23a8-classify

## s472 summary: folded item -304's 2nd confirm soak (0 fires on the new guard and all 8 siblings,
`hangarbay-entry` n=31, matches the manual pass closely; crashed on a 3rd distinct byte-offset of the
already-catalogued `heapFreeListDequeue` family, filed not chased) -- item -304 fully CLOSED. Then
classified `hi16=0x8011, offset=0x63d4` (170 sites, the largest bucket in the s465 scan) and
CLASSIFIED AND DEFERRED it as item -305: 26/27 manually-read sample sites (stratified across all 4
files and every tool-reported chain-depth group) are the identical `sltu`/`bne` "current DL pointer <
buffer-end limit" bounds-check idiom -- the reload is COMPARED, never dereferenced. The tool's only 2
`hit_deref=True` "risk" flags in the whole bucket were confirmed false positives on direct read (an
unrelated stack-pointer prologue adjustment a few lines after the reload, not an operation on the
reloaded value itself). Same disposition as item -302 -- not a guard-at-reload candidate. Also found
and documented a real tool bug: `scratch_s468_shapecheck_generic.py` silently returns "total sites: 0"
if the offset argument is passed in lowercase (generated code always emits uppercase hex literals) --
**always pass the offset in UPPERCASE hex** to this tool from now on.

Full derivation: `PORTING-STATE.md` Session 472; ledger updated in `docs/CURRENT-TRUTH.md` Next-steps
item -305 and the USER DIRECTIVE next-candidate pointer.

## This session's top work unit: classify `hi16=0x8012, offset=-0x23a8` (141 sites) — NOT a fresh bucket

**Read this caution before starting, it changes the whole approach vs. every other bucket closed in
this sub-arc:** item -296's `SIBLING_PTR_WRITE_GUARD` (closed s459, 119 sites) already guards the
DOWNSTREAM WRITE through this exact same global reload — `MEM_W(OFF, ctx->rN) = VAL` a few lines after
the `lui`+`lw` reload — not the reload itself. Confirm via `grep -n "23a8\|23A8" \
~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (look for the `SIBLING_PTR_WRITE_GUARD` comment/
pattern near s459's addition) before doing anything else, to see exactly what's already covered.

The 141-vs-119 gap (22 sites) and whether the raw reload itself needs its OWN guard (independent of
whether its eventual write is already guarded) is UNCLASSIFIED. This needs a genuinely different
analysis than the standard "classify then patch" recipe used for every other bucket in this scan:

1. **Global address**: `0x80120000 - 0x23A8 = 0x8011DC58` — cross-check this against item -296's
   comment in `fixup_game_funcs.py` (it should be the SAME address the write-guard already targets;
   if it's a different address, the whole "partially covered" premise from `NEXT.md`/`CURRENT-TRUTH`
   is wrong and this bucket is actually fresh — verify this first, don't assume the premise holds).
2. **Classify with the tool** (remember: UPPERCASE offset): `cd ~/Documents/Tools/N64Recomp && python3
   scratch_s468_shapecheck_generic.py 8012 -23A8`. Read across all sites, not just a sample of the
   tool's own buckets — the open question here isn't "is it a pointer" (item -296 already answered
   that for the write side) but "is the RELOAD used in a way the existing write guard doesn't already
   protect".
3. **For each of the 141 reload sites, determine**: does it reach the already-guarded write
   downstream (redundant, no new guard needed), or does it get used a DIFFERENT way first — a read
   before the write, a different write not covered by item -296's guard, or a branch that skips the
   guarded write entirely on some path? This requires reading full function bodies around a
   representative sample (recommend delegating to a subagent given the file-reading volume, same
   pattern as this session's item -305 classification), not just the ~10-line local window the
   generic tool captures.
4. **Decision tree**: if all 141 reach the already-guarded write with no earlier unguarded use, this
   bucket needs NO new code — document it as CLOSED-BY-EXISTING-GUARD (a new disposition category,
   not seen yet in this sub-arc) and move to the next candidate. If some sites use the reload before
   or independent of the guarded write, those need their own guard scoped to just those sites.

## Fallback if `-0x23a8` proves intractable or the caution above eats the session

Two next-ranked genuinely-fresh candidates, per the s465 scan, both far more scattered than anything
closed so far — budget accordingly:
- `hi16=0x8011, offset=-0x35e0` (23 sites, 9 files)
- `hi16=0x8013, offset=0xb50` (21 sites, 11 files)

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

Unchanged from prior sessions — 10 of item -296's 119 sites sit in `submitSceneNodeRender`, tied to a
still-open 2-occurrence wait-for-recurrence breadcrumb. 0 fires across every soak so far, including
s472's confirm soak. Passive, no action needed unless a soak result shows a fire.

## Soak queue status

Nothing new queued this session (item -305 was a classification-only result, no code change, no soak
needed). Check `scratch/agent/SOAK-RESULTS.md` tail at the start of next session as usual.
