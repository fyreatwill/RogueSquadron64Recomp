# M5 Session 3437 — frequency contract at osRecvMesg entry

The independent retail arm used the whole-RDRAM positive control, physical
`0x165ED0:0x165ED4`, both title origins, and a field dump at the actual
`osRecvMesg` entry `0x800331D0`. The control fired, both phase buckets were
live (`632` and `633` VI rows), and the field summary retained `7,815` rows.

The fresh-build port image arm used the qualified LLE-only, spin-yield,
phase-gated route. It reached title `0x00790400` and hangar `0x006AB400`; the
phase, image-stage, RSP-source, task, and PCM controls were live, with no
crash or abort markers. Its bounded frequency witness retained `256` rows and
`107` distinct normalized tuples.

The exact normalized tuple intersection over
`s0,s1,source_word,source_byte,branch_selector,branch_state` was zero.
Therefore this run selects `H-PortTupleFamilyMissing`: at the common entry
boundary, the port does not expose a tuple family observed on retail. It
refutes `H-PortTupleFamilyMatch` and the previous interior-PC/entry-boundary
join explanation. The result points earlier in the port input/dispatch path;
it does not identify that producer or change audio behavior.

Evidence: `scratch/agent/s3437_m5_frequency_entry/oracle.log`,
`scratch/agent/s3437_m5_frequency_entry/run.log`, and
`scratch/agent/s3437_m5_frequency_entry/results.txt`.
