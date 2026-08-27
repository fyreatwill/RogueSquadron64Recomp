# NEXT work unit (s2718) — M5 hangar writer/value boundary

HYPOTHESIS-ID: m5-hangar-c88-publication-boundary

## Work unit

Use the retail oracle to inspect the already identified hangar-side writer at
guest PC `0x80094648`, with the whole-RDRAM positive control first and the
hangar origin `0x006AB400:512` phase-gated. Capture its GPR fields and the
post-store value/destination evidence in one run. This is the remaining M5
Step-4 ground-truth boundary; do not change the port until the retail writer,
destination, and value transition are named.

## Competing hypotheses and discriminator

- `H-hangar-c88-writes-pcm`: the PC executes in hangar and its output/value
  joins the sampled nonzero PCM source or a named voice descriptor.
- `H-hangar-c88-writes-control`: it executes but writes a status/gate/control
  field unrelated to PCM publication.
- `H-hangar-c88-unreached`: the whole-RDRAM control passes but the hangar
  phase or watched PC does not, so the null is unevaluable.

The discriminator is the complete phase-gated `watch-pc` row: execution count,
caller/previous PC, GPR arguments/return, mode/field values, and any observed
destination/value transition joined to the hangar phase. Whole-RDRAM hits plus
hangar reach are required before interpreting a zero. A PCM/source join selects
the first hypothesis; a live unrelated field selects the second; absent phase
or control selects the third.

## Exact command

```sh
mkdir -p scratch/agent/s2718_m5_hangar_writer
env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 90 --watch-write 0x0:0x800000 --watch-pc 0x80094648 --pc-phase-log 0x006AB400 --pc-field-dump 0x80094648 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2718_m5_hangar_writer/run.log 2>&1
```

No writeback, remap, guard, or mitigation is authorized by this capture
alone.
