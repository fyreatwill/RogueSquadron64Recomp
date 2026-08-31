# M5 Session 3434 — frequency-result writer

The independent retail oracle ran with a whole-RDRAM positive-control watch,
the target watch at physical `0x165ED0:0x165ED4`, both observed title origins,
candidate execution watches, phase writer histograms, and post-store sampling.

Controls were valid: the whole-RDRAM watch reached 10,000 callbacks, and both
`0x00790400:1024` and `0x00790800:1024` phase buckets recorded 632 VI rows.
The target had 19,029 lifetime writes. In the phase histograms,
`0x800331E0` joined target writes in both buckets (1 and 2 rows), while
`0x80033420` joined only the second bucket (2 rows). The stronger post-store
control distinguished them: samples attributed to `0x800331E0` were 442/442
nonzero, while `0x80033420` was 0/8 nonzero. The target's final snapshot was
nonzero.

This selects `H-Candidate331E0` as the retail frequency-result writer at the
observed target boundary. It refutes `H-Candidate33420` as the nonzero result
writer and makes `H-UnlistedFrequencyWriter` unlikely at this boundary. The
candidate's caller/input contract remains unresolved; no port behavior or
audio path changed. Raw capture: `scratch/agent/s3434_m5_frequency_writer/oracle.log`.
