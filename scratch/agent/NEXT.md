# Next work unit (s4351): retail witness for the stable base-buffer producer

HYPOTHESIS-ID: m5-step9-base-buffer-producer

Session 4350 passed the retail oracle controls and found stable base
`0x801B2C60` from object `0x80153420+0x198`; the cursor at `+0x11C8` is an
ordinary advancing ring index written by `0x8009D790`. The next unit is one
qualified retail witness for the contents and producer of that stable base
buffer, joined to the cursor-indexed C904 input pointer.

Competing hypotheses:

- H-buffer-source: a writer into the stable base-buffer span supplies the
  retained `0x0010/0x3108` family or its selector state.
- H-selector-decode: the base buffer is ordinary ring data with no retained
  family; the semantic divergence is introduced after pointer construction.
- H-route-alias: the C904 input pointer is not formed from the stable base
  plus cursor geometry, or the observed base belongs to another route.

Discriminating measurement: phase-gated retail watches must record C904's
object, cursor, base, constructed input pointer, base-buffer words, and the
writer PCs/source values for the base-buffer span. A family-valued writer or
family-valued base-buffer word selects H-buffer-source; stable buffer data
with no family selects H-selector-decode; pointer/base mismatch selects
H-route-alias.

Static context:

`rg -n -C 100 '0x8009C0D8|0x8009C0E4|0x11C8|0x198\\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`

`rg -n -C 20 '0x8009C0D8|0x8009C0E4|0x11C8|0x198|decodeAndFillVoiceBlock' docs tools scratch`

Use one oracle build/run with whole-RDRAM write control, C904 witness, and
phase-gated watches for stable base `0x801B2C60` plus the C904-derived input
spans. Extend the reusable all-writer store capture only as needed to record
base-buffer writer PCs/source values; retain title/hangar/C904 controls. Do
not change decoder, RSP, AI, or runtime behavior. If the dynamic base span
cannot be safely bounded from the C904 rows, document that instrument gap and
redesign the witness before building.
