# M3-S3590 — audio selector source-field audit

## Work unit

Audit every generated writer of the source fields feeding the audio-record
selector stores: `+0x64` for `musyxKeyOnVoice`, and `+0x58/+0x59` for
`tickAudioChannel`. The discriminator was whether every writer and record
base could be shown bounded or sentinel-safe, or whether a concrete invalid
writer/value could be identified.

## Census

The relevant MusyX voice/channel code is in `funcs_22.c` through `funcs_24.c`;
stack-frame offsets and unrelated structures were excluded. The `+0x64`
writers are cleanup/reaping stores of `-1` at `0x800897B8`, `0x80089814`,
`0x80089A9C`, `0x8008DA68`, `0x8008DB80`, and `0x8008DC84`; the active-record
store at `0x8008C1C4`; render-loop stores at `0x800902D4`, `0x80090400`,
`0x80090520`, and `0x80090668`; envelope stores at `0x8008F5AC` and
`0x8008F5D0`; the release zero at `0x800922AC`; and the voice-attack envelope
store at `0x80092358`.

The `+0x58` writers are render/sample stores at `0x8009030C`, `0x80090340`,
`0x80090420`, `0x80090454`, `0x800905A0`, `0x800905D4`, `0x800906A0`,
`0x800906C0`, and `0x800906F4`; envelope/timing stores at `0x8008F544` and
`0x8008F5B4`; the release store at `0x800922B8`; and the voice-attack store at
`0x80092364`. They derive values from `+0x48`, `+0x30`, `+0x2A`, or the
masked voice argument. There is no independent `sb` writer at `+0x59`;
halfword/word stores at `+0x58` cover that byte.

The readers are `tickAudioChannel` at `0x8008BD40`/`0x8008BD44`, which loads
`+0x58/+0x59` and publishes them to `+0x4E/+0x4F`, and `musyxKeyOnVoice` at
`0x80090B6C`/`0x80090C4C`, which loads `+0x64` and publishes it to `+0x4E`.
The record bases and known 0x17C voice stride remain consistent with the
generated code.

## Result

`H-SourceFieldsUnsafe` was not selected: no concrete invalid source
writer/value was identified. `H-SourceFieldsMisread` was not selected: the
reader offsets and enclosing bases are structurally consistent. The bounded
hypothesis also remains unselected because the render/timing-derived values
span distinct record layouts and this static census does not prove one global
selector range or runtime allocator/lifetime contract.

This is a single-source static result. It closes writer enumeration but does
not establish runtime values reaching the selectors. No guard or mitigation is
authorized by this work unit.
