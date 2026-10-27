# NEXT: which span compare rejects the in-table dd4 windows, and what are the cell bytes?
HYPOTHESIS-ID: g1c-span-reject-predicate

s6519: dd4 EMPTY (703 calls) are all in-bounds windows (nclear=594 npass=0 on a 54x11 window of the 64x64 table); H-oob refuted.
Hypotheses: H-cmp0 (first compare span<cell+3 rejects: span bytes too small at dd4), H-cmp1 (second compare, cell+4 vs plane byte), H-stale (span grid bytes at 0x80130DB0 stale/0x80 vs refreshed at dd1).
Discriminator: one build combining s6515 split (ns0/ns1) and s6516 cell-rec on keyed EMPTY returns only (first 4 per call), plus span-grid hash at return; bucket offline by compare and by span value; control = dd1 ok calls same fields.
Reuse s6519_window.sh with s/s6519/s6520/ and apply s6515+s6516 patches' output into the [ret-sum] line.
