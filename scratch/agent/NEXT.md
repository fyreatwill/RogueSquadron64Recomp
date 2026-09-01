# NEXT work unit — phase-gated source-span writer table

HYPOTHESIS-ID: m5-image-task-retail-source-writer

The previous oracle selected target-phase writer `0x800078EC` and nonzero
post-value words, and joined the immediate `0x800052C4 -> 0x800078E0` path,
but did not expose a separate DMA event identifier or the earlier producer.
Do not change runtime behavior or add a port instrument. Run one retail
oracle table using the source-span writer histogram and field context in one
capture, with the same positive controls:

    env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB/projects/unix/libmupen64plus.dylib --rom ./rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 3:start,7:start,11:start,15:a,30:start,45:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 --watch-pc 0x800078EC,0x800078E0,0x800C825C,0x800052C4,0x8002BEEC --pc-phase-log-width 0x006AB400:512 --pc-field-dump 0x800078EC,0x800078E0,0x800052C4,0x8002BEEC --pc-hist-watch 1 --pc-hist-phase 0x006AB400:512 --post-value-watch 1 --post-value-pc 0x800078EC --post-value-pc-detail --vi-trace --detail-watch 1 --hit-cap 1 > /tmp/rs64_next_oracle.log 2>&1

Competing hypotheses and the discriminating measurement:

- H-RetailProducer: the phase-gated writer histogram/field rows identify a
  stable earlier guest-PC producer and its source buffer.
- H-RetailDmaOrder: a separately identified first source-span payload is
  before or after `0x800078EC`; if no event exists, ordering stays open.
- H-RetailValueParity: the joined nonzero words are stable and can be mapped
  to the port's corresponding zero source range.
- H-CaptureInvalid: any whole-RDRAM/source-span control or target phase is
  absent; the result is unevaluable and must not update truth.

Report controls, target-phase timing, source pointers, joined stored words,
writer PC, destination, producer/PC attribution, and ordering against the
first source-span DMA. Preserve the oracle log at an absolute path. If the
join or separate DMA event is unavailable, record that boundary as open.
