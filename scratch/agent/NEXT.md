# Next work unit (s4346): C904 input/selector attribution

HYPOTHESIS-ID: m5-step9-retail-input-selector-boundary

s4345 qualified the retail candidate writers. The phase-gated `0x8009C9EC`
and `0x8009CB0C` stores are `sh v0,0x18C(s8)` writes to object
`0x801535AC`, with varied small source values; they are not stores of the
retained C904 `0x0010/0x3108` family. The next unit moves one boundary earlier,
to the C904 low-index input and its immediate caller transformation.

Competing hypotheses:

- H-C904-reader: C904 directly reads the semantic branch family through its
  `s1`-indexed low-field load; reader PC attribution will show `0x0010/0x3108`.
- H-C904-input-selector: the immediate caller computes/selects the family
  before entry; its source registers and input values will carry the family
  while the C904 read is only a consumer.
- H-earlier-source: neither reader nor immediate caller carries the family;
  the semantic producer is earlier in the voice/object input path.

Discriminating measurement: add one batched oracle reader witness for the
physical low `s1`-indexed field read at C904, plus the immediate caller/input
transformation. Record reader PC, `s1`, loaded value, previous PC, `$v0`,
`$a1`, and the retained `0x0010/0x3108` comparison. A family-valued reader
selects H-C904-reader; a family-valued caller/input row with a non-family
reader selects H-C904-input-selector; neither selects H-earlier-source.

Before building, inspect the C904 instruction window in the existing generated
symbol/decomp output to identify the exact load PC and caller input edge. Add
the witness to `tools/oracle/rs64_oracle.c`, rebuild with:

`env CORE_SRC="/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core" bash tools/oracle/build.sh`

Run one 180-second retail oracle from the repo root with the debug core, ROM,
Rice video, the standard start schedule, whole-RDRAM watch, title/hangar VI
trace, C904 watch, and the new reader/input witness. Require visible positive
controls: whole-RDRAM writes, title `0x00790400`, hangar `0x006AB400`, and C904
execution. Do not alter decoder/RSP/AI behavior or add a mitigation.
