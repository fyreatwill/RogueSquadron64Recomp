# NEXT work unit — static caller/order audit for the remaining B1C source

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

Session 3314's corrected port run passed positive controls and showed
`$a0=0` at 6238, `$v0=0` at 6248, 6274 taking, and no 62B4. Known stores at
5EE8, 61D0, and 9360 were instrumented; only the prologue zero store fired.
Do not repeat that census.

## Competing hypotheses

- `H-PortB1CUncalled`: the nonzero writer is in a caller or alternate overlay
  path, not one of the three funcs_27 stores.
- `H-PortB1COrder`: a known writer exists but executes before the prologue
  zero, so the observed phase sees the reset value.
- `H-PortB1CDead`: all known nonzero writers are unreachable on this route and
  the port has no legitimate source corresponding to retail's late write.

## Discriminator

One bounded static audit, no runtime build: enumerate every reference to
`0x800B0B1C`/offset `0xB1C` in the generated functions and companion symbol
maps, then trace the callers of `cinematicLoopBody`, the 61D0 block, and the
9360 block. A complete caller/order table that names an alternate writer,
proves a pre-reset order, or proves all writers dead selects the matching
hypothesis. If generated code has no complete caller relation, stop and
request the Windows/source tree rather than adding another runtime field.

## Exact commands

```
rg -n '0X[Bb]1[Cc]|0x[Bb]1[Cc]|800B0B1C|800A61D0|800A9360' ../N64Recomp/RecompiledFuncs ../N64Recomp/syms
rg -n 'cinematicLoopBody|800A5D80|800A61D0|800A9360' ../N64Recomp/RecompiledFuncs/funcs_*.c
```

Record the table and selected hypothesis in a new evidence file. No M5 Step
3 or behavior change is authorized by this audit.
