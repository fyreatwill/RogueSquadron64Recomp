# Session 3157 — `musyxInitVoiceFromSample` voice-index audit

## Competing hypotheses

- `H-M3-Proven`: every reachable caller and indexed access proves a valid
  voice index and voice-array base.
- `H-M3-Unclassified`: a reachable caller or indexed access lacks a complete
  base/index/count proof.
- `H-M3-LoweringOnly`: apparent multiplicity is only duplicate delay-slot or
  shared-tail lowering.
- `H-M3-Dead`: no candidate caller/site is reachable from generated dispatch.

The discriminator is a complete caller/access/producer table, not a runtime
counter. A reachable row without a complete range proof selects
`H-M3-Unclassified`; all rows proven selects `H-M3-Proven`.

## Static inventory

| guest edge | generated site | index source | base/range result |
|---|---|---|---|
| `soundMacroOpPlaySampleKeymap` → `musyxInitVoiceFromSample` | `funcs_22.c:0x8008A38C` → `funcs_23.c:0x8008C454` → `funcs_24.c:0x80092128` | caller passes its incoming `$a0` unchanged as voice index; callee masks to 16 bits | no caller-local bound to `<64`; reachable via `tickAudioChannel` at `0x8008C454` |
| `startStreamedSampleVoice` → `musyxInitVoiceFromSample` | `funcs_26.c:0x800980EC` → `funcs_24.c:0x80092128` | `stopVoiceByKey` result in `$s0`, rejects only `-1`, then passes `$s0` | `stopVoiceByKey`/`allocateSynthVoice` has a nominal allocated-index contract, but the available source does not establish the voice-array's exact `<64` bound or complete lifecycle edge |
| callee first indexed record | `0x80092138`–`0x80092150` | `a3 = a0`; `a0 &= 0xffff`; `idx = a0*0x88` | base is global `0x801496F8`; existing entry guard proves only KSEG0/RDRAM base, not index range |
| callee second indexed record | `0x8009219C`–`0x800921E8` | same `a3`-derived `idx` | same `0x801496F8 + idx*0x88`; no second index check; companion describes a 64-slot pool |

The body has no duplicate-only access: the first record is formed before the
initialization stores, and the second record is independently recomputed after
the conditional ADSR-field block. The two direct callers are distinct
reachable edges; the `soundMacroOpPlaySampleKeymap` call itself has one
generated caller at `0x8008C454`.

The companion symbol file independently names `musyxInitVoiceFromSample` at
`0x80092128`, describes the base as `0x801496F8` with `0x88` stride, and names
the caller roles. Generated control flow independently supplies the two call
edges and the arithmetic above.

## Result

`H-M3-Unclassified` selected. The sound-macro caller supplies an incoming
voice index with no local `<64` proof, and the streamed caller's allocator
contract is not enough in the available source to prove the exact callee
array bound/lifecycle. This is static evidence only. No guard, audio change,
or runtime behavior change is authorized.

ORIGIN: generated control-flow/access inventory plus independent companion
symbol metadata; no guest value sample or retail attribution was available,
and no mitigation was added.
