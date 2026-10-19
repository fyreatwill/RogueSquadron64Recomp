Single next unit: audit generated conditional-move idioms (`movz`/`movn` and
their recompiler-emitted ternaries) as a whole-tree M3 class.

Competing hypotheses and discriminator:

1. H1: every conditional move preserves the MIPS source/destination semantics
   across the generated C expression and does not clobber a later operand.
2. H2: at least one reachable conditional move has a source/destination or
   zero-register mismatch that changes a value.
3. H3: apparent mismatches are invalid/data-gap fragments, duplicated delay
   slots, or dead conditional material.

Discriminating measurement: create one census script that enumerates every
`movz`/`movn` comment and its generated assignment, reports source,
destination, condition, and function classification, and includes positive
controls for one ordinary conditional move and one known invalid/data-gap
fragment. Every possible result must classify the whole table as H1, H2, or
H3; land a fix only for a concrete reachable mismatch. No runtime build is
planned.

Ground-truth gate: this is a generated-code semantic census, so no retail
writer claim is needed; if a candidate survives as reachable game logic,
consult `tools/oracle/README.md` before adding any runtime instrument.

Run after adding the census script:
`python3 tools/audit_conditional_move.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`

HYPOTHESIS-ID: m3-idiom-class-audit
