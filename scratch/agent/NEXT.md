# NEXT work unit — qualify the retail source writer after zero-fill

HYPOTHESIS-ID: m5-image-task-retail-source-writer

This is the next experiment after maintenance. Do not change runtime behavior
or add a port instrument. Run one retail oracle table with these controls and
watches:

    env tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom ./rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 3:start,7:start,11:start,15:a,30:start,45:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 --watch-pc 0x800078EC,0x800078E0,0x800C825C --pc-phase-log-width 0x006AB400:512 --vi-trace --detail-watch 1 --hit-cap 1 > /tmp/rs64_next_oracle.log 2>&1

Competing hypotheses and the discriminating measurement:

- H-RetailWriterSame: the source-span writer matches the known zero-fill
  family and precedes the first source DMA; this selects upstream input
  construction.
- H-RetailWriterOther: a different retail PC writes the source span; this
  selects that producer boundary.
- H-RetailOrdering: writer identity/value matches, but the write follows the
  first source DMA; this selects ordering.
- H-CaptureInvalid: any whole-RDRAM/source-span control or target phase is
  absent; the result is unevaluable and must not update truth.

The table must report writer PC, destination range, value, and ordering in the
`0x006AB400:512` bucket against the first source-span DMA. Preserve the oracle
log at an absolute path. If this run is not performed, do not claim a result.
