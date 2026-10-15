# M5 s4934 retail writer attribution

The bounded retail oracle capture tested whether the zero task-entry rows from
s4933 were caused by watching the wrong execution boundary.

Command:

```text
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 240 --vi-poll --vi-trace --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,56:start,66:start,76:start,86:start,96:start,106:start,116:start,126:start,136:start,146:start,156:start,166:start --watch-write 0x0:0x800000 --pc-phase-log-width 0x6AB400:512 --watch-pc 0x80091784 --pc-task-dump 0x80033FCC --pc-task-type 2
```

Controls passed: the whole-RDRAM watch reached its 10,000-hit cap; VI polling
recorded 14,386 frames over about 239.8 emulated seconds; the run exited
normally with 22,076 total watch hits. The writer execution watch recorded
12,076 hits, all with `prev_pc=0x80091780`.

Writer hits grouped by live 512-wide VI origin were:

| origin | writer hits |
|---|---:|
| `0x006AB400` | 618 |
| `0x00690400` | 2,151 |
| `0x00620400` | 2,135 |

The mission buckets included repeated rows with `a1=0x142, a2=2` (1,970 at
`0x00690400`, 1,945 at `0x00620400`). The old `0x80033FCC` task-entry watch
still produced zero rows, so the result selects **H-writer-attribution** over
H-retail-absent: retail reaches a mission-side writer boundary that the old
task-entry watch does not observe. It does not establish that this writer
publishes the OSTask itself; the writer's target/context still needs to be
identified.

No runtime mitigation, guard, skip, or behavior change is authorized. The
capture is independent retail evidence and remains single-source for the
writer-to-OSTask relationship.
