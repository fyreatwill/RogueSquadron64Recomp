# Session 2678 — MORT downstream consumer oracle

## Source-derived table

| edge | address / value | evidence |
|---|---|---|
| filter caller | `0x8009C540`, `0x8009C88C`, `0x8009D740` → `0x8009D7D0` | generated source and companion symbols |
| delay publication | `applyVoiceDelayFilter` `0x8009D8E4`: `$a0+0x166` | persistent object `$a0=0x80153420`, physical `0x153586` |
| next named consumer | `renderVoiceAudioBlock` `0x8009DB44` | caller `0x8009C4C0`, same `$a0=0x80153420`; sample block `$a0+0x140` |
| later mix input | `$a2` to render | phase rows included `0x801B2C60..0x801B4CE0`; not treated as one fixed destination |

## Retail capture

Command: `tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 45 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start --watch-write 0x0:0x800000 --watch-write 0x153580:0x153590 --watch-write 0x1B4A60:0x1B4B00 --hit-cap 1 --first-watch 1 --first-watch 2 --pc-hist-watch 1 --pc-hist-watch 2 --watch-pc 0x8009D7D0,0x8009D8C4,0x8009DB44 --pc-phase-log-width 0x006AB400:512 --pc-phase-log-width 0x006AB800:512 --vi-trace`.

Results: oracle rc 0, 2,645 VI, whole-RDRAM control 17,295 writes, delay
range 1,406 writes, sample range 5,889 writes. The phase-gated execution
counts were 792 at `0x8009D7D0`, 792 at `0x8009D8C4`, and 198 at
`0x8009DB44`; both `0x006AB400` and `0x006AB800` were observed. The delay
range writer histogram attributed 792 stores to `0x8009D8E4`; other writers
were `0x8002A0B8..C4` (4 each), `0x8009BE88` (4), `0x8009C330/368/390/3D0`
(99 each), and `0x8009DC58` (198). The sample-range histogram included
`0x8009DB2C` (560) plus retail stream/copy writers.

## Interpretation

This independently establishes a legitimate CPU-side MORT edge:
`applyVoiceDelayFilter` writes a persistent voice object and the downstream
named renderer consumes that same object in the target phase. It does not
establish the renderer's later PCM/AI publication, so `H-MORT-edge` is only
partially resolved and no audio behavior change or writeback is authorized.
