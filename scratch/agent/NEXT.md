# NEXT: are dd4 mission-table EMPTY calls outside the table (legit) or in-table rejected (defect)?
HYPOTHESIS-ID: g1c-span-reject-predicate

s6518: dd4 EMPTY on 802EE7B4 = 345/2402, dd1 = 0/2643 (pinned pose lvl1).
Hypotheses: H-oob (EMPTY calls request a window beyond the table bounds: legit), H-reject (window inside table but cell bytes fail the two span compares at dd4: defect), H-cap (EMPTY coincides with a pool/budget cap).
Discriminator: extend the [ret-sum] line with a0 window origin (row/col), table dims, and per-call compare-reject counts (reuse s6515 split); then bucket EMPTY calls by in-bounds vs out. Control: dd1 non-EMPTY rows bucket in-bounds. Reuse s6518_ret_sum.sh with s/s6518/s6519/.
