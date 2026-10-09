# Next work unit (s4394): compare writer values with published task words

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-semantic-value: semantic writer source values match the corresponding
  published task-data words more often than maintenance values; this supplies
  the second evidence line for semantic payload provenance.
- H-maintenance-value: maintenance writers have the stronger published-word
  match rate; the address-containment split mislabels the producer.
- H-transform-or-gap: neither class has stable value matches, or the task
  snapshot and store ordinal cannot be joined without overflow; the transform
  boundary remains open.

Discriminating measurement: one oracle build/run retaining the whole-RDRAM
positive control, all three VI buckets, exact task ordinals, exact writer
effective addresses/source values, scalar mismatch validation, and a bounded
phase/watch/writer-class table. For each joined scalar store, read the
corresponding guest word from the published task data span at the store's
effective address and report exact source-value equality, post-store equality,
and unavailable/unaligned cases separately. Semantic-versus-maintenance match
rates decide the hypotheses; task overflow, no-task joins, or unsupported
scalar stores make the result unevaluable rather than a null.

Exact commands:

    extend tools/oracle/rs64_oracle.c with the phase/task-ordinal value table
    build with tools/oracle/build.sh
    bash scratch/agent/run_s4394_m5_published_word_compare.sh

Controls: whole-RDRAM positive control must fire and be removed at threshold;
all title/hangar VI origins must be live; valid type-2 rows >= 1,000; ordinal
overflow 0; supported scalar mismatch 0; no mitigation or value rewrite.
