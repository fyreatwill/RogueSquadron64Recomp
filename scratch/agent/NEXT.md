# Next: H-matrix — terrain-pass view matrix translation row
HYPOTHESIS-ID: g3c-owner-visual
State (s6320): RAM float-triple scan found no position (only timeline ramp 0x8011A8F4). 
Hypotheses: H-matrix (matrix loaded by terrain pass at/near 0x8004AA94 has smoothly drifting translation row = world position) vs H-camrel (translation ~constant, camera-relative) = H-none.
Measurement: fixup-script log of the 16 floats at the matrix pointer the terrain pass uses (find via static look at callers of 0x8004AA94/0x80046214), one per frame, lvl1 dd3 scripted flight, compare to craft motion; positive control = log must show rotation orthonormal rows. If H-camrel: ask owner whether jagged edge still matters.
