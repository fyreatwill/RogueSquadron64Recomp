# Next: locate the true player/camera world position for G3c(a) fade centre
HYPOTHESIS-ID: g3c-owner-visual
State (s6319): footprint-centre idea refuted (AA94 = ring-wide sweep). 0x80138D20/0x80137DBC blocks are constant garbage.
Hypotheses: H-ramscan (a float triple in RDRAM changes smoothly during scripted flight and equals camera/craft position) vs H-matrix (position only exists inside the view matrix translation; read it from the matrix the terrain pass loads) vs H-none.
Discriminating measurement: one lvl1 run with a dump flag snapshotting 0x80000000-0x80800000 every ~30 VIs during steady flight (capture once); offline find 4-byte-aligned float triples whose per-snapshot deltas are small, smooth, and speed-consistent, plus a positive control (the known cell col/row ring indices should correlate with the recovered x/z). Then hook fade with that source.
