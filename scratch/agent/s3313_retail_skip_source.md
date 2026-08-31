# Session 3313 evidence — retail skip-allow source

Two independent no-press Rice runs armed whole-RDRAM and physical
`0x000B0B1C` write watches, watched PCs `0x800A5D80`, `0x800A5EE8`,
`0x800A6238`, `0x800A6248`, `0x800A6274`, and `0x800A62B4`, VI tracing,
and phase histograms. Both passed the 10,000-write positive control,
`[gpr-ctl]`, VI `640 @ 0x0066A500`, cinematic entry, and title VI-1024.

At the 48.1–48.5 s transition, `0x800A6238` repeatedly is not taken with
`$a0=0`, so the incoming controller operand is not the source. A late
physical `0x000B0B1C` write from `0x800A9360` appears in both runs. After
it, `0x800A6248` loads `$v0=1`, `0x800A6274` proceeds with `$a0=1`, and
`0x800A62B4` executes. Earlier B1C writes are boot/prologue stores from
`0x800078EC`, `0x800A5E7C`, `0x800A5EE8`, and `0x800A5F00`.

This selects `H-RetailB1CWrite` and refutes `H-RetailIncomingA0`,
`H-RetailBoth`, and `H-CoverageInvalid`. The stored byte is independently
established as nonzero by the subsequent `$v0=1` load in the same watched
sequence; the oracle's post-store formatter did not emit a separate value
tuple.

