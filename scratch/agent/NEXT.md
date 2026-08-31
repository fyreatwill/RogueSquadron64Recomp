# NEXT work unit — join qualified title source-writer values

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3460 qualified the repaired title witness: the title entry control
fired and the source-writer table emitted 1,024 rows (768 at `0x800644B0`, 256
at `0x80064524`), all with zero port values. Retail value evidence exists in
the s3458 post-store arm, but the source/value join is not yet qualified.

Competing hypotheses and discriminating outcomes:

- `H-PortRetailParity`: joined writer PCs and values match; the source edge is
  closed.
- `H-PortZeroLegitimate`: writer PCs match and retail also stores zero at the
  joined ordinals; zero is legitimate at this boundary.
- `H-PortWrongValue`: writer PCs match but retail stores nonzero values; the
  first value divergence selects the missing producer contract.
- `H-PortWriterRoute`: ordered writer PCs differ or a side is absent; the
  route/ordering boundary remains unresolved.

Before building, use the existing qualified retail post-store rows and the
port retry rows as ground-truth inputs; do not add another field. Build:
`cmake --build build --config Debug --target RogueSquadron64Recomp`
and run the existing title-writer recipe with a new output directory:
`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_WRITER_PARITY=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 tools/probe.sh scratch/agent/s3461_m5_source_value_join 45 0.5`.
The discriminator is the first phase/PC/ordinal writer/value join against the
retail table: matching PCs and values select `H-PortRetailParity` or
`H-PortZeroLegitimate`; matching PCs with a first nonzero retail value select
`H-PortWrongValue`; missing or reordered PCs select `H-PortWriterRoute`.
Do not alter audio waits, slots, dispatch, clear behavior, or PCM writeback.
