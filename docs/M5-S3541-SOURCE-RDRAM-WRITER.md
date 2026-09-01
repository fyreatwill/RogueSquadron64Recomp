# M5 session 3541 — source RDRAM writer attribution

The build completed successfully. The retail oracle used a whole-RDRAM
positive control plus a physical watch on `0x178C80..0x178D80`; it reached
title VI 1024 and hangar VI 512. The positive-control threshold fired at
10,000 callbacks. The target watch recorded 264 post-store samples and a
nonzero final 256-byte snapshot. In the 512 phase, the writer histogram
contained multiple retail guest PCs, including `0x8009025C`, `0x8008FF04`,
and `0x800906A0`.

The first port capture reached title and hangar with source, image-stage,
completion, and PCM controls live, but omitted the span-writer enable. Its
null writer result was therefore discarded as capture-invalid. The corrected
same-build capture enabled the span writer, candidate-store, and memset
hooks. It reached title VI 1024 and hangar VI 512 with no crash or abort.

The corrected port capture produced 768 `field348-writer` rows for the two
watched spans. For the selected `0x178C80` span, the rows were zero-valued
byte writes from exactly one writer, PC `0x800078EC`; no candidate-store or
memset rows fired. Downstream image-stage and join controls remained live,
and the stage source for the affected image task remained zero.

This selects `H-RdramWriterPort`: the port has a phase-qualified zero-fill
writer path at `0x800078EC`, while retail has a distinct guest writer family
and a nonzero final source range. It rules out an absent writer and an
invalid phase capture. The writer's host/writeback origin and why it emits
zero bytes remain open. No audio, PCM, or output state was changed.

Evidence: `scratch/agent/s3541_m5_source_writer/oracle.log` and
`port-fixed.log`.
