# NEXT work unit — direct retail mode-writer callsites

HYPOTHESIS-ID: m5-retail-mode-writer-boundary

## Single work unit

Run one independent retail-oracle capture watching the three known
`osViSetMode` callsite PCs directly. Retain the whole-RDRAM positive control,
validated Start schedule, VI trace, and title/hangar phase coverage. Do not
modify the port.

## Competing hypotheses

- H-ApplyPending: `0x8001B8DC` executes at the 640→1024 transition.
- H-OtherKnown: `0x8001BB54` or `0x8001B720` executes at that transition.
- H-Unenumerated: target phase is live but none of the three callsites fires
  at the transition.
- H-Unevaluable: the positive control or target phase is absent.

## Discriminating measurement

The same run must show 10,000 whole-RDRAM control callbacks, the title
`1024 @ 0x00790400` phase, and direct execution rows for the callsite PCs.
The callsite hit nearest the 640→1024 VI transition selects its hypothesis;
no hit with both controls live selects H-Unenumerated. Missing controls select
H-Unevaluable.

## Exact command

`env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 45 --watch-write 0x0:0x800000 --watch-pc 0x8001B8DC,0x8001BB54,0x8001B720 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --hit-cap 12000 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start --hold-ms 150 > scratch/agent/s3107_m5_retail_mode_callsites/oracle.log 2>&1`

Save the bounded result and classification in
`scratch/agent/s3107_m5_retail_mode_callsites/AUDIT.md`.
