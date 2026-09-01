# NEXT work unit — qualify the retail source value after writer attribution

HYPOTHESIS-ID: m5-image-task-retail-source-writer

The previous oracle selected target-phase writer `0x800078EC` and pre-target
ordering, but ordinary write rows did not include stored words. Do not change
runtime behavior or add a port instrument. Run one retail oracle table with
the same controls plus post-value sampling:

    env tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/iter974-armB/projects/unix/libmupen64plus.dylib" --rom ./rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 3:start,7:start,11:start,15:a,30:start,45:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 --watch-pc 0x800078EC,0x800078E0,0x800C825C --pc-phase-log-width 0x006AB400:512 --post-value-watch 1 --post-value-pc 0x800078EC --post-value-pc-detail --vi-trace --detail-watch 1 --hit-cap 1 > /tmp/rs64_next_oracle.log 2>&1

Competing hypotheses and the discriminating measurement:

- H-RetailValueZero: target-phase `0x800078EC` stores zero words, matching the
  port's zero-fill; this closes value parity at the writer boundary.
- H-RetailValueNonzero: target-phase `0x800078EC` stores nonzero or changing
  words; this selects a producer/value divergence despite matching writer.
- H-RetailDmaOrder: the first source-DMA event is measurably before the
  `0x800078EC` stores; this selects ordering rather than value construction.
- H-CaptureInvalid: any whole-RDRAM/source-span control or target phase is
  absent; the result is unevaluable and must not update truth.

Report controls, target-phase timing, stored words, writer PC, destination,
and ordering against the first source-span DMA. Preserve the oracle log at an
absolute path. If post-value output is still absent, record value/order as
open rather than selecting a hypothesis.
