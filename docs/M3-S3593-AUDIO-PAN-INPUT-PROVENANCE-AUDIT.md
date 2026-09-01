# M3-S3593 — audio pan-input and selector provenance audit

## Scope and discriminator

Static grep-enumerated audit of `computeVoicePanCoefficients`
(`0x8009C2D0`), all three direct callers, the 16-byte halfword source vector,
and the `voice+0x188` selector lifecycle. A concrete invalid edge would
select H-PanInputsGap; complete coverage without one selects
H-PanInputsComplete; an input-layout mismatch selects H-PanInputsMisread.

## Target contract

The routine takes `a0=voice`, `a1=source`, and audio arguments in `a2/a3`.
It reads eight signed halfwords at source offsets `0x0..0xE`. It reads
`voice+0x188`, shifts it left four, and selects one of two eight-halfword banks
starting at `voice+0x168` or `voice+0x178`. It writes the eight halfwords and
toggles `voice+0x188` with `value ^ 1` at `0x8009C4D0`.

## Caller and source table

| Call site | Function | Voice argument | Source argument | Preparation |
|---|---|---|---|---|
| `0x8009C584` | `updateVoiceChannelParams` | `s6` (incoming `a0`) | `s7` (incoming `a1`) | Four `filterVoiceSampleBlock` and `applyVoiceDelayFilter` iterations |
| `0x8009C8C4` | `updateVoiceChannelParamsLarge` | `s7` | `s6` | Four filter/delay iterations; byte inputs are masked (`0xF`, `0x3F`, `0x7`) while temporary parameters are built |
| `0x8009D778` | `decodeAndFillVoiceBlock` | `fp` (incoming `a0`) | stack `+0x10C` | Four filter/delay iterations over a fixed stack allocation |

These are the complete direct-call set in all generated `funcs_*.c` files.
The first two pass caller-owned vectors; the third passes a stack-local vector.
No caller supplies the selector as an argument.

`computeVoicePanCoefficients` has no source-count or pointer validation. The
source vectors are nevertheless fixed 16-byte layouts: the update routines
advance their four input pairs through fixed 0x1A-stride records, and the
decode path uses its fixed stack vector. `filterVoiceSampleBlock` processes
13 halfwords per pass. `applyVoiceDelayFilter` clamps its delay field to
`0x28..0x78` before storing `voice+0x166`.

## Object-field writers and selector lifecycle

Direct writes to the relevant offsets in `funcs_27.c` are limited to the
expected edges: `applyVoiceDelayFilter` writes `+0x166`,
`renderVoiceAudioBlock` writes `+0x164`, and the pan routine writes the
selected `+0x168` bank and toggles `+0x188`. Other generated-tree matches are
unrelated structures or consumers; no alternate writer to this voice
selector/bank object was found.

`audioMixStereoBlock8` reads `voice+0x188` and selects the current bank or the
bank at `+0x178`, then consumes eight bounded halfword pairs through its eight
indirect calls. The selector lifecycle is therefore a bounded two-bank
toggle. No concrete invalid selector, base, source pointer, or unchecked count
was found.

## Result

H-PanInputsMisread is not supported: the direct call graph and target body
agree on the 16-byte source-vector contract. H-PanInputsGap is not selected:
no concrete invalid caller, source writer, selector, object base, or unchecked
source count was found. H-PanInputsComplete is selected structurally, with
runtime source contents, allocator state, and audio DMA timing still
unproven. No guard or mitigation is warranted.
