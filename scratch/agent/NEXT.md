# NEXT: who writes the span grid at 0x80130DB0 and what column bound does it use?
HYPOTHESIS-ID: g1c-span-reject-predicate

s6520: dd4 span bytes read as 0x80 (never written) at x>=32 (72% of 4844 reads vs 10% baseline); dd1 has none.
Hypotheses: H-writer-bound (span-grid writer loops only over the dd1 window width; dd4 window reads past it), H-init (grid init clears to 0x80 and writer is skipped for far cells by another dd gate), H-stride (grid row stride is 32 so x>=32 aliases other rows).
Discriminator: one build, log all writes (PC, offset from 0x80130DB0, value) in the span-grid writer family (s6512 all-span-writers patch exists: reuse) for dd1 vs dd4 over one frame; bucket offline by column x. Positive control: dd1 columns <32 must show writes. No writes at x>=32 in dd4 => H-writer-bound/H-init (find loop bound); writes present but 0x80 => H-stride.
