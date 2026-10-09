# M5 s4341 — static branch-field candidate census

## Work unit

Performed one bounded source/data-flow census over the generated
`updateVoiceChannelParamsLarge` / `decodeAndFillVoiceBlock` region in
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`,
plus the retained retail C904 tuple (`s1`, `source_word`, `source_byte`, and
`branch_state`). No build, run, or runtime behavior changed.

## Boundary correction

The generated source places `0x8009C88C` inside
`updateVoiceChannelParamsLarge` as the `filterVoiceSampleBlock` callsite. Its
four arguments are the current loop's stack-derived values:

| Address | Generated operation | Candidate meaning |
|---|---|---|
| `0x8009C870` | `lh a0, 0(s2)` | decoded filter parameter halfword |
| `0x8009C874` | `lh a1, 0(s3)` | decoded delay/filter parameter halfword |
| `0x8009C878` | `addu a2, s1, zero` | current stack output cursor |
| `0x8009C87C` | `addiu a3, sp, 0xA8` | fixed stack output base |

Therefore a probe inserted at `decodeAndFillVoiceBlock` entry but labelled
`0x8009C88C` observes the C904 caller's arguments, not the actual C88C filter
arguments. This explains why the prior field rows cannot by themselves name a
C88C branch-state field.

## C904 candidate table

`decodeAndFillVoiceBlock` saves incoming `a0` as `fp` and has these relevant
non-stack references:

| Candidate | Data-flow role | Retail comparison outcome |
|---|---|---|
| `fp+0x11C8` | bitstream cursor; written back at `0x8009D790` | Not a branch-state match statically; it is an object cursor. |
| `fp+0x18A` | internal bit-accumulator remainder | Not a branch-state match; local decode carry. |
| `fp+0x18C` | internal bit-accumulator/count | Not a branch-state match; local decode carry/count. |
| `fp+0x1A0 + ((fp+0x11C8 >> 3) & 0xFFC)` | repeated backing-table word loads | Best H-port-table-field candidate; the value still needs a runtime join to retail `0x0010/0x3108`. |
| stack `sp+0x10..0x56` | decoded halfwords later supplied to filter/delay helpers | Best selector/decoded-field candidate; no static identity with retail branch state. |

The C904 body has no direct branch-state load. Its only external object data
source is the object-backed bit table; any earlier DMA/ROM producer would have
to populate that table.

## Hypothesis result

| Hypothesis | Result |
|---|---|
| H-port-table-field | Remains the only viable static candidate: the selected backing-table word. Not selected until its runtime value is observed. |
| H-port-selector-field | Unselected by static identity: C88C receives decoded halfwords and stack pointers, but a runtime value join remains possible. |
| H-retail-DMA-field | Not supported by this body: no DMA/ROM read occurs in C904; only the object-backed table is read. An earlier producer is not ruled out. |

The next discriminator is one co-located runtime witness recording cursor/index,
selected table word, and decoded stack halfwords immediately before the actual
C88C filter call, then comparing those values by phase and `s1` to retail C904.

ORIGIN: diagnostic-only static census. No mitigation or game behavior changed.
