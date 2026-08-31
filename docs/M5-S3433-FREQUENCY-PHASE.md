# M5 Session 3433 — retail frequency phase repair

The independent retail oracle first ran with `--vi-trace`, a whole-RDRAM
positive-control watch, and the validated Start schedule. The control reached
10,000 callbacks. The title route changed to width 1024 at origin
`0x00790400`, then alternated between `0x00790400` and `0x00790800`; the
earlier `0x00790400`-only phase configuration was incomplete.

A second oracle arm watched physical `0x165ED0:0x165ED4` and configured both
observed title origins at width 1024. The whole-RDRAM control again passed.
The target had 12,536 lifetime writes; phase writer histograms were live for
both buckets: 634 VI rows at `0x00790400` and 633 at `0x00790800`. The phase
writer sets included `0x800331E0` (1 and 2 writes respectively), alongside
other writers. Post-value sampling retained nonzero values, including
`0x00005622` and `0x0000561F`, but is not by itself an attribution of either
frequency return.

This selects `H-OraclePhaseOriginMismatch` and refutes a phase-signal absence
at the observed title route. It does not yet identify the exact frequency
writer; the next probe should use both corrected origins with a bounded
execution-watch set for the candidate writers and the frequency call/return
boundary. No port behavior changed.

Evidence: `scratch/agent/s3433_m5_frequency_phase/`.
