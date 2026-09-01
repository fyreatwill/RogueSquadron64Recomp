# NEXT work unit — join the retail nonzero source value to its producer/order

HYPOTHESIS-ID: m5-image-task-retail-source-writer

The previous oracle selected target-phase writer `0x800078EC` and nonzero
post-value words, but did not expose a separate DMA event identifier or the
producer that constructed those words. Do not change runtime behavior or add
a port instrument. Run one retail oracle table with source-pointer/value
joining and the same positive controls. First inspect supported options:

    env tools/oracle/build/rs64_oracle --help > /tmp/rs64_oracle_help.log 2>&1

    env tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/iter974-armB/projects/unix/libmupen64plus.dylib" --rom ./rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 3:start,7:start,11:start,15:a,30:start,45:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 --watch-pc 0x800078EC,0x800078E0,0x800C825C --pc-phase-log-width 0x006AB400:512 --post-value-watch 1 --post-value-pc 0x800078EC --post-value-pc-detail --vi-trace --detail-watch 1 --hit-cap 1 > /tmp/rs64_next_oracle.log 2>&1

Competing hypotheses and the discriminating measurement:

- H-RetailProducer: joined source pointers and values identify the producer
  that constructs the nonzero target span before `0x800078EC`.
- H-RetailDmaOrder: a separately identified first source-DMA payload is before
  or after the writer, selecting ordering as the remaining boundary.
- H-RetailValueParity: the joined retail words match or differ from the port's
  corresponding source values.
- H-CaptureInvalid: any whole-RDRAM/source-span control or target phase is
  absent; the result is unevaluable and must not update truth.

Report controls, target-phase timing, source pointers, joined stored words,
writer PC, destination, producer/PC attribution, and ordering against the
first source-span DMA. Preserve the oracle log at an absolute path. If the
join or separate DMA event is unavailable, record that boundary as open.
