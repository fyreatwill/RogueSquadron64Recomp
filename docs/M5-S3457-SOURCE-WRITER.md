# M5 Session 3457 — source-slot writer attribution

The independent retail oracle ran with Rice video, the documented Start
schedule, a whole-RDRAM positive control, a title-phase write watch for
physical `0x001E8710:0x001E8714`, and an execution watch at `0x800645AC`.
The whole-RDRAM control recorded 11,483 writes, the source watch recorded
1,483 writes, and the producer execution watch recorded 1,707 hits. Title
writers were `0x800644B0` (510), `0x80064524` (164), `0x800078EC` (28),
`0x80018F5C` (1), `0x80018F80` (36), `0x80028F90` (4), `0x800C871C` (1),
and `0x80006FF4` (1).

The port was rebuilt with a phase-gated extension to the regeneration-safe
scalar-store census. Its four-PC output/state positive control fired, the
title phase was reached, and the source-writer table emitted 1,024 rows:
`0x800644B0` appeared 812 times and `0x80064524` appeared 212 times. No
retail-only writer PC appeared in the port table. These are independent
oracle and port evidence lines, both with same-run positive controls.

This selects `H-RetailWriter` at the observed title source-slot boundary and
rules out a port-only writer as the explanation for the differing loaded
`s0`. It does not establish that the retail-only stores produce the differing
word: the existing generated parity call passes `0` as its value argument,
so the writer-value field is not evidence. The next probe must preserve the
same phase/PC/ordinal join while capturing the actual post-store word.

ORIGIN: the source slot is written by the game-side generated scalar-store
sites identified above; the legitimacy of each stored value is unresolved.

Evidence: `scratch/agent/s3457_m5_source_writer/oracle.log` and
`scratch/agent/s3457_m5_source_writer/port_phase/run.log`.
