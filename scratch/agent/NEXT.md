# NEXT work unit — map retail producer destination

HYPOTHESIS-ID: m5-retail-producer-destination-map

Session 3413 established only a global retail negative: the producer executed
9,667 times, but the port source span had zero writes and no phase-qualified
rows. The next unit must determine whether retail publishes to the previously
observed destination instead.

Competing hypotheses and discriminating measurement:

- H-RetailPublishes1935E0: hangar-phase writes from `0x800078EC` land in
  physical `0x1935E0:0x1935F0`, with nonzero post-store values; this selects a
  retail destination mismatch against the port span.
- H-RetailPublishes1797B0: hangar-phase writes land in physical
  `0x1797B0:0x179A48`; nonzero post-store values select the corresponding
  source-span contract.
- H-RetailPublishesNeither: both destination watches remain empty in the
  hangar bucket while producer execution is controlled; this selects an
  unresolved producer-route/phase attribution problem.

The single discriminator is one retail-oracle run with whole-RDRAM positive
control, the producer execution watch, both destination watches, post-store
sampling, and a hangar-phase writer histogram. Require complete controls and
both destination histograms before classifying.

Exact commands:

1. `mkdir -p scratch/agent/s3414_retail_destination_map && tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-glide64mk2.dylib --secs 120 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179A48 --watch-write 0x1935E0:0x1935F0 --watch-pc 0x800078EC --pc-phase-log 0x006AB400 --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-phase 0x006AB400 --post-value-watch 1 --post-value-watch 2 --post-value-pc 0x800078EC > scratch/agent/s3414_retail_destination_map/oracle.log 2>&1`
2. Check whole-RDRAM, title/hangar, producer execution, both destination
   histograms, and retained post-values; classify only if the controls and
   hangar bucket are complete.
