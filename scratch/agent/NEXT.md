# Attribute the retail target writer
HYPOTHESIS-ID: m5-audio-destub

s4604 refuted retail use of the port source span: in the driven retail
hangar phase the candidate source range `0x62B9F8..0x62BA98` was all `0xFF`,
while target `0x1724C0..0x17250C` contained the same five name-like records,
including `late`. The alternate retail source location is not yet known.

Competing hypotheses:

- H-one-writer: one retail guest writer publishes all five target records from
  a different table or direct literals.
- H-composed-writers: multiple retail guest writers compose the target span.
- H-host-path: the target bytes are produced by a host/translation path with
  no attributable guest writer.

Discriminating measurement: phase-gated retail writer-PC histogram for target
watch 0x1724C0..0x17250C, with whole-RDRAM positive control in the same run.
One writer PC covering all 76 target writes selects H-one-writer; multiple
writer PCs covering distinct target offsets select H-composed-writers; zero
target writer callbacks despite target snapshot bytes selects H-host-path.

Run from the repo root; no build is needed:

```sh
mkdir -p scratch/agent/s4605_retail_target_writer
env tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --watch-write 0x0:0x800000 --watch-write 0x1724C0:0x17250C \
  --first-watch 1 --pc-hist-watch 1 --pc-hist-phase 0x006AB400:512 \
  --hit-cap 200 --pc-phase-quiet --pc-phase-log-width 0x006AB400:512 --vi-trace \
  > scratch/agent/s4605_retail_target_writer/retail.log 2>&1
```

Do not add a mitigation.
