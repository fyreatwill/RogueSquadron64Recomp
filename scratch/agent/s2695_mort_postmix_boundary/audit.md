# s2695 M5 post-mix output-block handoff audit

Source snapshot: `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c` and `funcs_26.c`, plus the companion `main_overlay.txt` symbol map. Static only; no build or runtime probe was authorized.

## Handoff

`musyxSynthFrame` enters at `0x8009123C`. Its three mix sites are `0x800914C8`, `0x80091588`, and `0x8009163C`, each calling `musyxMixActiveVoices` (`0x80090E04`). At `musyxMixActiveVoices+0xFC` (`0x80090F00`), the active voice's render call receives `$a3` as the per-frame output address (`$t0 + voice_index * 0x88`); `musyxRenderVoiceSamples` writes through that address. The mix helper then only advances the voice cursor and clears the voice status byte before returning.

## Complete post-mix consumer table

| Location | Consumer / handoff | Reads or writes the output block? | Payload copy/transform and destination | Queue/service/order |
|---|---|---|---|---|
| `0x800916A8` | `flushStreamedVoiceBuffers` (`0x80097F54`) | No output-block argument; operates on global streamed-voice descriptors | Calls `copyFourHalfwordsWriteback` for descriptors in state 1. That helper copies four halfwords from descriptor `$a0` to `$a0 + 2*$a1`, then calls `osWritebackDCache`; no source is the synth `$a3` block and no AI destination is formed | Stream-buffer maintenance; no AI call or signal |
| `0x800916C8` | `osRecvMesg` | No | None; receives control state from the global message queue | Blocking message wait, followed by `yieldFromSpThread`; no payload publication |
| `0x800916D0` | `yieldFromSpThread` | No | None | Scheduler yield only |
| `0x80091684` | `LOOKUP_FUNC($v1)` | No statically resolvable target; `$v1` is loaded from the callback/state table | No caller-owned output pointer is passed; arguments are global stream/control values. Requires dynamic target/source audit, but this site is not a named output-block handoff | Indirect service callback; no visible ordering edge to `osAiSetNextBuffer` |
| `0x800917D0` | `serviceStreamedVoices` (`0x80097DA8`) | No output-block argument; scans streamed-voice state tables | Indirect callbacks receive stream descriptor/sample pointers and lengths; the body updates stream ownership/cursors and descriptor links, with no named copy to `0x801496B0` | Stream service maintenance; no AI call or signal |
| `0x80091854` | `osGetTime` | No | None | Timing only |
| `0x80091868` | `factor5QueueSignal` (`0x800920D0`) | No | Sends a zero message to the Factor 5 queue; no buffer pointer or payload | Synth-frame completion signal, after post-mix maintenance; not AI publication |

The `musyxSynthFrame` body has no direct `osAiSetNextBuffer` call, no direct read of the `$a3` output block after the three mixer calls, and no named call that receives that block as an argument after return. The only concrete copy in the post-mix chain is the four-halfword descriptor-local copy in `copyFourHalfwordsWriteback`; its source and destination are both derived from streamed-voice descriptor pointers, not the rendered output block.

## Result

The table selects `H-consumer-only` for the named post-mix consumers and retains `H-unresolved-address` for the complete MORT-to-PCM publication edge. The unresolved indirect callback at `0x80091684` is a bounded follow-up source-read target, not evidence of publication. No runtime watch, writeback, remap, gate bypass, or mitigation is authorized.
