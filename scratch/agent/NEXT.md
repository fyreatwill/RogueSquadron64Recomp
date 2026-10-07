# Next work unit: M5 exact descriptor-selector store census

HYPOTHESIS-ID: m5-descriptor-selector-writer

The broad retail selector-range census is complete but did not arm the exact
candidate store PCs. The next bounded unit must close that attribution gap.

Competing hypotheses:

- Hwriter-live: one of the known `s1+0x22` store PCs fires in a target phase
  and its scalar value explains the selector transition.
- Hselector-absent: the qualified retail route reaches the descriptor call but
  never writes the dynamic field in title or hangar.
- Hcoverage: the whole-RDRAM control or one target VI phase is absent, so a
  selector-field null is not interpretable.

Discriminating measurement: run the retail oracle once with the whole-RDRAM
positive control, title/hangar phase gates, the corrected physical watch
`0x171E22:0x172D00`, and `--store-field-dump 1:` for
`0x800909B4,0x800909FC,0x80090AAC,0x80090BA4,0x80090F3C,0x80090F8C,0x80092170`.
A phase-qualified exact row with its scalar value selects Hwriter-live;
qualified zero rows across both buckets select Hselector-absent; missing
control/phase selects Hcoverage.

Ground truth has been checked in `tools/oracle/README.md`: the watch addresses
are physical, whole-RDRAM must fire, and phase buckets must use VI origin plus
width. No port instrumentation or behavior change is authorized by this unit.

Command:

`env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --watch-write 0x0:0x800000 --watch-write 0x171E22:0x172D00 --watch-pc 0x80090A3C,0x80090DE8,0x80090768 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --pc-field-dump 0x80090A3C,0x80090DE8 --store-field-dump 1:0x800909B4,0x800909FC,0x80090AAC,0x80090BA4,0x80090F3C,0x80090F8C,0x80092170 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --pc-hist-watch 1 --post-value-watch 1 --hit-cap 10000 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150`
