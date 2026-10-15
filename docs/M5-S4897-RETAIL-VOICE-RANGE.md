# s4897 — retail voice-render range boundary

The independent retail oracle ran the USA ROM for 180.2 seconds with the
Rice video plugin, the validated eleven-Start schedule, and the debugger
enabled. The command was:

```text
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/rogue_squadron.z64 --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib --rsp /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib --secs 180 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-pc-range 0x8008FFAC:0x80090640 --watch-pc 0x80090C80,0x800921E8,0x800903F0 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150
```

The positive control reached 24,235,022 whole-RDRAM writes. The run reached
title origin `0x00790400` at width 1024 and hangar origin `0x006AB400` at
width 512, with 10,777 VI frames total. The watched range produced
1,278,314 phase-gated title rows and 3,780,858 phase-gated hangar rows.

The two independent statically selected writer PCs were live: `0x80090C80`
produced 155 title and 96 hangar rows, and `0x800921E8` produced 155 title and
169 hangar rows. The exact prior consumer watch `0x800903F0` produced zero
rows in either phase. The full range and writer controls therefore qualify
the voice-render route while placing the unresolved boundary before the exact
consumer instruction. This selects H1, rejects H2 and H3, and does not
authorize a runtime mitigation.

Raw output: `scratch/agent/soak_results/s4897_external_retail_voice_range.log`.
