# Session 3140 M5 retail-source census

## Work unit and hypotheses

The prescribed work was a source census before any new oracle or port
instrument. The competing hypotheses were:

- `H-RetailBoundaryFound`: new source exposes an un-watched target-phase edge.
- `H-RetailBoundaryAbsent`: a newly found candidate is control-only or absent.
- `H-SourceInsufficient`: no defensible candidate exists in the available source.

The discriminator is whether the census exposes a new transition-capable
instruction. If it did, the next measurement would be one phase-keyed oracle
run with a whole-RDRAM positive control and title `1024`/hangar `512` controls.

## Measurement and result

Command:

```sh
rg -n 'pending|descriptor|osViSetMode|__osViSwapContext|VI_ORIGIN_REG' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 \
  syms docs --glob '!PORTING-STATE.md'
```

The companion bodies remain literal `INCLUDE_ASM` stubs:

```c
INCLUDE_ASM("asm/nonmatchings/libultra/io/visetmode", osViSetMode);
INCLUDE_ASM("asm/nonmatchings/libultra/io/viswapcontext", __osViSwapContext);
```

The project symbol table has only addresses/sizes (`osViSetMode` at
`0x800352D0`, `__osViSwapContext` at `0x80035550`). Remaining matches are
existing declarations, comments, symbol records, and closed probes. No new
transition-capable PC or pending-to-descriptor edge was found.

`H-SourceInsufficient` is selected. No build, oracle watch, port
instrumentation, audio change, or route change was justified. This is
single-source static evidence and is falsifiable by supplying an equivalent
generated body or instruction-level disassembly.
