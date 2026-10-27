# NEXT: distinguish rasterizer ordering from out-of-range computed bins at dd4
HYPOTHESIS-ID: g1c-dd8-limit
s6496: `binPolygonIntoTerrainGrid` is the table writer. In one pinned dd1/dd4 run,
dd4 EMPTY returns had repeated nonzero-area polygon inputs and stable divisor 12.8,
but all-127 tables and collapsed window w=0,54/56,0,10. H-footprint-degenerate at
the input boundary is refuted. H-order and H-scale remain.

Hypotheses:
- H-order: stream returns before the rasterizer refreshes the table, so the empty return sees a stale/cleared all-127 table.
- H-scale: rasterizer computes integer bins outside the 64x64 table (or rejects all rows) at dd4 despite valid polygon inputs.
- H-writer: a later clear or overwrite erases valid rows before stream consumes them.

Do exactly one build/run: extend `tools/apply_s6496_bin_inputs.py` to log the
rasterizer's four computed bounds immediately after 0x800429BC and the first/last
table-store address in its clear/fill loops; increment a sequence at rasterizer
entry/return and include it in `[streamdump]`. Apply the script, build Debug, and
run `zsh scratch/agent/s6492_forface.sh` (pinned dd1/dd4, 150 s). Positive controls:
dd1 nonempty stream rows and at least one rasterizer fill. Discriminator: an EMPTY
stream with no intervening rasterizer sequence selects H-order; bounds outside
0..63 or stores outside 0x80130DB0..0x80132DAF select H-scale; valid in-range
bounds followed by a clear/overwrite before stream selects H-writer. Preserve
the three hypotheses and the one-run arm table in the session entry.
