# M5 s4596: voice `+0x34` static census

The selected bad call is `musyxRenderVoiceSamples` at `0x800903F0`, where
`s1 = 0x801724C0`, `a3 = *(s1 + 0x34)`, and the delay slot computes
`a1 = a3 + (((a1 & ~3) << 1))`. The generated body has no string, ROM, or
tag translation on this path.

## Stores to a voice record `+0x34`

| PC | instruction | role | static value provenance |
|---|---|---|---|
| `0x800921E8` | `sw v1, 0x34(a0)` | `musyxInitVoiceFromSample` | `a0` is the indexed voice slot; `v1` is `*(sampleDesc + 4)` |
| `0x80090C80` | `sw v1, 0x34(s1)` | `musyxKeyOnVoice` | `s1` is the destination voice; `v1` is `*(s0 + 0x38)` |

The first writer is the sample initialization path and the second is the
key-on copy path. Both are pointer-copy operations in the static source; no
static path produces printable ASCII. Earlier runtime qualification found
only B0xxxxxx pointer values at `0x800921E8` in retail. The port's `late`
value therefore remains a runtime input/translation defect, not a legitimate
tag.

## Caller uses

Within `musyxRenderVoiceSamples` (`0x8008FFAC`), the four
`fillSampleStreamRange` calls use `s1+0x34` directly:

| call PC | load | operand construction |
|---|---|---|
| `0x8009024C` | `lw a3, 0x34(s1)` at `0x8009023C` | `a1 = a3 + (aligned block index << 3) + 0x100`; `a3 += 0x100` |
| `0x800902CC` | `lw a3, 0x34(s1)` at `0x800902BC` | same form |
| `0x8009039C` | `lw a3, 0x34(s1)` at `0x80090390` | `a1 = a3 + (aligned sample offset << 1)` |
| `0x800903F0` | `lw a3, 0x34(s1)` at `0x800903E4` | `a1 = a3 + (aligned sample offset << 1)` |

The `s0+0x34` stores at `0x8009025C`, `0x800903AC`, `0x80090484`,
`0x800904D0`, `0x800905F0`, and `0x80090638` update the output/render record,
not the selected `s1` voice. Other `+0x34` loads in this function are reads of
that output record. No unclassified store or caller-side builder remains in
the preserved generated source.

## Result

H-writer/input is selected over H-builder: the caller only loads and offsets
the voice field, while the only relevant writers are the two named pointer
copies. The unresolved boundary is which runtime store/input supplies
printable data to the selected voice before `0x800903F0`. The next measurement
must attribute all port stores to physical `0x1724F4` (guest `0x801724F4`) with
a positive-control watch; no mitigation is justified by this census.
