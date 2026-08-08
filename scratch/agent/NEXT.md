# NEXT work unit

HYPOTHESIS-ID: m3-lui-sw-direct-store-scan

## s476 summary: tool-bug-#5 (label-gap) backfill audit CLOSED clean; s465 `lui`+`lw` scan lineage
fully spent

Generalized `scratch_s475_label_gap_check.py` into `scratch_s476_label_gap_generic.py` (N64Recomp
repo, untracked, hi16/offset-parameterized like `scratch_s468_shapecheck_generic.py`) and ran it
against all 7 already-CLOSED M3 idiom-class buckets (items -298/-299/-300/-301/-303/-304/-306).
**Result: strict == permissive hit count for all 7 — 0 label-gap sites anywhere.** Tool bug #5 (the
`lui`->label->`lw` blind spot that undercounted item -308 by 3 sites/1 file) does not recur in any
already-CLOSED bucket. No per-site patch needed anywhere; this closes the open question cleanly.

While reconciling counts, found item -299's raw strict hit count (87) didn't match its guard's site
count (84) — traced to an UNRELATED cause (`scratch_s466_shapecheck_63fc.py` hardcoded
`files = ["funcs_3.c", "funcs_4.c"]`, silently never scanning `funcs_6.c`'s 3 sites). Directly
re-read all 3 `funcs_6.c` sites: confirmed `fixup_game_funcs.py`'s own comment was right — those 3
are COMPARE_ONLY (`bne` against a computed array-bound address, never dereferenced), correctly
excluded already. Item -299 remains soundly CLOSED. No code change this session; no soak queued
(nothing in `RecompiledFuncs/` changed).

Full derivation: `PORTING-STATE.md` Session 476; ledger: `docs/CURRENT-TRUTH.md` item -308 amendment.

**The entire s465 `lui`+`lw` frequency-scan discovery pipeline is now fully spent**: 8 buckets
CLOSED with guards (298 sites total: -291/-298/-299/-300/-301/-303/-304/-306), 4 buckets CLASSIFIED
AND DEFERRED as compare-only/integer-index idioms (-302/-305/-307/-308), and the methodology itself
now audited clean end-to-end (all 5 found tool bugs either fixed or shown not to change any past
bucket's disposition). Re-deriving buckets from the same `lui`+`lw` frequency table has no further
expected value.

## This session's top work unit: new discovery source — `lui`+`sw` direct-store scan

Per CURRENT-TRUTH's updated M3 priority note: pivot to a genuinely NEW instruction-pattern scan
rather than continuing to mine the exhausted `lui`+`lw` table. Every closed/deferred bucket in the
s454-s476 lineage started from a `lui` reload (`ctx->rL = S32(0XHHHH << 16)`) immediately followed
by an `lw` reload (`ctx->rL = MEM_W(ctx->rL, 0XOFFSET)`) — i.e. a global POINTER being READ back
into a register. A DIFFERENT idiom this lineage has never scanned: `lui`+`sw` DIRECT STORE, where a
global is computed and WRITTEN TO without any intervening `lw` reload of the old value:

    ctx->rL = S32(0XHHHH << 16);          // lui
    MEM_W(0XOFFSET, ctx->rL) = ctx->rSrc;  // sw directly off the lui'd base, no reload in between

This is a different risk shape from every bucket audited so far (all of which were READ-then-
compare-or-deref of a *stale* global; a pure write doesn't depend on the global's prior contents,
so a "guard the read" idea doesn't apply — but a write to a bad/uninitialized address computed via
`lui`+`addiu`+arithmetic rather than a direct small-offset store might be a different crash source
worth enumerating and ruling in/out on its own terms).

**Hypotheses:**
1. `lui`+`sw` direct-store sites are dominated by legitimate global-variable stores at fixed, valid
   addresses (RDRAM-resident statics) — no crash risk, nothing to guard, this whole discovery
   direction is a dead end for M3 (matches the character of every closed-clean bucket in the `lw`
   lineage: idioms audited so far have mostly been benign).
2. A minority of `lui`+`sw` sites store through a POINTER that was itself `lui`+`lw`-loaded earlier
   in the same function (i.e., pointer arithmetic feeding a write, same "wild pointer from stale
   reload" risk class as every guard placed so far) — these are new guard candidates not covered by
   any of the 8 read-side guards already placed, because a write-only global was never a `lw` reload
   target and so never entered the s465 frequency table.
3. The pattern is too diffuse (too many trivial single-site global-variable stores, no clusterable
   high-frequency bucket) to produce anything as clean as the `lw` lineage's top-N buckets — in which
   case this discovery source itself should be abandoned after one scan, not iterated on.

**Discriminating measurement**: write a frequency scanner (adapt `scratch_s465_scan.py`, N64Recomp
repo) that finds every `ctx->rL = S32(0XHHHH << 16);` immediately (allowing comment/breadcrumb
lines) followed by `MEM_W(0XOFFSET, ctx->rL) = ...;` with NO intervening `lw`-shaped reload of
`ctx->rL`, group by `(hi16, offset)` pair, and rank by site count. The top bucket's site count and
whether ANY of its sites trace back to a pointer that was itself dynamically loaded (not a fixed
compile-time small-offset global address) is the discriminating split between hypotheses 1/2 vs 3.

Recommended approach:
1. `cd ~/Documents/Tools/N64Recomp`, write `scratch_s477_sw_scan.py`: glob all
   `RecompiledFuncs/funcs_*.c`, regex-match the `lui` line, look ahead (same comment/breadcrumb/
   label skip logic as `scratch_s476_label_gap_generic.py` — reuse its skip predicates) for a
   `MEM_W(0XOFFSET, ctx->rL) = ...;` write using the SAME register, with no `MEM_W(ctx->rL, ...)`
   read of that register appearing first. Bucket by `(hi16, offset)`, print top 15 by site count.
2. Pick the top 2-3 buckets (by the same "highest expected value = highest site count, multi-file"
   heuristic that worked for the `lw` lineage) and read a stratified sample directly (not just tool
   `hit_deref`/`hit_write` flags — this lineage's own history shows every automated classifier so
   far has had at least one blind spot on first use) to determine hypothesis 1 vs 2 vs 3.
3. If a bucket matches hypothesis 2 (write-through-a-stale-pointer, not a fixed-address global
   store), design and apply a guard using the established per-site literal-anchor mechanism
   (`fixup_game_funcs.py`, same pattern as items -298 through -306), regen/build/live-verify, queue
   a confirm soak.
4. If hypothesis 1 or 3 dominates (all fixed-address stores, or too diffuse to cluster), CLASSIFY
   AND DEFER with no code change — same disposition precedent as items -302/-305/-307/-308 — and the
   session after that should consider M3 fully mined out for now (time to return to M5 or general
   crash-breadcrumb triage instead of continuing to invent new opcode-pattern scans).

## Soak queue status

None queued this session (s476 had no code change to verify — the label-gap audit and the item -299
recheck were both read-only). Check `scratch/agent/SOAK-RESULTS.md` tail at the start of next
session as usual for any soaks the loop ran in the background.
