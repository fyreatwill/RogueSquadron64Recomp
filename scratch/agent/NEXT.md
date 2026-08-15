# NEXT work unit (s1177)

HYPOTHESIS-ID: musyx-sample-writer-retail-execution

Run one retail-oracle capture to test whether the statically identified
`musyxInitVoiceFromSample` sample/stream stores execute on the driven path.
Do not infer a voice-array range from `0x001496F8`, and do not add a
destination watch until this execution test is positive.

Competing hypotheses and discriminator:

- H1: the retail driven path executes one or more of the four real
  sample/stream stores at `0x800921E8`, `0x80092220`, `0x80092228`, or
  `0x80092230`.
- H2: the retail path remains in the bookkeeping/audio-global path and none
  of those writer PCs executes.
- H3: a writer PC executes, but the descriptor/destination evidence is not
  coherent enough to authorize a destination-range watch.

The discriminating measurement is the same-run `--watch-pc` result for all
four writer PCs, paired with separate whole-RDRAM read and write positive
controls. H1 is selected by at least one writer-PC hit with valid descriptor
context; H2 by zero writer-PC hits while both controls pass; H3 by a writer
hit without coherent descriptor/destination attribution. A zero watch result
is invalid if either whole-RDRAM control does not fire.

Exact commands from the repository root (use the local oracle paths if the
standard paths differ):

    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --secs 180 --vi-trace \
      --watch-write 0x0:0x800000 --watch-read 0x0:0x800000 \
      --watch-pc 0x800921E8,0x80092220,0x80092228,0x80092230 \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
      > scratch/agent/oracle_musyx_writer_s1177.log 2>&1

Inspect only bounded summaries, for example:

    grep -c '^\[hit\]' scratch/agent/oracle_musyx_writer_s1177.log
    grep -n '800921E8\|80092220\|80092228\|80092230\|whole-RDRAM\|oracle' scratch/agent/oracle_musyx_writer_s1177.log | tail -80

If H1 is selected, the next unit must batch a physical destination watch with
the same whole-RDRAM controls; do not guess the voice range from the failed
`0x001496F8` calibration.
