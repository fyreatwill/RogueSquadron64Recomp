# M5 Session 4149 — source-setup join route qualification

The planned source-construction predecessor/state join was not qualified as a
paired comparison. The retail oracle passed the whole-RDRAM control and both
target phase buckets, and its setup execution watches fired: title setup PCs
`0x8008F2A8/BC/C0/C4/C8` each hit twice with predecessor `0x80001C90`; hangar
`0x800AB694` hit 437 times with predecessor `0x800AB690`. The concurrent port
remained at VI 640 and produced no target-phase setup rows, so the comparison
is route-invalid.

The iteration did land two regeneration-safe instrument repairs. The port setup
phase filter now admits the qualified title origin `0x00790400`, and
`fixup_game_funcs.py` now inserts the existing setup-step/state probes when the
`s2240` callsite annotation lies between the delay slot and `rs_memset`; the
old anchor was not unique after regeneration. The Debug target rebuilt after
the fixup.

ORIGIN: the setup PCs and predecessors are retail guest execution witnesses;
the port route was not altered. No guest behavior, audio wait, cap, predicate,
slot state, or host writeback changed.

Evidence: `scratch/agent/s4148_m5_source_callsite/`.
