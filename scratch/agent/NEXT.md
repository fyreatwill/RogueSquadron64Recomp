# NEXT: dd1 (retail) gate census + table-row population (H-link-empty)
HYPOTHESIS-ID: g1c-dd8-limit
Established (s6477): dd2/dd3 ~99% of cells exit at BB18 because table 0x80136FCC row[cell+0x1E].link==0xFFFF; indices vary 469..2532 (real rows). Pass cells have valid links.
Work: rerun s6477_gate.sh with a dd1 arm (ROGUESQ_DRAW_DISTANCE=1) alongside dd3; compare BB18 share and pass count per window. Also dump row[]link fraction of the whole table once (offline from RDRAM) to see how many rows are 0xFFFF globally.
Outcomes: dd1 share ~equal => far cells legitimately empty; widening needs more populated cells (terrain data limit, not gate) -> look at what sets the cell list/row link (loader). dd1 share much lower => dd>1 corrupts cell->row mapping (find writer of cell+0x1E).
