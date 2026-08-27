# s2700 M5 queue-publication boundary audit

## Scope

The audited object is the Factor 5 queue at `0x80149990`, formed by
`0x80150000 - 0x6670`. The companion symbol file identifies it as the
recursive Factor 5 mutex queue. The queue storage is initialized at
`0x801499A8` (`0x80150000 - 0x6658`) with one entry.

## Complete queue table

| Site | Queue operation | Message argument | Payload behavior | Immediate role |
|---|---|---|---|---|
| `initFactor5Mutex` `0x80091FC4` | `osCreateMesgQueue` | queue `0x80149990`, buffer `0x801499A8`, count `1` | creates one-slot queue | mutex initialization |
| `initFactor5Mutex` `0x80091FF4` | `osSendMesg(NOBLOCK)` | `msg=0`, flag `0` | posts the initial zero token | mutex initialization |
| `factor5MutexAcquire` `0x80092010` | `osRecvMesg(BLOCK)` | `msg=0`, flag `1` | token is discarded; no message word is read | recursive mutex acquire |
| `factor5MutexRelease` `0x8009205C` | `osSendMesg(NOBLOCK)` when recursion reaches zero | `msg=0`, flag `0` | posts a zero token; no data payload | recursive mutex release |
| `factor5QueueBlock` `0x800920A4` | `osRecvMesg(BLOCK)` | `msg=0`, flag `1` | token is discarded; no message word is read | synth-frame serialization |
| `factor5QueueSignal` `0x800920D0` | `osSendMesg(NOBLOCK)` | `msg=0`, flag `0` | posts a zero token; no data payload | synth-frame serialization |

The acquire/release wrappers are called broadly by the audio and streaming
helpers, but every call reaches the same queue only through these fixed
wrappers. The only direct `factor5QueueBlock` caller is `musyxSynthFrame`
(`0x8009123C`), which calls it before timestamp work. The only direct
`factor5QueueSignal` caller is the same synth-frame function at `0x80091868`,
after scalar timing stores at `0x800A176C..1774` and mutex state; no audio
buffer pointer is placed in the queue call arguments.

## Downstream join check

No queue site reads or writes rendered samples, voice `+0x140` words, the
candidate AI allocation at `0x801496B0`, any other named PCM span, or an
`osAiSetNextBuffer` argument. The AI worker at `0x8008ED70` submits its own
`0x300` buffers and receives a separate queue at `0x80149670` in the worker's
state; there is no call-chain join from this mutex queue to that worker in
the audited generated source.

## Result

`H-queue-services` is selected for this boundary: the queue is an exclusive
access/token service, not a rendered-PCM publication channel. This is static
source evidence. It does not identify the missing producer for the AI source,
so no runtime watch, writeback, remap, or mitigation is authorized.
