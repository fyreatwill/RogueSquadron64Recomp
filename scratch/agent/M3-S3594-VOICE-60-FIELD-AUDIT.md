# Session 3594 — MusyX voice `+0x60` field audit

## Scope and discriminator

The generated tree was searched for every `MEM_[BHW]` access at `+0x60`
(and the adjacent `+0x62` halfword) in the audio overlays. The selected
class was the MusyX voice-record field, excluding the unrelated cutscene,
stack-frame, and song/channel uses. The discriminator was a complete
writer → consumer → base/layout → lifetime/bound chain: a concrete invalid
edge selects `H-NextClassGap`; complete structural coverage selects
`H-NextClassComplete`; mixed or missing layouts select
`H-NextClassUnevaluable`.

## Candidate ranking

| Candidate | Why it was considered | Result |
|---|---|---|
| MusyX voice `+0x60` | Reset writers, envelope update, key-on reads, and render accesses | Selected |
| MusyX voice `+0x30..+0x40` | Dense initialization/render field family | Deferred; mixed word/halfword aliases |
| Channel state `+0x24` | Broad macro and tick reuse | Deferred; weak object identity |

## Site census

| Site/function | Operation | Effective object evidence | Classification |
|---|---|---|---|
| `soundMacroOpPlaySampleKeymap` | writes and later reads `+0x60` | channel/voice state pointer held in `r21`; macro path, not proven to be the MusyX render voice base | channel-layout alias |
| `tickAudioChannel` | writes `+0x60`, later reads it | channel tick record in the `0x88`-stride audio-channel family | channel-layout writer/consumer |
| `advanceVolumeFadeEnvelope` | clears, reads, and updates `+0x60` | caller-provided envelope/voice pointer; no local slot bound in the body | envelope-layout writer/consumer; bound open |
| `musyxRenderVoiceSamples` | writes halfword `+0x60`; reads adjacent `+0x62` | render voice pointer is carried through the MORT voice loop; field is consumed as a pair of halfwords | render-layout writer; not word-compatible by proof |
| `musyxKeyOnVoice` | reads halfword `+0x60` on each key-on branch | source voice descriptor from the voice table; destination command record is a different pointer | source-layout consumer |
| `musyxStartVoiceRelease` | clears word `+0x60` | voice slot computed from global voice base plus masked index | reset writer; index is masked but slot-count proof is outside the function |
| `musyxTriggerVoiceAttack` | clears word `+0x60` | voice slot computed from global voice base plus 16-bit index | reset writer; no local upper-bound proof |
| `beginVoiceFadeRelease` | clears word `+0x60` | voice slot pointer derived by its caller | reset writer; caller/lifetime edge open |

The remaining `+0x60` hits in `funcs_25.c`/`funcs_26.c` are stack-frame
spill slots or song/streamed-channel locals, and the `funcs_27.c` hits are
cutscene/positional-audio records or stack-frame slots. They are not evidence
for the MusyX voice-record field without an effective-address join.

## Result

The field spelling is not one statically identifiable object field. The
generated code exposes at least four layouts: macro/channel state, envelope
state, the render voice halfword pair, and the source voice descriptor used by
key-on. Even within the MusyX voice path, the reset writers store a word while
the render/key-on paths use halfwords, and the index masks do not prove a
voice-table upper bound at each writer. No site provides a complete
writer-to-consumer lifetime chain or a concrete bad runtime value.

This selects `H-NextClassUnevaluable`, not `H-NextClassGap`: the missing
discriminator is object identity and caller-proven bounds, rather than an
observed invalid store. No guard or runtime change is authorized.

Independent evidence lines are (1) the generated access census and effective
base calculations, and (2) the distinct function-level roles and stride/index
patterns in the companion MusyX voice code. Neither line supplies runtime
allocator contents or DMA timing.

ORIGIN: the visible `+0x60` writers are `musyxStartVoiceRelease`,
`musyxTriggerVoiceAttack`, `beginVoiceFadeRelease`, `advanceVolumeFadeEnvelope`,
`tickAudioChannel`, and `musyxRenderVoiceSamples`. Their zero/reset values are
legitimate state transitions; any wild value or stale lifetime remains
unobserved. No mitigation was added.
