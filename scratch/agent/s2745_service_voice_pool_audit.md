# s2745 `serviceVoicePoolFrame` static audit

Scope: generated `serviceVoicePoolFrame` at guest PC `0x8009B5A8`
(`../N64Recomp/RecompiledFuncs/funcs_26.c`, current generated snapshot), its
callback-dispatch entry, and the named routines it calls. This is static
evidence only; no runtime watch, writeback, remap, or mitigation is justified.

## Entry and caller edge

| Edge | Evidence | Contract classification |
|---|---|---|
| callback caller | `spTaskSchedulerThread`/VI callback loop at `0x80019B68..0x80019B84` loads up to four function pointers and calls each through `jalr $v0` at `0x80019B74`; current generated source has no direct `jal 0x8009B5A8` call | Indirect callback caller is established; which callback-table slot contains `0x8009B5A8` is runtime/data-driven and not statically fixed here |
| entry gate | Reads `0x800A5121`; zero returns after frame bookkeeping, nonzero receives token from queue `0x80154650` | Worker/service gate, not PCM production |
| frame ownership | Receives one queue token at entry, processes four records, sends a zero token to the same queue at exit | Synchronization/periodic service ownership; message carries no audio payload |

## Per-record source/destination/order table

The loop advances by `0x1228` bytes and services four records rooted at
`0x80153420 + i*0x1228`. The `status` byte is at `+0x4620`; the nearby
stream-control fields are `+0x11DD`, `+0x1208`, `+0x120C`, and `+0x1218`.

| Path | Reads | Writes | Named calls/order | Relation to MORT/PCM/AI |
|---|---|---|---|---|
| every active record | status `slot+0x4620`; stream state `slot+0x11DD`; timing/control fields `slot+0x1208`, `+0x1228`, `+0x1230`, `+0x1234`, `+0x1239` | none before service call | `serviceStreamingVoice(slot)`; rereads status | Services slot state and timing. No read of `slot+0x140` mixed words, synth output block, `0x801496B0:0x8014C6B0` AI span, or named AI call |
| status 1/2 transition | `slot+0x1208` sample/control value, `slot+0x45C0` table halfword, constant scale | clears `slot+0x463C`; sets status `slot+0x4620=2`; stores computed float at `slot+0x4640` | `advanceVoiceStateToPlaying(slot)`; then `startStreamedSampleVoice` with slot metadata and stack arguments | Candidate streamed-voice startup only. The calculation is a timing/rate value, not PCM publication; no destination buffer is supplied from synth/MORT output |
| failed streamed start | return from `startStreamedSampleVoice` | stores return at `slot+0x120C`; calls `stopVoice(slot)`; clears status `slot+0x4620=0` | `startStreamedSampleVoice` → conditional `stopVoice` | Slot failure/reaping path; no audio-buffer copy or AI ordering |
| status 3 cleanup | stream/reap byte `slot+0x1218`; handle/pointer `slot+0x120C` | if terminal condition, clears status `slot+0x4620=0`; otherwise calls stop and writes `slot+0x120C=-1`, decrements `slot+0x1218` | `stopStreamedVoice(slot+0x120C)` precedes handle invalidation; then cursor/state decrement | Stream-resource reaping only. The handle is not PCM data and no MORT or AI span is named |
| frame completion | prior `osGetTime` result and saved timestamp `0x8015466C` | `0x8015466C`, `0x80154680`, `0x80154678` | `osGetTime` → `osSendMesg(queue=0x80154650,msg=0)` | Timing/publication of service completion token only; zero message has no audio payload |

## Immediate named consumers and writers

- `advanceVoiceStateToPlaying` only changes the voice status byte when its
  input state permits it; it does not copy samples or publish PCM.
- `startStreamedSampleVoice` is the only startup consumer in this routine's
  normal transition. Its arguments are slot metadata, timing/control bytes,
  and a stack-held timestamp/value. The service routine does not pass the
  renderer's `voice+0x140`, the synth per-frame output block, or the AI
  allocation.
- `stopVoice` returns the constant stop state; it is not an audio-buffer
  writer. `stopStreamedVoice` consumes a stream handle/pointer and is a
  resource teardown edge.
- The callback dispatcher is the immediate caller visible in generated
  source. Its callback table is data-driven; no named caller passes a PCM
  destination or consumes a return value from this service.
- A repository-wide generated-source search found no direct call to
  `serviceVoicePoolFrame` and no reference from this routine to
  `renderVoiceAudioBlock`, `musyxRenderVoiceSamples`, `audioMixStereoBlock8`,
  `osAiSetNextBuffer`, `0x801496B0`, or the MORT CPU output fields.

## Selection

`H-service-edge-absent` is selected for the bounded surface. The routine owns
per-slot streaming state, startup/reaping, and a queue/timestamp service
cadence. It does not name a source, destination, payload transform, ownership
handoff, or ordering edge joining MORT/renderer output to the AI source span.
The callback-table slot and runtime reachability remain unevaluable by this
static audit, but that uncertainty does not turn the service's explicit
state/resource operations into a publication edge.

This is single-source generated evidence. Retail writer attribution and
payload legitimacy are still required before any behavior change; no status
force-clear, wait replacement, writeback, or remap follows from this audit.
