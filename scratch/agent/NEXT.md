# Next: DL-chunk demand vs return at dd3 — pre-grow once, measure in-use high-water
HYPOTHESIS-ID: cpatch-pipeline-qualification
s6285: finder-grow + b030 + blanket top-up each moved the dd3 crash to another unguarded cache pop (447 inline sites); blanket top-up breaks rs_free in menu. Consuming sites cannot be patched one by one.
Hypotheses: H-demand (dd3 frames legitimately need >1356 chunks live), H-leak (chunks are not returned by reclaimDisplayListChunk/frame end at dd3).
Work unit: one build, one run: (a) log per frame the cache length at beginFrameDLChunk entry and at reclaim entry, dd1 vs dd3 (s6098 ROGUESQ_DLPOOLLOG already walks it); (b) single-site pre-grow: at beginFrameDLChunk entry add N=ROGUESQ_DLPOOLX_PRE (default 0) chunks once, with all s6285 topup/b030/finder-grow sites reverted (git: tools/apply_s6098_dlpool.py apply_topup, _apply4, fixup_patches_host.py finder-grow gated off). Try PRE=2000,4000 with MB=4 at dd3.
Outcomes: if min cache length per frame tracks frame demand and PRE>=demand survives 120 s -> H-demand, ship pre-grow under DRAW_DISTANCE>=3; if cache length falls monotonically across frames even at dd1-like load -> H-leak, find the missing return.
