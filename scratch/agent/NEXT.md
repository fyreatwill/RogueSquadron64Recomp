# NEXT work unit (s1010)

s1009 (static retail-ROM audit): the original Factor 5 stream stores color at
record `+0x10` but the shaded emitter at PC `0x1740` never reads that word.
Generated output preserves the instruction sequence; the fixup script does not
remove a color read. `H-original-omits-color` is selected. No mitigation was
made.

HYPOTHESIS-ID: m4-zero-shade-emission-constant

## One work unit

Trace the intended shade-record semantics from the retail Factor 5 emitter
through the GLideN64 reference and generated `TriGen`/triangle consumers.
Static audit only; no build/run required. Do not edit generated output.

Competing hypotheses and discriminating measurement:

- `H-intentional-sentinel`: the emitter intentionally writes the fixed shade
  sentinel for an unlit/no-lighting mode, and the consumer is correct.
- `H-missing-lighting-source`: a lighting/vector source should populate shade,
  but the original emitter selects or preserves the sentinel incorrectly.
- `H-record-consumer-mismatch`: the emitter writes a valid shade record, but
  RT64 or the downstream triangle consumer reads a different record layout.

Discriminator: map the original `0x1740` shade stores and their vector
producers to the reference's `PrepareVtxData`/triangle record fields, then map
the generated `TriGen` output and RT64 triangle read offsets. A reference
no-lighting path that intentionally yields the sentinel selects
`H-intentional-sentinel`; a valid lighting source absent or bypassed selects
`H-missing-lighting-source`; matching producer data with a downstream offset
discrepancy selects `H-record-consumer-mismatch`.

The `slotDispatcherIter` sp-guard soak crashed at a different site before
producing a guard record; it remains a separate queued investigation and is
not this work unit.
