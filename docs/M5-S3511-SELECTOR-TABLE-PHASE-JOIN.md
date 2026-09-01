# M5 Session 3511 — selector-table phase-matched join

The independent retail capture passed the whole-RDRAM positive control at
10,000 callbacks and reached 632 title VI frames. The writer PCs were live,
and post-value watches observed hangar stores at `0x8008F228`/`0x8008F264`
with values `0x80171E70`/`0x80173CB0`.

The first port retry reached title and hangar, but its witness remained
title-only because the port hangar phase is VI width 512. The fixed witness
admitted `width=512, origin=0x006AB400`; the same run emitted title values
`0x80171CE0`/`0x80173B20` and hangar values `0x80171E70`/`0x80173CB0` at the
same writer PCs. Selector load/writer/producer controls were positive.

At the matched hangar stores, retail and port agree on both stored values and
writer PCs, but the writer context already differs: retail reports
`s1=0x0000561F`, port reports `s1=0x00005622`; shared fields include
`s0=0x12` and `a0=0`. This selects `H-InputDivergence` at the writer-input
boundary, rules out a writer-route-only explanation at the measured PCs, and
refutes capture invalidity. The exact producer of the differing context
remains open. The witness is diagnostic-only.
