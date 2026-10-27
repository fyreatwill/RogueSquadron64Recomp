# Session 6505 EBC writer audit

The audit was offline; no build or game run was performed.

## Census

- `s6500_wcount[4]` is declared once in `funcs_9.c`; there is no assignment,
  clear, or second declaration of the counter array in the generated file or
  the s6500-s6503 fixups.
- `s6500_note_writer` is defined once. Its only counter mutation is
  `s6500_wcount[i]++`.
- The live EBC store at 0x80042EBC calls `s6500_note_writer` exactly once.
- EC4 appears twice because N64Recomp emits the 0x80042EC4 delay slot both
  before the unconditional `goto L_8004301C` and at the fallthrough label.
  The second copy is unreachable C; it is not a second live writer.
- The other live instrumented stores are DB4 at 0x800426D8, DB4 at
  0x80042820, DB4 at 0x80042DB4, and DC0 at 0x80042DC0. Each calls the helper
  on its in-range path.

## Control-flow result

The post snapshot is at the return tail of `binPolygonIntoTerrainGrid`
(0x80042B44/0x80042B4C). The EBC and EC4 stores are in the later
`streamTerrainGridCellsByDistance` function (0x80042EBC/0x80042EC4). The
probe therefore joins state across a function boundary. Guest-thread ID
equality does not make file-scope cumulative counters a safe join key: they
are shared mutable host state, and s6502 already showed the generated calls
can execute on different host threads.

## Hypothesis decision

- H-duplicate: refuted by the complete declaration/assignment census.
- H-uninstrumented: refuted for EBC; its only live generated store is wrapped.
- H-boundary: selected as the remaining structural defect. The snapshot and
  writer are separate calls joined through unsynchronized cumulative globals;
  an unsigned negative delta is invalid evidence even when sampled guest IDs
  match.

The next probe must replace the cumulative counter join with a per-invocation
key captured at the actual stream interval, while retaining dd1 nonempty and
dd4 EMPTY positive controls in one run.
