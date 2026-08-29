# Session 3161 — `musyxTriggerVoiceAttack` voice-index audit

## Discriminator

Outcomes: `H-M3-Proven` if every reachable caller proves the mixer index;
`H-M3-Unclassified` if any reachable caller lacks that proof; or
`H-M3-Dead` if all apparent sites are unreachable/lowering artifacts.

## Complete site table

| Guest PC | Caller | Index source and proof | Callee access | Independent evidence |
|---|---|---|---|---|
| `0x8008CE7C` | `tickAllAudioChannels` (`0x8008C9AC`) | `$s6` starts at 0, increments at `0x8008D724`, and loops while `$s6 < MEM_BU[0x80141AD0]` (`0x8008D728`). Companion metadata identifies the channel array as 0x20 entries, so this edge is `0..31`. | Base `MEM_W[0x801496F8]`, index times `0x88`. | `main_overlay.txt:311` identifies the mixer base/stride; `:445` identifies the 0x20-entry channel array and loop. |
| `0x80098194` | `startStreamedSampleVoice` (`0x80097FE8`) | `$s0` is replaced by `stopVoiceByKey`'s return at `0x8009805C`; only `$s0 == -1` is rejected at `0x80098064`. The shown `allocateSynthVoice` producer flow has no dominating `<64` proof. | Same base and `idx * 0x88` computation. | `main_overlay.txt:311` confirms the mixer stride; `:2244-2245` identifies `allocateSynthVoice`/`stopVoiceByKey`, without a 64-slot return contract. |

`musyxTriggerVoiceAttack` (`0x8009231C`) masks the argument to 16 bits,
computes `idx * 0x88`, and accesses one record at `+0x28`, `+0x5C`, `+0x60`,
`+0x64`, `+0x68`, `+0x6C`, and `+0x58` (guest PCs `0x80092340` and
`0x80092348..0x80092364`). The existing base-pointer guard is unrelated to
the index bound and was not changed.

## Result

The complete reachable class selects `H-M3-Unclassified`: the tick edge is
range-proven, while the streamed edge has an unresolved producer contract.
`H-M3-Proven` and `H-M3-Dead` are ruled out at static scope. This is two-source
static evidence (generated control flow plus companion symbol metadata), not
a retail-invalid-value claim. No guard, generated source, audio behavior,
build, or run changed.
