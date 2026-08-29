# Session 3211 — M3 voice-slot producer idiom audit

## Scope and discriminator

Audited the complete generated-source call/access set for
`musyxInitVoiceFromSample` (`0x80092128`), its voice-slot `+0x34` write, the
shared voice-array base, and adjacent index consumers. No build, run, oracle
watch, generated-source edit, guard, or audio behavior change was made.

The discriminator was one whole-class static census: every direct caller,
indexed record construction, base/count writer, and `+0x67` field store,
cross-checked against companion symbol metadata.

## Complete table

| Guest edge/site | Producer or access | Bound/provenance | Result |
|---|---|---|---|
| `0x8008A564` in `soundMacroOpPlaySampleKeymap` (`0x8008A38C`) | Loads `$a0 = record+0x67`, calls init | No dominating `<64` check; no connected live writer for this field found | reachable, unclassified |
| `0x800980EC` in `startStreamedSampleVoice` (`0x80097FE8`) | `$s0 = stopVoiceByKey(...)`; rejects only `-1`, then passes `$s0` | `stopVoiceByKey` delegates to `allocateSynthVoice`; exact `<64` consumer bound is not proven | reachable, unclassified |
| `0x80092138`–`0x80092150` | First record: `0x801496F8 + ((a0 & 0xffff) * 0x88)` | Entry guard proves only KSEG0/RDRAM base, not index range | incomplete proof |
| `0x8009219C`–`0x800921E8` | Independent second record; final `sw` writes `record+0x34` | Same unchecked index/base | incomplete proof |
| `0x8008F0CC`, `0x8008F0E4`, `0x8008F0EC` | `allocateSongChannelArray` stores count and malloc result/base | Legitimate allocator/base writer; no complete index contract for both callers | incomplete index proof |
| `+0x67` stores in generated funcs 21–26 | Whole-class literal search | No live MusyX voice-record writer recovered | writer unresolved |

## Independent cross-check

Companion `main_overlay.txt` independently corroborates the function addresses,
base `0x801496F8`, stride `0x88`, and caller roles. It does not supply the
missing field-writer or range proof.

## Result

`H-BadProducer` is not selected: no concrete invalid value was observed and no
writer was identified. `H-UnreachableGuard` is rejected because both direct
call edges are present. `H-LegitimateWriter` cannot be selected because the
sound-macro `+0x67` producer is unresolved and the streamed edge lacks a
complete `<64` proof.

Selected classification: **H-Unclassified**. This is static contract evidence,
not proof of a retail-invalid value. No mitigation is authorized.

ORIGIN: generated call/access census plus independent companion symbol
metadata; unresolved writer evidence is not a mitigation target.
