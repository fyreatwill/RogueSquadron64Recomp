# M5 Session 3661 — descriptor writer-PC census

Ran one paired 90-second census with the retail oracle and the validated
real-audio/LLE/spin-yield/autopilot port. The oracle watched whole RDRAM as a
positive control, descriptor ranges `0x171CE0`, `0x171E70`, `0x173B20`, and
`0x173CB0`, and dumped phase-gated type-2 tasks at `0x80033FCC`. The port kept
the existing `audtask-abi`, audio-object, task/DMA, and RSP-source rows.

The controls were valid: whole-RDRAM writes reached 194,936; the oracle
reported 1,610 phase-valid type-2 task rows with 0 invalid pointers; and the
port reached title `0x00790400`/1024 and hangar `0x006AB400`/512 with 3,582
ABI rows, 1,024 RSP-source rows, and 88 bounded audio-object rows.

The writer histograms do not support one universal writer for all four ranges.
In title, `0x173B20` and `0x173CB0` were written by the same dominant family,
headed by `0x80090DE4` (6,779 and 480 rows respectively) and including
`0x80091078`, `0x8009114C`, and the `0x80090A..0x80090DD8` family. The title
phase had no phase-gated writes for `0x171CE0` or `0x171E70`.

In hangar, `0x171E70` and `0x173CB0` shared that same family, headed by
`0x80090DE4` (9,729 and 2,575 rows respectively), while `0x173B20` had no
phase-gated writes. The oracle's task rows selected `data_ptr=0x80171E70`
for the hangar target, matching the port's repeated `audtask-abi` rows.

This selects `H-SharedPhaseProducer` for the ranges that are actively written
within each phase, and rejects `H-OneWriterAllRanges`. It does not establish
that the phase-inactive ranges are owned by another producer: their values may
have been initialized before the phase gate. The port task/source rows remain
the second evidence line for logical target identity; exact ownership of the
interleaved objects and pre-phase initialization remains open. No mitigation
or game-state change was made.

ORIGIN: diagnostic-only writer, task, phase, and source observations; no
guest or host state was modified.
