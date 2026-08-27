# Session 2750 M5 callback-edge audit

## Address correction

The proposed `+0x194` callback edge is an offset mix-up. In
`serviceStreamingVoice` (`0x8009BF14`), the indirect call at `0x8009C040`
loads the target from voice-slot `+0x190`, not `+0x194`:

| site | operation | meaning established from the call chain |
|---|---|---|
| `0x8009C020` | `lw a0, 0x194(s0)` | source/sample base, later advanced by the consumed offset |
| `0x8009C02C` | `lw v0, 0x190(s0)` | callback target for `jalr v0` |
| `0x8009C030..C044` | build `a0`, `a1`, `a2`, `a3` | source, destination, byte count, and completion queue |
| `0x8009C040` | `jalr v0` | invokes the slot callback |

Therefore `+0x194` is a payload/source field, not a callback field.

## Complete writer-to-target table for the corrected edge

| field | writer | value | evidence / consequence |
|---|---|---|---|
| slot `+0x190` | `initMusyXVoiceSlot` at `0x8009BEA0` | fourth stack argument | `allocAndConfigureNewVoice` places `0x8009BE08` in caller stack `+0x10`; after the callee frame adjustment this is callee `+0x38`, loaded as `s1`, then stored at slot `+0x190` |
| slot `+0x194` | `initMusyXVoiceSlot` at `0x8009BE8C` | second argument, sample pointer | `allocAndConfigureNewVoice` reads `speechSampleOffsets[voiceId]` at `0x8015467C`, masks the type byte, adds `speechFile` at `0x80154684`, and passes the resulting sample address as `a1`; init stores it at `+0x194` |
| slot `+0x198` | `initMusyXVoiceSlot` at `0x8009BE90` | third argument | stored as the companion slot pointer/size field; no callback target |
| slot `+0x19C` | `initMusyXVoiceSlot` at `0x8009BE94` | fourth register argument | stored as the completion-message destination used by the streaming callback |

The only slot-field writer found by enumerating generated non-stack stores for
these offsets is the initializer above. Other `0x194` matches are stack-frame
saves, an unrelated effect-object field at `0x800AAD7C`, a halfword field at
`0x800AE174`, or unrelated structures. The companion symbol file independently
identifies `speechSampleOffsets` and `speechFile` at the two source globals and
identifies `initMusyXVoiceSlot`'s four pointer arguments.

## Callback target and dataflow

The target is the named `dmaVoiceSampleAndSignal` at `0x8009BE08`, selected by
the fixed call-site setup in `allocAndConfigureNewVoice`; it is not a data-driven
callback table. Its body calls `synchronousDmaTransfer` (`0x80005200`) with the
service-built arguments and then calls `osSendMesg` on the saved `a3` queue.
It performs a legitimate sample DMA into the slot's destination ring and
signals completion. It contains no AI task submission, AI source publication,
PI-service call, or renderer-facing write.

The callback arguments at the service call are:

- `a0 = slot->sampleBase + slot->currentOffset` (`+0x194` plus `+0x11D0`)
- `a1 = slot + ((slot->currentOffset & 0xFF8) + 0x1A0)`
- `a2 = selected transfer length` (up to `0x400`, or the remaining ring span)
- `a3 = slot->completion destination` (`+0x19C`)

The callback thus explains the ring-fill edge, but not the missing AI
publication edge. No callback-specific runtime watch is justified by this
audit.

## Discriminator result

`H-callback-publishes` is refuted for this edge: the callback's legitimate
write is sample DMA into the voice ring, with queue signaling afterward, and
there is no AI-visible destination or ordering edge. `H-callback-services` is
selected for the corrected `+0x190` callback edge. The original `+0x194`
callback hypothesis was unevaluable as phrased because it named the payload
field rather than the indirect target.

