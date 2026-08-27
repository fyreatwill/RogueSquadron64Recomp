# Session 2742 M5 CPU-side publication audit

## Scope and discriminator

This is a static audit of the named post-mix path from the renderer's voice
object output to the AI worker/source span. It uses the generated snapshot and
the companion symbol/source census; it does not add runtime instrumentation,
writeback, remapping, or mitigation.

The discriminator is whether a complete source/destination/order edge can be
named, whether only a partial candidate exists, or whether no candidate exists
in the bounded named path.

## Source/destination table

| Site | Source read | Destination/write | Handoff/order | Result |
|---|---|---|---|---|
| `renderVoiceAudioBlock` `0x8009DB44` | `voice+0x140..0x15C` | same `voice+0x140..0x15C` at `0x8009DC38..0x8009DC54`; delay halfword at `voice+0x164` | five internal `audioMixStereoBlock8` dispatches and filter/compand calls; no outward pointer | renderer-local only |
| `audioMixStereoBlock8` `0x8009DC98` | voice sample fields at `+0x168`/`+0x178` | packed return registers consumed by enclosing renderer | indirect mix-function calls only | no memory publication |
| `musyxMixActiveVoices` `0x80090E04` / `musyxSynthFrame` `0x8009123C` | active voice state and caller-provided per-frame `$a3` output block | render kernel's caller-provided block and voice-local state | post-call work is cursor/status bookkeeping, then stream flush/service | output block has no named AI relation |
| `copyFourHalfwordsWriteback` `0x800925A8` | four halfwords at caller `$a0` | same descriptor at `$a0 + 2*$a1`, offsets `0,2,4,6` | `osWritebackDCache`; called by `flushStreamedVoiceBuffers` | descriptor-local streamed-voice copy, not renderer-to-AI |
| `flushStreamedVoiceBuffers` `0x80097F54` | per-slot fields `+0x2A28` and `+0x2A2C` | arguments to the descriptor-local copy above | loops slot metadata; no AI call | no publication edge |
| `serviceStreamedVoices` `0x80097DA8` | stream/slot cursors and state | slot/service state | no renderer output or AI source argument | no publication edge |
| `runAiAudioStreamPlaybackLoop` `0x8008ED70` | base allocated at `0x801496B0`, aliases `+0x300*n` | no payload writer; whole `0x3000` span is cleared, then aliases passed to AI | `osRecvMesg` controls rotation; `osAiSetNextBuffer(..., 0x300)` submits current alias | AI source is clear-only on named generated surface |
| `osAiSetNextBuffer_recomp` / `queue_audio_buffer` | exact caller RDRAM pointer and byte count | exact `TO_PTR` span passed to callback/SDL | no host copy, gate, or remap | host preserves pointer |
| `submitDmaRequestBatch` / `sendServiceMessage` / `piDmaWorker` | request descriptor fields | PI ring `0x801112B0`; `osPiStartDma` receives device/DRAM/size fields | completion marks descriptor and signals return queue | generic DMA service; no synth/AI source relation |
| `musyxSynthFrame` indirect callback at `0x80091684` | callback slot `0x801499DC` initialized to `submitDmaRequestBatch` | PI descriptor ring only | service wakeup | callback is unrelated to publication |

## Findings

The complete named table contains no source pointer from `voice+0x140`, the
per-frame synth output block, or the streamed-voice output into
`0x801496B0`/its aliases, and no copy or queue message supplies that relation.
The AI worker's only visible writes to its source span are allocation aliases
and the full clear before submission. The companion census adds no alternate
implementation: its 12 matches are symbol comments/definitions, with no
source-level publication body.

This selects `H-publish-edge-absent` for the bounded named path. It rules out
`H-publish-edge-found` and `H-publish-edge-partial` for the audited sites, but
does not prove that an opaque indirect/data-driven producer is absent from the
whole program. The next discriminator must name such a remaining boundary
before any runtime watch is added.

Evidence files: `s2742_mort_publication_census.txt`,
`s2742_mort_companion_census.txt`, and `s2742_mort_publication_context.txt`.
