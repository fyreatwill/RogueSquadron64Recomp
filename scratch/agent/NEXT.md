# Next work unit (s4349): retail witness for the lattice input-span source

HYPOTHESIS-ID: m5-step9-input-writer-source

Session 4348 resolved `0x8009DB2C` as the legitimate quantized output of
`runVoiceLatticeFilter`, not the semantic source. The next unit is one
qualified retail witness for the input span read through `$t1`/`a1`; the
caller forms it from the voice object's `+0x11C8` base plus an index-derived
`<<3` offset at `0x8009C0E4`.

Competing hypotheses:

- H-input-span-source: the source span itself carries the retained family and
  its writer is the next semantic boundary.
- H-index/base-source: the source span does not carry the family; the relevant
  producer is the `+0x11C8` base/index publication feeding `0x8009C0E4`.
- H-route/alias: the observed source span is reused or alternate-route data;
  its pointer geometry or writer PCs do not match the C904 family path.

Discriminating measurement: phase-gated retail watches must record the
constructed input pointer, its first words, the `+0x11C8` base/index inputs,
and writer PCs/values, while whole-RDRAM, title, hangar, and C904 controls
remain armed. A family value in the source span selects H-input-span-source;
no family in the source but a matching base/index publication selects
H-index/base-source; pointer or writer geometry outside that path selects
H-route/alias.

Commands:

`rg -n -C 80 '0x8009C0E4|0x8009D980|0x8009DB2C|0x11C8' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`

`rg -n -C 12 '0x8009C0E4|0x11C8|decodeAndFillVoiceBlock' docs tools scratch`

Do not change decoder, RSP, AI, or runtime behavior. If the existing oracle
cannot arm the source-span witness with positive controls, document the exact
measurement failure and redesign the witness before building.
