# Session 5300 symbol audit

Candidate: `spawnChildNpcWithTransform = 0x8003F1D0`.

The companion symbol file defines the named callable at that address. The
bounded rename helper, run over `0x8003F1D0..0x8003F1D4` with `python3`,
reported `already-synchronized` and renamed zero references in zero files.
Independent searches of the generated tree found the named body in
`funcs_9.c`, its declaration in `funcs.h`, and its overlay record in
`recomp_overlays.inl`. No `func_8003F1D0`, `fake_func_8003F1D0`, or conflicting
callable/data fragment was found.

Conclusion: preserve the existing name. This work unit required no build or
soak.
