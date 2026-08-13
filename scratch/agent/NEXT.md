# NEXT work unit (s865)

HYPOTHESIS-ID: m3-coalesce-entry-state

Run one retail-oracle writer-PC experiment. Preserve the whole-RDRAM watch,
VI trace, ROM, and repeated-Start schedule, but inspect the oracle's global
200-hit detail cap and make the smallest bounded tool change needed to retain
detail for the target watch indices. Then run the same three watches on one
30-second retail capture. Do not change emulated game behavior or add a
mitigation.

Competing hypotheses:

- H-init-writer: target writes are only boot/heap initialization PCs.
- H-runtime-writer: a later gameplay/heap-maintenance PC writes the state.
- H-control-invalid: whole-RDRAM or VI control fails after the tool change.

Discriminating measurement: whole-RDRAM and VI must fire, and each target hit
must print its guest PC. Target PCs at boot versus later runtime split
H-init-writer from H-runtime-writer; failed controls select
H-control-invalid. Counts without PCs are unevaluable.

Exact command:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 30 --watch-write 0x0:0x800000 \
  --watch-write 0x1163E4:0x1163F0 --watch-write 0x10FF18:0x10FF1C \
  --vi-trace \
  --press '6:start,11:start,16:start,21:start,26:start'
```

Keep the current probe build; no port run is needed unless the attributed PC
requires a paired port measurement.
