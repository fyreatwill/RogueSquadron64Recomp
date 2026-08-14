# NEXT work unit (s994)

HYPOTHESIS-ID: m4-zero-shade-writer

## One work unit

Perform one bounded static classification of every exact-target generated
store PC recorded by s993. Map each PC to its fresh generated C function,
assignment expression, base/offset provenance, and value expression. Do not
build, rerun, hand-edit generated files, or add a mitigation.

Competing hypotheses and discriminating measurement:

- H-direct-expected: target stores have bounded, semantically expected value
  sources.
- H-direct-wild: a target store's value expression is an unbounded or
  corrupted pointer/state field.
- H-copy-shaped: target stores are coherent source copies whose bad value must
  originate upstream.

The discriminating measurement is a complete PC-to-assignment/value-source
table covering all 39 phase-4 and 59 phase-6 exact-target sites from s993.
An incomplete PC set is invalid. The s993 run does not capture assigned
values, so do not infer legitimacy from its address records.

## Exact commands

Extract all target records and deduplicate by phase, guest PC, and physical
address from the bounded capture:

`perl -ne 'if (/\\[vtx-generated-write-control\\].*phase=(4|6).*pc=(0x[0-9A-Fa-f]+).*phys=(0x[0-9A-Fa-f]+)/) { $a=hex($3); print if (($a>=0x726200 && $a<0x726C50) || ($a>=0x732A10 && $a<0x73E3B0)); }' scratch/agent/probe_s993/run.log`

For every emitted PC, locate the preceding guest-PC comment and assignment in
`../N64Recomp/RecompiledFuncs/funcs_*.c` with `rg`, then cross-check the
function/semantic name in the companion symbol/decomp trees with `rg`. Count
all 98 sites and classify the RHS as constant/bounded state, wild pointer or
index-derived state, or coherent source copy. Record the table or its compact
classification in the s994 ledger entry.

No runtime controls are needed for this static unit. If fewer than 98 unique
phase/site records can be mapped, report the missing PCs and do not select a
value-legitimacy hypothesis.
