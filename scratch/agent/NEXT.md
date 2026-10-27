# NEXT: which descriptor (t0/r8) selects table 802525E4 on dd4 EMPTY returns
HYPOTHESIS-ID: g1c-span-reject-predicate

s6516: cell +3..+5 are constant per table (DA/-38 for 802EE7B4 and 802525E4,
6D/109 for 80246434), offsets in-table. dd4 EMPTY returns read 802525E4, dd1
EMPTY read 80246434. Open input: the descriptor pointer r8 (t0) at 0x80042D7C.

Hypotheses: H-far-layer (802525E4 is the far/outer-ring table that dd4 auto-far
enables, so reading it on EMPTY is design), H-stale-desc (t0 for the EMPTY
pass is left pointing at a previous layer's descriptor), H-caller-arg (the
caller passes a different descriptor under dd4 scaling).

Single build: log r8, [r8+0..16], caller RA, and the pass index at function entry
for every keyed return in both arms (with 100% of EMPTY keys, not first 24 rows),
plus the descriptor owner table (grep who stores 802525E4 into a descriptor).
Controls: [span-base], [span-pred] npass>0 on ok keys, base 802525E4 present in
dd1 rows. Reuse tools/apply_s6516_cell_record.py as template; no guard.
