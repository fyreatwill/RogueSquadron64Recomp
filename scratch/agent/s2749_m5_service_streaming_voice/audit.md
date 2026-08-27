# Session 2749 — `serviceStreamingVoice` static audit

Sources: `../N64Recomp/RecompiledFuncs/funcs_27.c:369-977`,
`funcs_26.c:12861-13055`, and the generated declarations/overlay table.

## Call graph and data flow

| Edge | Evidence | Classification |
|---|---|---|
| `serviceVoicePoolFrame` -> `serviceStreamingVoice` | `funcs_26.c:13030`, guest call `0x8009B644`, `a0 = 0x80153420 + slot_index * 0x1228` | Only named direct caller found repository-wide |
| service -> `osRecvMesg` | `0x8009BF40`, queue `voice + 0x11AC`, nonblocking receive | Input/event gate; no payload copy |
| service -> `decodeAndFillVoiceBlock` | `0x8009C0E4`, output base `voice + 0x198` plus ring offset; source/context uses `voice + 0x194` | Legitimate ring payload transform/write; no AI destination |
| service -> `bzero` | `0x8009C1B4`, `voice + 0x198` plus block offset, length `0x140` | Ring-block clear; no publication |
| service -> `(*voice->0x194)` | `0x8009C040`, indirect `jalr`, arguments derived from `+0x194`, `+0x11D0`, `+0x1A0`, `+0x11AC` | Named data-driven callback; target/side effects unresolved |

The function updates only descriptor-local cursor/timing/state fields:
`+0x11A0`, `+0x11A2`, `+0x11A4`, `+0x11C8`, `+0x11CC`, `+0x11D0`,
`+0x11DC`, `+0x11DD`, and `+0x11DE`. It advances/wraps the stream cursor,
decodes available blocks, clears old ring blocks, and changes state bytes.

`initMusyXVoiceSlot` stores caller-provided values into `+0x194` and
`+0x198`; `serviceVoicePoolFrame` supplies the per-slot descriptor. Thus
`+0x198` is a legitimate voice-ring/base field, while `+0x194` is the
caller-supplied indirect callback field. No direct AI, PI, or publication
call occurs in the service body.

## Discriminator result

The complete immediate surface selects **H-streaming-opaque-edge**. The
service has a legitimate ring-buffer payload write through
`decodeAndFillVoiceBlock`, but no direct copy or transform into an AI
destination and no publication ordering edge. The callback loaded from
`voice + 0x194` is the only unresolved edge and is the next target. This is
a static result; no runtime conclusion or mitigation is authorized.

`consumeVoiceSamples`, `advanceVoiceStateToPlaying`, and `stopVoice` only
update state/counters and do not consume the `+0x198` payload. Queue,
AI-worker, PI, mixer, renderer, and host-AI surfaces were not re-audited.
