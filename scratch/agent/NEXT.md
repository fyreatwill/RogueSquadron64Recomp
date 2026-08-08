# NEXT work unit

HYPOTHESIS-ID: item-308-labelgap-backfill-audit

## s475 summary: item -308 `hi16=0x8013, offset=0xb50` CLASSIFIED AND DEFERRED (24 sites, 12 files,
not the 21/11 originally reported); found and fixed tool bug #5

This session's work unit (NEXT.md's top and, per s474's note, final candidate from the s465 scan):
`hi16=0x8013, offset=0xb50` (global `0x8012F4B0`). No overlap with any existing guard's address.

`scratch_s468_shapecheck_generic.py 8013 B50` reported 21 sites/11 files, 1 flagged
`ADD32(...)->WRITE_THROUGH`. Direct read of the flagged site (`funcs_30.c:15666`) confirmed the
already-known tool-bug-#1 pattern (s474: `ctx->r2`/`ctx->r29` substring false positive) -- the real
next use of the reload is `ctx->r2 = ctx->r2 & 0X60;` then a `bne`-and-discard, not a write-through.

While confirming that, noticed the generated code sometimes places a `L_XXXXXXXX:` branch-target
label between a bucket's `lui` and its `lw` reload (when the reload address is itself a jump target
from elsewhere in the function). **`scratch_s468_shapecheck_generic.py`'s lookahead loop doesn't
recognize label lines** -- it only skips disassembly-comment and breadcrumb lines while hunting for
the reload after a `lui` match, and silently gives up (no site reported, no warning) on any other
line shape. This is **tool bug #5**. Wrote `scratch_s475_label_gap_check.py` (N64Recomp repo,
untracked) -- same scan logic plus a label-skip -- and re-ran: **24 sites, not 21** (3 missed:
`funcs_27.c:108435`, `funcs_30.c:14600`, `funcs_32.c:29556` -- the last in a whole file,
`funcs_32.c`, that didn't even appear in the original tool's file list).

Direct-read all 24 sites across all 12 files (not just a sample -- the label-gap fix produced a
short enough list to read exhaustively): 100% the same `andi $vN, $vN, MASK` (masks
`0x1/0x8/0x10/0x20/0x60`, a packed status/capability bitfield) immediately after the reload,
consumed only by a conditional branch, never dereferenced. 0 write sites to the global anywhere in
`RecompiledFuncs/funcs_*.c` (grepped `MEM_W(0XB50`). Same compare-only-idiom disposition as items
-305/-307. No code change, no soak queued.

Full derivation: `PORTING-STATE.md` Session 475; ledger: `docs/CURRENT-TRUTH.md` item -308.

## This session's top work unit: backfill-check tool bug #5 against every already-CLOSED bucket

Tool bug #5 (label-line blind spot in `scratch_s468_shapecheck_generic.py`) has ONLY been confirmed
against this session's fresh bucket. It has NOT been checked against any of the buckets this sub-arc
already CLOSED with a guard: items -298 (`DL_LIST_RESET_GUARD`), -299 (`DL_BUFFER_POOL_GUARD`), -300
(`NODE_LIST_HEAD_GUARD`/`NODE_LIST_HEAD_WRITE_GUARD`), -301 (`TEXDATA_TABLE_GUARD`), -303
(`TEXDATA_PTR_ARRAY_GUARD`), -304 (`MATERIAL_ARRAY_PTR_GUARD`), -306 (`SIBLING_PTR_WRITE_GUARD`,
120 sites). If any of those buckets ALSO has `lui`->label->`lw` sites the original scan silently
dropped, those sites are unguarded today -- a real residual-risk gap, not just a methodology
footnote. This is now the highest-expected-value M3 work: bounded, mechanical, and closes a
correctness question about six-plus items already believed fully closed.

**Hypotheses:**
1. The label-gap bug is unique to this session's bucket (unlikely a priori -- the branch-recompile
   pattern that produces a `lui`->label->`lw` shape isn't bucket-specific, it depends on whether some
   OTHER branch in the function happens to target the `lw` instruction's address, which is a property
   of the surrounding code, not of which global is being loaded).
2. Some already-closed buckets have label-gap sites, but all of them turn out to be the same
   harmless compare-only/no-use idiom as every other site in that bucket (most likely, given 100% of
   sites in every bucket audited so far turned out to share one idiom).
3. At least one already-closed bucket has a label-gap site that IS a real unguarded deref/write --
   the discriminating, worst-case outcome. Would mean the corresponding guard needs a new per-site
   literal-anchor patch added (mechanism: items -298/-299/-300/-301/-303/-304).

**Discriminating measurement**: for each of the 7 closed buckets' hi16/offset pairs, run
`scratch_s475_label_gap_check.py` (generalize it to take hi16/offset args like
`scratch_s468_shapecheck_generic.py` does, rather than hand-editing per bucket) and diff its site
count against that item's own recorded site count in `docs/CURRENT-TRUTH.md`. A count MISMATCH
(permissive > recorded) directly falsifies hypothesis 1 for that bucket and produces the exact
file:line list of missed sites to read for hypothesis 2 vs 3.

Recommended approach:
1. `cd ~/Documents/Tools/N64Recomp`, generalize `scratch_s475_label_gap_check.py` into
   `scratch_s476_label_gap_generic.py` taking `<hi16hex4> <offsethex>` like the s468 tool does
   (reuse its arg-parsing for the case-sensitivity/sign handling item -305 already fixed once).
2. Run it against all 7 closed buckets' hi16/offset pairs (grep each item's ledger entry in
   `docs/CURRENT-TRUTH.md` for the exact `0x80NNNNNN` global or `hi16=..., offset=...` if still
   phrased that way -- items -298/-299/-306 may need their global address converted back to
   hi16/offset form, `offset = global & 0xFFFF` sign-extended, `hi16 = (global >> 16) & 0xFFFF`,
   verify against a known site's `lui`/`lw` comment pair before trusting the arithmetic).
3. For any bucket where the permissive count exceeds the recorded count, list the new file:line
   sites (same diff technique this session used) and read each directly.
4. If ALL extra sites across all 7 buckets are the same idiom already established for that bucket
   (no-use, compare-only, or already-covered-by-the-guard-mechanism), CLOSE the tool-bug-#5 question
   outright with a ledger note -- no code change needed, hypothesis 2 confirmed for all 7.
5. If ANY extra site is a genuine unguarded deref/write-through, patch it into that bucket's existing
   guard family per the established per-site literal-anchor mechanism, regen/build/live-verify, queue
   a confirm soak — this reopens that specific CLOSED item.

## After this audit: M3 needs a new discovery source

Once the backfill audit lands (clean or with fixes), the s465 scan's discovery pipeline is fully
spent. The session after this one should pivot to a NEW instruction-pattern scan (e.g. `lui`+`sw`
direct-store idioms without an intervening `lw`, or a different opcode class entirely) rather than
continuing to re-derive buckets from the same `lui`+`lw` frequency table.

## Soak queue status

None queued this session (item -308 had no code change to verify). Check `scratch/agent/SOAK-
RESULTS.md` tail at the start of next session as usual.
