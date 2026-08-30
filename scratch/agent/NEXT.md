# NEXT work unit — retail cinematic loop/exit ground truth

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

## Resume context

Session 3305 passed every post-viewer control and recorded the complete port
edge sequence through `mainGameLoop`'s call at `0x8003E10C` and
`cinematicLoopBody` entry `0x800A5D80`. The port never emitted the function
return at `0x800A6618`, caller return, second menu activation, or title 1024,
while VI updates and SP completions continued. This selects
`H-CinematicEntryStalls` as single-source port evidence. Retail Session 3283
already proves the call returns, but does not identify its internal loop/exit
path. Iron rule 12 requires that independent path before a port probe.

## Competing hypotheses

- `H-RetailFiniteLoop`: retail enters `0x800A6024`, takes the
  `0x800A64B4→0x800A6024` backedge a finite number of times, then reaches
  `0x800A64BC`, the `0x800A65E4` epilogue, `0x800A6618`, and caller
  continuation `0x8003E114`.
- `H-RetailEarlyExit`: retail takes the early `0x800A5DD8→0x800A65E4` path;
  the presumed main loop is not part of this attract call.
- `H-RetailAlternateExit`: retail returns and reaches `0x8003E114`, but the
  selected early-exit and main-loop edges do not describe the live path.
- `H-CoverageInvalid`: the whole-RDRAM control, VI trace, cinematic entry, or
  caller continuation is missing; no null is interpretable.

## Discriminator

Run the retail ROM once under the oracle with Rice, a whole-RDRAM write
positive control, VI trace, and one execution table containing entry,
early-exit branch, loop head, loop exit gate and target, backedge, epilogue,
return, caller continuation, and second menu call. Use lifetime counts,
`prev_pc`, and the printed `$v0/$s1/$a0/$a2` tuples to select the live path.

Entry plus repeated loop-head/backedge rows followed by `0x800A64BC`,
epilogue, return, and caller continuation selects `H-RetailFiniteLoop`.
Entry followed by epilogue with `prev_pc=0x800A5DD8`, then return and caller
continuation, selects `H-RetailEarlyExit`. A proven return/caller continuation
without either predecessor selects `H-RetailAlternateExit`. Any missing
positive control selects `H-CoverageInvalid`.

## Exact commands

Create one self-contained driver at
`scratch/agent/s3306_retail_cinematic_exit/run.sh` that runs:

```sh
env tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 30 --hit-cap 10000 \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x800A5D80,0x800A5DD8,0x800A6024,0x800A6074,0x800A64B4,0x800A64BC,0x800A65E4,0x800A6618,0x8003E114,0x8003E13C \
  --vi-trace
```

The driver must capture stdout/stderr under its session directory, require at
least 10,000 whole-RDRAM hits plus VI 640 and `0x800A5D80`, parse every PC's
lifetime `exec-prev` count/order, and reject the run if `0x8003E114` is absent.
No port instrumentation or build belongs in this work unit.
