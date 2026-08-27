# Session 2743 — M5 opaque callback boundary audit

## Selected boundary

The newly audited data-driven edge is the indirect `jalr` at guest PC
`0x80091684` in `musyxSynthFrame`.

## Static source/destination/order table

| Field | Evidence | Result |
|---|---|---|
| Dispatch/key source | `musyxSynthFrame` loads `$a0` from `0x80149928` at `0x80091668`; `$a2` is set to `0x80149730` but is not consumed by the selected target | A scalar callback key is passed; no renderer buffer or synth-output pointer is established |
| Indirect target | `0x801499DC` is initialized by `initN64RspMixer` to `findAndZeroTableSlotMatching` (`0x8000794C`) and loaded into `$v1` at `0x80091670` | The target is named and resolved, not an opaque audio publisher |
| Target read set | `findAndZeroTableSlotMatching` reads four words at `0x8011A8A4`, advancing by four bytes until four entries are checked | The data-driven object is a four-entry callback table |
| Target write set | On equality with `$a0`, the target stores zero at the matching entry (`0x80007968`) | It removes a matching callback registration; it does not copy or transform payload data |
| Ownership/legitimacy | `registerSiCallback` is documented as populating this same four-entry table for the SI polling thread | The destination is SI callback-registration state, not the AI source span or a MORT/voice PCM buffer |
| Ordering | The indirect call occurs after the audio countdown/gate work and before `flushStreamedVoiceBuffers` at `0x800916A8`; no task, AI, queue-publication, or PCM call is ordered through it | The sequence is callback deregistration followed by streamed-voice flush, with no identified renderer-to-AI edge |
| AI join | No read/write of `0x801496B0:0x8014C6B0`, `osAiSetNextBuffer`, `voice+0x140`, or the synth output block occurs in this callback | No complete publication edge |

## Decision

The complete table selects `H-opaque-edge-absent` for this boundary. The
callback key's own writer remains outside this bounded audit, but the named
consumer's complete behavior is registration-table matching and zeroing; an
unresolved scalar writer cannot turn that destination into an audio payload
publication edge. This is static, single-source evidence. No runtime watch,
writeback, remap, or mitigation is authorized.
