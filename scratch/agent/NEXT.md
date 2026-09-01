# NEXT work unit — source-buffer construction writer

HYPOTHESIS-ID: m5-image-task-retail-source-writer

Session 3583 repeated the full PC field table without exposing an earlier
constructor. The next single work unit is one retail-oracle capture watching
the qualified source buffer itself, not another field-table repeat.

Competing hypotheses and the discriminating measurement:

- H-RetailSourceWriter: a phase-gated write watch on physical
  `0x0065FA30..0x0065FA4C` identifies a stable guest writer PC that constructs
  the tuple later passed through `0x800052C4`.
- H-RetailCopyOrDma: the source-buffer watch is written by a stable DMA/copy
  PC distinct from the known `0x800078EC` target-span writer; that would move
  the producer boundary upstream.
- H-RetailNoStableSourceWriter: only changing or unrelated writers appear,
  so the earlier-constructor boundary is unavailable to this oracle and must
  remain open.
- H-CaptureInvalid: whole-RDRAM or source-span controls, or the target VI
  phase, fail; the result is unevaluable.

The discriminating measurement is the source-buffer writer-PC histogram in
the same run as the whole-RDRAM and target-span positive controls, phase-gated
to origin `0x006AB400` width 512. A stable non-`0x800078EC` writer selects
H-RetailSourceWriter or H-RetailCopyOrDma; no stable writer selects
H-RetailNoStableSourceWriter; missing controls selects H-CaptureInvalid.

Exact command, run from `build/`:

    env ../tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB/projects/unix/libmupen64plus.dylib --rom ./rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 3:start,7:start,11:start,15:a,30:start,45:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 --watch-write 0x65FA30:0x65FA4C --watch-pc 0x800078EC,0x800078E0,0x800C825C,0x800052C4 --pc-hist-watch 2 --pc-hist-phase 0x006AB400:512 --post-value-watch 2 --post-value-pc 0x800078EC --post-value-pc-detail --vi-trace --detail-watch 1 --hit-cap 1 > /tmp/rs64_source_buffer_writer.log 2>&1

Report the three control counts, target VI timing, source-buffer writer
histogram, source-buffer values, and whether the writer is distinct from
`0x800078EC`. Preserve `/tmp/rs64_source_buffer_writer.log`; if no stable
writer or DMA identifier is available, record that boundary as open.
