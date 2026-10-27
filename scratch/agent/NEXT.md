# NEXT: capture the dd4 EMPTY stream row with rasterizer bounds and store range
HYPOTHESIS-ID: g1c-dd8-limit
s6497: the bounds/store/sequence instrument built and ran cleanly, and dd1
positive controls passed, but this dd4 attempt logged only 8 `ok` stream rows.
The existing ForFace empty breadcrumb fired, so the target stream EMPTY row was
not observed and no hypothesis was selected. The duplicate diagnostic emission
was fixed in the script and generated source.

Hypotheses:
- H-order: stream returns before the rasterizer refreshes the table, so the empty return sees a stale/cleared all-127 table.
- H-scale: rasterizer computes integer bins outside the 64x64 table or rejects all rows at dd4 despite valid polygon inputs.
- H-writer: a later clear or overwrite erases valid rows before stream consumes them.

Do exactly one build/run: keep the current instrument, build Debug, and run
`zsh scratch/agent/s6492_forface.sh` (pinned dd1/dd4, 150 s). Increase only the
stream-return capture budget if needed so an EMPTY dd4 row is retained; do not
change the arm recipe or the bounds/store fields. Positive controls: dd1
nonempty stream rows, an in-range rasterizer fill, and matching `seq==ret` rows.
Discriminator: an EMPTY stream with no intervening rasterizer sequence selects
H-order; bounds outside 0..63 or stores outside 0x80130DB0..0x80132DAF select
H-scale; valid in-range bounds followed by a clear/overwrite before stream
selects H-writer. If no EMPTY row is captured, record the instrument as
unevaluable and do not infer a null.
