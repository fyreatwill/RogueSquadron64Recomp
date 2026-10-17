# Session 5203 retail entry field revisit

The fixed retail-oracle run used the whole-RDRAM positive control and both
mission VI origins. The control fired, the `0x00690400` and `0x00620400`
phase rows were 40 and 46, and the run completed normally after 270 seconds.

`fillSampleStreamRange = 0x8008FAAC` executed 290,798 times, including
155,501 retained hit rows, while the exact interior `0x800903F0` executed
zero times and produced zero field rows. The bounded field dump at the entry
recorded 145,514 phase-gated hits before its 32,768-row retention cap; the
interior remained at zero.

This selects `H-retail-branch-diff` as single-source oracle evidence: retail
enters the containing function but does not reach the watched interior. The
entry field tuples are now available for a future port-side join, but this run
does not identify the port writer or prove a port defect. The earlier range
watch attempt was invalidated because combining it with the whole-RDRAM
control produced an unbounded 4.3 GB trace; it was SIGKILLed and is not used
as evidence.
