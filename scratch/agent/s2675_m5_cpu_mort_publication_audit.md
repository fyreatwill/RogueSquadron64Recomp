# s2675 M5 CPU-side MORT publication audit

## Discriminator

The batched retail oracle watch covered the whole-RDRAM positive control and
the three named MORT/voice boundaries. A complete result required a watched
callsite to be joined to a legitimate destination, nonzero payload, port PCM
consumer, and target-phase ordering.

## Capture

Command:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 55 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start --watch-write 0x0:0x800000 --watch-pc 0x8009C540,0x8009C88C,0x8009D740 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --hit-cap 12000

The whole-RDRAM control fired 10,000 writes. The run reached 3,240 VI
callbacks (~54 emulated seconds), including the driven 512/hangar origin.

| retail boundary | oracle executions | predecessor | target evidence | publication edge |
|---|---:|---|---|---|
| `0x8009C540` | 0 | n/a | none | absent |
| `0x8009C88C` | 0 | n/a | none | absent |
| `0x8009D740` | 1,984 | `0x8009D73C` for all hits | rows at `0x006AB400` | no destination/payload join |

`0x8009D740` carries changing register arguments and is therefore a live
voice-related execution boundary, but the watch supplies no memory-write
attribution. The run retained no legitimate source/destination, payload
polarity, or ordering relation to the port PCM rows. This is not evidence
that the function is dead, and it does not authorize output writeback or a
remap.

## Verdict

`H-MORT-unmapped` at the measured boundary. `H-MORT-edge` is not established;
`H-image-edge` is also not established by this CPU-only watch. The positive
control makes the three narrow results interpretable, but a follow-up must
watch a destination proven by source inspection rather than reuse the broad
ring/task spans.

Raw capture: `s2675_m5_cpu_mort_oracle.log`.
