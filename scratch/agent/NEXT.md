# NEXT work unit — qualify the retail source writer after zero-fill

HYPOTHESIS-ID: m5-image-task-retail-source-writer

Session 3577 closed the remaining predecessor-input question: retail
`0x800C825C` calls `0x800078E0` with `a2=0x80`, not the port's
`0x801797B0/0/0x298` tuple. The next boundary is the writer that publishes
the retail source span `0x1797B0..0x179930` and its ordering relative to the
zero-fill/first source DMA.

Competing hypotheses and discriminator:

- H-RetailWriterSame: the retail source-span writes come from the same
  `0x800078EC` zero-fill family and occur before the first source DMA, so the
  remaining difference is upstream input construction.
- H-RetailWriterOther: a different retail PC writes the source span, selecting
  that writer as the next producer boundary.
- H-RetailOrdering: the writer PC and values match, but the writer occurs
  after the first source DMA, selecting ordering as the defect.

The single retail table must retain whole-RDRAM and source-span controls,
watch `0x800078EC`, `0x800078E0`, and `0x800C825C`, and log all source-span
writes with `--detail-watch 1` in the target bucket
`--pc-phase-log-width 0x006AB400:512`. Match writer PC, destination range,
and timestamp/order against the first source-span DMA. Same writer and
pre-DMA order selects H-RetailWriterSame; a different writer selects
H-RetailWriterOther; same writer with post-DMA ordering selects
H-RetailOrdering. Missing any positive control or target phase is unevaluable.

Run from the repo root and capture to an absolute path:

    env tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom ./rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 3:start,7:start,11:start,15:a,30:start,45:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 --watch-pc 0x800078EC,0x800078E0,0x800C825C --pc-phase-log-width 0x006AB400:512 --vi-trace --detail-watch 1 --hit-cap 1 > /tmp/rs64_next_oracle.log 2>&1

Do not change runtime behavior or add a port instrument for this unit.
