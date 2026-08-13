# NEXT work unit (systematic rs_malloc/free-list writer audit)

HYPOTHESIS-ID: m3-rsmalloc-freelist-writer

The s788 source audit separated the s786 allocator failure from s787's
host-only zero-height tile-copy assertion. Do not run another reachability
soak yet and do not add a guard from either crash.

## Competing hypotheses

- H-freelist-writer: a game/runtime writer creates the malformed free-list
  header or pointer consumed by `rs_malloc`. Prediction: source enumeration
  finds a writer capable of producing zero-header/`0x80000000` state, and an
  existing trace attributes the same value to that writer.
- H-rsmalloc-consumer: the allocator's own free-list traversal is the defect,
  with no upstream writer identified. Prediction: all suspicious values enter
  `rs_malloc` from already-corrupt RDRAM and no writer site explains them.
- H-independent-prechain: s785/s786/s787 are unrelated consumers. Prediction:
  the writer audit finds no common value or writer, while RT64's zero-height
  input remains confined to its two host call sites.

## Discriminating measurement

One bounded source audit, before any build: enumerate every `rs_malloc`/`rs_free`
free-list header/pointer write and every zero-header or loop-back guard in the
active generated source and fixup script; map each candidate to the existing
`[fl-zero-fault]`/header trace values. H-freelist-writer wins only if the
writer and legitimacy are identified by both source and trace. H-rsmalloc-
consumer wins if the source shows only reads/consumption at the bad value and
no writer explains it. H-independent-prechain wins if the audit confirms no
shared writer/value and keeps the RT64 input disjoint. Any result that cannot
name a writer remains unclassified and forbids mitigation.

## Exact audit

1. Locate active generated `funcs_*.c`, fixup rules, and build provenance.
2. Enumerate `rs_malloc`/`rs_free` writes to free-list headers and all
   fixup-installed guards; separately retain the two RT64 tile-copy call sites
   as the independent consumer control.
3. For each suspicious value, map the guest address/value writer and classify
   legitimate versus wild. No code change or mitigation is allowed unless a
   writer is identified.
4. If no writer can be tied to the trace, record the class as unclassified and
   choose the highest-information writer probe; do not run a reachability soak.

Expected outcomes: a source-and-trace writer match selects H-freelist-writer;
allocator-only consumption selects H-rsmalloc-consumer; disjoint consumers
with no shared value selects H-independent-prechain. A missing active source
or unmapable trace blocks classification rather than justifying a guard.
