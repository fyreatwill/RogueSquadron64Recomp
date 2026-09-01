# NEXT work unit — earlier producer discriminator

HYPOTHESIS-ID: m5-image-task-retail-source-writer

Session 3582 qualified the target-phase writer and immediate producer context,
but did not expose a separate DMA event identifier or the earlier producer.
Do not change runtime behavior or add a port instrument. Run one retail oracle
capture with the same positive controls, adding only a bounded phase-gated
field table for likely source-buffer construction sites identified from the
existing `0x800052C4` rows. The result must either identify a stable earlier
guest PC and source buffer, or leave that boundary explicitly open.

Exact command baseline:

    env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB/projects/unix/libmupen64plus.dylib --rom ./rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 3:start,7:start,11:start,15:a,30:start,45:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 --watch-pc 0x800078EC,0x800078E0,0x800C825C,0x800052C4,0x8002BEEC --pc-phase-log-width 0x006AB400:512 --pc-field-dump 0x800078EC,0x800078E0,0x800052C4,0x8002BEEC --pc-hist-watch 1 --pc-hist-phase 0x006AB400:512 --post-value-watch 1 --post-value-pc 0x800078EC --post-value-pc-detail --vi-trace --detail-watch 1 --hit-cap 1 > /tmp/rs64_next_oracle.log 2>&1

Competing hypotheses and the discriminating measurement:

- H-RetailProducer: the phase-gated table identifies a stable earlier guest-PC
  producer and its source buffer.
- H-RetailValueParity: the earlier producer's source words map to the target
  range and explain the retail nonzero values versus the port zeros.
- H-RetailDmaOrder: a separately identified DMA event establishes ordering;
  if no event exists, ordering stays open.
- H-CaptureInvalid: any whole-RDRAM/source-span control or target phase is
  absent; the result is unevaluable and must not update truth.

Use the prior command in the session-3582 evidence note as the baseline, with
one capture and all arms/fields enabled. Report controls, target-phase timing,
source pointers, joined stored words, writer PC, destination, producer/PC
attribution, and ordering against the first source-span DMA. Preserve the
oracle log at an absolute path. If the earlier producer or separate DMA event
is unavailable, record that boundary as open.
