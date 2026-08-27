# NEXT work unit (s2583) — retail writer/value boundary for M5 contract

HYPOTHESIS-ID: m5-audio-contract-gap

## Single work unit

Run one retail-oracle capture that attributes the existing candidate output/PCM
ranges by writer PC and post-store value, phase-gated to title and hangar.
Do not alter the port or promote any task/output field.

## Competing hypotheses and discriminator

- `H-RetailLegitZero`: retail reaches the same boundary and legitimately writes
  zero/empty values; the port's zero PCM is not evidence of a missing producer.
- `H-RetailWriterMissing`: retail has a nonzero writer/value event in the target
  phase that the port does not reproduce.
- `H-RetailAddressMismatch`: retail writes a nonzero value, but to a different
  candidate range or through a different phase-owned address than the port
  observer uses.

The discriminator is one phase-keyed oracle table for watches at `0xA0F50`,
`0x141AD0`, and `0x1498A`, including first hits, writer-PC histograms, and
post-store nonzero/FNV summaries. Whole-RDRAM callbacks must reach 10,000 and
VI must include title `0x00790400 @ 1024` and hangar `0x006AB400 @ 512`;
otherwise the capture is unevaluable. A phase-matched nonzero retail writer
selects `H-RetailWriterMissing`; a zero retail table selects `H-RetailLegitZero`;
a nonzero writer absent from all three watches selects `H-RetailAddressMismatch`
and requires a new bounded address census.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 120 --watch-write 0x0:0x800000 \
  --watch-write 0xA0F50:0xA0F54 --watch-write 0x141AD0:0x141AF0 \
  --watch-write 0x1498A:0x1498B \
  --first-watch 1 --first-watch 2 --first-watch 3 \
  --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 \
  --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 \
  --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace > scratch/agent/s2583_m5_retail_writer_value.log 2>&1
```

Record the oracle result before any port-side instrumentation or mitigation.
