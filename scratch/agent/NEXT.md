# NEXT work unit (s2185) — retail writer census for the six cinematic words

HYPOTHESIS-ID: m5-a1-retail-writer-census

## Work unit

Run one 45-second Rice retail-oracle session. The current port run supplied
the missing image-DMA positive control and selected
`H-AudioDmaTitleHangarOnly` for that completing image-arm run, so ask the
independent retail ROM whether it writes any of the six named physical words
and which guest PCs write them. Do not add a port instrument, rebuild, or land
a mitigation.

Exact command from the repository root:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 45 --hit-cap 64 --vi-trace \
  --watch-write 0x0:0x800000 \
  --watch-write 0x25A580:0x25A584 \
  --watch-write 0x0CA748:0x0CA74C \
  --watch-write 0x0C7B0C:0x0C7B10 \
  --watch-write 0x165E40:0x165E44 \
  --watch-write 0x0CDB58:0x0CDB5C \
  --watch-write 0x2231EC:0x2231F0 \
  --first-watch 0 --first-watch 1 --first-watch 2 --first-watch 3 \
  --first-watch 4 --first-watch 5 --first-watch 6 \
  --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 \
  --pc-hist-watch 4 --pc-hist-watch 5 --pc-hist-watch 6 \
  --watch-pc 0x800078EC,0x800A8144,0x80057100 \
  > scratch/agent/oracle_s2185_cinematic_writer.log 2>&1
```

Record a compact table in `scratch/agent/s2185_cinematic_writer.txt` with
the whole-RDRAM control count, each target watch count, target writer-PC
histogram, and VI transitions. Require the whole-RDRAM watch to fire before
interpreting any target zero.

## Competing hypotheses and discriminator

- `H-RetailWritesNamedWords`: one or more target watches fire with the whole-
  RDRAM control present; the writer-PC histogram names a legitimate retail
  producer, and known producer PCs show their live VI width/origin.
- `H-RetailDoesNotWriteNamedWords`: whole-RDRAM control fires and the retail
  route reaches 640, but all six target watches remain zero.
- `H-RetailWritesOnlyNonCinematic`: target watches fire, but the writer
  histogram and same-run VI transitions place them outside the 640 route.
- `H-OracleCoverageFailure`: whole-RDRAM control or Rice/640 coverage is
  absent; classify the run as coverage-only and make no writer claim.

The discriminator is one same-run table of whole-RDRAM hits, six target-watch
hits, target writer-PC histograms, and VI transitions. If target writes occur,
identify the writer and whether the value is legitimate before proposing any
port-side change. Do not add a copyToRAM/CIMG/DMA guard, disable `NAN_CHECK`,
skip/allow the cinematic loads, or re-flip the image arm default.
