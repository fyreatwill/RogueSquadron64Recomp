# Next work unit (s4350): retail witness for the caller base/index publication

HYPOTHESIS-ID: m5-step9-base-index-publication

Session 4349 captured 128 hangar-phase C904 input spans under a qualified
whole-RDRAM watch. Their observed writers were bzero (`0x8002A0B8/BC`) and
`runVoiceLatticeFilter` output (`0x8009DB2C`), with no captured exact
`0x0010/0x3108` family value. The next unit is one qualified retail witness
for the caller's base/index inputs at `0x8009C0D8..0x8009C0E8`.

Competing hypotheses:

- H-index/base-source: the `+0x11C8` cursor and `+0x198` base publication feed
  the source pointer and carry the retained family or its selector state.
- H-span-reuse: the base/index values are ordinary ring-buffer scheduling;
  the semantic family is introduced by a later selector/decoder path.
- H-route/alias: the C904 input pointer is not formed from the expected object
  fields, or its writer geometry belongs to another route.

Discriminating measurement: phase-gated retail watches must record C904's
object, `+0x11C8` cursor, `+0x198` base, constructed input pointer, and the
writer PCs/source values for both fields. A retained-family value or stable
retail-correlated selector in those fields selects H-index/base-source;
ordinary ring-buffer progression with no family selects H-span-reuse; a
pointer/base mismatch or alternate writer geometry selects H-route/alias.

Static context:

`rg -n -C 80 '0x8009C0D8|0x8009C0E4|0x11C8|0x198\\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`

`rg -n -C 12 '0x8009C0D8|0x8009C0E4|0x11C8|0x198|decodeAndFillVoiceBlock' docs tools scratch`

Use one oracle build/run with whole-RDRAM write control, C904 witness, and
phase-gated watches for object `0x80153420` fields `+0x11C8` and `+0x198`.
Do not change decoder, RSP, AI, or runtime behavior. If the existing oracle
cannot arm both field watches with positive controls, document the exact
measurement failure and redesign the witness before building.
