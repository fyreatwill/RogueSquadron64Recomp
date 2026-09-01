# M5 session 3543 — source-range pre-clear ordering

The independent retail oracle first passed its whole-RDRAM control (11,058
writes), then reached title VI 1024 and hangar VI 512. It wrote 384 bytes in
`0x178C80:0x178E00` and 674 bytes in `0x1797B0:0x179930`; the retail writer
census included `0x800078EC` for the first range and
`0x8001E2C0`/`0x80007670`/`0x8001FAxx` for the second.

The same-build real-audio port passed its phase and downstream controls and
recorded both entry and exit of the two target `rs_memset` calls. Title entered
the clear with `pre_fnv=25E26BC5`, `pre_nz=0`, then exited zero. Hangar entered
with `pre_fnv=0394E335`, `pre_nz=344`, then exited with `pre_fnv=25E26BC5`,
`pre_nz=0`. The port also produced 1,024 source-DMA rows, 768 field-range
writer rows, 4,075 image-stage rows, and 87 paired PCM-boundary rows; no crash
or abort occurred.

This selects `H-PreclearProducer` for the hangar range: nonzero source data is
present immediately before the legitimate clear. Title separately matches
`H-ClearBeforeProducer` at this boundary. The port capture did not identify
the writer that established the hangar pre-clear bytes; the existing
target-phase scalar writer census saw only the zeroing loop, so writer identity
remains open. No audio, PCM, or output state was changed.

Evidence: `scratch/agent/retail_preclear_groundtruth.log` and
`scratch/agent/s3543_m5_preclear_capture/run.log`.

ORIGIN: the only mitigation-shaped operation observed here is the legitimate
`rs_memset` zero fill at `0x800078EC`; this iteration added no guard or skip.
