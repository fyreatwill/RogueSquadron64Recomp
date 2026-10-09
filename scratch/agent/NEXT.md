# Next work unit (s4393): join exact writers to published task spans

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-semantic-payload-span: semantic PCs write addresses contained in the
  nearest task's published `data_ptr/data_size` span more often than the
  maintenance PCs; this selects semantic payload provenance.
- H-maintenance-payload-span: maintenance PCs have the stronger containment
  rate, so the named semantic stores are setup/maintenance traffic.
- H-transform-or-gap: neither named class is contained, or the task span is
  too small/ambiguous to evaluate; the transform/publication boundary remains
  open and the span model is not yet ground truth.

Discriminating measurement: one oracle build/run retaining the existing
positive control, three phase buckets, task rows, exact writer rows, scalar
mismatch fields, and a bounded table keyed by phase/watch/writer class/value
class that reports whether each writer effective address is in the joined
task's `data_ptr/data_size` span, in its `data_ptr+0x100` field, or outside.
Each possible result above is decided by comparing containment counts/rates for
the semantic PCs (`0x80090DE4`/`0x80090B68`) and maintenance PCs
(`0x80090CA4`/`0x80091078`); invalid pointers, task overflow, or unresolved
size semantics select H-transform-or-gap.

Exact commands:

    extend tools/oracle/rs64_oracle.c with the bounded containment table
    build with tools/oracle/build.sh
    bash scratch/agent/run_s4393_m5_exact_span_containment.sh

Controls: whole-RDRAM positive control must fire and be removed at threshold;
all title/hangar VI origins must be live; valid type-2 rows >= 1,000;
ordinal overflow 0; supported scalar mismatch 0; no mitigation or value
rewrite.
